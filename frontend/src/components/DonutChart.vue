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
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

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

// Template data for demonstration
const templateData = [
  { name: 'Category A', value: 335, count: 335 },
  { name: 'Category B', value: 234, count: 234 },
  { name: 'Category C', value: 148, count: 148 },
  { name: 'Category D', value: 310, count: 310 },
  { name: 'Category E', value: 251, count: 251 }
]

// Chart options
const getChartOptions = () => ({
  tooltip: {
    trigger: 'item',
    formatter: (params: any) => {
      return `Count: ${params.data.count}`
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
      data: templateData
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

// Watch for prop changes
watch(() => [props.title, props.columnName, props.filters], () => {
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
  margin-bottom: 16px;
  font-weight: 500;
}

.chart-wrapper {
  position: relative;
}
</style>
