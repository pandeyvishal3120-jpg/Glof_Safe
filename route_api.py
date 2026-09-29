from fastapi import APIRouter, HTTPException

from database import SessionLocal
from models import GlacialLake
from route_optimizer import calculate_route

router = APIRouter(
    prefix="/route",
    tags=["Evacuation Route"]
)


@router.get("/{lake_id}")
def get_route(
    lake_id: int,
    risk_level: str = "HIGH"
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
        **calculate_route(
            latitude=lake.latitude,
            longitude=lake.longitude,
            risk_level=risk_level
        )
    }
