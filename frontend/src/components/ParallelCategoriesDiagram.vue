<template>
  <div ref="plotlyChart" class="parcats-chart" style="width:100%;"></div>
</template>

<script setup lang="ts">
import Plotly from 'plotly.js-dist'
import { useAsyncResultRef } from 'unwrapped/vue'
import { usePropertiesStore } from 'stores/properties'

const plotlyChart = ref<HTMLDivElement | null>(null)
let reapplyStyles: ((evt: { event?: { type?: string } }) => void) | null = null
let mutationObserver: MutationObserver | null = null
let rafId: number | null = null
const columns = ["Microstructure type", "Typology based on Italian Code", "No of leaves", "Average vertical LMT", "Average horizontal LMT", "Average shape factor", "Vertical loading_GMQI_class"]
const mutationObserverConfig = {
  childList: true,
  subtree: true,
  attributes: true,
  attributeFilter: ['stroke', 'stroke-width', 'width', 'x', 'height', 'y', 'd', 'fill-opacity', 'transform']
}

const propertiesStore = usePropertiesStore()
const binnedProperties = useAsyncResultRef(propertiesStore.getBinnedProperties())

function formatBinRange(min: number, max: number | "Infinity"): string {
  if (max === "Infinity") {
    return `> ${min}`
  }
  return `(${min} - ${max})`
}

function applyChartStyles(isUnhover = false) {
  if (mutationObserver) {
    mutationObserver.disconnect()
    activeReapply = true
  }

  if (!plotlyChart.value) {
    activeReapply = false
    return
  }

  const svg = plotlyChart.value.querySelector('svg')
  if (!svg) {
    activeReapply = false
    return
  }

  applyBlockStyles()

  const paths = svg.querySelectorAll<SVGPathElement>('path.path')
  const lastIdx = paths.length - 1
  paths.forEach((path, i) => {
    path.setAttribute('fill-opacity',
      isUnhover ? '0.2' : (i === lastIdx ? '0.5' : '0.2'))
  })

  styleHoverTooltips()

  activeReapply = false
  if (mutationObserver && plotlyChart.value) {
    const layer = plotlyChart.value.querySelector('svg g.parcatslayer')
    if (layer) {
      mutationObserver.observe(layer, mutationObserverConfig)
    }
  }
}

function applyBlockStyles() {
  if (!plotlyChart.value) return
  const svg = plotlyChart.value.querySelector('svg')
  if (!svg) return

  // Remove borders and widen blocks with rounded corners
  const catrects = svg.querySelectorAll<SVGRectElement>('rect.catrect')
  catrects.forEach((rect) => {
    const baseWidth = parseFloat(rect.getAttribute('data-original-width') || rect.getAttribute('width') || '0')
    if (!rect.hasAttribute('data-original-width')) {
      rect.setAttribute('data-original-width', String(baseWidth))
    }
    const newWidth = baseWidth * 1.5
    const baseX = parseFloat(rect.getAttribute('data-original-x') || rect.getAttribute('x') || '0')
    if (!rect.hasAttribute('data-original-x')) {
      rect.setAttribute('data-original-x', String(baseX))
    }
    const xShift = (baseWidth - newWidth) / 2

    rect.setAttribute('width', String(newWidth))
    rect.setAttribute('x', String(baseX + xShift))
    rect.setAttribute('rx', '4')
    rect.setAttribute('stroke', 'none')
  })

  const bandrects = svg.querySelectorAll<SVGRectElement>('rect.bandrect')
  bandrects.forEach((rect) => {
    const baseWidth = parseFloat(rect.getAttribute('data-original-width') || rect.getAttribute('width') || '0')
    if (!rect.hasAttribute('data-original-width')) {
      rect.setAttribute('data-original-width', String(baseWidth))
    }
    const newWidth = baseWidth * 1.5
    const baseX = parseFloat(rect.getAttribute('data-original-x') || rect.getAttribute('x') || '0')
    if (!rect.hasAttribute('data-original-x')) {
      rect.setAttribute('data-original-x', String(baseX))
    }
    const xShift = (baseWidth - newWidth) / 2

    rect.setAttribute('width', String(newWidth))
    rect.setAttribute('x', String(baseX + xShift))
    rect.setAttribute('rx', '4')
    rect.setAttribute('stroke', 'none')
  })

  // Shift catlabels outward for more horizontal space between blocks and text
  const catlabels = svg.querySelectorAll<SVGTextElement>('text.catlabel')
  catlabels.forEach((label) => {
    const baseX = parseFloat(label.getAttribute('data-original-x') || label.getAttribute('x') || '0')
    if (!label.hasAttribute('data-original-x')) {
      label.setAttribute('data-original-x', String(baseX))
    }
    const anchor = label.getAttribute('text-anchor')
    const margin = 6
    let extraX: number
    if (anchor === 'start') {
      extraX = margin
    } else {
      extraX = -margin
    }

    label.setAttribute('x', String(baseX + extraX))

    label.querySelectorAll('tspan').forEach((tspan) => {
      const tspanX = parseFloat(tspan.getAttribute('data-original-x') || tspan.getAttribute('x') || '0')
      if (!tspan.hasAttribute('data-original-x')) {
        tspan.setAttribute('data-original-x', String(tspanX))
      }
      tspan.setAttribute('x', String(tspanX + extraX))
    })
  })

  // Shift dimlabels (column titles) upward
  const dimlabels = svg.querySelectorAll<SVGTextElement>('text.dimlabel')
  dimlabels.forEach((label) => {
    const baseY = parseFloat(label.getAttribute('data-original-y') || label.getAttribute('y') || '-5')
    if (!label.hasAttribute('data-original-y')) {
      label.setAttribute('data-original-y', String(baseY))
    }
    label.setAttribute('y', String(baseY - 10))
  })
}

