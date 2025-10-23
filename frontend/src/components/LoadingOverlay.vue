<template>
  <div :class="['loading-wrapper', { 'visible': props.visible }]">
    <q-circular-progress indeterminate rounded size="50px" color="primary" class="q-ma-md" />
  </div>
</template>

<script setup lang="ts">

const props = defineProps<{
  visible: boolean;
}>();

</script>

<style scoped>

.loading-wrapper {
  position: absolute;
  inset: 0;
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.loading-wrapper.visible {
  opacity: 1;
}

</style>