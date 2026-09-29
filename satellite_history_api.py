from fastapi import APIRouter, HTTPException

from database import SessionLocal
from models import GlacialLake
from satellite_history import get_satellite_history


router = APIRouter(
    prefix="/satellite",
    tags=["Satellite History"]
)


@router.get("/history/{lake_id}")
def satellite_history_for_lake(lake_id: int):

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

    history = get_satellite_history(lake_id)

    return {
        "lake_id": lake.id,
        "lake_name": lake.name,
        "count": len(history),
        "history": history
    }
