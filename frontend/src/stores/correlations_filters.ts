import { defineStore } from 'pinia'

const numericColumns = [
  "Volumetric stone ratio",
  "Shape factor",
  "Vertical LMT",
  "Horizontal LMT",
  "LMT for wall-leaf connection",
  "Vertical MQI",
  "In-plane MQI",
  "Out-of-plane MQI",
]


export const useCorrelationsFiltersStore = defineStore('correlationsFilters', () => {
  const xColumn = ref<string | null>("Shape factor")
  const yColumn = ref<string | null>("Vertical LMT")

  const setXColumn = (column: string | null) => xColumn.value = column
  const setYColumn = (column: string | null) => yColumn.value = column

  return {
    numericColumns: readonly(numericColumns),
    xColumn: readonly(xColumn),
    yColumn: readonly(yColumn),
    setXColumn,
    setYColumn,
  }
})
