<template>
  <div>
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
        {{ propertiesStore.getColumnLabel(key) }}: {{ value }}
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

    <div class="row q-col-gutter-md justify-center">
      <div
        v-for="column in columns"
        :key="column"
        class="col-12 col-sm-6 col-md-4"
      >
        <donut-chart
          :title="propertiesStore.getColumnLabel(column) as string"
          :title-tooltip="tooltips[column]"
          :column-name="column"
          :filters="filters"
          @sectorClick="handleSectorClick"
        ></donut-chart>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import DonutChart from './DonutChart.vue'

const { t } = useI18n();
const propertiesStore = usePropertiesStore()

const columns = ["Microstructure type", "Typology based on Italian Code", "Vertical loading_GMQI_class"]
const tooltips: Record<string, string> = {
  "Typology based on Italian Code": `${t("definitions.typology")} ${["A", "B", "C", "D", "E", "E1"].map(typology => typology + ": " + t("typologies." + typology)).join(", ")}`,
  "Vertical loading_GMQI_class": t("definitions.GMQI"),
}
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
