from fastapi import APIRouter, HTTPException

from database import SessionLocal
from models import GlacialLake
from bathymetry_engine import estimate_bathymetry
from sar_optical_gapfill import find_best_cloud_free_composite

router = APIRouter(prefix="/module1", tags=["Module 1 - Data & Bathymetry"])


@router.get("/bathymetry/{lake_id}")
def get_bathymetry(lake_id: int):
    db = SessionLocal()
    lake = db.query(GlacialLake).filter(GlacialLake.id == lake_id).first()
    db.close()

    if not lake:
        raise HTTPException(status_code=404, detail="Lake not found")

    result = estimate_bathymetry(
        latitude=lake.latitude,
        longitude=lake.longitude,
        area_km2=lake.area_km2,
    )

    return {
        "lake_id": lake.id,
        "lake_name": lake.name,
        **result,
    }


@router.get("/cloud-composite/{lake_id}")
def get_cloud_free_composite(lake_id: int):
    db = SessionLocal()
    lake = db.query(GlacialLake).filter(GlacialLake.id == lake_id).first()
    db.close()

    if not lake:
        raise HTTPException(status_code=404, detail="Lake not found")

    result = find_best_cloud_free_composite(lake.latitude, lake.longitude)

    return {
        "lake_id": lake.id,
        "lake_name": lake.name,
        **result,
    }
