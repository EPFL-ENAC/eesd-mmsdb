import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'src/boot/api';

export const useWallsStore = defineStore('walls', () => {
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Get wall data as ArrayBuffer
   * @param downscaled - Whether to get downscaled version
   * @param id - Wall identifier of the form "OC01"
   * @returns Promise that resolves to ArrayBuffer or null if error
   */
  async function getWall(downscaled: boolean, id: string): Promise<ArrayBuffer | null> {
    loading.value = true;
    error.value = null;

    try {
      const wallPath = (await api.get(`/files/wall-path/${id}`)).data;
      const filePath = `${downscaled?"downscaled":"original"}/01_Microstructures_data/${wallPath}/02_Wall_data/${id}.ply`;
      console.log(`Fetching wall data from: ${filePath}`);
      const response = await api.get(`/files/get/${filePath}`, {
        params: {
          d: false
        },
        responseType: 'arraybuffer'
      });

      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An unknown error occurred';
      return null;
    } finally {
      loading.value = false;
    }
  };

  return {
    loading,
    error,
    getWall,
  };
});
