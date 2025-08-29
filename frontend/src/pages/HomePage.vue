<template>
  <q-page>
    <microstructure-view
      :ply-data="result"
      :width="Math.min(400, q.screen.width)"
      :height="400"
      sliceable
      class="microstucture-container"
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

const q = useQuasar();
const wallsStore = useWallsStore();
const result = ref<ArrayBuffer | null>(null)

onMounted(async () => {
  result.value = await wallsStore.getWall(true, "OC01");
});

const { t } = useI18n();
</script>

<style scoped>
.microstucture-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
</style>
