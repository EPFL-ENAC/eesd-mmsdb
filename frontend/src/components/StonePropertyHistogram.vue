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
import type { Property } from '../models';

interface Props {
  title: string
  wallID: string
  columnName: string
}

const props = defineProps<Props>()

const stonePropertiesStore = useStonePropertiesStore()
const stoneProperties = ref<Property[][] | null>(null)

async function fetchStoneProperties(wallId: string) {
  if (!wallId) {
    stoneProperties.value = null
    return
  }
  stoneProperties.value = await stonePropertiesStore.getProperties(wallId)
}

watch(() => props.wallID, fetchStoneProperties, { immediate: true })

const binsConfiguration = computed(() => {
  return {
    "Stone length [m]": [
      {
        "name": "NF",
        "fullName": "< 20cm (Not Fulfilled)",
        "min": 0,
        "max": 0.2,
      },
      {
        "name": "PF",
        "fullName": "20-40cm (Partially Fulfilled)",
        "min": 0.2,
        "max": 0.4,
      },
      {
        "name": "F",
        "fullName": "≥ 40cm (Fulfilled)",
        "min": 0.4,
        "max": Infinity,
      },
    ],

    "Shape factor [-]": [
      {
        "name": "NF",
        "fullName": "< 0.57 (Not Fulfilled)",
        "min": 0,
        "max": 0.57,
      },
      {
        "name": "PF",
        "fullName": "0.57-0.73 (Partially Fulfilled)",
        "min": 0.57,
        "max": 0.73,
      },
      {
        "name": "F",
        "fullName": "≥ 0.73 (Fulfilled)",
        "min": 0.73,
        "max": Infinity,
      },
    ],

  }[props.columnName] || [...Array(5).keys()].map((_, i) => ({
    name: ((i + 0.5) * 0.2).toFixed(1),
    fullName: `${(i * 0.2).toFixed(1)}-${((i + 1) * 0.2).toFixed(1)}`,
    min: i * 0.2,
    max: (i + 1) * 0.2
  }))
})

const chartContainer = ref<HTMLDivElement>()
let chartInstance: echarts.ECharts | null = null

const chartData = computed(() => {
  if (!stoneProperties.value || !Array.isArray(stoneProperties.value)) {
    return []
  }

  const counts = binsConfiguration.value.map(bin =>
    (stoneProperties.value as Property[][]).filter(propertyEntry => {
      const property = propertyEntry.find(p => p.name === props.columnName)
      if (property?.value !== undefined) {
        const value = parseFloat(property.value)
        return value >= bin.min && value < bin.max
      }
      return false
    }).length
  )
  const total = stoneProperties.value.length
  return binsConfiguration.value.map((bin, index) => [bin.name, counts[index] as number / total * 100])
})

const getChartOptions = () => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    formatter: function (params: any) {
      const binIndex = params[0].dataIndex
      const bin = binsConfiguration.value[binIndex]
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
  },
  series: [
    {
      type: 'bar',
      data: chartData.value.map(([_, count]) => (count as number).toFixed(2)),
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
    left: '5%',
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
