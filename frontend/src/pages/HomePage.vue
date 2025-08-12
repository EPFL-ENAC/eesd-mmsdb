<template>
  <q-page>
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
import citationItems from 'src/assets/citation_items.json';

const { t } = useI18n();
</script>
