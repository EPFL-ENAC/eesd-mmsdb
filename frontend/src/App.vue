<template>
  <router-view />
</template>

<script setup lang="ts">
 import { usePropertiesStore } from 'stores/properties';

 const propertiesStore = usePropertiesStore();

onMounted(async () => {
  await propertiesStore.fetchProperties();
});
</script>
