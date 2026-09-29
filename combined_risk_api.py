from fastapi import APIRouter, HTTPException

from database import SessionLocal
from models import GlacialLake
from combined_risk_engine import calculate_combined_risk
from population_impact import calculate_population_impact
from dem_inundation import terrain_inundation


router = APIRouter(
    prefix="/combined-risk",
    tags=["Combined GLOF Risk"]
)


@router.get("/{lake_id}")
def get_combined_risk(
    lake_id: int,
    water_level_m: float = None,
    water_change_m: float = None,
    seismic_activity: float = None,
    anomaly: bool = False,
    satellite_change_percent: float = 0,
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

    if water_level_m is None:
        water_level_m = lake.water_level_m

    if water_change_m is None:
        water_change_m = 0

    if seismic_activity is None:
        seismic_activity = 0

    dem_result = terrain_inundation(
        latitude=lake.latitude,
        longitude=lake.longitude,
        water_level_increase_m=max(water_change_m, 0)
    )

    if dem_result.get("status") == "DEM_INUNDATION_CALCULATED":
        inundation_area = dem_result["estimated_inundation_area_km2"]
        inundation_method = "DEM terrain analysis"
    else:
        # Existing estimation fallback if DEM is unavailable.
        inundation_area = lake.area_km2 * (
            1 + max(water_change_m, 0) * 0.15
        )
        inundation_method = "Lake-level expansion fallback"

    population_impact = calculate_population_impact(
        inundation_area_km2=inundation_area,
        population=population
    )

    risk = calculate_combined_risk(
        water_level=water_level_m,
        water_change=water_change_m,
        seismic_activity=seismic_activity,
        anomaly=anomaly,
        lake_area_km2=lake.area_km2,
        satellite_change_percent=satellite_change_percent,
        inundation_area_km2=inundation_area,
        affected_population=population_impact[
            "estimated_affected_population"
        ]
    )

    return {
        "lake_id": lake.id,
        "lake_name": lake.name,
        **risk,
        "dem_inundation": dem_result,
        "inundation_method": inundation_method,
        "population_impact": population_impact
    }
