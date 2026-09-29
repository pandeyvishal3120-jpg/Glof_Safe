from fastapi import APIRouter, HTTPException

from database import SessionLocal
from models import GlacialLake
from alert_service import create_alert

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


@router.get("/{lake_id}")
def get_alert(
    lake_id: int,
    risk_level: str = "LOW"
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

    return create_alert(
        risk_level=risk_level,
        lake_name=lake.name
    )
