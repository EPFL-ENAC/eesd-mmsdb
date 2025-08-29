import { defineStore } from 'pinia'
import { computed, ref, readonly } from 'vue'
import { usePropertiesStore } from './properties'
import type { PropertyEntry } from '../models'

const STRING_COLUMNS = [
  'Microstructure type',
  'Typology based on Italian Code',
  'Vertical loading_GMQI_class'
] as const

const NUMERIC_COLUMNS = [
  'No of leaves',
  'Average vertical LMT',
  'Average horizontal LMT',
  'Average shape factor'
] as const

const FLOAT_DECIMALS = 2

type StringColumnName = typeof STRING_COLUMNS[number]
type NumericColumnName = typeof NUMERIC_COLUMNS[number]

interface NumericFilter {
  min: number
  max: number
}

interface StringFilter {
  values: string[]
}

type DatabaseFilters = {
  [K in StringColumnName]: StringFilter
} & {
  [K in NumericColumnName]: NumericFilter
}

export const useDatabaseFiltersStore = defineStore('databaseFilters', () => {
  const createInitialFilters = (): DatabaseFilters => {
    const filters: Partial<DatabaseFilters> = {}

    STRING_COLUMNS.forEach(column => {
      filters[column] = { values: [] }
    })

    NUMERIC_COLUMNS.forEach(column => {
      filters[column] = { min: 0, max: 100 }
    })

    return filters as DatabaseFilters
  }

  const filters = ref<DatabaseFilters>(createInitialFilters())
  const propertiesStore = usePropertiesStore()

  function roundRange(range: NumericFilter): NumericFilter {
    return {
      min: Math.floor(range.min * Math.pow(10, FLOAT_DECIMALS)) / Math.pow(10, FLOAT_DECIMALS),
      max: Math.ceil(range.max * Math.pow(10, FLOAT_DECIMALS)) / Math.pow(10, FLOAT_DECIMALS)
    }
  }

  function getNumericRange(propertyName: string): NumericFilter {
    if (!Array.isArray(propertiesStore.properties)) return { min: 0, max: 100 }

    const values = propertiesStore.properties
      .flatMap(entry => {
        const property = entry.properties.find(p => p.name === propertyName)
        return property?.value ? [parseFloat(property.value)] : []
      })
      .filter(value => !isNaN(value))

    if (values.length === 0) return { min: 0, max: 100 }

    return roundRange({
      min: Math.min(...values),
      max: Math.max(...values)
    })
  }

  function getStringOptions(propertyName: string): string[] {
    if (!Array.isArray(propertiesStore.properties)) return []

    const values = propertiesStore.properties
      .flatMap(entry => {
        const property = entry.properties.find(p => p.name === propertyName)
        return property?.value ? [property.value] : []
      })
      .filter(Boolean)

    return [...new Set(values)].sort((a, b) => a.localeCompare(b))
  }

  function getStringColumnOptions(columnName: StringColumnName): string[] {
    return getStringOptions(columnName)
  }

  function getNumericColumnRange(columnName: NumericColumnName): NumericFilter {
    const range = getNumericRange(columnName)

    if (columnName === 'No of leaves') {
      return {
        min: Math.floor(range.min),
        max: Math.ceil(range.max)
      }
    }

    return range
  }



  function matchesStringFilter(propertyName: string, filter: StringFilter, props: PropertyEntry['properties']): boolean {
    if (filter.values.length === 0) return true

    const propertyValue = props.find(p => p.name === propertyName)?.value
    return propertyValue ? filter.values.includes(propertyValue) : false
  }

  function matchesNumericFilter(propertyName: string, filter: NumericFilter, props: PropertyEntry['properties']): boolean {
    const propertyValue = props.find(p => p.name === propertyName)?.value
    if (!propertyValue) return true

    const numericValue = parseFloat(propertyValue)
    if (isNaN(numericValue)) return true

    return numericValue >= filter.min && numericValue <= filter.max
  }

  function matchesFilters(propertyEntry: PropertyEntry): boolean {
    const props = propertyEntry.properties

    for (const columnName of STRING_COLUMNS) {
      if (!matchesStringFilter(columnName, filters.value[columnName], props)) {
        return false
      }
    }

    for (const columnName of NUMERIC_COLUMNS) {
      if (!matchesNumericFilter(columnName, filters.value[columnName], props)) {
        return false
      }
    }

    return true
  }

  const filteredWallIds = computed(() => {
    if (!Array.isArray(propertiesStore.properties)) return []

    const filteredEntries = (propertiesStore.properties as PropertyEntry[])
      .filter(matchesFilters)

    const wallIds = filteredEntries
      .map(propertyEntry => {
        const wallIdProperty = propertyEntry.properties.find(p => p.name === 'Wall ID')
        return wallIdProperty?.value
      })
      .filter(Boolean)

    return [...new Set(wallIds)] as string[]
  })

  const allWallIds = computed(() => {
    if (!Array.isArray(propertiesStore.properties)) return []

    const wallIds = (propertiesStore.properties as PropertyEntry[])
      .map(propertyEntry => {
        const wallIdProperty = propertyEntry.properties.find(p => p.name === 'Wall ID')
        return wallIdProperty?.value
      })
      .filter(Boolean)

    return [...new Set(wallIds)] as string[]
  })

  function initializeFilters() {
    if (propertiesStore.properties) {
      NUMERIC_COLUMNS.forEach(columnName => {
        const range = getNumericColumnRange(columnName)
        filters.value[columnName] = { min: range.min, max: range.max }
      })
    }
  }

  function clearFilters() {
    STRING_COLUMNS.forEach(columnName => {
      filters.value[columnName].values = []
    })

    NUMERIC_COLUMNS.forEach(columnName => {
      const range = getNumericColumnRange(columnName)
      filters.value[columnName] = { min: range.min, max: range.max }
    })
  }

  function updateStringFilter(columnName: StringColumnName, values: string[]) {
    filters.value[columnName].values = values
  }

  function updateNumericFilter(columnName: NumericColumnName, range: NumericFilter) {
    filters.value[columnName] = range
  }

  return {
    STRING_COLUMNS,
    NUMERIC_COLUMNS,

    filters: readonly(filters),
    filteredWallIds,
    allWallIds,

    getStringColumnOptions,
    getNumericColumnRange,
    updateStringFilter,
    updateNumericFilter,

    initializeFilters,
    clearFilters,

    matchesFilters
  }
})
