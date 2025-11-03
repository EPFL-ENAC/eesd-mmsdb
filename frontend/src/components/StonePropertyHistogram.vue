<template>
  <div class="histogram-container">
    <h6 class="chart-title q-ma-sm">{{ title }}</h6>
    <div
      ref="chartContainer"
      class="chart-wrapper"
      style="width: 100%; height: 300px;"
    ></div>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { useReactiveAction } from 'src/reactiveCache/vue/composables';
import type { StaticTable } from 'src/utils/table';

interface Props {
  title: string
  wallID: string
  columnName: string
}

const props = defineProps<Props>()

const stonePropertiesStore = useStonePropertiesStore()
const stoneProperties = useReactiveAction(props.wallID, (wallId) => stonePropertiesStore.getProperties(wallId))

const binsConfiguration = computed(() => {
  return stonePropertiesStore.getColumnBins(props.columnName) ?? [];
})

const chartContainer = ref<HTMLDivElement>()
let chartInstance: echarts.ECharts | null = null

function getNumberOfCellsInRange(table: StaticTable, columnName: string, min: number, max: number): number {
  const isCellInRange = (value: string | undefined): boolean => {
    if (value === undefined) return false
    const numValue = parseFloat(value)
    return numValue >= min && numValue < max
  }

  return table.getCellsFiltered(columnName, isCellInRange)?.length || 0
}

const chartData = computed(() => {
  const table = stoneProperties.value.unwrapOrNull();
  if (!table) {
    return []
  }

  const counts = binsConfiguration.value.map(bin => getNumberOfCellsInRange(table, props.columnName, bin.min, bin.max))
  const total = table.getRowsCount() || 1
  return binsConfiguration.value.map((bin, index) => [bin.name, counts[index] as number / total * 100])
})

const getChartOptions = () => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    formatter: function (params: { dataIndex: number }[]) {
      const binIndex = params[0]?.dataIndex
      const bin = binsConfiguration.value[binIndex || 0]
      return bin?.fullName
    },
    confine: true
  },
  xAxis: {
    type: 'category',
    data: binsConfiguration.value.map(bin => bin.name),
    axisTick: {
      alignWithLabel: true
    },
  },
  yAxis: {
    type: 'value',
    name: 'Amount (%)',
    min: 0,
    // max: 100
    nameLocation: 'middle',
    nameGap: 25,
  },
  series: [
    {
      type: 'bar',
      data: chartData.value.map(([, count]) => (count as number).toFixed(2)),
      label: {
        show: true,
        position: 'top',
        formatter: '{c} %'
      },
      itemStyle: {
        color: '#409eff'
      },
      barWidth: '90%'
    }
  ],
  grid: {
    left: '10%',
    top: '10%',
    right: '5%',
    bottom: '5%',
    containLabel: true
  }
})

const initChart = () => {
  if (chartContainer.value) {
    chartInstance = echarts.init(chartContainer.value)
    chartInstance.setOption(getChartOptions())
  }
}

const resizeChart = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

watch(() => [props.title, props.wallID, props.columnName, chartData.value], () => {
  if (chartInstance) {
    chartInstance.setOption(getChartOptions())
  }
}, { deep: true })

onMounted(() => {
  initChart()
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
.histogram-container {
  width: 100%;
}

.chart-title {
  text-align: center;
  font-weight: bold;
}

.chart-wrapper {
  position: relative;
}
</style>
