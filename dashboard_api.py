from fastapi import APIRouter, HTTPException

from database import SessionLocal
from models import GlacialLake
from sensor_flow import process_sensor_flow
from combined_risk_engine import calculate_combined_risk
from population_impact import calculate_population_impact
from dem_inundation import terrain_inundation
from satellite_area import calculate_ndwi_area

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/{lake_id}")
def get_dashboard(lake_id: int):

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

    # Sensor data
    sensor = process_sensor_flow()

    # Satellite NDWI
    satellite = calculate_ndwi_area(
        lat=lake.latitude,
        lon=lake.longitude
    )

    satellite_change_percent = satellite.get(
        "change_percent",
        0
    )

    # DEM inundation
    inundation = terrain_inundation(
        latitude=lake.latitude,
        longitude=lake.longitude,
        water_level_increase_m=max(
            sensor["water_change_m"],
            0
        )
    )

    inundation_area = inundation.get(
        "estimated_inundation_area_km2",
        0
    )

    # Population impact
    population = calculate_population_impact(
        inundation_area_km2=inundation_area,
        population=10000
    )

    # Combined risk
    risk = calculate_combined_risk(
        water_level=sensor["water_level_m"],
        water_change=sensor["water_change_m"],
        seismic_activity=sensor["seismic_activity"],
        anomaly=sensor["anomaly"],
        lake_area_km2=lake.area_km2,
        satellite_change_percent=satellite_change_percent,
        inundation_area_km2=inundation_area,
        affected_population=population.get(
            "estimated_affected_population",
            0
        )
    )

    return {
        "status": "DASHBOARD_DATA_READY",

        "lake": {
            "id": lake.id,
            "name": lake.name,
            "latitude": lake.latitude,
            "longitude": lake.longitude,
            "area_km2": lake.area_km2
        },

        "sensor": sensor,

        "satellite": satellite,

        "dem_inundation": inundation,

        "population_impact": population,

        "risk": risk
    }
