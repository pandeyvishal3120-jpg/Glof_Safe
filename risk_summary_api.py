from fastapi import APIRouter
from database import SessionLocal
from models import GlacialLake
from risk_engine import calculate_risk
import random

router = APIRouter(prefix="/risk-summary", tags=["Risk Summary"])

@router.get("")
def get_risk_summary():
    db = SessionLocal()

    try:
        lakes = db.query(GlacialLake).all()

        result = []
        counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }

        for lake in lakes:
            # Simulated monitoring values for dashboard visualization
            water_level = random.uniform(50, 72)
            water_change = random.uniform(-1, 4)
            seismic = random.uniform(0, 5)

            risk = calculate_risk(
                water_level,
                water_change,
                seismic
            )

            level = risk["risk_level"].upper()
            counts[level] += 1

            result.append({
                "id": lake.id,
                "name": lake.name,
                "latitude": lake.latitude,
                "longitude": lake.longitude,
                "area_km2": lake.area_km2,
                "water_level_m": round(water_level, 2),
                "water_change_m": round(water_change, 2),
                "seismic_activity": round(seismic, 2),
                "risk_score": risk["risk_score"],
                "risk_level": level
            })

        return {
            "total_lakes": len(result),
            "critical": counts["CRITICAL"],
            "high": counts["HIGH"],
            "medium": counts["MEDIUM"],
            "low": counts["LOW"],
            "risk_distribution": counts,
            "data_type": "SIMULATED_MONITORING",
            "lakes": result
        }

    finally:
        db.close()
