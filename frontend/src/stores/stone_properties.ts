import { defineStore } from 'pinia';
import type { ColumnInfo, Table } from '../models';
import { api } from 'src/boot/api';
import columnsJson from 'src/assets/stone_properties_columns_info.json';

const columns = columnsJson as ColumnInfo[];

const columnsDict = Object.fromEntries(
  columns.map(entry => [entry.key, entry])
);

export const useStonePropertiesStore = defineStore('stone_properties', () => {
  const properties = ref<Record<string, Table>>({});
  const loading = ref<Record<string, boolean>>({});
  const error = ref<string | null>(null);

  const getProperties = async (wallId: string): Promise<Table | null> => {
    if (properties.value[wallId]) {
      return properties.value[wallId];
    }

    loading.value[wallId] = true;
    error.value = null;

    try {
      const response = await api.get(`/properties/stones/${wallId}`);
      properties.value[wallId] = response.data;
      return properties.value[wallId] || null;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error fetching stone properties';
      return null;
    } finally {
      loading.value[wallId] = false;
    }
  }

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

  const getColumnBins = (key: string): ColumnInfo['bins'] => {
    if (columnsDict[key]?.bins) {
      return columnsDict[key].bins;
    }

    return [...Array(5).keys()].map((_, i) => ({
      name: ((i + 0.5) * 0.2).toFixed(1),
      fullName: `${(i * 0.2).toFixed(1)}-${((i + 1) * 0.2).toFixed(1)}`,
      min: i * 0.2,
      max: (i + 1) * 0.2
    }))
  }

  const getColumnValues = (wallId: string, key: string): string[] | undefined => {
    return properties.value[wallId]?.find(col => col.name === key)?.values;
  }

  return {
    loading,
    error,
    getProperties,
    getColumnLabel,
    getColumnType,
    getColumnUnit,
    getColumnPrecision,
    getColumnBins,
    getColumnValues
  };
});