function styleHoverTooltips() {
  if (!plotlyChart.value) return
  const hoverlayer = plotlyChart.value.querySelector<SVGGElement>('g.hoverlayer')
  if (!hoverlayer) return

  hoverlayer.querySelectorAll<SVGGElement>('g.hovertext').forEach((g) => {
    const path = g.querySelector<SVGPathElement>('path')
    if (!path) return

    const bbox = path.getBBox()
    const rx = 6
    path.setAttribute('d',
      `M${bbox.x + rx},${bbox.y}` +
      `h${bbox.width - 2 * rx}` +
      `a${rx},${rx},0,0,1,${rx},${rx}` +
      `v${bbox.height - 2 * rx}` +
      `a${rx},${rx},0,0,1,${-rx},${rx}` +
      `h${-bbox.width + 2 * rx}` +
      `a${rx},${rx},0,0,1,${-rx},${-rx}` +
      `v${-bbox.height + 2 * rx}` +
      `a${rx},${rx},0,0,1,${rx},${-rx}` +
      'Z'
    )
  })
}

async function createChart() {
  const table = binnedProperties.value.unwrapOrNull();
  if (!table || plotlyChart.value === null) {
    return
  }

  const dimensions = columns.map((col) => {
    const values = table.getColumnValues(col) || []
    const prettyValues = values.map(v => {
      const bins = propertiesStore.getColumnBins(col)
      if (!bins) {
        return v
      }

      const bin = bins.find(b => b.name === v)
      if (!bin) {
        return v
      }

      return `${v}<br />${formatBinRange(bin.min, bin.max)}`
    })

    const sortedValues = [...new Set(prettyValues)]
    if (!propertiesStore.getColumnBins(col)) {
      sortedValues.sort()
    }

    return {
      label: propertiesStore.getColumnLabel(col),
      values: prettyValues,
      categoryorder: 'array',
      categoryarray: sortedValues,
    }
  })

  const data = [
    {
      type: 'parcats',
      dimensions: dimensions,
      line: {
        color: "#5470c6",
        shape: 'hspline'
      },
    }
  ]

  const layout = {
    title: 'Parallel Categories Diagram',
    autosize: true,
    height: 400,
    margin: {
      l: 40,
      r: 40,
      t: 30,
      b: 20
    },
    font: {
      family: "Roboto, -apple-system, Helvetica Neue, Helvetica, Arial, sans-serif",
      size: 14,
    },
  }

  const config = {
    responsive: true
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  await Plotly.newPlot(plotlyChart.value, data as any, layout as any, config)

  await new Promise((resolve) => setTimeout(resolve, 0))
  applyChartStyles(true)
  setupMutationObserver()

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const gd = plotlyChart.value as any
  if (reapplyStyles) {
    gd.off('plotly_hover', reapplyStyles)
    gd.off('plotly_unhover', reapplyStyles)
    gd.off('plotly_restyle', reapplyStyles)
  }
  reapplyStyles = (evt: { event?: { type?: string } }) => {
    const isUnhover = evt?.event?.type === 'mouseout'
    queueMicrotask(() => {
      applyChartStyles(isUnhover)
      styleHoverTooltips()
    })
  }
  gd.on('plotly_hover', reapplyStyles)
  gd.on('plotly_unhover', reapplyStyles)
  gd.on('plotly_restyle', reapplyStyles)
}

let activeReapply = false

function setupMutationObserver() {
  if (!plotlyChart.value) return

  if (mutationObserver) {
    mutationObserver.disconnect()
  }
  if (rafId !== null) {
    cancelAnimationFrame(rafId)
    rafId = null
  }

  const svg = plotlyChart.value.querySelector('svg')
  if (!svg) return
  const layer = svg.querySelector<SVGGElement>('g.parcatslayer')
  if (!layer) return

  mutationObserver = new MutationObserver(() => {
    if (activeReapply) return
    if (rafId !== null) return
    rafId = requestAnimationFrame(() => {
      rafId = null
      if (mutationObserver) {
        mutationObserver.disconnect()
        activeReapply = true
      }
      applyBlockStyles()
      activeReapply = false
      if (mutationObserver && plotlyChart.value) {
        const layer = plotlyChart.value.querySelector('svg g.parcatslayer')
        if (layer) {
          mutationObserver.observe(layer, mutationObserverConfig)
        }
      }
    })
  })
  mutationObserver.observe(layer, mutationObserverConfig)
}

onMounted(async () => {
  await createChart()
})

watch(binnedProperties, async (newVal) => {
  if (plotlyChart.value && newVal) {
    await createChart()
  }
}, { deep: true, immediate: true })

</script>

<style scoped>
:deep(.hovertext path) {
  fill: white !important;
  stroke: #5470c6 !important;
}

:deep(.hovertext text.nums),
:deep(.hovertext text.name) {
  font-family: Roboto, -apple-system, Helvetica Neue, Helvetica, Arial, sans-serif !important;
  font-size: 12px !important;
  fill: #666 !important;
}

:deep(path.path) {
  stroke: none !important;
}
</style>
