from fastapi import APIRouter
from pydantic import BaseModel

from crowd_intel_gateway import parse_crowd_report, get_recent_reports
from satellite_siren import trigger_satellite_siren

router = APIRouter(prefix="/module5", tags=["Module 5 - Crowd-Sourced & Last-Mile"])


class CrowdReportRequest(BaseModel):
    message: str
    latitude: float
    longitude: float
    has_photo: bool = False


class SirenTriggerRequest(BaseModel):
    lake_name: str
    risk_level: str
    target_zone: str


@router.post("/crowd-report")
def post_crowd_report(payload: CrowdReportRequest):
    return parse_crowd_report(
        message=payload.message,
        latitude=payload.latitude,
        longitude=payload.longitude,
        has_photo=payload.has_photo,
    )


@router.get("/crowd-reports")
def list_crowd_reports(limit: int = 50):
    return {"reports": get_recent_reports(limit)}


@router.post("/siren-trigger")
def post_siren_trigger(payload: SirenTriggerRequest):
    return trigger_satellite_siren(
        payload.lake_name, payload.risk_level, payload.target_zone
    )
