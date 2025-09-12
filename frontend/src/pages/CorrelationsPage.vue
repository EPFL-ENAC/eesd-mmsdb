<template>
  <q-page v-show=false>
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

const computeLinearRegression = (points: [number, number][]) => {
  if (points.length < 2) return null

  const n = points.length
  const sumX = points.reduce((sum, point) => sum + point[0], 0)
  const sumY = points.reduce((sum, point) => sum + point[1], 0)
  const sumXY = points.reduce((sum, point) => sum + point[0] * point[1], 0)
  const sumXX = points.reduce((sum, point) => sum + point[0] * point[0], 0)

  const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX)
  const intercept = (sumY - slope * sumX) / n

  return { slope, intercept }
}

const chartData = computed(() => {
  if (!properties.value || !Array.isArray(properties.value) || !correlationsFiltersStore.xColumn || !correlationsFiltersStore.yColumn) {
    return { scatterData: {}, regressionData: [] }
  }

  const scatterData: Record<string, { value: [number, number]; wallID: string }[]> = {}
  const allPoints: [number, number][] = []

  for (const propertyEntry of properties.value) {
    const wallID = propertyEntry.find(prop => prop.name === "Wall ID")?.value
    const referenceShortName = wallID?.substring(0, 2) || "Unknown"
    if (!scatterData[referenceShortName]) {
      scatterData[referenceShortName] = []
    }

    const xValue = parseFloat(propertyEntry.find(prop => propertiesStore.getColumnLabel(prop.name) === correlationsFiltersStore.xColumn)?.value || '')
    const yValue = parseFloat(propertyEntry.find(prop => propertiesStore.getColumnLabel(prop.name) === correlationsFiltersStore.yColumn)?.value || '')
    if (!isNaN(xValue) && !isNaN(yValue)) {
      scatterData[referenceShortName].push({
        value: [xValue, yValue],
        wallID: wallID || 'Unknown'
      })
      allPoints.push([xValue, yValue])
    }
  }

  // Compute linear regression for all data points
  const regression = computeLinearRegression(allPoints)
  let regressionData: [number, number][] = []

  if (regression && allPoints.length > 0) {
    const xValues = allPoints.map(point => point[0])
    const minX = Math.min(...xValues)
    const maxX = Math.max(...xValues)

    // Generate regression line points
    regressionData = [
      [minX, regression.slope * minX + regression.intercept],
      [maxX, regression.slope * maxX + regression.intercept]
    ]
  }

  return { scatterData, regressionData }
})

const getChartOptions = () => {
  const scatterSeries = Object.entries(chartData.value.scatterData).map(([category, points], idx) => ({
    name: category,
    type: 'scatter',
    symbol: ['circle', 'square', 'triangle', 'diamond', 'pin', 'arrow', 'roundRect'][idx % 7],
    data: points.map(point => point.value),
  }))

  const regressionSeries = chartData.value.regressionData.length > 0 ? [{
    name: 'Linear Regression',
    type: 'line',
    symbol: 'none',
    lineStyle: {
      color: '#aaaaaa',
      width: 2,
      type: 'dashed'
    },
    data: chartData.value.regressionData,
    tooltip: {
      formatter: function (params: { value: (string | number)[] }) {
        const xName = correlationsFiltersStore.xColumn;
        const yName = correlationsFiltersStore.yColumn;
        return `Linear Regression<br/>${xName}: ${params.value[0]}<br/>${yName}: ${params.value[1]}`;
      }
    }
  }] : []

  const allSeries = [...scatterSeries, ...regressionSeries]
  const legendData = [...Object.keys(chartData.value.scatterData)]

  return {
    tooltip: {
      trigger: 'item',
      formatter: function (params: { seriesName: string; value: (string | number)[]; dataIndex: number; seriesIndex: number; seriesType: string }) {
        if (params.seriesType === 'line') {
          // This is handled by the series-specific tooltip
          return null
        }

        const xName = correlationsFiltersStore.xColumn;
        const yName = correlationsFiltersStore.yColumn;
        // Find the wallID from the chartData
        const category = params.seriesName;
        const wallID = chartData.value.scatterData[category]?.[params.dataIndex]?.wallID || 'Unknown';
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
      data: legendData,
      top: '5%',
      left: 'center'
    },
    series: allSeries,
    grid: {
      left: '5%',
      top: '12%',
      right: '5%',
      bottom: '5%',
      containLabel: true
    }
  }
}

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
