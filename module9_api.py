from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from climate_projection import project_lake_growth

router = APIRouter(prefix="/module9", tags=["Module 9 - Climate Projection"])


class ProjectionRequest(BaseModel):
    years: List[int]
    lake_area_km2: List[float]
    target_year: int = 2035


@router.post("/project-growth")
def post_project_growth(payload: ProjectionRequest):
    return project_lake_growth(payload.years, payload.lake_area_km2, payload.target_year)


@router.get("/project-growth-default")
def get_project_growth_default(target_year: int = 2035):
    """Convenience endpoint using this project's own historical_trend
    data so the module can be demoed with one click."""
    years = [2022, 2023, 2024, 2025, 2026]
    areas = [4.1, 4.4, 4.8, 5.2, 5.7]
    return project_lake_growth(years, areas, target_year)
