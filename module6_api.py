from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

from structural_vulnerability import analyze_downstream_vulnerability

router = APIRouter(prefix="/module6", tags=["Module 6 - Structural Vulnerability"])


class VulnerabilityRequest(BaseModel):
    lake_id: int
    structures: List[Dict[str, Any]]
    flow_velocity_m_s: float = 3.0


@router.post("/analyze")
def post_analyze(payload: VulnerabilityRequest):
    return analyze_downstream_vulnerability(
        payload.lake_id, payload.structures, payload.flow_velocity_m_s
    )


@router.get("/analyze-default/{lake_id}")
def get_analyze_default(lake_id: int, flow_velocity_m_s: float = 3.0):
    """Convenience endpoint with a plausible default downstream
    infrastructure set, so the module can be demoed without a payload."""
    default_structures = [
        {"name": "Village Footbridge", "type": "footbridge", "distance_km": 3, "elevation_drop_m": 40},
        {"name": "Main Road Bridge", "type": "road_bridge_pier", "distance_km": 7, "elevation_drop_m": 90},
        {"name": "Riverside Houses", "type": "residential_building", "distance_km": 5, "elevation_drop_m": 60},
        {"name": "Transmission Tower T-14", "type": "transmission_tower", "distance_km": 9, "elevation_drop_m": 110},
    ]
    return analyze_downstream_vulnerability(lake_id, default_structures, flow_velocity_m_s)
