import { defineStore } from 'pinia'
import { api } from 'src/boot/api';
import type { CorrelationResult } from 'src/models';
import { usePropertiesStore } from 'stores/properties'

const propertiesStore = usePropertiesStore()

const numericColumns = [
  "Volumetric stone ratio",
  "Average shape factor",
  "Average vertical LMT",
  "Average horizontal LMT",
  "Average LMT for wall-leaf connection",
  "Vertical GMQI",
  "In-plane GMQI",
  "Out-of-plane GMQI",
]


export const useCorrelationsFiltersStore = defineStore('correlationsFilters', () => {
  const xColumn = ref<string | null>("Average shape factor")
  const yColumn = ref<string | null>("Average vertical LMT")
  const loading = ref(false)
  const error = ref<string | null>(null)

  const setXColumn = (column: string | null) => xColumn.value = column
  const setYColumn = (column: string | null) => yColumn.value = column

  const getCorrelationParameters = async (allowedCategories: string[] = []): Promise<CorrelationResult | null> => {
    if (!xColumn.value || !yColumn.value) {
      return null;
    }
    loading.value = true;
    const xColumnKey = propertiesStore.getColumnKeyFromLabel(xColumn.value);
    const yColumnKey = propertiesStore.getColumnKeyFromLabel(yColumn.value);

    if (!xColumnKey || !yColumnKey) {
      error.value = 'Invalid column selection';
      loading.value = false;
      return null;
    }

    const queryParams = new URLSearchParams({
      x_column: xColumnKey,
      y_column: yColumnKey,
    });
    allowedCategories.forEach(category => {
      queryParams.append('allowed_categories', category);
    });

    try {
      const response = await api.get<CorrelationResult>(`/compute/correlation?${queryParams}`);
      loading.value = false;
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error fetching correlation parameters';
      loading.value = false;
      return null;
    }
  }

  return {
    loading,
    error,
    numericColumns: readonly(numericColumns),
    xColumn: readonly(xColumn),
    yColumn: readonly(yColumn),
    setXColumn,
    setYColumn,
    getCorrelationParameters,
  }
})
