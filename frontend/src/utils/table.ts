import type { Column } from "src/models";

export class StaticTable {
  private _columns: Column[];
  private _columnsDict: Record<string, Column>;

  constructor(columns: Column[]) {
    this._columns = columns;
    this._columnsDict = Object.fromEntries(columns.map(col => [col.name, col]));
  }

  get columns(): Column[] {
    return this._columns;
  }

  getColumnNames(): string[] {
    return this._columns.map(col => col.name);
  }

  getColumnValues(columnName: string): string[] | undefined {
    return this._columnsDict[columnName]?.values;
  }

  getRowsCount(): number {
    return this._columns[0]?.values.length ?? 0;
  }

  getCellValue(columnName: string, rowIndex: number): string | undefined {
    const values = this.getColumnValues(columnName);
    if (!values) return undefined;
    return values[rowIndex];
  }

  getCellsFiltered(columnName: string, filterFn: (value: string) => boolean): string[] {
    const values = this.getColumnValues(columnName);
    if (!values) return [];
    return values.filter(filterFn);
  }

  rowIndexInColumn(columnName: string, value: string): number | undefined {
    const values = this.getColumnValues(columnName);
    if (!values) return undefined;
    const index = values.indexOf(value);
    return index >= 0 ? index : undefined;
  }

  findRowIndexInColumn(columnName: string, predicate: (value: string) => boolean): number | undefined {
    const values = this.getColumnValues(columnName);
    if (!values) return undefined;
    return values.findIndex(predicate);
  }

  findRowInColumn(columnName: string, predicate: (value: string) => boolean): string | undefined {
    const values = this.getColumnValues(columnName);
    if (!values) return undefined;
    return values.find(predicate);
  }

  filterColumns(predicate: (column: Column) => boolean): Column[] {
    return this._columns.filter(predicate);
  }
}