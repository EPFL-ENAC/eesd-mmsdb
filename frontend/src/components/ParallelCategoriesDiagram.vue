<template>
  <div ref="plotlyChart" style="width:100%; height:500px;"></div>
</template>

<script setup lang="ts">
import Plotly from 'plotly.js-dist'
import { usePropertiesStore } from 'stores/properties'
import type { PropertyEntry } from '../models';

const plotlyChart = ref(null)
const columns = ["Microstructure type", "Typology based on Italian Code", "No of leaves", "Average vertical LMT", "Average horizontal LMT", "Average shape factor", "Vertical loading_GMQI_class"]

const propertiesStore = usePropertiesStore()
const properties = computed(() => propertiesStore.properties)

async function createChart() {
  if (!Array.isArray(properties.value) || plotlyChart.value === null) {
    return
  }

  const dimensions = columns.map((col) => {
    const values = (properties.value as PropertyEntry[]).map(propertyEntry => {
      const property = propertyEntry.properties.find(p => p.name === col)
      let value = property?.value
      if (!isNaN(Number(value)) && col != "No of leaves") {
        value = Number(value).toFixed(1)
      }
      return value
    })

    const sortedValues = [...new Set(values)].sort()

    return {
      label: propertiesStore.columnLabels[col],
      values: values,
      categoryorder: 'array',
      categoryarray: sortedValues,
    }
  })

  const data = [
    {
      type: 'parcats',
      dimensions: dimensions,
      line: {
        color: "lightsteelblue",
        shape: 'hspline'
      },
    }
  ]

  const layout = {
    title: 'Parallel Categories Diagram',
    autosize: true,
    height: 500,
    font: {
      family: "Roboto, -apple-system, Helvetica Neue, Helvetica, Arial, sans-serif",
      size: 14,
    },
  }

  const config = {
    responsive: true
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  await Plotly.newPlot(plotlyChart.value, data as any, layout as any, config)
}

onMounted(async () => {
  await createChart()
})

watch(properties, async (newVal) => {
  if (plotlyChart.value && newVal) {
    await createChart()
  }
}, { deep: true, immediate: true })

</script>
