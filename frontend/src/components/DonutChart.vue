<template>
  <div class="donut-chart-container">
    <h6 class="chart-title q-ma-sm">
      {{ title }}
      <template v-if="props.titleTooltip">
        <q-icon
          name="help_outline"
          color="grey-6"
        >
          <q-tooltip><div class="multiline">{{ props.titleTooltip }}</div></q-tooltip>
        </q-icon>
      </template>
    </h6>

    <div
      ref="chartContainer"
      class="chart-wrapper"
      style="width: 100%; height: 300px;"
    ></div>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'

const propertiesStore = usePropertiesStore()

interface Props {
  title: string
  titleTooltip?: string | undefined
  columnName: string
  filters: Record<string, string>
}

const props = defineProps<Props>()

const emit = defineEmits<{
  sectorClick: [payload: { columnName: string; sectorLabel: string }]
}>()

const chartContainer = ref<HTMLDivElement>()
let chartInstance: echarts.ECharts | null = null

const chartData = computed(() => {
  const table = propertiesStore.properties.unwrapOrNull();
  if (!table) {
    return []
  }

  const matchingIndicesSet = new Set<number>([...Array(table.getRowsCount()).keys()])
  Object.entries(props.filters).forEach(([filterColumn, filterValue]) => {
    table.columns.forEach(col => {
      if (col.name !== filterColumn) return
      col.values.forEach((value: string, index: number) => {
        if (value !== filterValue) {
          matchingIndicesSet.delete(index)
        }
      })
    })
  })

  const matchingIndices = Array.from(matchingIndicesSet)
  const filteredProperties = table.columns.map(col => ({
    ...col,
    values: matchingIndices.map(index => col.values[index]) as string[]
  })) || []

  // Aggregate data for the specified column
  const columnData: Record<string, number> = {}

  filteredProperties.find(col => col.name === props.columnName)?.values?.forEach((value: string) => {
    if (value) {
      columnData[value] = (columnData[value] || 0) + 1
    }
  })

  return Object.entries(columnData)
    .map(([name, count]) => ({
      name,
      value: count,
      count
    }))
    .sort((a, b) => b.count - a.count)
})

const getChartOptions = () => ({
  tooltip: {
    trigger: 'item',
    formatter: (params: { data: { name: string, count: number } }) => {
      const percentage = ((params.data.count / chartData.value.reduce((sum, item) => sum + item.count, 0)) * 100).toFixed(1)
      return `${params.data.name}<br/>Count: ${params.data.count}<br/>Percentage: ${percentage}%`
    }
  },

  series: [
    {
      name: props.columnName,
      type: 'pie',
      // Increase the inner and outer radius for a larger donut and less padding
      radius: ['45%', '80%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 0,
        borderColor: '#fff',
        borderWidth: 0
      },
      label: {
        show: true,
        position: 'outside',
        formatter: '{b}',
        fontSize: 12
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: true,
        length: 15,
        length2: 5
      },
      data: chartData.value
    }
  ]
})

const initChart = () => {
  if (chartContainer.value) {
    chartInstance = echarts.init(chartContainer.value)
    chartInstance.setOption(getChartOptions())

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    chartInstance.on('click', (params: any) => {
      if (params.data) {
        emit('sectorClick', {
          columnName: props.columnName,
          sectorLabel: params.data.name
        })
      }
    })
  }
}

const resizeChart = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

watch(() => [props.title, props.columnName, props.filters, chartData.value], () => {
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
.donut-chart-container {
  width: 100%;
  padding: 8px;
}

.chart-title {
  text-align: center;
  font-weight: bold;
}

.chart-wrapper {
  position: relative;
}

.multiline {
  white-space: pre-line;
}
</style>
