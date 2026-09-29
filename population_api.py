from fastapi import APIRouter, HTTPException
import json
from pathlib import Path

from database import SessionLocal
from models import GlacialLake
from population_impact import calculate_population_impact
from worldpop_service import get_population_for_polygon

router = APIRouter(
    prefix="/population",
    tags=["Population Impact"]
)

LAKES_GEOJSON = Path(__file__).parent / "data" / "lakes" / "glacial_lake.geojson"


def get_lake_geometry(lake_id: int):
    if not LAKES_GEOJSON.exists():
        raise FileNotFoundError("Glacial lake GeoJSON not found")

    with open(LAKES_GEOJSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    for feature in data.get("features", []):
        properties = feature.get("properties", {})

        if str(properties.get("objectid")) == str(lake_id):
            return feature.get("geometry")

    return None


@router.get("/{lake_id}")
def get_population_impact(
    lake_id: int,
    inundation_area_km2: float = 0
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

    if inundation_area_km2 <= 0:
        inundation_area_km2 = lake.area_km2

    try:
        geometry = get_lake_geometry(lake_id)

        if not geometry:
            raise RuntimeError("Lake geometry not found in GeoJSON dataset")

        worldpop = get_population_for_polygon(
            geometry,
            year=2020
        )

        population = worldpop["total_population"]

        impact = calculate_population_impact(
            inundation_area_km2=inundation_area_km2,
            population=population
        )

        return {
            "lake_id": lake.id,
            "lake_name": lake.name,
            "latitude": lake.latitude,
            "longitude": lake.longitude,
            "population_source": "WorldPop",
            "population_year": 2020,
            **impact,
            "worldpop_taskids": worldpop["taskids"]
        }

    except HTTPException:
        raise

    except Exception as e:
        # WorldPop is an external, network-dependent service - it can be
        # unreachable (no internet at a venue, rate limiting, outage, etc).
        # Rather than fail the whole endpoint, fall back to a rough
        # population estimate derived from lake area, same "degrade
        # gracefully" pattern used by the satellite endpoints.
        estimated_population = round(lake.area_km2 * 8000)

        impact = calculate_population_impact(
            inundation_area_km2=inundation_area_km2,
            population=estimated_population
        )

        return {
            "lake_id": lake.id,
            "lake_name": lake.name,
            "latitude": lake.latitude,
            "longitude": lake.longitude,
            "population_source": "ESTIMATED_FALLBACK",
            "population_year": None,
            **impact,
            "fallback_reason": str(e)
        }
