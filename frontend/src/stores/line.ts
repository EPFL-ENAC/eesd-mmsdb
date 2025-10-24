import { defineStore } from 'pinia';
import { api } from 'src/boot/api';
import type { LineComputeParams, LineComputeResult } from 'src/models';

export const useLineStore = defineStore('line', () => {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const result = ref<LineComputeResult | null>(null);

  const computeLine = async (params: LineComputeParams): Promise<LineComputeResult | null> => {
    loading.value = true;
    error.value = null;
    result.value = null;

    try {
      const formData = new FormData();
      formData.append('image', params.image);

      const queryParams = new URLSearchParams({
        start_x: params.startX.toString(),
        start_y: params.startY.toString(),
        end_x: params.endX.toString(),
        end_y: params.endY.toString(),
        real_length: params.realLength.toString(),
        real_height: params.realHeight.toString(),
        analysis_type: params.analysisType.toString(),
        interface_weight: params.interfaceWeight.toString(),
        boundary_margin: params.boundaryMargin.toString(),
      });

      const response = await api.post(`/compute/line?${queryParams}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      result.value = response.data;
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error computing line of minimum trace';
      return null;
    } finally {
      loading.value = false;
    }
  };

  const clearResult = () => {
    result.value = null;
    error.value = null;
  };

  const clearError = () => {
    error.value = null;
  };

  return {
    loading,
    error,
    result,
    computeLine,
    clearResult,
    clearError,
  };
});
