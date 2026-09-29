from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from transboundary_discharge import estimate_discharge, detect_upstream_release

router = APIRouter(prefix="/module3", tags=["Module 3 - Transboundary Tracker"])


class DischargeSeriesRequest(BaseModel):
    readings_m3s: List[float]


@router.get("/discharge")
def get_discharge(
    latitude: float,
    longitude: float,
    river_width_m: Optional[float] = None,
    flow_depth_m: Optional[float] = None,
):
    return estimate_discharge(latitude, longitude, river_width_m, flow_depth_m)


@router.post("/upstream-release-check")
def check_upstream_release(payload: DischargeSeriesRequest):
    return detect_upstream_release(payload.readings_m3s)
