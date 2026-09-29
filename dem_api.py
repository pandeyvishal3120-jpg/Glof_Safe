from fastapi import APIRouter
from dem_inundation import terrain_inundation

router = APIRouter(
    prefix="/dem",
    tags=["DEM Inundation"]
)


@router.get("/inundation")
def dem_inundation(
    latitude: float,
    longitude: float,
    water_level_increase_m: float = 0.0,
    dem_path: str | None = None
):
    return terrain_inundation(
        latitude=latitude,
        longitude=longitude,
        water_level_increase_m=water_level_increase_m,
        dem_path=dem_path
    )
