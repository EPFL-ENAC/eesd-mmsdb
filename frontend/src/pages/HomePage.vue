<template>
  <q-page>
    <spinner-loader :result="wallPlyData">
      <template #default="{ value }">
        <microstructure-view
          :ply-data="value"
          :orientation="wallOrientation.unwrapOrNull()"
          :width="Math.min(400, q.screen.width)"
          :height="400"
          sliceable
          :wall-size="wallSize.unwrapOrNull() || 100"
          class="microstructure-container"
        />
      </template>
    </spinner-loader>

    <donut-charts class="q-mt-lg"/>

    <parallel-categories-diagram/>

    <q-card class="q-ma-lg q-mt-xl">
      <q-card-section>
        <div class="text-h6">{{ t('citation_text') }}</div>
        <citation-item
          v-for="item in citationItems"
          :key="item.title"
          v-bind="item"
          class="q-mt-xs q-mb-xs"
        />
      </q-card-section>
    </q-card>
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
import { SpinnerLoader } from 'src/components/utils/presets';
import { useReactiveAction } from 'unwrapped/vue';

const q = useQuasar();
const wallsStore = useWallsStore();
const propertiesStore = usePropertiesStore();
const wallID = "OC01";
const wallPlyData = wallsStore.getWall(true, wallID);
const wallSize = useReactiveAction(wallID, (id) => propertiesStore.getWallMaxSize(id), { immediate: true });
const wallOrientation = useReactiveAction(wallID, (id) => propertiesStore.getWallProperty(id, "Orientation (Up and Front)"), { immediate: true });

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
