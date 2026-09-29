from fastapi import APIRouter, HTTPException

from database import SessionLocal
from models import GlacialLake
from flood_model import generate_flood_scenario

router = APIRouter(
    prefix="/flood",
    tags=["Flood Prediction"]
)


@router.get("/{lake_id}")
def get_flood_prediction(
    lake_id: int,
    increase_m: float = 5,
    population: int = 10000
):
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

    return {
        "lake_id": lake.id,
        "lake_name": lake.name,
        "latitude": lake.latitude,
        "longitude": lake.longitude,
        **generate_flood_scenario(
            current_water_level_m=lake.water_level_m,
            increase_m=increase_m,
            lake_area_km2=lake.area_km2,
            population=population
        )
    }
