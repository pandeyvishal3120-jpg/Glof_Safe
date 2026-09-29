from fastapi.middleware.cors import CORSMiddleware
from sensor_simulator import get_sensor_data
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import engine, get_db
from models import Base, GlacialLake
from pathlib import Path
import sys
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'ml'))
from anomaly_detector import detect_anomaly


# Allow importing the ML module from ../ml
sys.path.append(str(Path(__file__).resolve().parent.parent / "ml"))

from risk_model import calculate_risk_score


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GLOF-SAFE API",
    description="GLOF Early Warning & Disaster Response System",
    version="0.1.0",
)


# ---------- Schemas ----------

class LakeCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    area_km2: float
    water_level_m: float
    risk_level: str = "Low"


class RiskRequest(BaseModel):
    water_level: float
    lake_area: float
    seismic_value: float
    water_level_change: float


# ---------- Basic Routes ----------

@app.get("/")
def root():
    return {
        "project": "GLOF-SAFE",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# ---------- Lake APIs ----------

@app.get("/lakes")
def get_lakes(db: Session = Depends(get_db)):
    lakes = db.query(GlacialLake).all()

    return [
        {
            "id": lake.id,
            "name": lake.name,
            "latitude": lake.latitude,
            "longitude": lake.longitude,
            "area_km2": lake.area_km2,
            "water_level_m": lake.water_level_m,
            "risk_level": lake.risk_level,
        }
        for lake in lakes
    ]


@app.post("/lakes")
def create_lake(
    lake: LakeCreate,
    db: Session = Depends(get_db),
):
    new_lake = GlacialLake(
        name=lake.name,
        latitude=lake.latitude,
        longitude=lake.longitude,
        area_km2=lake.area_km2,
        water_level_m=lake.water_level_m,
        risk_level=lake.risk_level,
    )

    db.add(new_lake)
    db.commit()
    db.refresh(new_lake)

    return {
        "message": "Glacial lake added successfully",
        "lake": {
            "id": new_lake.id,
            "name": new_lake.name,
            "latitude": new_lake.latitude,
            "longitude": new_lake.longitude,
            "area_km2": new_lake.area_km2,
            "water_level_m": new_lake.water_level_m,
            "risk_level": new_lake.risk_level,
        },
    }


# ---------- ML Risk Scoring ----------

@app.post("/risk-score")
def risk_score(request: RiskRequest):
    result = calculate_risk_score(
        water_level=request.water_level,
        lake_area=request.lake_area,
        seismic_value=request.seismic_value,
        water_level_change=request.water_level_change,
    )

    return result
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'ml'))
from anomaly_detector import detect_anomaly
    
@app.post("/sensor/anomaly")
def sensor_anomaly(
    water_level: float,
    previous_water_level: float,
    seismic_value: float
):
    return detect_anomaly(
        water_level=water_level,
        previous_water_level=previous_water_level,
        seismic_value=seismic_value,
    )

from sensor_api import save_sensor_reading
    
@app.post("/sensor/reading")
def save_reading(
    lake_id: int,
    water_level: float,
    seismic_value: float
):
    reading = save_sensor_reading(
        lake_id=lake_id,
        water_level=water_level,
        seismic_value=seismic_value
    )

    return {
        "message": "Sensor reading saved",
        "reading": {
            "id": reading.id,
            "lake_id": reading.lake_id,
            "water_level": reading.water_level,
            "seismic_value": reading.seismic_value,
            "timestamp": reading.timestamp
        }
    }




@app.get("/sensors")
def get_sensors():
    return get_sensor_data()

from risk_engine import calculate_risk

@app.get("/risk")
def get_risk():
    sensor = get_sensor_data()

    risk = calculate_risk(
        sensor["water_level_m"],
        sensor["water_change_m"],
        sensor["seismic_activity"]
    )

    return {
        **sensor,
        **risk
    }

from disaster_simulator import simulate_flood

@app.get("/simulate")
def simulate(
    water_level_increase: float = 2,
    population: int = 10000
):
    return simulate_flood(water_level_increase, population)

from evacuation import calculate_evacuation, create_alert

@app.get("/evacuation")
def get_evacuation():
    sensor = get_sensor_data()

    risk = calculate_risk(
        sensor["water_level_m"],
        sensor["water_change_m"],
        sensor["seismic_activity"]
    )

    evacuation = calculate_evacuation(risk["risk_level"])
    alert = create_alert(risk["risk_level"])

    return {
        **risk,
        **evacuation,
        "alert": alert
    }

from advanced_features import (
    historical_trend,
    satellite_damage_assessment,
    verify_misinformation
)

@app.get("/historical")
def get_historical():
    return historical_trend()


@app.get("/satellite-damage")
def get_satellite_damage():
    return satellite_damage_assessment()


@app.get("/verify")
def verify_claim(claim: str):
    return verify_misinformation(claim)

from satellite_api import router as satellite_router

app.include_router(satellite_router)

from satellite_area_api import router as satellite_area_router

app.include_router(satellite_area_router)

