from fastapi import APIRouter
import random

router = APIRouter(
    prefix="/advanced-hazard",
    tags=["Advanced Hazard Monitoring"]
)

@router.get("/river-level/{lake_id}")
def get_river_level(lake_id: int):
    """
    Prototype river-level monitoring.
    Values are simulated for demonstration.
    """

    river_level = round(random.uniform(4.0, 9.0), 2)
    danger_level = 7.5
    rise_3h = round(random.uniform(-0.5, 1.5), 2)

    if river_level >= danger_level + 1:
        status = "CRITICAL"
    elif river_level >= danger_level:
        status = "HIGH"
    elif rise_3h >= 1.0:
        status = "RISING_FAST"
    else:
        status = "NORMAL"

    return {
        "lake_id": lake_id,
        "data_type": "SIMULATED_RIVER_MONITORING",
        "river_level_m": river_level,
        "danger_level_m": danger_level,
        "rise_last_3h_m": rise_3h,
        "status": status
    }

@router.get("/cascade/{lake_id}")
def get_cascade_hazard(lake_id: int):
    """
    Prototype cascading-hazard detection.
    Values are simulated for demonstration.
    """

    river_blockage = random.choice([True, False])
    breach_risk = random.choice(["LOW", "MEDIUM", "HIGH"])
    lead_time_min = random.randint(30, 240)

    if river_blockage and breach_risk == "HIGH":
        status = "BREACH_RISK"
    elif river_blockage:
        status = "NATURAL_DAM_FORMING"
    else:
        status = "NORMAL"

    return {
        "lake_id": lake_id,
        "data_type": "SIMULATED_CASCADE_MONITORING",
        "river_blockage": river_blockage,
        "breach_risk": breach_risk,
        "warning_lead_time_min": lead_time_min,
        "status": status
    }

@router.get("/infrastructure/{lake_id}")
def get_infrastructure_risk(lake_id: int):
    """
    Prototype critical-infrastructure risk.
    Values are simulated for demonstration.
    """

    bridges = random.randint(0, 6)
    hydropower = random.randint(0, 3)
    hospitals = random.randint(0, 2)

    total = bridges + hydropower + hospitals

    if total >= 7:
        status = "CRITICAL"
    elif total >= 4:
        status = "HIGH"
    elif total >= 2:
        status = "MEDIUM"
    else:
        status = "LOW"

    return {
        "lake_id": lake_id,
        "data_type": "SIMULATED_INFRASTRUCTURE_RISK",
        "bridges_at_risk": bridges,
        "hydropower_at_risk": hydropower,
        "hospitals_at_risk": hospitals,
        "overall_status": status
    }

@router.get("/district-risk/{lake_id}")
def get_district_risk(lake_id: int):
    """
    Prototype district-level risk assessment.
    Values are simulated for demonstration.
    """

    districts = [
        "West Champaran",
        "Gopalganj",
        "East Champaran",
        "Muzaffarpur"
    ]

    district = random.choice(districts)
    risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    risk_level = random.choice(risk_levels)

    affected_population = random.randint(5000, 50000)

    return {
        "lake_id": lake_id,
        "data_type": "SIMULATED_DISTRICT_RISK",
        "district": district,
        "risk_level": risk_level,
        "estimated_affected_population": affected_population
    }

@router.get("/warning/{lake_id}")
def get_unified_warning(lake_id: int):
    """
    Prototype unified downstream warning.
    Combines simulated hazard signals.
    """

    river_level = round(random.uniform(5.0, 9.5), 2)
    danger_level = 7.5
    rise_3h = round(random.uniform(0.0, 1.8), 2)

    blockage = random.choice([True, False])
    breach_risk = random.choice(["LOW", "MEDIUM", "HIGH"])

    infrastructure_status = random.choice(
        ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    )

    district_risk = random.choice(
        ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    )

    score = 0

    if river_level >= danger_level:
        score += 2

    if rise_3h >= 1:
        score += 2

    if blockage:
        score += 2

    if breach_risk == "HIGH":
        score += 2
    elif breach_risk == "MEDIUM":
        score += 1

    if infrastructure_status in ["HIGH", "CRITICAL"]:
        score += 2

    if district_risk in ["HIGH", "CRITICAL"]:
        score += 2

    if score >= 8:
        warning_level = "CRITICAL"
        action = "INITIATE EVACUATION AND EMERGENCY RESPONSE"
    elif score >= 5:
        warning_level = "HIGH"
        action = "PREPARE EVACUATION AND ALERT DOWNSTREAM AREAS"
    elif score >= 3:
        warning_level = "MEDIUM"
        action = "ENHANCED MONITORING AND PREPAREDNESS"
    else:
        warning_level = "LOW"
        action = "CONTINUE MONITORING"

    return {
        "lake_id": lake_id,
        "data_type": "SIMULATED_UNIFIED_WARNING",
        "warning_score": score,
        "warning_level": warning_level,
        "recommended_action": action,
        "river_level_m": river_level,
        "danger_level_m": danger_level,
        "rise_last_3h_m": rise_3h,
        "river_blockage": blockage,
        "breach_risk": breach_risk,
        "infrastructure_status": infrastructure_status,
        "district_risk": district_risk
    }
