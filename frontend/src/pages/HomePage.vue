<template>
  <q-page>
    <microstructure-view
      :ply-data="wallPlyData"
      :orientation="wallOrientation"
      :width="Math.min(400, q.screen.width)"
      :height="400"
      sliceable
      :wall-size="wallSize || 100"
      class="microstructure-container"
    />

    <donut-charts class="q-mt-lg"/>

    <parallel-categories-diagram/>

    <div>
      {{ t('citation_text') }}
      <citation-item
        v-for="item in citationItems"
        :key="item.title"
        v-bind="item"
        class="q-mt-xs q-mb-xs"
      />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import CitationItem from 'src/components/CitationItem.vue';
import MicrostructureView from 'src/components/MicrostructureView.vue';
import DonutCharts from 'src/components/DonutCharts.vue';
import ParallelCategoriesDiagram from 'src/components/ParallelCategoriesDiagram.vue';
import citationItems from 'src/assets/citation_items.json';
import { useWallsStore } from 'src/stores/walls';
import { usePropertiesStore } from 'src/stores/properties';

const q = useQuasar();
const wallsStore = useWallsStore();
const propertiesStore = usePropertiesStore();
const wallPlyData = ref<ArrayBuffer | null>(null)
const wallSize = ref<number | null>(null);
const wallOrientation = ref<string | null>(null);
const wallID = "OC01";

onMounted(async () => {
  wallPlyData.value = await wallsStore.getWall(true, wallID);
  wallSize.value = propertiesStore.getWallMaxSize(wallID);
  wallOrientation.value = propertiesStore.getWallProperty(wallID, "Orientation (Up and Front)");
});

watch(() => propertiesStore.loading, () => {
  if (!propertiesStore.properties || wallSize.value) return;
  wallSize.value = propertiesStore.getWallMaxSize(wallID);
  wallOrientation.value = propertiesStore.getWallProperty(wallID, "Orientation (Up and Front)");
}, { immediate: true });

const { t } = useI18n();
</script>

<style scoped>
.microstructure-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
</style>
