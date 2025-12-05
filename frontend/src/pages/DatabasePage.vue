<template>
  <q-page class="q-pa-md">
    <div class="database-header q-mb-md">
      <q-btn color="primary" :disable="checkedWallIds.length < 2" @click="openCompareWallDialog">
        <template v-if="checkedWallIds.length < 2">
          Select at least 2 walls to compare
        </template>
        <template v-else>
          Compare {{ checkedWallIds.length }}
        </template>
      </q-btn>
      <q-btn v-if="checkedWallIds.length > 0" outline color="primary" @click="checkedWallIds = []">Clear selection</q-btn>
      <div class="header-text text-grey-6">
        Showing {{ filteredWallIds.length }} of {{ allWallIds.length }} walls
      </div>
    </div>

    <div class="microstructure-grid">
      <div v-for="wallId in filteredWallIds" :key="wallId" :class="['microstructure-card', { checked: checkedWallIds.includes(wallId) }]">
        <q-card class="cursor-pointer" @click="openWallDialog(wallId)">
          <q-card-section class="q-pa-none">
            <div class="card-header">
              <div class="wall-image-title q-ml-sm">{{ wallId }}</div>
              <q-checkbox v-model="checkedWallIds" :val="wallId" @click.stop color="primary" />
            </div>
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

    <single-wall-dialog ref="singleWallDialog" />
    <compare-wall-dialog ref="compareWallDialog" />
  </q-page>
</template>

<script setup lang="ts">
import { useWallsStore } from 'stores/walls'
import { useDatabaseFiltersStore } from 'stores/database_filters'
import SingleWallDialog from 'src/dialogs/SingleWallDialog.vue'
import CompareWallDialog from 'src/dialogs/CompareWallDialog.vue'

const wallsStore = useWallsStore()
const databaseFiltersStore = useDatabaseFiltersStore()

const singleWallDialogRef = useTemplateRef<InstanceType<typeof SingleWallDialog> | null>('singleWallDialog')
const compareWallDialogRef = useTemplateRef<InstanceType<typeof CompareWallDialog> | null>('compareWallDialog')

const filteredWallIds = computed(() => databaseFiltersStore.filteredWallIds)
const allWallIds = computed(() => databaseFiltersStore.allWallIds)
const checkedWallIds = ref<string[]>([])

const wallImages = computed(() => wallsStore.wallImages)
const loadingImages = computed(() => wallsStore.loadingImages)

onMounted(async () => {
  await Promise.all(allWallIds.value.map(wallId => wallsStore.loadWallImage(wallId)))
})

watch(allWallIds, async (newWallIds, oldWallIds) => {
  const newIds = newWallIds.filter(id => !oldWallIds?.includes(id))

  await Promise.all(newIds.map(wallId => wallsStore.loadWallImage(wallId)))
}, { immediate: false })

function openWallDialog(wallId: string) {
  singleWallDialogRef.value?.open(wallId)
}

function openCompareWallDialog() {
  compareWallDialogRef.value?.open(checkedWallIds.value)
}

onUnmounted(() => {
  wallsStore.revokeAllWallImageUrls()
})
</script>

<style scoped>
.database-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-text {
  margin-left: auto;
}

.microstructure-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
}

.microstructure-card {
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, opacity 0.4s ease;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.checked > .cursor-pointer {
  outline: 2px solid red;
  box-shadow: 0 0 10px black;
}
.microstructure-grid:has(.checked) .microstructure-card:not(.checked) {
  opacity: 0.6;
}
</style>
