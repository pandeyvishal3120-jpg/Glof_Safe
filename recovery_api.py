from fastapi import APIRouter

from recovery_manager import (
    create_incident,
    update_recovery_stage
)

router = APIRouter(
    prefix="/recovery",
    tags=["Recovery Management"]
)


@router.get("/incident")
def new_incident(
    lake_id: int,
    affected_population: int = 0,
    damage_level: str = "LOW"
):
    return create_incident(
        lake_id=lake_id,
        affected_population=affected_population,
        damage_level=damage_level
    )


@router.get("/status")
def recovery_status(
    stage: str = "DISASTER",
    affected_population: int = 0,
    rescued_people: int = 0,
    relief_packages: int = 0
):
    return update_recovery_stage(
        stage=stage,
        affected_population=affected_population,
        rescued_people=rescued_people,
        relief_packages=relief_packages
    )
