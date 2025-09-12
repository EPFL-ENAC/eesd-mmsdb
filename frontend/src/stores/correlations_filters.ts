import { defineStore } from 'pinia'
import { usePropertiesStore } from './properties'

const propertiesStore = usePropertiesStore()
const numericColumns = ref<string[]>([])

watch(() => propertiesStore?.columnsDict,
  (columnsDict) => {
    if (columnsDict) {
      numericColumns.value = Object.values(columnsDict)
        .filter(column => column.type === "int" || column.type === "float")
        .map(column => column.label)
    } else {
      numericColumns.value = []
    }
  },
  { immediate: true }
)

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
