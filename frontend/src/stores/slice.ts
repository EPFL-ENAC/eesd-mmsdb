import { defineStore } from 'pinia';
import { api } from 'src/boot/api';

export const useSliceStore = defineStore('slice', () => {
  const sliceImageData = ref<ArrayBuffer | null>(null);
  const realLength = ref<number>(100);
  const realHeight = ref<number>(100);
  const boundaryMargin = ref<number>(0);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchDefaultSliceImage = async () => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.get('/files/get/example_slice.png', {
        responseType: 'arraybuffer'
      });
      sliceImageData.value = response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An unknown error occurred';
    } finally {
      loading.value = false;
    }
  };

  return {
    sliceImageData,
    realLength,
    realHeight,
    boundaryMargin,
    loading,
    error,
    fetchDefaultSliceImage
  };
});
