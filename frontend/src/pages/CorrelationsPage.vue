<template>
  <q-page>
    <h6 class="chart-title q-ma-sm">Correlation</h6>
    <div class="chart-and-loading-wrapper">
      <div
        v-show="correlationsFiltersStore.xColumn && correlationsFiltersStore.yColumn"
        ref="chartContainer"
        class="chart-wrapper"
      ></div>
      <loading-overlay :visible="isRegressionLoading" />
    </div>

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
import type { CorrelationResult } from 'src/models';
import LoadingOverlay from 'src/components/LoadingOverlay.vue';

const propertiesStore = usePropertiesStore()
const correlationsFiltersStore = useCorrelationsFiltersStore()
const properties = computed(() => propertiesStore.properties)
const correlationParameters = ref<CorrelationResult | null>(null)

const chartContainer = ref<HTMLDivElement>()
let chartInstance: echarts.ECharts | null = null

interface ScatterDataItem {
  value: [number, number];
  wallID: string;
  reference: string;
}

const selectedCategories = ref<{ [key: string]: boolean }>({})
const isRegressionLoading = ref(false)

const scatterData = computed(() => {
  if (!properties.value || !Array.isArray(properties.value) || !correlationsFiltersStore.xColumn || !correlationsFiltersStore.yColumn) {
    return {}
  }

  const scatterData: Record<string, ScatterDataItem[]> = {}

  const wallIDs = propertiesStore.getColumnValues('Wall ID') as string[]
  const references = propertiesStore.getColumnValues('Reference') as string[]
  const xValues = propertiesStore.getColumnValues(propertiesStore.getColumnKeyFromLabel(correlationsFiltersStore.xColumn) as string) as string[]
  const yValues = propertiesStore.getColumnValues(propertiesStore.getColumnKeyFromLabel(correlationsFiltersStore.yColumn) as string) as string[]

  for (let i = 0; i < wallIDs.length; i++) {
    const wallID = wallIDs[i]
    const referenceShortName = wallID?.substring(0, 2) || "Unknown"
    if (!scatterData[referenceShortName]) {
      scatterData[referenceShortName] = []
    }

    const xValue = parseFloat(xValues[i] || '')
    const yValue = parseFloat(yValues[i] || '')
    if (!isNaN(xValue) && !isNaN(yValue)) {
      scatterData[referenceShortName].push({
        value: [xValue, yValue],
        wallID: wallID || 'Unknown',
        reference: references[i] || 'Unknown'
      })
    }
  }

  return scatterData
})

const regressionData = computed(() => {
  if (!correlationsFiltersStore.xColumn || !correlationsFiltersStore.yColumn || Object.keys(scatterData.value).length === 0 || !correlationParameters.value) {
    return []
  }

  const allPoints: [number, number][] = []
  Object.entries(scatterData.value).forEach(([category, points]) => {
    if (!selectedCategories.value[category]) {
      return
    }

    points.forEach(point => {
      allPoints.push(point.value)
    })
  })

  if (allPoints.length === 0) {
    return []
  }

  const xValues = allPoints.map(point => point[0])
  const minX = Math.min(...xValues)
  const maxX = Math.max(...xValues)

  return [
    [minX, correlationParameters.value.slope * minX + correlationParameters.value.intercept],
    [maxX, correlationParameters.value.slope * maxX + correlationParameters.value.intercept]
  ] as [number, number][]
})


