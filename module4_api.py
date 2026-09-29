from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

from database import SessionLocal
from models import GlacialLake
from bayesian_verifier import verify_alarm
from cap_generator import generate_cap_alert

router = APIRouter(prefix="/module4", tags=["Module 4 - Zero-Latency Decision Pipeline"])


class EvidenceRequest(BaseModel):
    evidence: Dict[str, bool]


@router.post("/verify-alarm")
def post_verify_alarm(payload: EvidenceRequest):
    return verify_alarm(payload.evidence)


@router.get("/cap-alert/{lake_id}")
def get_cap_alert(lake_id: int, risk_level: str = "HIGH"):
    db = SessionLocal()
    lake = db.query(GlacialLake).filter(GlacialLake.id == lake_id).first()
    db.close()

    if not lake:
        raise HTTPException(status_code=404, detail="Lake not found")

    headline = f"GLOF {risk_level.upper()} risk alert - {lake.name}"
    description = (
        f"Automated GLOF-SAFE monitoring has flagged {lake.name} at "
        f"{risk_level.upper()} risk. Current water level: "
        f"{lake.water_level_m} m. This alert was generated "
        f"automatically with no manual review step."
    )

    result = generate_cap_alert(
        lake_name=lake.name,
        latitude=lake.latitude,
        longitude=lake.longitude,
        risk_level=risk_level,
        headline=headline,
        description=description,
    )

    return {
        "lake_id": lake.id,
        "lake_name": lake.name,
        **result,
    }
