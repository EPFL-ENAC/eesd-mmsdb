<template>
  <q-page class="q-pa-md">
    <q-card class="q-pa-md">
      <div class="text-h4">Line of minimum trace</div>
      <q-card-section>
        <div class="text-h6">Upload slice image</div>
        <q-file
          v-model="uploadedImage"
          accept="image/*"
          filled
          label="Select an image"
          @update:model-value="onFileSelected"
          class="q-mt-md"
        >
          <template v-slot:prepend>
            <q-icon name="attach_file" />
          </template>
        </q-file>
      </q-card-section>

      <q-card-section v-show="imageLoaded">
        <div class="canvas-container q-mb-md">
          <canvas
            ref="canvasRef"
            @mousedown="onCanvasMouseDown"
            @mousemove="onCanvasMouseMove"
            @mouseup="onCanvasMouseUp"
          />
        </div>

        <div class="text-h6 q-mb-md">Parameters</div>

        <div class="row q-col-gutter-md q-mb-md">
          <div class="col-md-6 col-sm-6 col-xs-12">
            <div class="text-subtitle2 q-mb-xs">Real length (in cm)</div>
            <q-input
              v-model.number="sliceStore.realLength"
              type="number"
              filled
              dense
            />
          </div>

          <div class="col-md-6 col-sm-6 col-xs-12">
            <div class="text-subtitle2 q-mb-xs">Real height (in cm)</div>
            <q-input
              v-model.number="sliceStore.realHeight"
              type="number"
              filled
              dense
            />
          </div>
        </div>

        <div class="row q-col-gutter-md">
          <div class="col-md-3 col-sm-6 col-xs-12">
            <div class="text-subtitle2 q-mb-xs">Start X</div>
            <q-slider
              v-model="startX"
              :min="0"
              :max="imageWidth"
              :step="1"
              label
            />
          </div>

          <div class="col-md-3 col-sm-6 col-xs-12">
            <div class="text-subtitle2 q-mb-xs">Start Y</div>
            <q-slider
              v-model="startY"
              :min="0"
              :max="imageHeight"
              :step="1"
              label
            />
          </div>

          <div class="col-md-3 col-sm-6 col-xs-12">
            <div class="text-subtitle2 q-mb-xs">End X</div>
            <q-slider
              v-model="endX"
              :min="0"
              :max="imageWidth"
              :step="1"
              label
            />
          </div>

          <div class="col-md-3 col-sm-6 col-xs-12">
            <div class="text-subtitle2 q-mb-xs">End Y</div>
            <q-slider
              v-model="endY"
              :min="0"
              :max="imageHeight"
              :step="1"
              label
            />
          </div>
        </div>

        <div class="row q-col-gutter-md q-mb-md">
          <div class="col-md-6 col-sm-6 col-xs-12">
            <div class="text-subtitle2 q-mb-xs">Analysis Type</div>
            <q-select
              v-model="analysisType"
              :options="analysisTypeOptions"
              filled
              dense
            />
          </div>

          <div class="col-md-6 col-sm-6 col-xs-12">
            <div class="text-subtitle2 q-mb-xs">Interface Weight</div>
            <q-slider
              v-model="interfaceWeight"
              :min="0.1"
              :max="1"
              :step="0.01"
              label
              :marker-labels="[{value: 0.1, label: '0.1'}, {value: 1, label: '1'}]"
            />
          </div>
        </div>

        <div class="q-mt-md">
          <q-btn
            color="primary"
            label="Compute Lines"
            @click="computeLine"
            :loading="lineStore.loading"
            :disable="!canCompute"
            icon="calculate"
          />
        </div>

        <div v-if="lineStore.result?.total_length" class="q-mt-md">
          <div class="text-subtitle2 q-mt-md">Total length</div>
          <div>{{ lineStore.result.total_length.toFixed(2) }} cm</div>
        </div>

        <q-banner v-if="!lineStore.result?.success && lineStore.result?.error" class="bg-negative text-white">
          <template v-slot:avatar>
            <q-icon name="error" />
          </template>
          {{ lineStore.result.error }}
        </q-banner>

        <q-banner v-if="lineStore.error" class="bg-negative text-white q-mt-md">
          <template v-slot:avatar>
            <q-icon name="error" />
          </template>
          {{ lineStore.error }}
        </q-banner>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { useLineStore } from '../stores/line';
import { useSliceStore } from '../stores/slice';

const lineStore = useLineStore();
const sliceStore = useSliceStore();

const uploadedImage = ref<File | null>(null);
const canvasRef = ref<HTMLCanvasElement | null>(null);
const imageLoaded = ref(false);
const imageWidth = ref(0);
const imageHeight = ref(0);

const startX = ref(0);
const startY = ref(0);
const endX = ref(500);
const endY = ref(500);
const analysisTypeOptions = [
  { label: 'Vertical joints', value: 0 },
  { label: 'Horizontal bed joints', value: 1 },
  { label: 'Wall leaf connections', value: 2 },
];
const interfaceWeight = ref(0.1);
const analysisType = ref(analysisTypeOptions[0]);

const isDrawing = ref(false);
const ctx = ref<CanvasRenderingContext2D | null>(null);

const canCompute = computed(() => {
  return imageLoaded.value &&
    uploadedImage.value &&
    startX.value >= 0 && startX.value <= imageWidth.value &&
    startY.value >= 0 && startY.value <= imageHeight.value &&
    endX.value >= 0 && endX.value <= imageWidth.value &&
    endY.value >= 0 && endY.value <= imageHeight.value;
});

