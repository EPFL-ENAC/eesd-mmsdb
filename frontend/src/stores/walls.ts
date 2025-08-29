import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'src/boot/api';
// import axios from 'axios';

export const useWallsStore = defineStore('walls', () => {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const wallCache = ref<Record<string, ArrayBuffer>>({});
  const wallImageCache = ref<Record<string, ArrayBuffer>>({});
  const wallImages = ref<Record<string, string>>({});
  const loadingImages = ref<Record<string, boolean>>({});

  /**
   * Get wall data as ArrayBuffer
   * @param downscaled - Whether to get downscaled version
   * @param id - Wall identifier of the form "OC01"
   * @returns Promise that resolves to ArrayBuffer or null if error
   */
  async function getWall(downscaled: boolean, id: string): Promise<ArrayBuffer | null> {
    const cacheKey = `${downscaled}:${id}`;
    if (wallCache.value[cacheKey]) {
      return wallCache.value[cacheKey];
    }

    loading.value = true;
    error.value = null;

    // const response = await axios.get(`/downscaled/${id}.ply`, {responseType: 'arraybuffer'});
    // wallCache.value[cacheKey] = response.data;
    // return response.data

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

      wallCache.value[cacheKey] = response.data;
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An unknown error occurred';
      return null;
    } finally {
      loading.value = false;
    }
  };

  async function getWallImage(id: string): Promise<ArrayBuffer | null> {
    const cacheKey = id;
    if (wallImageCache.value[cacheKey]) {
      return wallImageCache.value[cacheKey];
    }

    const filePath = `original/02_Rendered_walls_photos/${id}.png`;
    loading.value = true;
    error.value = null;

    try {
      const response = await api.get(`/files/get/${filePath}`, {
        params: {
          d: false
        },
        responseType: 'arraybuffer'
      });
      wallImageCache.value[cacheKey] = response.data;
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An unknown error occurred';
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function loadWallImage(wallId: string): Promise<void> {
    if (wallImages.value[wallId] || loadingImages.value[wallId]) return;

    loadingImages.value[wallId] = true;

    try {
      const imageData = await getWallImage(wallId);
      if (imageData) {
        const blob = new Blob([imageData], { type: 'image/png' });
        wallImages.value[wallId] = URL.createObjectURL(blob);
      }
    } catch (error) {
      console.error(`Failed to load wall image for ${wallId}:`, error);
    } finally {
      loadingImages.value[wallId] = false;
    }
  }

  function revokeWallImageUrl(wallId: string): void {
    if (wallImages.value[wallId]) {
      URL.revokeObjectURL(wallImages.value[wallId]);
      delete wallImages.value[wallId];
    }
  }

  function revokeAllWallImageUrls(): void {
    Object.values(wallImages.value).forEach(url => {
      if (url) URL.revokeObjectURL(url);
    });
    wallImages.value = {};
  }

  return {
    loading,
    error,
    wallImages,
    loadingImages,
    getWall,
    getWallImage,
    loadWallImage,
    revokeWallImageUrl,
    revokeAllWallImageUrls,
  };
});
