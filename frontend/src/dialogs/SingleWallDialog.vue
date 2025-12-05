<template>
  <simple-dialog v-model="showWallDialog" :title="`Wall ${selectedWallId}`" size="lg">
    <div v-if="selectedWallId" class="wall-dialog-content">
      <div class="text-h6">Downscaled preview</div>
      <div class="text-caption q-mb-md">Full resolution models available in the "Download" section of this popup</div>

      <spinner-loader :result="currentWallData">
        <template #default="{ value: plyData }">
          <microstructure-view
            :ply-data="plyData"
            :ply-data-highlight="currentStoneData"
            :orientation="currentWallOrientation.unwrapOrNull()"
            :width="400"
            :height="400"
            sliceable
            :wall-size="currentWallMaxSize.unwrapOrNull() || 100"
            class="microstructure-item"
          />
        </template>
      </spinner-loader>

      <div>
        <stone-carousel
          ref="stoneCarouselRef"
          :wall-id="selectedWallId"
          :orientation="currentWallOrientation.unwrapOrNull()"
          :preload-next="5"
          :preload-previous="5"
        />
      </div>

      <div class="properties-section">
        <div class="text-h6 q-mb-md">Wall properties</div>
        <div class="properties-grid">
          <div v-for="prop in selectedWallProperties" :key="prop.name" class="property-item">
            <div class="property-name">{{ prop.name }}</div>
            <div class="property-value">{{ prop.value }} {{ prop.unit }}</div>
          </div>
        </div>
      </div>

      <div class="stones-section q-mt-md">
        <div class="text-h6 q-mb-md">Stones properties</div>
        <div class="properties-grid">
          <stone-property-histogram v-for="column of stoneColumns" :key="column"
            :title="stonePropertiesStore.getColumnLabel?.(column)" :wallID="selectedWallId" :columnName="column" />
        </div>
      </div>

      <div>
        <div class="text-h6 q-mb-md">Download</div>
        <wall-files-downloader :wallId="selectedWallId" />
      </div>
    </div>
  </simple-dialog>
</template>

<script setup lang="ts">
import { usePropertiesStore } from 'stores/properties'
import { useStonePropertiesStore } from 'stores/stone_properties'
import { useWallsStore } from 'stores/walls'
import { toDisplayedProperties, getDimensionsColumn } from 'src/utils/properties'
import MicrostructureView from 'src/components/MicrostructureView.vue'
import StoneCarousel from 'src/components/StoneCarousel.vue'
import SimpleDialog from 'src/components/SimpleDialog.vue'
import StonePropertyHistogram from 'src/components/StonePropertyHistogram.vue'
import WallFilesDownloader from 'src/components/WallFilesDownloader.vue'
import { useReactiveAction } from 'unwrapped/vue'
import { SpinnerLoader } from 'src/components/utils/presets'

const propertiesStore = usePropertiesStore()
const stonePropertiesStore = useStonePropertiesStore()
const wallsStore = useWallsStore()

defineExpose({
  open,
})

function open(wallId: string) {
  selectedWallId.value = wallId
  showWallDialog.value = true
}

const showWallDialog = ref(false)
const selectedWallId = ref<string | null>(null)
const currentWallData = useReactiveAction(selectedWallId, (id) => wallsStore.getWall(true, id!), { immediate: false });
const currentWallOrientation = useReactiveAction(selectedWallId, (id) => propertiesStore.getWallProperty(id!, "Orientation (Up and Front)"), { immediate: false });
const currentWallMaxSize = useReactiveAction(selectedWallId, (id) => propertiesStore.getWallMaxSize(id!), { immediate: false })

const dialogColumns = ["Microstructure type", "Typology based on Italian Code", "No of leaves", "Vertical loading_GMQI_class", "In-plane_GMQI_class", "Out-of-plane_GMQI_class", "Average vertical LMT", "Average horizontal LMT", "Average shape factor"]
const stoneColumns = ["Stone length [m]", "Elongation [-]", "Aspect ratio [-]"]
const stoneCarouselRef = ref<InstanceType<typeof StoneCarousel> | null>(null)

const currentStoneData = computed(() => stoneCarouselRef.value?.currentStone.unwrapOrNull() || null)

const selectedWallProperties = computed(() => {
  const table = propertiesStore.properties.unwrapOrNull();
  if (!selectedWallId.value || !table) return []

  const index = table.rowIndexInColumn("Wall ID", selectedWallId.value)
  if (index === undefined || index === -1) return []

  const p = dialogColumns
    .map(col => ({ name: col, values: table.getColumnValues(col) || [] }))
    .map(toDisplayedProperties(propertiesStore, index));

  const dimensions = getDimensionsColumn(propertiesStore, index, (col) => table.getColumnValues(col));

  p.push({
    name: 'Dimensions',
    value: dimensions,
    unit: '',
  })

  return p
})
</script>

<style scoped>

.wall-dialog-content {
  max-width: 100%;
}

.microstructure-section {
  text-align: center;
}

.microstructure-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.microstructure-placeholder {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.properties-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.property-item {
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #fafafa;
}

.property-name {
  font-weight: 500;
  color: #424242;
  font-size: 0.875rem;
  margin-bottom: 4px;
}

.property-value {
  font-size: 1rem;
  color: #1976d2;
  font-weight: 600;
}
</style>
