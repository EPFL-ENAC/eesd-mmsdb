<template>
  <q-page>
    <microstructure-view/>

    <donut-charts/>

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
import CitationItem from 'src/components/CitationItem.vue';
import MicrostructureView from 'src/components/MicrostructureView.vue';
import DonutCharts from 'src/components/DonutCharts.vue';
import ParallelCategoriesDiagram from 'src/components/ParallelCategoriesDiagram.vue';
import citationItems from 'src/assets/citation_items.json';

const { t } = useI18n();
</script>
