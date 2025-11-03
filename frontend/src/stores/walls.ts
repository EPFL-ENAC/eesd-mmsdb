import { defineStore } from 'pinia';
import { api } from 'src/boot/api';
import type { WallStonesList } from 'src/models';
import type { AsyncResult } from 'src/reactiveCache/core/asyncResult';
import { KeyedAsyncCache } from 'src/reactiveCache/core/cache';
import { ErrorBase } from 'src/reactiveCache/core/error';
import { Result } from 'src/reactiveCache/core/result';
// import axios from 'axios';


interface PreloadAround {
  before: number;
  after: number;
}

interface WallParams {
  downscaled: boolean;
  id: string;
}

function wallParamsToKey(key: WallParams): string {
  return `${key.downscaled ? 'downscaled' : 'original'}:${key.id}`;
}

export const useWallsStore = defineStore('walls', () => {
  const wallCache = new KeyedAsyncCache<WallParams, ArrayBuffer>(async (params: WallParams) => {
    return Result.tryFunction(
      async () => {
        const wallPath = (await api.get(`/files/wall-path/${params.id}`)).data;
        console.log(`Resolved wall path for ${params.id}: ${wallPath}`);
        const filePath = `${params.downscaled ? "downscaled" : "original"}/01_Microstructures_data/${wallPath}/02_Wall_data/${params.id}.ply`;
        console.log(`Fetching wall data from: ${filePath}`);
        const response = await api.get(`/files/get/${filePath}`, {
          params: {
            d: false
          },
          responseType: 'arraybuffer'
        });
        return response.data;
      },
      (error) => {
        console.error(`Error fetching wall data for ${params.id}:`, error);
        return new ErrorBase('fetch_error', 'Failed to fetch wall data');
      }
    );
  }, wallParamsToKey);

  const wallStonesListCache = new KeyedAsyncCache<string, WallStonesList>(async (id: string) => {
    return Result.tryFunction<WallStonesList, ErrorBase>(
      async () => (await api.get(`/files/wall-path/${id}/stones`)).data as WallStonesList,
      (error) => {
        console.error(`Error fetching wall stones list for ${id}:`, error);
        return new ErrorBase('fetch_error', 'Failed to fetch wall stones list');
      });
  }, id => id);

  const wallStoneCache = new KeyedAsyncCache<WallParams, ArrayBuffer>(async (params: WallParams) => {
    return Result.tryFunction(
      async () => {
        const filePath = `${params.downscaled ? "downscaled" : "original"}/01_Microstructures_data/${params.id}`;
        const response = await api.get(`/files/get/${filePath}`, {
          params: {
            d: false
          },
          responseType: 'arraybuffer'
        });
        return response.data;
      },
      (error) => {
        console.error(`Error fetching wall stone data for ${params.id}:`, error);
        return new ErrorBase('fetch_error', 'Failed to fetch wall stone data');
      }
    );
  }, wallParamsToKey);

  const wallImageCache = new KeyedAsyncCache<string, ArrayBuffer>(async (id: string) => {
    return Result.tryFunction(
      async () => {
        const filePath = `original/02_Rendered_walls_photos/${id}.png`;
        const response = await api.get(`/files/get/${filePath}`, {
          params: {
            d: false
          },
          responseType: 'arraybuffer'
        });
        return response.data;
      },
      (error) => {
        console.error(`Error fetching wall image for ${id}:`, error);
        return new ErrorBase('fetch_error', 'Failed to fetch wall image');
      }
    );
  }, id => id);

  const wallPropertiesCSVCache = new KeyedAsyncCache<string, ArrayBuffer>(async (id: string) => {
    return Result.tryFunction(
      async () => {
        const filePath = `original/03_Stones_geometric_properties/${id}.csv`;
        const response = await api.get(`/files/get/${filePath}`, {
          params: {
            d: false
          },
          responseType: 'arraybuffer'
        });
        return response.data;
      },
      (error) => {
        console.error(`Error fetching wall properties CSV for ${id}:`, error);
        return new ErrorBase('fetch_error', 'Failed to fetch wall properties CSV');
      }
    );
  }, id => id);

  const wallImages = ref<Record<string, string>>({});
  const loadingImages = ref<Record<string, boolean>>({});

  /**
   * Get wall data as ArrayBuffer
   * @param downscaled - Whether to get downscaled version
   * @param id - Wall identifier of the form "OC01"
   * @returns AsyncResult that resolves to ArrayBuffer or WallError
   */
  function getWall(downscaled: boolean, id: string): AsyncResult<ArrayBuffer> {
    return wallCache.get({ downscaled, id });
  };

  /**
   * Get list of stones for a given wall
   * @param id - Wall identifier of the form "OC01"
   * @returns AsyncResult that resolves to WallStonesList or WallError
   */
  function getWallStonesList(id: string): AsyncResult<WallStonesList> {
    return wallStonesListCache.get(id);
  };

  /**
   * Get wall data as ArrayBuffer
   * @param downscaled - Whether to get downscaled version
   * @param id - Wall identifier of the form "OC01"
   * @returns AsyncResult that resolves to ArrayBuffer or WallError
   */
  function getWallStoneModel(downscaled: boolean, path: string): AsyncResult<ArrayBuffer> {
    return wallStoneCache.get({ downscaled, id: path });
  };

  function _getWallStoneModelFromStoneListAndIndex(downscaled: boolean, stonesList: WallStonesList, index: number): AsyncResult<ArrayBuffer> {
    const stonePath = `${stonesList.folder}/${stonesList.files[index] || ""}`;
    return wallStoneCache.get({ downscaled, id: stonePath });
  }

  function getWallStoneModelFromStoneListAndIndex(downscaled: boolean, stonesList: WallStonesList, index: number, preload?: PreloadAround): AsyncResult<ArrayBuffer> {
    if (preload) {
      for (let offset = 1; offset <= preload.after; offset++) {
          const nextIndex = (index + offset) % stonesList.files.length;
          _getWallStoneModelFromStoneListAndIndex(downscaled, stonesList, nextIndex);
      }
      for (let offset = 1; offset <= preload.before; offset++) {
          const prevIndex = (index - offset + stonesList.files.length) % stonesList.files.length;
          _getWallStoneModelFromStoneListAndIndex(downscaled, stonesList, prevIndex);
      }
    }

    return _getWallStoneModelFromStoneListAndIndex(downscaled, stonesList, index);
  }

  function getWallImage(id: string): AsyncResult<ArrayBuffer> {
    return wallImageCache.get(id);
  }

  function getWallPropertiesCSVFile(id: string): AsyncResult<ArrayBuffer> {
    return wallPropertiesCSVCache.get(id);
  }

  async function loadWallImage(wallId: string): Promise<void> {
    if (wallImages.value[wallId] || loadingImages.value[wallId]) return;

    loadingImages.value[wallId] = true;

    try {
      const imageData = await getWallImage(wallId).unwrapOrThrowOnceSettled();
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
    wallImages,
    loadingImages,
    getWall,
    getWallStonesList,
    getWallStoneModel,
    getWallStoneModelFromStoneListAndIndex,
    getWallPropertiesCSVFile,
    getWallImage,
    loadWallImage,
    revokeWallImageUrl,
    revokeAllWallImageUrls,
  };
});
