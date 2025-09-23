<template>
  <q-page class="q-pa-md">
    <div class="database-header q-mb-md">
      <div class="text-grey-6">
        Showing {{ filteredWallIds.length }} of {{ allWallIds.length }} walls
      </div>
    </div>

    <div class="microstructure-grid">
      <div v-for="wallId in filteredWallIds" :key="wallId" class="microstructure-card">
        <q-card class="cursor-pointer" @click="openWallDialog(wallId)">
          <q-card-section class="text-center q-mt-sm q-pa-none">
            <div class="wall-image-title">{{ wallId }}</div>
          </q-card-section>

          <q-card-section class="q-pa-sm">
            <div class="wall-image-container">
              <img v-if="wallImages[wallId]" :src="wallImages[wallId]" :alt="`Wall ${wallId} preview`"
                class="wall-image" />
              <div v-else class="wall-image-placeholder">
                <q-spinner v-if="loadingImages[wallId]" color="primary" size="2em" />
                <q-icon v-else name="image" size="3em" color="grey-5" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <simple-dialog v-model="showWallDialog" :title="`Wall ${selectedWallId}`" size="lg">
      <div v-if="selectedWallId" class="wall-dialog-content">
        <microstructure-view :ply-data="wallData[selectedWallId] || null" :width="400" :height="400" sliceable
          class="microstructure-item" />

        <div v-if="wallStoneList[selectedWallId]">
          <stone-carousel :stones="wallStoneList[selectedWallId]!" :preload-next="5" :preload-previous="5" />
        </div>

        <div class="parameters-section">
          <div class="text-h6 q-mb-md">Parameters</div>
          <div class="parameters-grid">
            <div v-for="param in selectedWallParameters" :key="param.name" class="parameter-item">
              <div class="parameter-name">{{ param.name }}</div>
              <div class="parameter-value">{{ param.value }} {{ param.unit }}</div>
            </div>
          </div>
        </div>

        <div class="stones-section q-mt-md">
          <div class="text-h6 q-mb-md">Stones</div>
          <div class="parameters-grid">
            <stone-property-histogram v-for="column of stoneColumns" :key="column"
              :title="stonePropertiesStore.getColumnLabel?.(column)" :wallID="selectedWallId" :columnName="column" />
          </div>
        </div>

        <div>
          <div class="text-h6 q-mb-md">Download</div>
          <wall-files-downloader :wallId="selectedWallId" :stones="wallStoneList[selectedWallId]!" />
        </div>
      </div>
    </simple-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { usePropertiesStore } from 'stores/properties'
import { useStonePropertiesStore } from 'stores/stone_properties'
import { useWallsStore, type WallStonesList } from 'stores/walls'
import { useDatabaseFiltersStore } from 'stores/database_filters'
import type { Column } from '../models';
import MicrostructureView from 'src/components/MicrostructureView.vue'
import StoneCarousel from 'src/components/StoneCarousel.vue'
import SimpleDialog from 'src/components/SimpleDialog.vue'
import StonePropertyHistogram from 'src/components/StonePropertyHistogram.vue'
import WallFilesDownloader from 'src/components/WallFilesDownloader.vue'

const dialogColumns = ["Microstructure type", "Typology based on Italian Code", "No of leaves", "Vertical loading_GMQI_class", "In-plane_GMQI_class", "Out-of-plane_GMQI_class", "Average vertical LMT", "Average horizontal LMT", "Average shape factor"]
const dimensionsColumns = ["Length [cm]", "Height [cm]", "Width [cm]"]
const stoneColumns = ["Stone length [m]", "Elongation [-]", "Aspect ratio [-]"]
const propertiesStore = usePropertiesStore()
const stonePropertiesStore = useStonePropertiesStore()
const wallsStore = useWallsStore()
const databaseFiltersStore = useDatabaseFiltersStore()

const filteredWallIds = computed(() => databaseFiltersStore.filteredWallIds)
const allWallIds = computed(() => databaseFiltersStore.allWallIds)


