import type { usePropertiesStore } from 'stores/properties'
import type { useStonePropertiesStore } from 'stores/stone_properties'
import type { Column } from '../models';


type Store = ReturnType<typeof usePropertiesStore> | ReturnType<typeof useStonePropertiesStore>
export const dimensionsColumns = ["Length [cm]", "Height [cm]", "Width [cm]"]
export const dimensionsColumnsStones = ["Stone length [m]", "stone height [m]", "Stone width [m]"]


export const toDisplayedProperties = (propertiesStore: Store, index: number) => (col: Column) => {
  const precision = propertiesStore.getColumnPrecision(col.name)
  let value = col.values[index] as string
  let unit = propertiesStore.getColumnUnit(col.name) || ''
  let floatValue = parseFloat(value)

  // Special cases for numeric values
  if (!isNaN(floatValue)) {
    if (["Stone volume [m^3]", "Bounding box volume [m^3]"].includes(col.name) && unit === 'm³') {
      // convert value to cm³
      floatValue = floatValue * 1e6
      unit = 'cm³'
    }

    if (precision !== undefined) {
      // Use this instead of `.toFixed(precision)` to have 123.4 instead of 123.400
      const numberValue = Math.floor(floatValue * Math.pow(10, precision)) / Math.pow(10, precision)
      value = numberValue.toString()
    }
  }

  return {
    name: propertiesStore.getColumnLabel(col.name) || col.name,
    value: value,
    unit: unit,
  }
}


export const getDimensionsColumn = (
  propertiesStore: Store,
  index: number,
  getColumnValuesFunc: (key: string) => string[] | undefined,
  stones?: boolean
): string =>
  (stones ? dimensionsColumnsStones : dimensionsColumns)
  .map(col => ({ name: col, values: getColumnValuesFunc(col) || [] }))
  .map(toDisplayedProperties(propertiesStore, index))
  .reduce((acc, dimensionsString) => {
    if (acc.length > 0) acc += ' × '
    acc += `${dimensionsString.value} ${dimensionsString.unit}`
    return acc
  }, '');
