from datetime import datetime


VALID_STAGES = [
    "DISASTER",
    "RESCUE",
    "RELIEF",
    "RECOVERY",
    "COMPLETED"
]


def create_incident(
    lake_id: int,
    affected_population: int = 0,
    damage_level: str = "LOW"
):
    return {
        "incident_id": f"GLOF-{lake_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "lake_id": lake_id,
        "stage": "DISASTER",
        "affected_population": max(int(affected_population), 0),
        "damage_level": str(damage_level).upper(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }


def update_recovery_stage(
    stage: str,
    affected_population: int = 0,
    rescued_people: int = 0,
    relief_packages: int = 0
):
    stage = str(stage).upper()

    if stage not in VALID_STAGES:
        return {
            "status": "INVALID_STAGE",
            "allowed_stages": VALID_STAGES
        }

    affected_population = max(int(affected_population), 0)
    rescued_people = max(int(rescued_people), 0)
    relief_packages = max(int(relief_packages), 0)

    rescue_percent = 0

    if affected_population > 0:
        rescue_percent = min(
            100,
            (rescued_people / affected_population) * 100
        )

    return {
        "status": "RECOVERY_STATUS_UPDATED",
        "stage": stage,
        "affected_population": affected_population,
        "rescued_people": rescued_people,
        "rescue_completion_percent": round(rescue_percent, 2),
        "relief_packages": relief_packages,
        "updated_at": datetime.utcnow().isoformat()
    }
