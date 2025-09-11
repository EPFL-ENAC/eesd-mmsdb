import { defineStore } from 'pinia';
import type { Property } from '../models';
import { api } from 'src/boot/api';
import columns from 'src/assets/stone_properties_columns.json';

const columnsDict = Object.fromEntries(
  columns.map(entry => [entry.key, entry])
);

export const useStonePropertiesStore = defineStore('stone_properties', () => {
  const properties = ref<Record<string, Property[][][]>>({});
  const loading = ref<Record<string, boolean>>({});
  const error = ref<string | null>(null);

  const getProperties = async (wallId: string): Promise<Property[][][] | null> => {
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

  return {
    loading,
    error,
    getProperties,
    getColumnLabel,
    getColumnType,
    getColumnUnit,
    getColumnPrecision,
  };
});
