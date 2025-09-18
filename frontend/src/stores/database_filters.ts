import { defineStore } from 'pinia'
import { usePropertiesStore } from './properties'

const columnFilters = ["Microstructure type", "Typology based on Italian Code", "No of leaves", "Vertical loading_GMQI_class", "In-plane_GMQI_class", "Out-of-plane_GMQI_class", "Length [cm]", "Height [cm]", "Width [cm]"]

const propertiesStore = usePropertiesStore()

interface NumericFilter {
  min: number
  max: number
}


type StringFilters = {
  [K: string]: string[]
}

type NumericFilters = {
  [K: string]: NumericFilter
}

export const useDatabaseFiltersStore = defineStore('databaseFilters', () => {
  const createInitialStringFilters = (): StringFilters => {
    const filters: StringFilters = {}

    columnFilters.forEach(column => {
      const type = propertiesStore.getColumnType(column)
      if (type === 'string') {
        filters[column] = []
      }
    })

    return filters
  }

  const createInitialNumericFilters = (): NumericFilters => {
    const filters: NumericFilters = {}

    columnFilters.forEach(column => {
      const type = propertiesStore.getColumnType(column)
      if (type !== 'string') {
        filters[column] = { min: 0, max: 100 }
      }
    })

    return filters
  }

  const stringFilters = ref<StringFilters>(createInitialStringFilters())
  const numericFilters = ref<NumericFilters>(createInitialNumericFilters())

  function roundRange(range: NumericFilter, precision: number): NumericFilter {
    return {
      min: Math.floor(range.min * Math.pow(10, precision)) / Math.pow(10, precision),
      max: Math.ceil(range.max * Math.pow(10, precision)) / Math.pow(10, precision)
    }
  }

  function getNumericRange(columnName: string): NumericFilter {
    if (!Array.isArray(propertiesStore.properties)) return { min: 0, max: 100 }

    const values = propertiesStore.getColumnValues(columnName)
      ?.map(value => parseFloat(value))
      .filter(value => !isNaN(value))
      || []

    if (values.length === 0) return { min: 0, max: 100 }

    let range = {
      min: Math.min(...values),
      max: Math.max(...values)
    }

    const precision = propertiesStore.getColumnPrecision(columnName)
    if (precision !== undefined) {
      const precision = propertiesStore.getColumnPrecision(columnName) || 0
      range = roundRange(range, precision)
    }

    return range
  }

  function getStringOptions(columnName: string): string[] {
    if (!Array.isArray(propertiesStore.properties)) return []
    const values = propertiesStore.getColumnValues(columnName)?.filter(Boolean)
    return [...new Set(values)].sort((a, b) => a.localeCompare(b))
  }

  function getStringColumnOptions(columnName: string): string[] {
    return getStringOptions(columnName)
  }

  function getNumericColumnRange(columnName: string): NumericFilter {
    const range = getNumericRange(columnName)
    return range
  }

  function matchesStringFilter(filter: string[], value: string): boolean {
    if (filter.length === 0) return true
    return value ? filter.includes(value) : false
  }

  function matchesNumericFilter(filter: NumericFilter, value: string): boolean {
    const numericValue = parseFloat(value)
    if (isNaN(numericValue)) return false
    return numericValue >= filter.min && numericValue <= filter.max
  }

  const filteredWallIds = computed(() => {
    if (!Array.isArray(propertiesStore.properties)) return []

    const matchingIndicesSet = new Set<number>([...Array(propertiesStore.properties[0]?.values.length).keys()])
    Object.entries(stringFilters.value).forEach(([columnName, filterValues]) => {
      const values = propertiesStore.getColumnValues(columnName) || []
      values.forEach((value, index) => {
        if (!matchesStringFilter(filterValues, value)) {
          matchingIndicesSet.delete(index)
        }
      })
    })
    Object.entries(numericFilters.value).forEach(([columnName, filterRange]) => {
      const values = propertiesStore.getColumnValues(columnName) || []
      values.forEach((value, index) => {
        if (!matchesNumericFilter(filterRange, value)) {
          matchingIndicesSet.delete(index)
        }
      })
    })
    const matchingIndices = Array.from(matchingIndicesSet).sort((a, b) => a - b)
    const wallIds = matchingIndices.map(index => propertiesStore.getColumnValues('Wall ID')?.[index])
    return wallIds as string[]
  })

  const allWallIds = computed(() => {
    if (!Array.isArray(propertiesStore.properties)) return []
    return propertiesStore.getColumnValues('Wall ID') || []
  })

  function initializeFilters() {
    if (propertiesStore.properties) {
      columnFilters.forEach(columnName => {
        const type = propertiesStore.getColumnType(columnName)
        if (type === 'string') {
          stringFilters.value[columnName] = []
        } else {
          const range = getNumericColumnRange(columnName)
          numericFilters.value[columnName] = { min: range.min, max: range.max }
        }
      })
    }
  }

  function clearFilters() {
    columnFilters.forEach(columnName => {
      const type = propertiesStore.getColumnType(columnName)
      if (type === 'string') {
        if (stringFilters.value[columnName]) {
          stringFilters.value[columnName] = []
        }
      } else {
        const range = getNumericColumnRange(columnName)
        numericFilters.value[columnName] = { min: range.min, max: range.max }
      }
    })
  }

  function updateStringFilter(columnName: string, values: string[]) {
      stringFilters.value[columnName] = values
  }

  function updateNumericFilter(columnName: string, range: NumericFilter) {
    numericFilters.value[columnName] = range
  }

  return {
    columnFilters,

    stringFilters: readonly(stringFilters),
    numericFilters: readonly(numericFilters),
    filteredWallIds,
    allWallIds,

    getStringColumnOptions,
    getNumericColumnRange,
    updateStringFilter,
    updateNumericFilter,

    initializeFilters,
    clearFilters,
  }
})