const onFileSelected = (file: File | null) => {
  if (!file) {
    imageLoaded.value = false;
    return;
  }

  const img = new Image();
  img.onload = async () => {
    imageWidth.value = img.width;
    imageHeight.value = img.height;

    await nextTick();

    if (canvasRef.value) {
      canvasRef.value.width = img.width;
      canvasRef.value.height = img.height;

      ctx.value = canvasRef.value.getContext('2d');
      if (ctx.value) {
        ctx.value.drawImage(img, 0, 0);
        drawLine();
      }
    }

    imageLoaded.value = true;

    startX.value = Math.floor(img.width / 2);
    startY.value = 0;
    endX.value = Math.floor(img.width / 2);
    endY.value = img.height;
  };

  img.src = URL.createObjectURL(file);
};

const getCanvasCoordinates = (event: MouseEvent) => {
  if (!canvasRef.value) return { x: 0, y: 0 };

  const rect = canvasRef.value.getBoundingClientRect();
  const scaleX = canvasRef.value.width / rect.width;
  const scaleY = canvasRef.value.height / rect.height;

  const x = Math.round((event.clientX - rect.left) * scaleX);
  const y = Math.round((event.clientY - rect.top) * scaleY);

  return { x, y };
};

const onCanvasMouseDown = (event: MouseEvent) => {
  if (!canvasRef.value) return;

  const coords = getCanvasCoordinates(event);

  if (!isDrawing.value) {
    startX.value = coords.x;
    startY.value = coords.y;
    endX.value = coords.x;
    endY.value = coords.y;
    isDrawing.value = true;
  }
};

const onCanvasMouseMove = (event: MouseEvent) => {
  if (!canvasRef.value || !isDrawing.value) return;

  const coords = getCanvasCoordinates(event);

  endX.value = coords.x;
  endY.value = coords.y;
};

const onCanvasMouseUp = () => {
  isDrawing.value = false;
};

const redrawCanvas = () => {
  if (!canvasRef.value || !ctx.value || !uploadedImage.value) return;

  const img = new Image();
  img.onload = () => {
    if (ctx.value) {
      ctx.value.clearRect(0, 0, canvasRef.value!.width, canvasRef.value!.height);
      ctx.value.drawImage(img, 0, 0);
      drawLine();
      drawResults();
    }
  };
  img.src = URL.createObjectURL(uploadedImage.value);
};

const drawLine = () => {
  if (!ctx.value) return;

  ctx.value.beginPath();
  ctx.value.moveTo(startX.value, startY.value);
  ctx.value.lineTo(endX.value, endY.value);
  ctx.value.strokeStyle = '#aaaaaa';
  ctx.value.lineWidth = 4;
  ctx.value.setLineDash([5, 5]);
  ctx.value.stroke();

  // Draw start and end points
  ctx.value.beginPath();
  ctx.value.arc(startX.value, startY.value, 10, 0, 2 * Math.PI);
  ctx.value.fillStyle = '#ff0000';
  ctx.value.fill();

  ctx.value.beginPath();
  ctx.value.arc(endX.value, endY.value, 10, 0, 2 * Math.PI);
  ctx.value.fillStyle = '#0000ff';
  ctx.value.fill();
};

const drawResults = () => {
  if (!ctx.value || !lineStore.result?.path_coordinates) return;

  ctx.value.beginPath();
  ctx.value.strokeStyle = '#00d000';
  ctx.value.lineWidth = 8;
  ctx.value.setLineDash([]);

  lineStore.result.path_coordinates.pixel_coordinates.forEach((point: [number, number], index: number) => {
    if (index === 0) {
      ctx.value!.moveTo(point[0], point[1]);
    } else {
      ctx.value!.lineTo(point[0], point[1]);
    }
  });

  ctx.value.stroke();
}

const computeLine = async () => {
  if (!uploadedImage.value || !canCompute.value) return;

  await lineStore.computeLine({
    startX: startX.value,
    startY: startY.value,
    endX: endX.value,
    endY: endY.value,
    image: uploadedImage.value,
    realLength: sliceStore.realLength,
    realHeight: sliceStore.realHeight,
    analysisType: (analysisType.value as typeof analysisTypeOptions[0]).value,
    interfaceWeight: interfaceWeight.value,
    boundaryMargin: sliceStore.boundaryMargin,
  });
};

onMounted(() => {
  if (sliceStore.sliceImageData) {
    uploadedImage.value = new File([new Blob([sliceStore.sliceImageData])], 'slice_image.png', { type: 'image/png' });
    onFileSelected(uploadedImage.value);
  }
});

watch(() => sliceStore.sliceImageData, (newData) => {
  if (newData) {
    uploadedImage.value = new File([new Blob([newData])], 'slice_image.png', { type: 'image/png' });
    onFileSelected(uploadedImage.value);
  }
});

watch([startX, startY, endX, endY, () => lineStore.result], () => {
  if (imageLoaded.value) {
    redrawCanvas();
  }
});
</script>

<style scoped>
.canvas-container {
  overflow: auto;
  position: relative;
  display: flex;
  justify-content: center;
}

canvas {
  max-width: 500px;
  height: auto;
  border: 1px solid #ccc;
  border-radius: 8px;
}

pre {
  background-color: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
