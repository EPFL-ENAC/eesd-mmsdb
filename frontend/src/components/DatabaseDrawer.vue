<template>
  <div class="database-drawer-content">
    <div class="text-h6 q-mb-md">Filters</div>

    <div v-for="key in columnFilters" :key="key" class="q-mb-xs">
      <div class="text-subtitle2 q-mb-xs">{{ propertiesStore.getColumnLabel(key) }}
      </div>

      <q-select
        v-if="propertiesStore.getColumnType(key) === 'string'"
        :model-value="databaseFiltersStore.stringFilters[key] || []"
        @update:model-value="(val) => databaseFiltersStore.updateStringFilter(key, val || [])"
        :options="databaseFiltersStore.getStringColumnOptions(key)"
        label="Select filters"
        outlined
        dense
        clearable
        multiple
        use-chips
        class="q-mb-md"
      />

      <div v-else class="range-slider-container">
        <q-range
          :model-value="databaseFiltersStore.numericFilters[key] || { min: 0, max: 100 }"
          @update:model-value="(val) => databaseFiltersStore.updateNumericFilter(key, val)"
          :min="databaseFiltersStore.getNumericColumnRange(key).min"
          :max="databaseFiltersStore.getNumericColumnRange(key).max"
          :step="1"
          label
          dense
        />
        <div class="range-labels">
          <span>{{ databaseFiltersStore.getNumericColumnRange(key).min }} {{ propertiesStore.getColumnUnit(key) }}</span>
          <span>{{ databaseFiltersStore.getNumericColumnRange(key).max }} {{ propertiesStore.getColumnUnit(key) }}</span>
        </div>
      </div>
    </div>

    <q-btn
      label="Clear Filters"
      color="grey"
      outline
      size="sm"
      class="full-width q-mt-md"
      @click="databaseFiltersStore.clearFilters"
    />
  </div>
</template>

<script setup lang="ts">
import { useDatabaseFiltersStore } from 'stores/database_filters'
import { usePropertiesStore } from 'stores/properties'

const columnFilters = ["Microstructure type", "Typology based on Italian Code", "No of leaves", "Vertical loading_GMQI_class", "In-plane_GMQI_class", "Out-of-plane_GMQI_class", "Length [cm]", "Height [cm]", "Width [cm]"]
const databaseFiltersStore = useDatabaseFiltersStore()
const propertiesStore = usePropertiesStore()

watch(() => propertiesStore.properties, () => {
  databaseFiltersStore.initializeFilters()
}, { immediate: true })

</script>

<style scoped>
.database-drawer-content {
  height: 100%;
}

.text-subtitle2 {
  font-weight: 500;
  color: #424242;
}

.range-slider-container {
  padding: 0 8px;
}

.range-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #666;
  margin-top: 4px;
}
</style>
