<template>
  <div>
    <!-- Filter chips -->
    <div>
      <q-chip
        v-for="(value, key) in filters"
        :key="key"
        removable
        color="primary"
        text-color="white"
        @remove="removeFilter(key)"
        class="q-ma-xs"
        size="sm"
      >
        {{ propertiesStore.columnLabels[key] }}: {{ value }}
      </q-chip>

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

    <!-- Donut charts -->
    <div class="row q-col-gutter-md justify-center">
      <div
        v-for="column in columns"
        :key="column"
        class="col-12 col-sm-6 col-md-4"
      >
        <donut-chart
          :title="propertiesStore.columnLabels[column] as string"
          :column-name="column"
          :filters="filters"
          @sectorClick="handleSectorClick"
        ></donut-chart>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import DonutChart from './DonutChart.vue'

const propertiesStore = usePropertiesStore()

const columns = ["Microstructure type", "Typology based on Italian Code", "Vertical loading_GMQI_class"]
const filters = ref<Record<string, string>>({})

const handleSectorClick = (payload: { columnName: string; sectorLabel: string }) => {
  filters.value[payload.columnName] = payload.sectorLabel
}

const removeFilter = (filterKey: string) => {
  delete filters.value[filterKey]
}

const clearAllFilters = () => {
  filters.value = {}
}
</script>

<style scoped>
</style>
