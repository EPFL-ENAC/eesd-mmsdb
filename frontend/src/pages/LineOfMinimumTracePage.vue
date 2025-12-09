<template>
  <q-page class="q-pa-md">
    <h4 class="text-h4 q-mt-sm">Line of minimum trace</h4>
    <div class="grid">
      <div class="left-part">
        <q-card-section>
          <div class="text-h6">Slice image info</div>
          <div class="text-subtitle1">{{ sliceStore.sliceData.fromWallId ? `Obtained from wall ${sliceStore.sliceData.fromWallId}` : 'No wall to get the information from, please enter the relevant information below' }}</div>
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
          <div class="wall-dimensions q-mt-sm">
            <div>
              <div class="text-subtitle2 q-mb-xs">Wall length (in cm)</div>
                <q-input
                  v-model.number="sliceStore.sliceData.wallDimensions.length"
                  :disable="sliceStore.sliceData.wallDimensions.provided"
                  type="number"
                  filled
                  dense
                />
              </div>
              <div>
                <div class="text-subtitle2 q-mb-xs">Wall height (in cm)</div>
                <q-input
                  v-model.number="sliceStore.sliceData.wallDimensions.height"
                  :disable="sliceStore.sliceData.wallDimensions.provided"
                  type="number"
                  filled
                  dense
                />
              </div>
              <div>
                <div class="text-subtitle2 q-mb-xs">Wall width (in cm)</div>
                <q-input
                  v-model.number="sliceStore.sliceData.wallDimensions.width"
                  :disable="sliceStore.sliceData.wallDimensions.provided"
                  type="number"
                  filled
                  dense
                />
            </div>
          </div>
        </q-card-section>
        <q-card-section v-show="imageLoaded">
          <div class="canvas-container q-mb-md">
            <lmt-canvas
              v-model:input-line="lineInputCoords"
              :uploadedImage="uploadedImage"
              :traces="traces.getAllSuccessValues()"
            />
          </div>
          <div class="text-h6 q-mb-md">Parameters</div>
          <div class="row q-col-gutter-md">
            <div class="col-md-3 col-sm-6 col-xs-12">
              <div class="text-subtitle2 q-mb-xs">Start X</div>
              <q-slider
                v-model="lineInputCoords.startX"
                :min="0"
                :max="imageWidth - 1"
                :step="1"
                label
              />
            </div>
            <div class="col-md-3 col-sm-6 col-xs-12">
              <div class="text-subtitle2 q-mb-xs">Start Y</div>
              <q-slider
                v-model="lineInputCoords.startY"
                :min="0"
                :max="imageHeight - 1"
                :step="1"
                label
              />
            </div>
            <div class="col-md-3 col-sm-6 col-xs-12">
              <div class="text-subtitle2 q-mb-xs">End X</div>
              <q-slider
                v-model="lineInputCoords.endX"
                :min="0"
                :max="imageWidth - 1"
                :step="1"
                label
              />
            </div>
            <div class="col-md-3 col-sm-6 col-xs-12">
              <div class="text-subtitle2 q-mb-xs">End Y</div>
              <q-slider
                v-model="lineInputCoords.endY"
                :min="0"
                :max="imageHeight - 1"
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
              :loading="traces.anyLoading()"
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
      </div>
      <div class="right-part">
        <q-list padding>
          <q-item-label class="text-h6">Computation History</q-item-label>
          <q-separator />
          <template v-for="entry in traces.entries" :key="entry[0]">
            <LmtComputeTraceSpinnerLoader :result="(entry[1] as AsyncResult<LineComputeTrace>)">
              <template #default="{ value }">
                <q-item
                  class="computation-result" :style="`--border-color: ${value.color};`"
                >
                  <q-item-section>
                    <q-item-label>{{ entry[0] }}</q-item-label>
                    <q-item-label caption>
                      <div>
                        <strong>Length:</strong> {{ value.result.total_length ? value.result.total_length.toFixed(2) + ' cm' : 'N/A' }}
                      </div>
                      <div>
                        <strong>Type:</strong> {{
                          analysisTypeOptions.find(option => option.value === value.params.analysisType)?.label
                        }}
                      </div>
                      <div>
                        <strong>LMP Type:</strong> {{ value.result.lmp_type || 'N/A' }}
                      </div>
                      <div>
                        <strong>LMT Result:</strong> {{ value.result.lmt_result || 'N/A' }}
                      </div>
                      <div>
                        <strong>LMT Vertical:</strong> {{ (value.result.total_length && sliceStore.sliceData.wallDimensions.height) ? 
                          (value.result.total_length / sliceStore.sliceData.wallDimensions.height).toFixed(2) : 'N/A' }}
                      </div>
                      <div>
                        <strong>LMT Horizontal:</strong> {{ (value.result.total_length && sliceStore.sliceData.wallDimensions.length) ? 
                          (value.result.total_length / sliceStore.sliceData.wallDimensions.length).toFixed(2) : 'N/A' }}
                      </div>
                      <div>
                        <strong>LMT Wall-Leaf:</strong> {{ (value.result.total_length && sliceStore.sliceData.wallDimensions.width) ? 
                          (value.result.total_length / sliceStore.sliceData.wallDimensions.width).toFixed(2) : 'N/A' }}
                      </div>
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-btn round color="primary" icon="delete" @click="traces.remove(entry[0])" />
                  </q-item-section>
                </q-item>
              </template>
            </LmtComputeTraceSpinnerLoader>
          </template>
        </q-list>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import type { LineComputeInputLineCoords, LineComputeParams, LineComputeTrace } from 'src/models';
