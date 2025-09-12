<template>
  <q-page>
    <h6 class="chart-title q-ma-sm">Correlation</h6>
    <div
      v-show="correlationsFiltersStore.xColumn && correlationsFiltersStore.yColumn"
      ref="chartContainer"
      class="chart-wrapper"
      style="width: 100%; max-width: 800px; height: 800px;"
    ></div>

    <div v-show="!correlationsFiltersStore.xColumn || !correlationsFiltersStore.yColumn">
      <q-banner class="bg-warning text-black">
        Please select both X and Y columns to display the correlation chart.
      </q-banner>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { usePropertiesStore } from 'stores/properties'
import { useCorrelationsFiltersStore } from 'stores/correlations_filters'
const propertiesStore = usePropertiesStore()
const correlationsFiltersStore = useCorrelationsFiltersStore()
const properties = computed(() => propertiesStore.properties)

const chartContainer = ref<HTMLDivElement>()
let chartInstance: echarts.ECharts | null = null

const chartData = computed(() => {
  if (!properties.value || !Array.isArray(properties.value) || !correlationsFiltersStore.xColumn || !correlationsFiltersStore.yColumn) {
    return {}
  }

  const data: Record<string, { value: [number, number]; wallID: string }[]> = {}

  for (const propertyEntry of properties.value) {
    const wallID = propertyEntry.find(prop => prop.name === "Wall ID")?.value
    const referenceShortName = wallID?.substring(0, 2) || "Unknown"
    if (!data[referenceShortName]) {
      data[referenceShortName] = []
    }

    const xValue = parseFloat(propertyEntry.find(prop => propertiesStore.getColumnLabel(prop.name) === correlationsFiltersStore.xColumn)?.value || '')
    const yValue = parseFloat(propertyEntry.find(prop => propertiesStore.getColumnLabel(prop.name) === correlationsFiltersStore.yColumn)?.value || '')
    if (!isNaN(xValue) && !isNaN(yValue)) {
      data[referenceShortName].push({
        value: [xValue, yValue],
        wallID: wallID || 'Unknown'
      })
    }
  }

  return data
})

const getChartOptions = () => ({
  tooltip: {
    trigger: 'item',
    formatter: function (params: { seriesName: string; value: (string | number)[]; dataIndex: number; seriesIndex: number }) {
      const xName = correlationsFiltersStore.xColumn;
      const yName = correlationsFiltersStore.yColumn;
      // Find the wallID from the chartData
      const category = params.seriesName;
      const wallID = chartData.value[category]?.[params.dataIndex]?.wallID || 'Unknown';
      return `Wall ID: ${wallID}<br/>${xName}: ${params.value[0]}<br/>${yName}: ${params.value[1]}`;
    },
    confine: true
  },
  xAxis: {
    type: 'value',
    name: correlationsFiltersStore.xColumn,
    axisTick: {
      alignWithLabel: true
    },
    scale: true,
    nameLocation: 'middle',
    nameGap: 35
  },
  yAxis: {
    type: 'value',
    name: correlationsFiltersStore.yColumn,
    scale: true,
    nameLocation: 'middle',
    nameGap: 35,
  },
  legend: {
    data: Object.keys(chartData.value),
    top: '5%',
    left: 'center'
  },
  series: Object.entries(chartData.value).map(([category, points], idx) => ({
    name: category,
    type: 'scatter',
    symbol: ['circle', 'square', 'triangle', 'diamond', 'pin', 'arrow', 'roundRect'][idx % 6],
    data: points.map(point => point.value),
  })),
  grid: {
    left: '5%',
    top: '12%',
    right: '5%',
    bottom: '5%',
    containLabel: true
  }
})

const initChart = async () => {
  await nextTick()
  if (chartContainer.value) {
    if (chartInstance) {
      chartInstance.dispose()
    }
    chartInstance = echarts.init(chartContainer.value)
    chartInstance.setOption(getChartOptions())
  }
}

const resizeChart = () => {
  if (chartInstance) {
    requestAnimationFrame(() => {
      chartInstance?.resize({
        animation: {
          duration: 300,
          easing: 'cubicOut'
        }
      })
    })
  }
}

const onDrawerToggled = resizeChart

watch(
  () => [properties.value, correlationsFiltersStore.xColumn, correlationsFiltersStore.yColumn],
  async () => {
    if (correlationsFiltersStore.xColumn && correlationsFiltersStore.yColumn) {
      await initChart()
    } else if (chartInstance) {
      chartInstance.clear()
    }
  },
  { immediate: true }
)

onMounted(async () => {
  await nextTick()
  if (correlationsFiltersStore.xColumn && correlationsFiltersStore.yColumn) {
    await initChart()
  }
  window.addEventListener('resize', resizeChart)
  window.addEventListener('drawer-toggled', onDrawerToggled)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', resizeChart)
  window.removeEventListener('drawer-toggled', onDrawerToggled)
})
</script>

<style scoped>
.chart-title {
  text-align: center;
  font-weight: bold;
}

.chart-wrapper {
  position: relative;
  transition: all 0.3s ease-in-out;
  margin: 0 auto;
}

.chart-wrapper canvas {
  transition: all 0.3s ease-in-out;
}
</style>