const wallData = ref<Record<string, ArrayBuffer | null>>({})
const wallStoneData = ref<Record<string, ArrayBuffer | null>>({})
const wallStoneList = ref<Record<string, WallStonesList | null>>({})
const loadingWallData = ref(false)

const wallImages = computed(() => wallsStore.wallImages)
const loadingImages = computed(() => wallsStore.loadingImages)

const showWallDialog = ref(false)
const selectedWallId = ref<string | null>(null)

const selectedWallParameters = computed(() => {
  if (!selectedWallId.value || !Array.isArray(propertiesStore.properties)) return []

  const index = propertiesStore.getColumnValues("Wall ID")?.findIndex(id => id === selectedWallId.value)
  if (index === undefined || index === -1) return []

  const toDisplayedParameters = (col: Column) => {
    const precision = propertiesStore.getColumnPrecision(col.name)
    let value = col.values[index] as string

    if (precision !== undefined) {
      const numberValue = Math.floor(parseFloat(value) * Math.pow(10, precision)) / Math.pow(10, precision)
      value = numberValue.toString()
    }

    return {
      name: propertiesStore.getColumnLabel(col.name) || col.name,
      value: value,
      unit: propertiesStore.getColumnUnit(col.name) || '',
    }
  }

  const properties = dialogColumns
    .map(col => ({ name: col, values: propertiesStore.getColumnValues(col) || [] }))
    .map(toDisplayedParameters);

  const dimensions = dimensionsColumns
    .map(col => ({ name: col, values: propertiesStore.getColumnValues(col) || [] }))
    .map(toDisplayedParameters)
    .reduce((acc, dimensionsString) => {
      if (acc.length > 0) acc += ' × '
      acc += `${dimensionsString.value} ${dimensionsString.unit}`
      return acc
    }, '');

  properties.push({
    name: 'Dimensions',
    value: dimensions,
    unit: '',
  })

  return properties
})

onMounted(async () => {
  await Promise.all(allWallIds.value.map(wallId => wallsStore.loadWallImage(wallId)))
})

watch(allWallIds, async (newWallIds, oldWallIds) => {
  const newIds = newWallIds.filter(id => !oldWallIds?.includes(id))

  await Promise.all(newIds.map(wallId => wallsStore.loadWallImage(wallId)))
}, { immediate: false })

async function openWallDialog(wallId: string) {
  selectedWallId.value = wallId
  showWallDialog.value = true

  if (!wallData.value[wallId]) {
    loadingWallData.value = true
    try {
      wallData.value[wallId] = await wallsStore.getWall(true, wallId)

      const stoneList = await wallsStore.getWallStonesList(wallId)
      wallStoneList.value[wallId] = stoneList

      const firstStonePath = `${stoneList?.folder}/${stoneList?.files[0] || ""}`;
      const firstStone = await wallsStore.getWallStoneModel(true, firstStonePath)
      wallStoneData.value[wallId] = firstStone
    } catch (error) {
      console.error(`Failed to load wall data for ${wallId}:`, error)
      wallData.value[wallId] = null
    } finally {
      loadingWallData.value = false
    }
  }
}

onUnmounted(() => {
  wallsStore.revokeAllWallImageUrls()
})
</script>

<style scoped>
.database-header {
  text-align: center;
}

.microstructure-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
}

.microstructure-card {
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease;
}

.microstructure-card:hover {
  transform: translateY(-2px);
}

.wall-image-container {
  width: 100%;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wall-image-title {
  font-weight: bold;
}

.wall-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  /* Show the whole image, don't crop */
}

.wall-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

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

.parameters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.parameter-item {
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #fafafa;
}

.parameter-name {
  font-weight: 500;
  color: #424242;
  font-size: 0.875rem;
  margin-bottom: 4px;
}

.parameter-value {
  font-size: 1rem;
  color: #1976d2;
  font-weight: 600;
}
</style>
