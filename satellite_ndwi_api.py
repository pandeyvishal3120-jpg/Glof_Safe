from fastapi import APIRouter, HTTPException
from satellite_ndwi import calculate_ndwi_area
from satellite_history import save_satellite_history
from database import SessionLocal
from models import GlacialLake

router = APIRouter(
    prefix="/satellite",
    tags=["Satellite NDWI"]
)


@router.get("/ndwi/{lake_id}")
def get_ndwi_area(lake_id: int):

    db = SessionLocal()

    lake = db.query(GlacialLake).filter(
        GlacialLake.id == lake_id
    ).first()

    db.close()

    if not lake:
        raise HTTPException(
            status_code=404,
            detail="Lake not found"
        )

    result = calculate_ndwi_area(
        lake.latitude,
        lake.longitude
    )

    if result.get("status") != "SATELLITE_SCENE_FOUND":
        return {
            "lake_id": lake.id,
            "lake_name": lake.name,
            **result
        }

    return {
        "lake_id": lake.id,
        "lake_name": lake.name,
        **result
    }
