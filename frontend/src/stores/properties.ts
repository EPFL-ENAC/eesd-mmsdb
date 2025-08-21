import { defineStore } from 'pinia';
import axios from 'axios';
import type { PropertyEntry } from '../models';

export const usePropertiesStore = defineStore('properties', () => {
  const properties = ref<PropertyEntry[] | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchProperties = async () => {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.get('/properties');
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
