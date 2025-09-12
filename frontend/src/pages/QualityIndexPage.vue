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
        <div class="canvas-container flex justify-center" style="position: relative; display: inline-block;">
          <canvas
            ref="canvasRef"
            @mousedown="onCanvasMouseDown"
            @mousemove="onCanvasMouseMove"
            @mouseup="onCanvasMouseUp"
          />
        </div>

        <div class="text-h6 q-mb-md">Parameters</div>

        <div class="row q-gutter-md">
          <div class="col-md-2 col-sm-5 col-xs-12">
            <div class="text-subtitle2 q-mb-xs">Start X</div>
            <q-slider
              v-model="startX"
              :min="0"
              :max="imageWidth"
              :step="1"
              label
            />
          </div>

          <div class="col-md-2 col-sm-5 col-xs-12">
            <div class="text-subtitle2 q-mb-xs">Start Y</div>
            <q-slider
              v-model="startY"
              :min="0"
              :max="imageHeight"
              :step="1"
              label
            />
          </div>

          <div class="col-md-2 col-sm-5 col-xs-12">
            <div class="text-subtitle2 q-mb-xs">End X</div>
            <q-slider
              v-model="endX"
              :min="0"
              :max="imageWidth"
              :step="1"
              label
            />
          </div>

          <div class="col-md-2 col-sm-5 col-xs-12">
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
      </q-card-section>
    </q-card>

    <!-- Results -->
    <q-card v-if="lineStore.result" class="q-mt-md">
      <q-card-section>
        <div class="text-h6 q-mb-md">Computation Result</div>
        <pre>{{ JSON.stringify(lineStore.result, null, 2) }}</pre>
      </q-card-section>
    </q-card>

    <!-- Error Display -->
    <q-banner v-if="lineStore.error" class="bg-negative text-white q-mt-md">
      <template v-slot:avatar>
        <q-icon name="error" />
      </template>
      {{ lineStore.error }}
    </q-banner>
  </q-page>
</template>

<script setup lang="ts">
import { useLineStore } from '../stores/line';

const lineStore = useLineStore();

// File and image handling
const uploadedImage = ref<File | null>(null);
const canvasRef = ref<HTMLCanvasElement | null>(null);
const imageLoaded = ref(false);
const imageWidth = ref(0);
const imageHeight = ref(0);

// Line parameters
const startX = ref(0);
const startY = ref(0);
const endX = ref(100);
const endY = ref(100);

// Canvas interaction
const isDrawing = ref(false);
const ctx = ref<CanvasRenderingContext2D | null>(null);

// Computed properties
const canCompute = computed(() => {
  return imageLoaded.value &&
    uploadedImage.value &&
    startX.value >= 0 && startX.value <= imageWidth.value &&
    startY.value >= 0 && startY.value <= imageHeight.value &&
    endX.value >= 0 && endX.value <= imageWidth.value &&
    endY.value >= 0 && endY.value <= imageHeight.value;
});

// File selection handler
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

    // Set default end coordinates
    endX.value = Math.min(100, img.width);
    endY.value = Math.min(100, img.height);
  };

  img.src = URL.createObjectURL(file);
};

// Helper function to convert display coordinates to canvas coordinates
const getCanvasCoordinates = (event: MouseEvent) => {
  if (!canvasRef.value) return { x: 0, y: 0 };

  const rect = canvasRef.value.getBoundingClientRect();
  const scaleX = canvasRef.value.width / rect.width;
  const scaleY = canvasRef.value.height / rect.height;

  const x = Math.round((event.clientX - rect.left) * scaleX);
  const y = Math.round((event.clientY - rect.top) * scaleY);

  return { x, y };
};

// Canvas interaction handlers
const onCanvasMouseDown = (event: MouseEvent) => {
  if (!canvasRef.value) return;

  const coords = getCanvasCoordinates(event);

  if (!isDrawing.value) {
    startX.value = coords.x;
    startY.value = coords.y;
    isDrawing.value = true;
  }
};

const onCanvasMouseMove = (event: MouseEvent) => {
  if (!canvasRef.value || !isDrawing.value) return;

  const coords = getCanvasCoordinates(event);

  endX.value = coords.x;
  endY.value = coords.y;

  redrawCanvas();
};

const onCanvasMouseUp = () => {
  isDrawing.value = false;
};

// Canvas drawing functions
const redrawCanvas = () => {
  if (!canvasRef.value || !ctx.value || !uploadedImage.value) return;

  // Clear canvas and redraw image
  const img = new Image();
  img.onload = () => {
    if (ctx.value) {
      ctx.value.clearRect(0, 0, canvasRef.value!.width, canvasRef.value!.height);
      ctx.value.drawImage(img, 0, 0);
      drawLine();
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

// Compute line handler
const computeLine = async () => {
  if (!uploadedImage.value || !canCompute.value) return;

  await lineStore.computeLine({
    startX: startX.value,
    startY: startY.value,
    endX: endX.value,
    endY: endY.value,
    image: uploadedImage.value
  });
};

// Watch for parameter changes to redraw line
import { watch } from 'vue';
watch([startX, startY, endX, endY], () => {
  if (imageLoaded.value) {
    redrawCanvas();
  }
});
</script>

<style scoped>
.canvas-container {
  max-width: 100%;
  overflow: auto;
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
