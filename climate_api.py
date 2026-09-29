from fastapi import APIRouter
from climate_analysis import generate_climate_summary

router = APIRouter(
    prefix="/climate",
    tags=["Climate Analysis"]
)


@router.get("/trend")
def climate_trend():
    return generate_climate_summary(
        years=[2022, 2024, 2026],
        lake_area_km2=[2.1, 2.8, 4.5],
        water_level_m=[40, 48, 56]
    )
