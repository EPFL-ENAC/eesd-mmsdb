import { defineStore } from 'pinia';
import type { ColumnInfo, Table } from '../models';
import { api } from 'src/boot/api';
import columnsJson from 'src/assets/properties_columns_info.json';
import { StaticTable } from 'src/utils/table';
import { useAsyncResultRefFromPromise } from 'unwrapped/vue';
import { ColumnInfoManager } from 'src/utils/columnInfoManager';
import { AsyncResult, ErrorBase, Result } from 'unwrapped/core';

export const usePropertiesStore = defineStore('properties', () => {
  const columns = new ColumnInfoManager(columnsJson as ColumnInfo[]);

  const propertiesResult = useAsyncResultRefFromPromise(
    Result.tryFunction(
      async () => {
        const response = await api.get('/properties/');
        return new StaticTable(response.data as Table);
      },
      (error) => new ErrorBase('fetch_error', 'Failed to fetch properties', error)
    )
  );

  const getBinnedProperties = (): AsyncResult<StaticTable> => {
    return propertiesResult.value.chain((table) => {
      const binnedColumns = table.columns.map(col => {
        if (!columns.getColumnBins(col.name)) {
          return col;
        }

        return {
          ...col,
          values: col.values.map(value => {
            const binName = columns.getColumnBins(col.name)?.find(bin => {
              const floatValue = parseFloat(value);
              return floatValue >= bin.min && floatValue < bin.max;
            })?.name || value;

            return binName;
          })
        }
      });

      return Result.ok(new StaticTable(binnedColumns));
    });
  }

  const getColumnValuesOrUndefined = (key: string): string[] | undefined => {
    const table = propertiesResult.value.unwrapOrNull();
    if (!table) return undefined;

    return table.getColumnValues(key);
  }

  const getColumnValues = (key: string) => {
    return propertiesResult.value.chain((table) => {
      const r = table.getColumnValues(key);
      if (r === undefined) return Result.err(new ErrorBase("missing_column", `Column ${key} does not exist`));
      return Result.ok(r);
    });
  }

  function _getWallProperty(table: StaticTable, wallID: string, propertyKey: string): Result<string> {
    const wallIndex = table.rowIndexInColumn("Wall ID", wallID);
    if (wallIndex === undefined || wallIndex === -1) {
      return Result.err(new ErrorBase("missing_wall", `Wall ID ${wallID} does not exist`));
    }

    const column = table.getColumnValues(propertyKey);
    if (!column) {
      return Result.err(new ErrorBase("missing_column", `Column ${propertyKey} does not exist`));
    }

    const value = column[wallIndex];
    if (value === undefined) {
      return Result.err(new ErrorBase("missing_value", `Value for Wall ID ${wallID} in column ${propertyKey} is missing`));
    }

    return Result.ok(value);
  }

  const getWallProperty = (wallID: string, propertyKey: string): AsyncResult<string> => {
    return propertiesResult.value.chain((table) => _getWallProperty(table, wallID, propertyKey));
  }

  const getWallPropertyOrNull = (wallID: string, propertyKey: string): string | null => {
    console.log(wallID)
    const table = propertiesResult.value.unwrapOrNull();
    console.log("table", table);
    if (!table) {
      return null;
    }
    return _getWallProperty(table, wallID, propertyKey).unwrapOrNull();
  }

  const getWallMaxSize = (wallID: string) => {
    const individualLengths = [
      getWallProperty(wallID, "Length [cm]"),
      getWallProperty(wallID, "Height [cm]"),
      getWallProperty(wallID, "Width [cm]")
    ];
    return AsyncResult.ensureAvailable(individualLengths).chain(([lengthStr, heightStr, widthStr]) => {
      return Result.ok(Math.max(parseFloat(lengthStr ?? "0"), parseFloat(heightStr ?? "0"), parseFloat(widthStr ?? "0")));
    });
  }

  const getWallMaxSizeOrNull = (wallID: string): number | null => {
    const table = propertiesResult.value.unwrapOrNull();
    if (!table) {
      return null;
    }

    const wallLength = parseFloat(_getWallProperty(table, wallID, "Length [cm]").unwrapOrNull() || "0");
    const wallHeight = parseFloat(_getWallProperty(table, wallID, "Height [cm]").unwrapOrNull() || "0");
    const wallWidth = parseFloat(_getWallProperty(table, wallID, "Width [cm]").unwrapOrNull() || "0");
    return Math.max(wallLength, wallHeight, wallWidth);
  }

  return {
    get properties() {
      return propertiesResult;
    },
    getColumnLabel: columns.getColumnLabel,
    getColumnType: columns.getColumnType,
    getColumnUnit: columns.getColumnUnit,
    getColumnPrecision: columns.getColumnPrecision,
    getColumnBins: columns.getColumnBins,
    getColumnKeyFromLabel: columns.getColumnKeyFromLabel,
    getColumnValuesOrUndefined,
    getColumnValues,
    getBinnedProperties,
    getWallProperty,
    getWallPropertyOrNull,
    getWallMaxSize,
    getWallMaxSizeOrNull
  };
});
