<template>
  <q-page class="q-pa-md">
    <div class="microstructure-grid">
      <div
        v-for="wallId in wallIds"
        :key="wallId"
        class="microstructure-card"
      >
        <q-card class="cursor-pointer" @click="openWallDialog(wallId)">
          <q-card-section class="text-center q-pa-sm">
            <div class="wall-image-title">{{ wallId }}</div>
          </q-card-section>

          <q-card-section class="q-pa-sm">
            <div class="wall-image-container">
              <img
                v-if="wallImages[wallId]"
                :src="wallImages[wallId]"
                :alt="`Wall ${wallId} preview`"
                class="wall-image"
              />
              <div v-else class="wall-image-placeholder">
                <q-spinner v-if="loadingImages[wallId]" color="primary" size="2em" />
                <q-icon v-else name="image" size="3em" color="grey-5" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <simple-dialog
      v-model="showWallDialog"
      :title="`Wall ${selectedWallId}`"
      size="lg"
    >
      <div v-if="selectedWallId" class="wall-dialog-content">
        <microstructure-view
          v-if="wallData[selectedWallId]"
          :ply-data="wallData[selectedWallId]"
          :width="400"
          :height="400"
          sliceable
          class="microstructure-item"
        />

        <div class="parameters-section">
          <div class="text-h6 q-mb-md">Parameters</div>
          <div v-if="selectedWallParameters.length > 0" class="parameters-grid">
            <div
              v-for="param in selectedWallParameters"
              :key="param.name"
              class="parameter-item"
            >
              <div class="parameter-name">{{ param.name }}</div>
              <div class="parameter-value">{{ param.value }} {{ param.unit || '' }}</div>
            </div>
          </div>
          <div v-else class="text-grey-6">No parameters available</div>
        </div>
      </div>
    </simple-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { usePropertiesStore } from 'stores/properties'
import { useWallsStore } from 'stores/walls'
import MicrostructureView from 'src/components/MicrostructureView.vue'
import SimpleDialog from 'src/components/SimpleDialog.vue'
import type { PropertyEntry, Property } from '../models';

const propertiesStore = usePropertiesStore()
const wallsStore = useWallsStore()
const properties = computed(() => propertiesStore.properties)

// Get unique wall IDs from properties
const wallIds = computed(() => {
  if (!Array.isArray(properties.value)) return []

  const wallIds = (properties.value as PropertyEntry[])
    .map(propertyEntry => {
      const wallIdProperty = propertyEntry.properties.find(p => p.name === 'Wall ID')
      return wallIdProperty?.value
    })
    .filter(Boolean)

  return [...new Set(wallIds)] as string[]
})

// Store wall images and loading states
const wallImages = ref<Record<string, string>>({})
const loadingImages = ref<Record<string, boolean>>({})

// Store wall data for 3D view (loaded on demand)
const wallData = ref<Record<string, ArrayBuffer | null>>({})
const loadingWallData = ref(false)

// Dialog state
const showWallDialog = ref(false)
const selectedWallId = ref<string | null>(null)

// Get parameters for selected wall
const selectedWallParameters = computed(() => {
  if (!selectedWallId.value || !Array.isArray(properties.value)) return []

  const propertyEntry = (properties.value as PropertyEntry[])
    .find(entry => {
      const wallIdProperty = entry.properties.find(p => p.name === 'Wall ID')
      return wallIdProperty?.value === selectedWallId.value
    })

  if (!propertyEntry) return []

  // Filter out Wall ID since it's already shown in the title
  return propertyEntry.properties.filter(p => p.name !== 'Wall ID')
})

// Load wall images
async function loadWallImage(wallId: string) {
  if (wallImages.value[wallId] || loadingImages.value[wallId]) return

  loadingImages.value[wallId] = true

  try {
    const imageData = await wallsStore.getWallImage(wallId)
    if (imageData) {
      const blob = new Blob([imageData], { type: 'image/png' })
      wallImages.value[wallId] = URL.createObjectURL(blob)
    }
  } catch (error) {
    console.error(`Failed to load wall image for ${wallId}:`, error)
  } finally {
    loadingImages.value[wallId] = false
  }
}

// Load wall images for all unique wall IDs in parallel
onMounted(async () => {
  await Promise.all(wallIds.value.map(wallId => loadWallImage(wallId)))
})

// Watch for changes in unique wall IDs and load new images in parallel
watch(wallIds, async (newWallIds, oldWallIds) => {
  const newIds = newWallIds.filter(id => !oldWallIds?.includes(id))

  await Promise.all(newIds.map(wallId => loadWallImage(wallId)))
}, { immediate: false })

// Open wall dialog and load 3D data
async function openWallDialog(wallId: string) {
  selectedWallId.value = wallId
  showWallDialog.value = true

  // Load 3D data if not already loaded
  if (!wallData.value[wallId]) {
    loadingWallData.value = true
    try {
      wallData.value[wallId] = await wallsStore.getWall(true, wallId)
    } catch (error) {
      console.error(`Failed to load wall data for ${wallId}:`, error)
      wallData.value[wallId] = null
    } finally {
      loadingWallData.value = false
    }
  }
}

// Clean up object URLs when component is unmounted
onUnmounted(() => {
  Object.values(wallImages.value).forEach(url => {
    if (url) URL.revokeObjectURL(url)
  })
})
</script>

<style scoped>
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
  object-fit: contain; /* Show the whole image, don't crop */
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
