from math import sqrt


def predict_inundation(
    water_level_increase: float,
    lake_area_km2: float,
    population: int = 10000
):
    """
    Estimate potential flood/inundation impact from a lake-level increase.

    This is a deterministic engineering-style estimation layer.
    It does not claim to replace DEM/hydraulic modelling.
    """

    water_level_increase = max(float(water_level_increase), 0.0)
    lake_area_km2 = max(float(lake_area_km2), 0.0)
    population = max(int(population), 0)

    if water_level_increase <= 0 or lake_area_km2 <= 0:
        return {
            "status": "NO_INUNDATION",
            "water_level_increase_m": round(water_level_increase, 2),
            "estimated_inundation_area_km2": 0.0,
            "estimated_affected_population": 0,
            "risk_level": "LOW",
        }

    # Approximate expansion factor.
    expansion_factor = 1 + (water_level_increase * 0.15)

    inundation_area = lake_area_km2 * expansion_factor

    # Population impact is estimated from the fraction of the
    # surrounding area represented by the expansion.
    impact_ratio = min(
        0.95,
        (water_level_increase / 10.0) * 0.20
    )

    affected_population = round(population * impact_ratio)

    if water_level_increase >= 8:
        risk_level = "CRITICAL"
    elif water_level_increase >= 5:
        risk_level = "HIGH"
    elif water_level_increase >= 2:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "status": "INUNDATION_PREDICTED",
        "water_level_increase_m": round(water_level_increase, 2),
        "lake_area_km2": round(lake_area_km2, 4),
        "estimated_inundation_area_km2": round(inundation_area, 4),
        "estimated_affected_population": affected_population,
        "risk_level": risk_level,
        "method": "Lake-level expansion estimation",
    }


def generate_flood_scenario(
    current_water_level_m: float,
    increase_m: float,
    lake_area_km2: float,
    population: int = 10000
):
    current_water_level_m = float(current_water_level_m)
    increase_m = float(increase_m)

    result = predict_inundation(
        water_level_increase=increase_m,
        lake_area_km2=lake_area_km2,
        population=population,
    )

    result["current_water_level_m"] = round(current_water_level_m, 2)
    result["predicted_water_level_m"] = round(
        current_water_level_m + max(increase_m, 0),
        2
    )

    return result
