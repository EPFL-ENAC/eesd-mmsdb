export interface DBModel {
  id?: number | string;
  [Key: string]: unknown;
}

export interface Person extends DBModel {
  name: string;
  email: string;
  email_public: boolean;
  institution: string;
}

export interface Certification extends DBModel {
  program: string;
  level: string;
}

export interface Building extends DBModel {
  identifier: string;
  country: string;
  city: string;
  postcode?: string | undefined;
  timezone?: string;
  long?: number | undefined;
  lat?: number | undefined;
  altitude?: number | undefined;
  climate_zone?: string | undefined;
  type?: string;
  other_type?: string | undefined;
  outdoor_env?: string;
  other_outdoor_env?: string | undefined;
  green_certified?: string;
  construction_year?: number;
  renovation?: string;
  renovation_details?: string | undefined;
  renovation_year?: number | undefined;
  mechanical_ventilation?: string;
  particle_filtration_system?: string;
  particle_filtration_rating?: number;
  operable_windows?: string;
  airtightness?: number;
  age_group?: string;
  socioeconomic_status?: string;
  smoking?: string;
  spaces?: Space[];
  certifications?: Certification[];
}

interface ListResult {
  total: number;
  skip: number | undefined;
  limit: number | undefined;
}

export interface BuildingsResult extends ListResult {
  data: Building[];
}

export interface Study extends DBModel {
  identifier: string;
  name: string;
  description: string;
  website?: string;
  start_year?: number;
  end_year?: number;
  duration?: number;
  occupant_impact?: string[];
  other_indoor_param?: string[];
  citation?: string;
  doi?: string;
  funding?: string;
  ethics?: string;
  license?: string;
  data_processing?: string;
  contributors?: Person[];
  buildings?: Building[];
  instruments?: Instrument[];
  datasets?: Dataset[];
}

export interface StudiesResult extends ListResult {
  data: Study[];
}

export interface StudySummary extends DBModel {
  identifier: string;
  name: string;
  description: string;
  color: string;
  countries: string[];
  cities: string[];
}
export interface StudySummariesResult extends ListResult {
  data: StudySummary[];
}
export interface Space extends DBModel {
  identifier: string;
  type: string;
  floor_area?: number;
  space_volume?: number;
  occupancy_density?: number | undefined;
  occupancy_number?: number | undefined;
  occupancy?: string | undefined;
  mechanical_ventilation_type?: string;
  other_mechanical_ventilation_type?: string | undefined;
  cooling_type?: string | undefined;
  other_cooling_type?: string | undefined;
  heating_type?: string | undefined;
  other_heating_type?: string | undefined;
  air_filtration?: string;
  printers?: string;
  carpets?: string;
  combustion_sources?: string;
  major_combustion_sources?: string | undefined;
  minor_combustion_sources?: string | undefined;
  pets?: string;
  dampness?: string;
  mold?: string;
  detergents?: string;
}

export interface SpacesResult extends ListResult {
  data: Space[];
}

export interface Instrument extends DBModel {
  identifier: string;
  manufacturer: string;
  model: string;
  equipment_grade_rating: string;
  placement: string;
  parameters?: InstrumentParameter[];
}

export interface InstrumentParameter extends DBModel {
  physical_parameter: string;
  analysis_method?: string;
  measurement_uncertainty?: string;
  note?: string;
}

export interface InstrumentsResult extends ListResult {
  data: Instrument[];
}

export interface Variable extends DBModel {
  name: string;
  type: string;
  unit?: string;
  format?: string;
  reference?: string;
}

export interface Dataset extends DBModel {
  name: string;
  description?: string;
  folder: FileNode;
  variables?: Variable[];
}

export interface FileNode {
  name: string;
  path: string;
  size: number | undefined;
  alt_name: string | undefined;
  alt_path: string | undefined;
  alt_size: number | undefined;
  is_file: boolean;
  children: FileNode[] | undefined;
}

export interface UploadResult {
  files: FileNode[];
}

export interface GroupByCount {
    value: string | null;
    count: number;
}

export interface GroupByResult {
    field: string;
    counts: GroupByCount[];
}

export interface Contribution extends DBModel {
  created_at?: string;
  created_by?: string;
  updated_at?: string;
  updated_by?: string;
  published_at?: string;
  published_by?: string;
  data_embargo?: string;
}

export interface StudyBundle {
  study: Study;
  contribution?: Contribution;
}
