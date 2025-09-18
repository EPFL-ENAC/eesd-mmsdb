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

export interface LineComputeParams {
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  image: File;
}

export interface LineComputeResult {
  "success": boolean,
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
