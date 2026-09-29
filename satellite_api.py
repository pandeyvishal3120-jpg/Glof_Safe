from fastapi import APIRouter, HTTPException
from satellite_service import (
    get_all_satellite_observations,
    search_sentinel2,
    SessionLocal,
)
from models import GlacialLake

router = APIRouter(
    prefix="/satellite",
    tags=["Satellite"]
)


@router.get("/observations")
def satellite_observations():
    return {
        "source": "Copernicus Sentinel-2 L2A",
        "results": get_all_satellite_observations()
    }


@router.get("/observations/{lake_id}")
def satellite_observation_for_lake(lake_id: int):

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

    observation = search_sentinel2(
        lake.latitude,
        lake.longitude
    )

    if not observation:
        return {
            "lake_id": lake.id,
            "lake_name": lake.name,
            "status": "NO_RECENT_SATELLITE_OBSERVATION"
        }

    return {
        "source": "Copernicus Sentinel-2 L2A",
        "lake_id": lake.id,
        "lake_name": lake.name,
        "latitude": lake.latitude,
        "longitude": lake.longitude,
        **observation,
    }
