import { defineStore } from 'pinia';
import type { PropertyEntry } from '../models';
import { api } from 'src/boot/api';
import columns from 'src/assets/properties_columns.json';

const columnsDict = Object.fromEntries(
  columns.map(entry => [entry.key, entry])
);

export const usePropertiesStore = defineStore('properties', () => {
  const properties = ref<PropertyEntry[] | null>(null);
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

  function getColumnLabel(key: string): string {
    return columnsDict[key]?.label || key;
  }

  function getColumnType(key: string): string {
    return columnsDict[key]?.type || 'string';
  }

  function getColumnUnit(key: string): string | undefined {
    return columnsDict[key]?.unit || undefined;
  }

  function getColumnPrecision(key: string): number | undefined {
    return columnsDict[key]?.precision;
  }

  return {
    properties,
    loading,
    error,
    fetchProperties,
    getColumnLabel,
    getColumnType,
    getColumnUnit,
    getColumnPrecision,
  };
});
