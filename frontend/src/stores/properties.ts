import { defineStore } from 'pinia';
import type { PropertyEntry } from '../models';
import { api } from 'src/boot/api';

export const usePropertiesStore = defineStore('properties', () => {
  const properties = ref<PropertyEntry[] | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchProperties = async () => {
    loading.value = true;
    error.value = null;

    try {
      const response = await api.get('/properties');
      properties.value = response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An unknown error occurred';
    } finally {
      loading.value = false;
    }
  };

  return {
    properties,
    loading,
    error,
    fetchProperties,
  };
});
