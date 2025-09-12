<template>
  <q-page>
    <h6 class="chart-title q-ma-sm">Correlation</h6>
    <div
      v-show="correlationsFiltersStore.xColumn && correlationsFiltersStore.yColumn"
      ref="chartContainer"
      class="chart-wrapper"
      style="width: 100%; height: 600px;"
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

  const data: Record<string, [number, number][]> = {}

  for (const propertyEntry of properties.value) {
    const referenceShortName = propertyEntry.find(prop => prop.name === "Wall ID")?.value?.substring(0, 2) || "Unknown"
    if (!data[referenceShortName]) {
      data[referenceShortName] = []
    }

    const xValue = parseFloat(propertyEntry.find(prop => prop.name === correlationsFiltersStore.xColumn)?.value || '')
    const yValue = parseFloat(propertyEntry.find(prop => prop.name === correlationsFiltersStore.yColumn)?.value || '')
    if (!isNaN(xValue) && !isNaN(yValue)) {
      data[referenceShortName].push([xValue, yValue])
    }
  }

  return data
})

const getChartOptions = () => ({
  tooltip: {
    trigger: 'item',
    formatter: function (params: { seriesName: string; value: (string | number)[] }) {
      return `${params.seriesName}<br/>x: ${params.value[0]}<br/>y: ${params.value[1]}`;
    },
    confine: true
  },
  xAxis: {
    type: 'value',
    name: correlationsFiltersStore.xColumn,
    axisTick: {
      alignWithLabel: true
    },
  },
  yAxis: {
    type: 'value',
    name: correlationsFiltersStore.yColumn,
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
    data: points,
  })),
  grid: {
    left: '10%',
    top: '15%',
    right: '10%',
    bottom: '10%',
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
    chartInstance.resize()
  }
}

watch(
  () => [properties.value, correlationsFiltersStore.xColumn, correlationsFiltersStore.yColumn],
  async () => {
    // Only render chart if both columns are selected
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
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', resizeChart)
})
</script>

<style scoped>
.chart-title {
  text-align: center;
  font-weight: bold;
}

.chart-wrapper {
  position: relative;
}
</style>
