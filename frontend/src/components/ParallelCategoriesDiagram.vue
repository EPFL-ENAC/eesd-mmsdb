<template>
  <div ref="plotlyChart" style="width:100%; height:500px;"></div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import Plotly from 'plotly.js-dist'

const plotlyChart = ref(null)

onMounted(async () => {
  const data = [
    {
      type: 'parcats',
      dimensions: [
        {
          label: 'Region',
          values: ['North', 'North', 'South', 'South', 'East', 'East']
        },
        {
          label: 'Product',
          values: ['A', 'B', 'A', 'C', 'B', 'C']
        },
        {
          label: 'Outcome',
          values: ['Win', 'Lose', 'Win', 'Win', 'Lose', 'Lose']
        }
      ],
      line: {
        color: 'grey',
        shape: 'hspline'
      }
    }
  ]

  const layout = {
    title: 'Parallel Categories Diagram',
    width: 800,
    height: 500,
    font: {
      family: "Roboto, -apple-system, Helvetica Neue, Helvetica, Arial, sans-serif"
    },
  }

  if (plotlyChart.value) {
    await Plotly.newPlot(plotlyChart.value, data, layout)
  }
})
</script>
