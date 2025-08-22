<template>
  <div class="donut-chart-container">
    <h6 class="chart-title q-ma-sm">{{ title }}</h6>
    <div
      ref="chartContainer"
      class="chart-wrapper"
      style="width: 100%; height: 400px;"
    ></div>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'

const propertiesStore = usePropertiesStore()
const properties = computed(() => propertiesStore.properties)

// Props
interface Props {
  title: string
  columnName: string
  filters: Record<string, string>
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  sectorClick: [payload: { columnName: string; sectorLabel: string }]
}>()

// Refs
const chartContainer = ref<HTMLDivElement>()
let chartInstance: echarts.ECharts | null = null

// Computed data from properties store
const chartData = computed(() => {
  if (!properties.value || !Array.isArray(properties.value)) {
    return []
  }

  // Filter properties based on filters prop
  const filteredProperties = properties.value.filter(propertyEntry => {
    return Object.entries(props.filters).every(([filterColumn, filterValue]) => {
      const property = propertyEntry.properties.find(p => p.name === filterColumn)
      return !filterValue || property?.value === filterValue
    })
  })

  // Aggregate data for the specified column
  const columnData: Record<string, number> = {}

  filteredProperties.forEach(propertyEntry => {
    const property = propertyEntry.properties.find(p => p.name === props.columnName)
    if (property?.value) {
      const value = property.value
      columnData[value] = (columnData[value] || 0) + 1
    }
  })

  // Convert to chart format
  return Object.entries(columnData)
    .map(([name, count]) => ({
      name,
      value: count,
      count
    }))
    .sort((a, b) => b.count - a.count) // Sort by count descending
})

// Chart options
const getChartOptions = () => ({
  tooltip: {
    trigger: 'item',
    formatter: (params: any) => {
      const percentage = ((params.data.count / chartData.value.reduce((sum, item) => sum + item.count, 0)) * 100).toFixed(1)
      return `${params.data.name}<br/>Count: ${params.data.count}<br/>Percentage: ${percentage}%`
    }
  },

  series: [
    {
      name: props.columnName,
      type: 'pie',
      radius: ['40%', '70%'],
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
        length2: 10
      },
      data: chartData.value
    }
  ]
})

// Initialize chart
const initChart = () => {
  if (chartContainer.value) {
    chartInstance = echarts.init(chartContainer.value)
    chartInstance.setOption(getChartOptions())

    // Add click event listener
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

// Resize chart
const resizeChart = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// Watch for prop changes and data changes
watch(() => [props.title, props.columnName, props.filters, chartData.value], () => {
  if (chartInstance) {
    chartInstance.setOption(getChartOptions())
  }
}, { deep: true })

// Lifecycle hooks
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
  padding: 16px;
}

.chart-title {
  text-align: center;
  font-weight: bold;
}

.chart-wrapper {
  position: relative;
}
</style>
