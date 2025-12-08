<template>
  <q-page>
    <ArrayBufferSpinnerLoader :result="wallPlyData">
      <template #default="{ value }">
        <microstructure-view
          :ply-data="value"
          :orientation="wallOrientation.unwrapOrNull()"
          :width="Math.min(400, q.screen.width)"
          :height="400"
          sliceable
          :wall-dimensions="wallDimensions.unwrapOrNull()"
          class="microstructure-container"
        />
      </template>
    </ArrayBufferSpinnerLoader>

    <donut-charts class="q-mt-lg"/>

    <parallel-categories-diagram/>

    <q-card class="q-ma-lg q-mt-xl max-width">
      <q-card-section>
        <div class="text-h6">{{ t('citation_text') }}</div>
        <citation-item
          v-for="item in items"
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
import { ArrayBufferSpinnerLoader } from 'src/components/utils/presets';
import { useReactiveChain } from 'unwrapped/vue';

const q = useQuasar();
const wallsStore = useWallsStore();
const propertiesStore = usePropertiesStore();
const wallID = "OC01";
const wallPlyData = wallsStore.getWall(true, wallID);
const wallDimensions = useReactiveChain(() => wallID, (id) => propertiesStore.getWallDimensions(id), { immediate: true });
const wallOrientation = useReactiveChain(() => wallID, (id) => propertiesStore.getWallProperty(id, "Orientation (Up and Front)"), { immediate: true });
const items = computed(() => Object.values(citationItems));

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