import { useLineStore } from '../stores/line';
import { useSliceStore } from '../stores/slice';
import { type AsyncResult, Result } from 'unwrapped/core';
import LmtCanvas from 'src/components/LmtCanvas.vue';
import { useAsyncResultList } from 'unwrapped/vue';
import { LmtComputeTraceSpinnerLoader } from 'src/components/utils/presets';

const lineStore = useLineStore();
const sliceStore = useSliceStore();

const traces = useAsyncResultList<LineComputeTrace>();

const uploadedImage = ref<File | null>(null);
const imageLoaded = ref(false);
const imageWidth = ref(0);
const imageHeight = ref(0);
const tracesCount = ref(0);

const lineInputCoords = ref<LineComputeInputLineCoords>({
  startX: 0,
  startY: 0,
  endX: 500,
  endY: 500,
});

const analysisTypeOptions = [
  { label: 'Vertical joints', value: 0 },
  { label: 'Horizontal bed joints', value: 1 },
  { label: 'Wall leaf connections', value: 2 },
];
const interfaceWeight = ref(1.0);
const analysisType = ref(analysisTypeOptions[0]);

const canCompute = computed(() => {
  return imageLoaded.value &&
    uploadedImage.value &&
    lineInputCoords.value.startX >= 0 && lineInputCoords.value.startX <= imageWidth.value &&
    lineInputCoords.value.startY >= 0 && lineInputCoords.value.startY <= imageHeight.value &&
    lineInputCoords.value.endX >= 0 && lineInputCoords.value.endX <= imageWidth.value &&
    lineInputCoords.value.endY >= 0 && lineInputCoords.value.endY <= imageHeight.value;
});

function onFileSelected(file: File | null) {
  sliceStore.sliceData.fromWallId = null;
  sliceStore.sliceData.wallDimensions = { provided: false, length: 100, height: 100, width: 100 };
  onImageChanged(file);
};

function onImageChanged(file: File | null) {
  traces.value.clear();

  if (!file) {
    imageLoaded.value = false;
    return;
  }

  const img = new Image();
  img.onload = async () => {
    imageWidth.value = img.width;
    imageHeight.value = img.height;

    await nextTick();

    imageLoaded.value = true;

    lineInputCoords.value.startX = Math.floor(img.width / 2);
    lineInputCoords.value.startY = 0;
    lineInputCoords.value.endX = Math.floor(img.width / 2);
    lineInputCoords.value.endY = img.height;
    tracesCount.value = 0;
  };

  img.src = URL.createObjectURL(file);
};

function computeLine() {
  if (!uploadedImage.value || !canCompute.value) return;

  const maxDimension = Math.max(sliceStore.sliceData.wallDimensions.length, sliceStore.sliceData.wallDimensions.height, sliceStore.sliceData.wallDimensions.width);

  const params: LineComputeParams = {
    startX: lineInputCoords.value.startX,
    startY: lineInputCoords.value.startY,
    endX: lineInputCoords.value.endX,
    endY: lineInputCoords.value.endY,
    image: uploadedImage.value,
    realLength: maxDimension,
    realHeight: maxDimension,
    analysisType: (analysisType.value as typeof analysisTypeOptions[0]).value,
    interfaceWeight: interfaceWeight.value,
    boundaryMargin: sliceStore.sliceData.boundaryMargin,
  };

  tracesCount.value += 1;
  traces.value.add(
    `Trace ${tracesCount.value}`,
    lineStore.getLine(params).chain((result) => Result.ok({
      params,
      result,
      color: `hsl(${Math.floor(Math.random() * 360)}, 70%, 50%)`,
    })),
    false
  );
};

onMounted(() => {
  if (sliceStore.sliceData.sliceImageData) {
    const fileName = sliceStore.sliceData.fromWallId ? `slice_from_wall_${sliceStore.sliceData.fromWallId}.png` : 'slice_image.png';
    uploadedImage.value = new File([new Blob([sliceStore.sliceData.sliceImageData])], fileName, { type: 'image/png' });
    onImageChanged(uploadedImage.value);
  }
});

watch(() => sliceStore.sliceData.sliceImageData, (newData) => {
  if (newData) {
    const fileName = sliceStore.sliceData.fromWallId ? `slice_from_wall_${sliceStore.sliceData.fromWallId}.png` : 'slice_image.png';
    uploadedImage.value = new File([new Blob([newData])], fileName, { type: 'image/png' });
    onImageChanged(uploadedImage.value);
  }
});
</script>

<style scoped>
.wall-dimensions {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1rem;
}

.grid {
  display: grid;
  grid-template-areas: "left-part right-part";
  grid-template-columns: 1fr 300px;
  gap: 1rem;
}

.left-part {
  grid-area: left-part;
}

.right-part {
  grid-area: right-part;
}

.canvas-container {
  overflow: auto;
  position: relative;
  display: flex;
  justify-content: center;
}

.computation-result {
  border-left: 6px solid var(--border-color);
  padding-left: 8px;
}
</style>
