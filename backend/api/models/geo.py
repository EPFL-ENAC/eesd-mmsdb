from typing import List, Literal
from pydantic import BaseModel


class Geometry(BaseModel):
    coordinates: List[float]
    type: Literal["Point"]


class BuildingProperties(BaseModel):
    id: str
    identifier: str
    country: str
    city: str
    altitude: int
    climate_zone: str | None = None
    age_group: str | None = None
    socioeconomic_status: str | None = None
    building_type: str | None = None
    construction_year: int | None = None
    outdoor_env: str | None = None
    mechanical_ventilation: str | None = None
    mechanical_ventilation_types: str | None = None
    spaces_count: int
    study_id: str
    study_name: str
    color: str


class BuildingFeature(BaseModel):
    geometry: Geometry
    properties: BuildingProperties
    type: Literal["Feature"]


class BuildingFeatures(BaseModel):
    features: List[BuildingFeature]
    type: Literal["FeatureCollection"]


class ClimateZone(BaseModel):
    id: int
    name: str
    lon: float
    lat: float


class Elevation(BaseModel):
    altitude: float
    lon: float
    lat: float


class TimeZone(BaseModel):
    name: str
    lon: float
    lat: float
