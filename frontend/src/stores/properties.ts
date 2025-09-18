import { defineStore } from 'pinia';
import type { ColumnInfo, Table } from '../models';
import { api } from 'src/boot/api';
import columnsJson from 'src/assets/properties_columns_info.json';
const columns = columnsJson as ColumnInfo[];

export const usePropertiesStore = defineStore('properties', () => {
  const properties = ref<Table | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchProperties = async () => {
    loading.value = true;
    error.value = null;

    try {
      const response = await api.get('/properties/');
      properties.value = response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An unknown error occurred';
    } finally {
      loading.value = false;
    }
  };

  const columnsDict = Object.fromEntries(
    columns.map(entry => [entry.key, entry])
  );

  const getColumnLabel = (key: string): string => {
    return columnsDict[key]?.label || key;
  };

  const getColumnType = (key: string): string => {
    return columnsDict[key]?.type || 'string';
  };

  const getColumnUnit = (key: string): string | undefined => {
    return columnsDict[key]?.unit || undefined;
  };

  const getColumnPrecision = (key: string): number | undefined => {
    return columnsDict[key]?.precision;
  };

  const getColumnBins = (key: string): ColumnInfo['bins'] | undefined => {
    return columnsDict[key]?.bins;
  }

  const getColumnValues = (key: string): string[] | undefined => {
    return properties.value?.find(col => col.name === key)?.values;
  }

  const getBinnedProperties = (): Table | null => {
    return properties.value?.map(col => {
      if (!getColumnBins(col.name)) {
        return col;
      }

      return {
        ...col,
        values: col.values.map(value => {
          const binName = getColumnBins(col.name)?.find(bin => {
            const floatValue = parseFloat(value);
            return floatValue >= bin.min && floatValue < bin.max;
          })?.name || value;

          return binName;
        })
      }
    }) || null;
  }

  return {
    properties,
    loading,
    error,
    fetchProperties,
    columnsDict,
    getColumnLabel,
    getColumnType,
    getColumnUnit,
    getColumnPrecision,
    getColumnBins,
    getColumnValues,
    getBinnedProperties,
  };
});