const getChartOptions = () => {
  const scatterSeries = Object.entries(scatterData.value).map(([category, points], idx) => ({
    name: category,
    type: 'scatter',
    symbol: ['circle', 'square', 'triangle', 'diamond', 'pin', 'arrow', 'roundRect'][idx % 6],
    data: points.map(point => point.value),
  }))

  const regressionSeries = regressionData.value.length > 0 ? [{
    name: 'Linear Regression',
    type: 'line',
    symbol: 'none',
    lineStyle: {
      color: '#aaaaaa',
      width: 2,
      type: 'dashed'
    },
    data: regressionData.value,
    tooltip: {
      formatter: function (params: { value: (string | number)[] }) {
        const xName = correlationsFiltersStore.xColumn;
        const yName = correlationsFiltersStore.yColumn;
        return `Linear Regression<br/>${xName}: ${params.value[0]}<br/>${yName}: ${params.value[1]}`;
      }
    }
  }] : []

  const allSeries = [...scatterSeries, ...regressionSeries]
  const legendData = [...Object.keys(scatterData.value)]

  return {
    tooltip: {
      trigger: 'item',
      formatter: function (params: { seriesName: string; value: (string | number)[]; dataIndex: number; seriesIndex: number; seriesType: string }) {
        if (params.seriesType === 'line') {
          return false
        }

        const xName = correlationsFiltersStore.xColumn;
        const yName = correlationsFiltersStore.yColumn;

        const category = params.seriesName;
        const metadata: ScatterDataItem | undefined = scatterData.value[category]?.[params.dataIndex];
        const wallID = metadata?.wallID || 'Unknown';

        return `<b>Wall ID:</b> ${wallID}<br/><b>${xName}</b>: ${Number(params.value[0]).toFixed(2)}<br/><b>${yName}</b>: ${Number(params.value[1]).toFixed(2)}<br/><b>Reference:</b> ${metadata?.reference || 'Unknown'}`;
      },
      confine: true
    },
    xAxis: {
      type: 'value',
      name: `${correlationsFiltersStore.xColumn} [${propertiesStore.getColumnUnit(propertiesStore.getColumnKeyFromLabel(correlationsFiltersStore.xColumn as string) as string) || '-'}]`,
      axisTick: {
        alignWithLabel: true
      },
      scale: true,
      nameLocation: 'middle',
      nameGap: 35
    },
    yAxis: {
      type: 'value',
      name: `${correlationsFiltersStore.yColumn} [${propertiesStore.getColumnUnit(propertiesStore.getColumnKeyFromLabel(correlationsFiltersStore.yColumn as string) as string) || '-'}]`,
      scale: true,
      nameLocation: 'middle',
      nameGap: 35,
    },
    legend: {
      data: legendData,
      top: '30px',
      left: '0px',
      orient: 'vertical',
      formatter: (name: string) => {
        const fsd = scatterData.value[name]?.at(0)
        return `${name} (${fsd?.reference || 'Unknown reference'})`
      }
    },
    series: allSeries,
    grid: {
      left: '200px',
      top: '30px',
      right: '10px',
      bottom: '10px',
      containLabel: true
    },
    graphic: [
      {
        type: 'text',
        z: 100,
        left: 'center',
        top: 0,
        style: {
          fill: '#333',
          width: 400,
          overflow: 'break',
          text: correlationParameters.value
            ? `${correlationsFiltersStore.yColumn} = ${correlationParameters.value.slope.toFixed(2)} × ${correlationsFiltersStore.xColumn} ${correlationParameters.value.intercept >= 0 ? '+' : '-'} ${Math.abs(correlationParameters.value.intercept).toFixed(2)}\nR² = ${correlationParameters.value.R2.toFixed(2)}`
            : '',
        }
      }
    ]
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

    chartInstance.on('legendselectchanged', (event) => {
      selectedCategories.value = (event as { name: string, selected: { [key: string]: boolean }, type: "legendselectchanged" }).selected
    })

    populateSelectedCategoriesFromChartLegend()
  }
}

function populateSelectedCategoriesFromChartLegend() {
  if (chartInstance) {
    const legend = (chartInstance.getOption().legend as { data: string[], selected: { [key: string]: boolean } }[])?.[0];
    if (legend) {
      const selectedAvailable = Object.keys(legend.selected).length > 0
      selectedCategories.value = selectedAvailable ? legend.selected : legend.data.reduce((acc, curr) => {
        acc[curr] = true
        return acc
      }, {} as { [key: string]: boolean })
    }
  }
}

async function updateChart() {
  if (!chartInstance) {
    return await initChart()
  }
  chartInstance.setOption(getChartOptions())
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
  () => [correlationsFiltersStore.xColumn, correlationsFiltersStore.yColumn, selectedCategories.value],
  async () => {
    if (correlationsFiltersStore.xColumn && correlationsFiltersStore.yColumn) {
      isRegressionLoading.value = true

      const allowedCategories = Object.entries(selectedCategories.value)
        .filter(([, isSelected]) => isSelected)
        .map(([category]) => category)
      correlationParameters.value = await correlationsFiltersStore.getCorrelationParameters(allowedCategories)

      isRegressionLoading.value = false
    } else {
      correlationParameters.value = null
    }
  },
  { immediate: true }
)

watch(
  () => [scatterData.value, regressionData.value],
  async () => {
    if (correlationsFiltersStore.xColumn && correlationsFiltersStore.yColumn) {
      await updateChart()
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

.chart-and-loading-wrapper {
  position: relative;
  width: 100%;
  max-width: 1000px;
  height: 800px;
  max-height: calc(100vh - clamp(250px, -20vw + 450px, 350px));
  margin: 0 auto;
}

.chart-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
  transition: all 0.3s ease-in-out;
  margin: 0 auto;
}

.chart-wrapper canvas {
  transition: all 0.3s ease-in-out;
}
</style>
