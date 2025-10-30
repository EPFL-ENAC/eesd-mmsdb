<template>
  <router-view />
</template>

<script setup lang="ts">
 import { useSliceStore } from 'stores/slice';

 const sliceStore = useSliceStore();

onMounted(async () => {
  await sliceStore.fetchDefaultSliceImage();
});
</script>
