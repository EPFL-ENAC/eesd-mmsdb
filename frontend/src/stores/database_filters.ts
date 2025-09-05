import { defineStore } from 'pinia'
import { computed, ref, readonly } from 'vue'
import { usePropertiesStore } from './properties'
import type { PropertyEntry } from '../models'

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
      const type = propertiesStore.columnTypes[column]
      if (type === 'string') {
        filters[column] = []
      }
    })

    return filters
  }

  const createInitialNumericFilters = (): NumericFilters => {
    const filters: NumericFilters = {}

    columnFilters.forEach(column => {
      const type = propertiesStore.columnTypes[column]
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

    const values = propertiesStore.properties
      .map(entry => {
        const property = entry.properties.find(p => p.name === columnName)
        return property?.value ? parseFloat(property.value) : NaN
      })
      .filter(value => !isNaN(value))

    if (values.length === 0) return { min: 0, max: 100 }

    let range = {
      min: Math.min(...values),
      max: Math.max(...values)
    }

    const precision = propertiesStore.columnPrecisions[columnName]
    if (precision !== undefined) {
      const precision = propertiesStore.columnPrecisions[columnName] || 0
      range = roundRange(range, precision)
    }

    return range
  }

  function getStringOptions(columnName: string): string[] {
    if (!Array.isArray(propertiesStore.properties)) return []

    const values = propertiesStore.properties
      .flatMap(entry => {
        const property = entry.properties.find(p => p.name === columnName)
        return property?.value ? [property.value] : []
      })
      .filter(Boolean)

    return [...new Set(values)].sort((a, b) => a.localeCompare(b))
  }

  function getStringColumnOptions(columnName: string): string[] {
    return getStringOptions(columnName)
  }

  function getNumericColumnRange(columnName: string): NumericFilter {
    const range = getNumericRange(columnName)
    return range
  }

  function matchesStringFilter(columnName: string, filter: string[], props: PropertyEntry['properties']): boolean {
    if (filter.length === 0) return true

    const propertyValue = props.find(p => p.name === columnName)?.value
    return propertyValue ? filter.includes(propertyValue) : false
  }

  function matchesNumericFilter(columnName: string, filter: NumericFilter, props: PropertyEntry['properties']): boolean {
    const propertyValue = props.find(p => p.name === columnName)?.value
    if (!propertyValue) return true

    const numericValue = parseFloat(propertyValue)
    if (isNaN(numericValue)) return true

    return numericValue >= filter.min && numericValue <= filter.max
  }

  function matchesFilters(propertyEntry: PropertyEntry): boolean {
    const props = propertyEntry.properties

    for (const columnName of columnFilters) {
      const type = propertiesStore.columnTypes[columnName]
      if (type === 'string') {
        if (stringFilters.value[columnName] && !matchesStringFilter(columnName, stringFilters.value[columnName], props)) {
          return false
        }
      } else {
        if (numericFilters.value[columnName] && !matchesNumericFilter(columnName, numericFilters.value[columnName], props)) {
          return false
        }
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
      columnFilters.forEach(columnName => {
        const type = propertiesStore.columnTypes[columnName]
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
      const type = propertiesStore.columnTypes[columnName]
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

    matchesFilters
  }
})
