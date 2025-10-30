import type { ColumnInfo } from "src/models";

export class ColumnInfoManager {
  private columnInfos: ColumnInfo[];
  private columnsDict: Record<string, ColumnInfo>;

  constructor(columnInfos: ColumnInfo[]) {
    this.columnInfos = columnInfos;
    this.columnsDict = Object.fromEntries(columnInfos.map(info => [info.key, info]));
  }

  getColumnLabel = (key: string): string => {
    return this.columnsDict[key]?.label || key;
  }

  getColumnKeyFromLabel = (label: string): string | null => {
    const column = this.columnInfos.find(col => col.label === label);
    return column ? column.key : null;
  }

  getColumnType = (key: string): string => {
    return this.columnsDict[key]?.type || 'string';
  }

  getColumnUnit = (key: string): string | undefined => {
    return this.columnsDict[key]?.unit || undefined;
  }

  getColumnPrecision = (key: string): number | undefined => {
    return this.columnsDict[key]?.precision;
  }

  getColumnBins = (key: string): ColumnInfo['bins'] => {
    if (this.columnsDict[key]?.bins) {
      return this.columnsDict[key].bins;
    }

    return [...Array(5).keys()].map((_, i) => ({
      name: ((i + 0.5) * 0.2).toFixed(1),
      fullName: `${(i * 0.2).toFixed(1)}-${((i + 1) * 0.2).toFixed(1)}`,
      min: i * 0.2,
      max: (i + 1) * 0.2
    }))
  }
}