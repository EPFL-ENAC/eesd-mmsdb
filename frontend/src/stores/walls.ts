import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'src/boot/api';

export const useWallsStore = defineStore('walls', () => {
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Get wall data as ArrayBuffer
   * @param downscaled - Whether to get downscaled version
   * @param type - Type of wall: 'real' or 'virtual'
   * @param id - Wall identifier of the form "OC01"
   * @returns Promise that resolves to ArrayBuffer or null if error
   */
  async function getWall(downscaled: boolean, type: 'real' | 'virtual', id: string): Promise<ArrayBuffer | null> {
    loading.value = true;
    error.value = null;

    // TODO: find automatically
    // const reference_directory = "01_OC";
    // const id_directory = "01_OC01";

    try {
      // const filePath = `${downscaled?"downscaled":"original"}/01_Microstructures_data/${type === 'real' ? '01_Real' : '02_Virtual'}_walls/${reference_directory}/${id_directory}/02_Wall_data/${id}.ply`;
      const filePath = "downscaled/01_Microstructures_data/01_Real_walls/01_OC/01_OC01/01_Stones_data/OC01_stone_0.ply";
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
