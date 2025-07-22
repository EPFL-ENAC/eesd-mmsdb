import type { Variable } from 'src/models';

export interface DataFile {
  file: File;
  variables: Variable[];
}

export interface TableRequestProps {
  pagination: {
    page: number;
    rowsPerPage: number;
    sortBy: string;
    descending: boolean;
  };
}