<template>
  <div ref="plotlyChart" style="width:100%;"></div>
</template>

<script setup lang="ts">
import Plotly from 'plotly.js-dist'
import { usePropertiesStore } from 'stores/properties'

const plotlyChart = ref(null)
const columns = ["Microstructure type", "Typology based on Italian Code", "No of leaves", "Average vertical LMT", "Average horizontal LMT", "Average shape factor", "Vertical loading_GMQI_class"]

const propertiesStore = usePropertiesStore()
const properties = computed(() => propertiesStore.getBinnedProperties())

function formatBinRange(min: number, max: number | "Infinity"): string {
  if (max === "Infinity") {
    return `> ${min}`
  }
  return `(${min} - ${max})`
}

async function createChart() {
  if (!Array.isArray(properties.value) || plotlyChart.value === null) {
    return
  }

  const dimensions = columns.map((col) => {
    const values = properties.value?.find(c => c.name === col)?.values || []
    const prettyValues = values.map(v => {
      const bins = propertiesStore.getColumnBins(col)
      if (!bins) {
        return v
      }

      const bin = bins.find(b => b.name === v)
      if (!bin) {
        return v
      }

      return `${v}<br />${formatBinRange(bin.min, bin.max)}`
    })

    const sortedValues = [...new Set(prettyValues)]
    if (!propertiesStore.getColumnBins(col)) {
      sortedValues.sort()
    }

    return {
      label: propertiesStore.getColumnLabel(col),
      values: prettyValues,
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
    height: 400,
    margin: {
      l: 40,
      r: 40,
      t: 30,
      b: 20
    },
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
