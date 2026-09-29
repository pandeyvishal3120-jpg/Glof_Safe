from fastapi import APIRouter, HTTPException
from satellite_area import calculate_ndwi_area
from database import SessionLocal
from models import GlacialLake

router = APIRouter(
    prefix="/satellite",
    tags=["Satellite Area"]
)


@router.get("/area/{lake_id}")
def get_lake_satellite_area(lake_id: int):

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

    return {
        "lake_id": lake.id,
        "lake_name": lake.name,
        "latitude": lake.latitude,
        "longitude": lake.longitude,
        **result
    }
