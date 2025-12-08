import { defineStore } from 'pinia';
import { api } from 'src/boot/api';
import type { LineComputeParams, LineComputeResult } from 'src/models';
import { ErrorBase, KeyedAsyncCache, Result } from 'unwrapped/core';

export const useLineStore = defineStore('line', () => {
  const linesCache = new KeyedAsyncCache<LineComputeParams, LineComputeResult>(async (params: LineComputeParams) => {
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

    return Result.tryFunction(
      async () => {
        const result = await api.post(`/compute/line?${queryParams}`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        return result.data as LineComputeResult;
      },
      (error) => new ErrorBase('minimum_trace_error', `Failed to compute line of minimum trace`, error)
    );
  });

  const loading = ref(false);
  const error = ref<string | null>(null);
  const result = ref<LineComputeResult | null>(null);


  function getLine(params: LineComputeParams) {
    return linesCache.get(params);
  }

  return {
    getLine,
    loading,
    error,
    result,
  };
});
