import { defineStore } from 'pinia';
import type { ColumnInfo } from '../models';
import { api } from 'src/boot/api';
import columnsJson from 'src/assets/stone_properties_columns_info.json';
import { StaticTable } from 'src/utils/table';
import { ColumnInfoManager } from 'src/utils/columnInfoManager';
import { ErrorBase, KeyedAsyncCache, Result } from 'unwrapped/core';

export const useStonePropertiesStore = defineStore('stone_properties', () => {
  const columns = new ColumnInfoManager(columnsJson as ColumnInfo[]);

  const stoneProperties = new KeyedAsyncCache<string, StaticTable>(async (wallId: string) => {
    return Result.tryFunction(
      async () => {
        const response = await api.get(`/properties/stones/${wallId}`);
        return new StaticTable(response.data);
      },
      (error) => new ErrorBase('fetch_error', `Failed to fetch stone properties of wall ${wallId}`, error)
    );
  });

  function getProperties(wallId: string) {
    return stoneProperties.get(wallId);
  }

  const getColumnValuesOrUndefined = (wallId: string, key: string): string[] | undefined => {
    const table = stoneProperties.get(wallId).unwrapOrNull();
    if (!table) return undefined;

    return table.getColumnValues(key);
  }

  const getColumnValues = (wallId: string, key: string) => {
    return stoneProperties.get(wallId).chain((table) => {
      const r = table.getColumnValues(key);
      if (r === undefined) return Result.err(new ErrorBase("missing_column", `Column ${key} does not exist`));
      return Result.ok(r);
    });
  }

  return {
    getProperties,
    getColumnLabel: columns.getColumnLabel,
    getColumnType: columns.getColumnType,
    getColumnUnit: columns.getColumnUnit,
    getColumnPrecision: columns.getColumnPrecision,
    getColumnBins: columns.getColumnBins,
    getColumnValuesOrUndefined,
    getColumnValues
  };
});
