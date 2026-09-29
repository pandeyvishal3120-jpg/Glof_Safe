from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LakeBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    water_level_m: float = 0.0
    area_km2: float = 0.0


class LakeCreate(LakeBase):
    pass


class LakeResponse(LakeBase):
    id: int

    class Config:
        from_attributes = True


class SensorReading(BaseModel):
    water_level_m: float
    water_change_m: float = 0.0
    seismic_activity: float = 0.0
    timestamp: Optional[datetime] = None


class RiskResponse(BaseModel):
    risk_score: int
    risk_level: str


class AlertResponse(BaseModel):
    status: str
    lake_name: str
    risk_level: str
    priority: str
    message: str
    recommended_action: str
    timestamp: str


class PopulationImpactResponse(BaseModel):
    status: str
    population: int
    inundation_area_km2: float
    estimated_affected_population: int
    impact_percentage: float
    impact_level: str


class RouteResponse(BaseModel):
    status: str
    priority: str
    safe_zone: str
    safe_zone_latitude: float
    safe_zone_longitude: float
    distance_km: float
    estimated_time_min: float
    risk_level: str


class RecoveryStatus(BaseModel):
    stage: str
    affected_population: int = Field(default=0, ge=0)
    rescued_people: int = Field(default=0, ge=0)
    relief_packages: int = Field(default=0, ge=0)
