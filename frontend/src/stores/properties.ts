import { defineStore } from 'pinia';
import type { ColumnInfo, Table } from '../models';
import { api } from 'src/boot/api';
import columnsJson from 'src/assets/properties_columns_info.json';
const columns = columnsJson as ColumnInfo[];

export const usePropertiesStore = defineStore('properties', () => {
  const properties = ref<Table | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchProperties = async () => {
    loading.value = true;
    error.value = null;

    try {
      const response = await api.get('/properties/');
      properties.value = response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An unknown error occurred';
    } finally {
      loading.value = false;
    }
  };

  const columnsDict = Object.fromEntries(
    columns.map(entry => [entry.key, entry])
  );

  const getColumnLabel = (key: string): string => {
    return columnsDict[key]?.label || key;
  };

  const getColumnType = (key: string): string => {
    return columnsDict[key]?.type || 'string';
  };

  const getColumnUnit = (key: string): string | undefined => {
    return columnsDict[key]?.unit || undefined;
  };

  const getColumnPrecision = (key: string): number | undefined => {
    return columnsDict[key]?.precision;
  };

  const getColumnBins = (key: string): ColumnInfo['bins'] | undefined => {
    return columnsDict[key]?.bins;
  }

  const getColumnKeyFromLabel = (label: string): string | null => {
    const column = columns.find(col => col.label === label);
    return column ? column.key : null;
  }

  const getColumnValues = (key: string): string[] | undefined => {
    return properties.value?.find(col => col.name === key)?.values;
  }

  const getBinnedProperties = (): Table | null => {
    return properties.value?.map(col => {
      if (!getColumnBins(col.name)) {
        return col;
      }

      return {
        ...col,
        values: col.values.map(value => {
          const binName = getColumnBins(col.name)?.find(bin => {
            const floatValue = parseFloat(value);
            return floatValue >= bin.min && floatValue < bin.max;
          })?.name || value;

          return binName;
        })
      }
    }) || null;
  }

  const getWallProperty = (wallID: string, propertyKey: string): string | null => {
    if (!properties.value) {
      return null;
    }
    const wallIndex = getColumnValues("Wall ID")?.findIndex(id => id === wallID);
    if (wallIndex === undefined || wallIndex === -1) {
      return null;
    }

    const column = getColumnValues(propertyKey);
    if (!column) {
      return null;
    }

    return column[wallIndex] || null;
  }

  const getWallMaxSize = (wallID: string): number | null => {
    const wallLength = parseFloat(getWallProperty(wallID, "Length [cm]") || "0");
    const wallHeight = parseFloat(getWallProperty(wallID, "Height [cm]") || "0");
    const wallWidth = parseFloat(getWallProperty(wallID, "Width [cm]") || "0");
    return Math.max(wallLength, wallHeight, wallWidth);
  }

  return {
    properties,
    loading,
    error,
    fetchProperties,
    columnsDict,
    getColumnLabel,
    getColumnType,
    getColumnUnit,
    getColumnPrecision,
    getColumnBins,
    getColumnKeyFromLabel,
    getColumnValues,
    getBinnedProperties,
    getWallProperty,
    getWallMaxSize
  };
});
