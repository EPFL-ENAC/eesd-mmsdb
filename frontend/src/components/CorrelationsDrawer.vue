<template>
  <div class="correlations-drawer-content">
    <div class="text-h6 q-mb-md">Axes</div>

    <div class="q-mb-xs">
      <diV class="text-subtitle2 q-mb-xs">X axis</div>
      <q-select
        :model-value="correlationsFiltersStore.xColumn"
        @update:model-value="(val) => correlationsFiltersStore.setXColumn(val)"
        :options="correlationsFiltersStore.numericColumns"
        label="Select parameter"
        outlined
        dense
        class="q-mb-md"
      />
    </div>

    <div class="q-mb-xs">
      <diV class="text-subtitle2 q-mb-xs">Y axis</div>
      <q-select
        :model-value="correlationsFiltersStore.yColumn"
        @update:model-value="(val) => correlationsFiltersStore.setYColumn(val)"
        :options="correlationsFiltersStore.numericColumns"
        label="Select parameter"
        outlined
        dense
        class="q-mb-md"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useCorrelationsFiltersStore } from 'stores/correlations_filters'
const correlationsFiltersStore = useCorrelationsFiltersStore()

</script>

<style scoped>
.correlations-drawer-content {
  height: 100%;
}

.text-subtitle2 {
  font-weight: 500;
  color: #424242;
}
</style>
