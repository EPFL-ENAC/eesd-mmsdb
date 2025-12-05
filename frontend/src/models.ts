export interface CitationItem {
  authors: string;
  title: string;
  journal: string;
  year?: string;
  doi?: string;
  type?: string;
}

export interface ColumnInfo {
  key: string;
  label: string;
  type: string;
  unit?: string;
  precision?: number;
  bins?: {
    name: string;
    fullName: string;
    min: number;
    max: number;
  }[];
}

export interface Column {
  name: string;
  values: string[];
}

export type Table = Column[];

export interface CorrelationResult {
  slope: number;
  intercept: number;
  R2: number;
  MAE: number;
  outlier_indices: number[];
}

export interface LineComputeInputLineCoords {
  startX: number;
  startY: number;
  endX: number;
  endY: number;
}

export interface LineComputeParams {
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  image: File;
  realLength: number;
  realHeight: number;
  analysisType: number;
  interfaceWeight: number;
  boundaryMargin: number;
}

export interface LineComputeResult {
  "success": boolean,
  "error"?: string,
  "lmp_type": string,
  "lmt_result": number,
  "total_length": number,
  "path_coordinates": {
    "pixel_coordinates": [number, number][],
    "real_world_coordinates": [number, number][],
  },
  "start_point_used": [number, number],
  "end_point_used": [number, number],
  "image_dimensions": {
    "width": number,
    "height": number,
  },
  "scale_factors": {
    "length_scale": number,
    "height_scale": number,
  },
}

export interface LineComputeTrace {
  params: LineComputeParams;
  color: string;
  result: LineComputeResult;
}

export interface WallStonesList {
  wallId: string;
  folder: string;
  files: string[];
}

export interface FileInfo {
  name: string;
  size: number;
}

export interface Contribution {
  name: string;
  email: string;
  affiliation?: string;
  type: string;  // Microstructure type: Real or Virtual
  method?: string;  // Photogrammetry, CT scan, Procedural, Other
  reference?: string;  // Reference to a publication or project
  comments?: string;
}

export interface UploadInfo {
  path: string;
  date: string;
  files: FileInfo[];
  total_size: number;
  state: string;
  contribution: Contribution | null;
}

export interface UploadInfoState {
  path: string;
  state: string;
}

export interface User {
  username: string;
  full_name: string;
  email?: string;
  role: string;
}
