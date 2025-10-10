<template>
  <router-view />
</template>

<script setup lang="ts">
 import { usePropertiesStore } from 'stores/properties';
 import { useSliceStore } from 'stores/slice';

 const propertiesStore = usePropertiesStore();
 const sliceStore = useSliceStore();

onMounted(async () => {
  await propertiesStore.fetchProperties();
  await sliceStore.fetchDefaultSliceImage();
});
</script>
