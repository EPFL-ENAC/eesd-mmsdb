import { defineStore } from 'pinia';
import { api } from 'src/boot/api';

export type WallDimensions = {
  provided: boolean;
  length: number;
  height: number;
  width: number;
};

export interface SliceData {
  fromWallId?: string | null;

  sliceImageData: ArrayBuffer | null;
  boundaryMargin: number;

  wallDimensions: WallDimensions;
}

export const useSliceStore = defineStore('slice', () => {
  const loading = ref(false);
  const error = ref<string | null>(null);

  const sliceData = ref<SliceData>({
    sliceImageData: null,
    boundaryMargin: 0,
    wallDimensions: {
      provided: false,
      length: 100,
      height: 100,
      width: 100
    }
  });

  const fetchDefaultSliceImage = async () => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.get('/files/get/example_slice.png', {
        responseType: 'arraybuffer'
      });

      sliceData.value = {
        fromWallId: null,
        sliceImageData: response.data,
        boundaryMargin: 0,
        wallDimensions: {
          provided: false,
          length: 100,
          height: 100,
          width: 100
        }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An unknown error occurred';
    } finally {
      loading.value = false;
    }
  };

  return {
    sliceData,
    loading,
    error,
    fetchDefaultSliceImage
  };
});
