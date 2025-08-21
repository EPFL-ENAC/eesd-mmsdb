<template>
  <div>
    <div class="q-mb-md">
      <!-- Filters Display Section -->
      <div class="q-mb-md">
        <div class="q-mb-sm text-subtitle2">Active Filters:</div>
        <div class="filters-container">
          <!-- Individual Filter Chips -->
          <q-chip
            v-for="(value, key) in filters"
            :key="key"
            removable
            color="primary"
            text-color="white"
            @remove="removeFilter(key)"
            class="q-ma-xs"
          >
            {{ key }}: {{ value }}
          </q-chip>

          <!-- Clear All Filters Button -->
          <q-btn
            v-if="Object.keys(filters).length > 0"
            flat
            color="negative"
            label="Clear filters"
            size="sm"
            @click="clearAllFilters"
            class="q-ml-sm"
          />
        </div>

        <!-- No Filters Message -->
        <div v-if="Object.keys(filters).length === 0" class="text-grey-6">
          No active filters
        </div>
      </div>
    </div>

    <donut-chart
      title="Example Donut Chart"
      column-name="exampleColumn"
      :filters="filters"
      @sectorClick="handleSectorClick"
    ></donut-chart>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue'
  import DonutChart from './DonutChart.vue'

  // Reactive filters dictionary
  const filters = ref<Record<string, string>>({
    exampleFilter: 'value'
  })

  // Handle sector click event
  const handleSectorClick = (payload: { columnName: string; sectorLabel: string }) => {
    console.log('Sector clicked:', payload)

    // Add the clicked sector as a filter
    filters.value[payload.columnName] = payload.sectorLabel
  }

  // Remove a specific filter
  const removeFilter = (filterKey: string) => {
    delete filters.value[filterKey]
  }

  // Clear all filters
  const clearAllFilters = () => {
    filters.value = {}
  }
</script>

<style scoped>
.filters-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  min-height: 40px;
  padding: 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: #fafafa;
}
</style>
