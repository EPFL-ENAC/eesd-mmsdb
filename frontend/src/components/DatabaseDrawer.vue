<template>
  <div class="database-drawer-content">
    <div class="text-h6 q-mb-md">Filters</div>

    <div class="filter-section">
      <div class="text-subtitle2 q-mb-xs">Microstructure Type</div>
      <q-select
        :model-value="databaseFiltersStore.filters['Microstructure type'].values"
        @update:model-value="(val) => databaseFiltersStore.updateStringFilter('Microstructure type', val || [])"
        :options="databaseFiltersStore.getStringColumnOptions('Microstructure type')"
        label="Select Types"
        outlined
        dense
        clearable
        multiple
        use-chips
        class="q-mb-md"
      />
    </div>

    <div class="filter-section">
      <div class="text-subtitle2 q-mb-xs">Typology</div>
      <q-select
        :model-value="databaseFiltersStore.filters['Typology based on Italian Code'].values"
        @update:model-value="(val) => databaseFiltersStore.updateStringFilter('Typology based on Italian Code', val || [])"
        :options="databaseFiltersStore.getStringColumnOptions('Typology based on Italian Code')"
        label="Select Typologies"
        outlined
        dense
        clearable
        multiple
        use-chips
        class="q-mb-md"
      />
    </div>

    <div class="filter-section">
      <div class="text-subtitle2 q-mb-xs">Number of Leaves</div>
      <div class="range-slider-container">
        <q-range
          :model-value="databaseFiltersStore.filters['No of leaves']"
          @update:model-value="(val) => databaseFiltersStore.updateNumericFilter('No of leaves', val)"
          :min="databaseFiltersStore.getNumericColumnRange('No of leaves').min"
          :max="databaseFiltersStore.getNumericColumnRange('No of leaves').max"
          :step="1"
          label
          dense
        />
        <div class="range-labels">
          <span>{{ databaseFiltersStore.getNumericColumnRange('No of leaves').min }}</span>
          <span>{{ databaseFiltersStore.getNumericColumnRange('No of leaves').max }}</span>
        </div>
      </div>
    </div>

    <div class="filter-section">
      <div class="text-subtitle2 q-mb-xs">Vertical LMT</div>
      <div class="range-slider-container">
        <q-range
          :model-value="databaseFiltersStore.filters['Average vertical LMT']"
          @update:model-value="(val) => databaseFiltersStore.updateNumericFilter('Average vertical LMT', val)"
          :min="databaseFiltersStore.getNumericColumnRange('Average vertical LMT').min"
          :max="databaseFiltersStore.getNumericColumnRange('Average vertical LMT').max"
          :step="0.01"
          label
          dense
        />
        <div class="range-labels">
          <span>{{ databaseFiltersStore.getNumericColumnRange('Average vertical LMT').min }}</span>
          <span>{{ databaseFiltersStore.getNumericColumnRange('Average vertical LMT').max }}</span>
        </div>
      </div>
    </div>

    <div class="filter-section">
      <div class="text-subtitle2 q-mb-xs">Horizontal LMT</div>
      <div class="range-slider-container">
        <q-range
          :model-value="databaseFiltersStore.filters['Average horizontal LMT']"
          @update:model-value="(val) => databaseFiltersStore.updateNumericFilter('Average horizontal LMT', val)"
          :min="databaseFiltersStore.getNumericColumnRange('Average horizontal LMT').min"
          :max="databaseFiltersStore.getNumericColumnRange('Average horizontal LMT').max"
          :step="0.01"
          label
          dense
        />
        <div class="range-labels">
          <span>{{ databaseFiltersStore.getNumericColumnRange('Average horizontal LMT').min }}</span>
          <span>{{ databaseFiltersStore.getNumericColumnRange('Average horizontal LMT').max.toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <div class="filter-section">
      <div class="text-subtitle2 q-mb-xs">Shape Factor</div>
      <div class="range-slider-container">
        <q-range
          :model-value="databaseFiltersStore.filters['Average shape factor']"
          @update:model-value="(val) => databaseFiltersStore.updateNumericFilter('Average shape factor', val)"
          :min="databaseFiltersStore.getNumericColumnRange('Average shape factor').min"
          :max="databaseFiltersStore.getNumericColumnRange('Average shape factor').max"
          :step="0.01"
          label
          dense
        />
        <div class="range-labels">
          <span>{{ databaseFiltersStore.getNumericColumnRange('Average shape factor').min }}</span>
          <span>{{ databaseFiltersStore.getNumericColumnRange('Average shape factor').max }}</span>
        </div>
      </div>
    </div>

    <div class="filter-section">
      <div class="text-subtitle2 q-mb-xs">MQI Masonry Class</div>
      <q-select
        :model-value="databaseFiltersStore.filters['Vertical loading_GMQI_class'].values"
        @update:model-value="(val) => databaseFiltersStore.updateStringFilter('Vertical loading_GMQI_class', val || [])"
        :options="databaseFiltersStore.getStringColumnOptions('Vertical loading_GMQI_class')"
        label="Select Classes"
        outlined
        dense
        clearable
        multiple
        use-chips
      />
    </div>

    <div class="filter-section">
      <q-btn
        label="Clear Filters"
        color="grey"
        outline
        size="sm"
        class="full-width q-mb-sm"
        @click="databaseFiltersStore.clearFilters"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useDatabaseFiltersStore } from 'stores/database_filters'
import { usePropertiesStore } from 'stores/properties'

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

.filter-section {
  margin-bottom: 1.5rem;
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
