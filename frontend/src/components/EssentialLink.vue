<template>
  <q-item clickable tag="a" target="_blank" :href="link">
    <q-item-section v-if="image" avatar>
      <q-img :src="image" :alt="title" height="100px" width="100px" rounded class="image-avatar" />
    </q-item-section>
    <q-item-section v-else-if="icon" avatar>
      <q-icon :name="icon" />
    </q-item-section>

    <q-item-section>
      <q-item-label>{{ t(title) }}</q-item-label>
      <q-item-label caption>{{ t(caption || '') }}</q-item-label>
      <q-item-label v-if="contribution">{{ t(contribution) }}</q-item-label>
    </q-item-section>
  </q-item>
</template>

<script setup lang="ts">
export interface EssentialLinkProps {
  title: string;
  caption?: string;
  contribution?: string;
  link?: string;
  image?: string;
  icon?: string;
}
withDefaults(defineProps<EssentialLinkProps>(), {
  caption: '',
  link: '#',
  icon: '',
});
const { t } = useI18n();
</script>

<style scoped>
.image-avatar {
  border-radius: 50%;
}
</style>
