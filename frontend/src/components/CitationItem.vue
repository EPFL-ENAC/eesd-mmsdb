<template>
  <div>
    <q-icon name="article" class="q-mr-xs" />
    {{ authors }}, <em>{{ title }},</em> {{ journal }}<span v-if="year">, {{ year }}</span><span v-if="doi">, <a :href="doi">{{ doi }}</a></span><span v-if="type" class="type"> [{{ type }}]</span>
  </div>
</template>

<script setup lang="ts">
export interface CitationItemProps {
  authors: string;
  title: string;
  journal: string;
  year?: string;
  doi?: string;
  type?: string;
}
withDefaults(defineProps<CitationItemProps>(), {
  year: '',
  doi: '',
  type: '',
});
</script>

<style lang="scss" scoped>
.type {
  color: $grey-6;
}
</style>
