import { defineStore } from 'pinia';
import type { Property } from '../models';
import { api } from 'src/boot/api';
import columns from 'src/assets/properties_columns.json';

export const usePropertiesStore = defineStore('properties', () => {
  const properties = ref<Property[][] | null>(null);
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
  };
});
