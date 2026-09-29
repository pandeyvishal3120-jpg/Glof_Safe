from fastapi import APIRouter, HTTPException

from database import SessionLocal
from models import GlacialLake
from precursor_hazard import (
    analyze_slope_instability,
    estimate_debris_flow_runout,
)

router = APIRouter(prefix="/module2", tags=["Module 2 - Precursor & Cascading Hazard"])


@router.get("/slope-instability/{lake_id}")
def get_slope_instability(lake_id: int, radius_km: float = 5.0):
    db = SessionLocal()
    lake = db.query(GlacialLake).filter(GlacialLake.id == lake_id).first()
    db.close()

    if not lake:
        raise HTTPException(status_code=404, detail="Lake not found")

    result = analyze_slope_instability(lake.latitude, lake.longitude, radius_km)

    return {
        "lake_id": lake.id,
        "lake_name": lake.name,
        **result,
    }


@router.get("/debris-flow-runout")
def get_debris_flow_runout(volume_m3: float, elevation_drop_m: float):
    return estimate_debris_flow_runout(volume_m3, elevation_drop_m)
