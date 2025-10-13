import type { usePropertiesStore } from 'stores/properties'
import type { useStonePropertiesStore } from 'stores/stone_properties'
import type { Column } from '../models';


type Store = ReturnType<typeof usePropertiesStore> | ReturnType<typeof useStonePropertiesStore>
export const dimensionsColumns = ["Length [cm]", "Height [cm]", "Width [cm]"]
export const dimensionsColumnsStones = ["Stone length [m]", "stone height [m]", "Stone width [m]"]


export const toDisplayedProperties = (propertiesStore: Store, index: number) => (col: Column) => {
  const precision = propertiesStore.getColumnPrecision(col.name)
  let value = col.values[index] as string

  if (precision !== undefined) {
    const numberValue = Math.floor(parseFloat(value) * Math.pow(10, precision)) / Math.pow(10, precision)
    value = numberValue.toString()
  }

  return {
    name: propertiesStore.getColumnLabel(col.name) || col.name,
    value: value,
    unit: propertiesStore.getColumnUnit(col.name) || '',
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
