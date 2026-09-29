from fastapi import APIRouter, HTTPException

from database import SessionLocal
from models import GlacialLake
from damage_analysis import assess_damage
from damage_satellite import satellite_damage_assessment


router = APIRouter(
    prefix="/damage",
    tags=["Damage Assessment"]
)


@router.get("/assess/{lake_id}")
def damage_assessment(
    lake_id: int,
    event_date: str | None = None
):
    db = SessionLocal()

    try:
        lake = db.query(GlacialLake).filter(
            GlacialLake.id == lake_id
        ).first()
    finally:
        db.close()

    if not lake:
        raise HTTPException(
            status_code=404,
            detail="Lake not found"
        )

    satellite_result = satellite_damage_assessment(
        lat=lake.latitude,
        lon=lake.longitude,
        event_date=event_date
    )

    if satellite_result.get("status") != "SATELLITE_DAMAGE_ASSESSED":
        return {
            "lake_id": lake.id,
            "lake_name": lake.name,
            "latitude": lake.latitude,
            "longitude": lake.longitude,
            **satellite_result
        }

    pre_area = satellite_result["pre_event_area_km2"]
    post_area = satellite_result["post_event_area_km2"]

    assessment = assess_damage(
        pre_event_area_km2=pre_area,
        post_event_area_km2=post_area
    )

    return {
        "lake_id": lake.id,
        "lake_name": lake.name,
        "latitude": lake.latitude,
        "longitude": lake.longitude,
        "satellite": satellite_result,
        "damage_assessment": assessment
    }

