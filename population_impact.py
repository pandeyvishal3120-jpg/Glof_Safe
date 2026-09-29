def calculate_population_impact(
    inundation_area_km2: float,
    population: float
):
    inundation_area_km2 = max(float(inundation_area_km2), 0.0)
    population = max(float(population), 0.0)

    if inundation_area_km2 <= 0 or population <= 0:
        return {
            "status": "NO_SIGNIFICANT_IMPACT",
            "estimated_affected_population": 0,
            "impact_level": "LOW"
        }

    # Estimate the proportion of population affected
    # based on the inundation area.
    affected_ratio = min(
        0.95,
        inundation_area_km2 * 0.12
    )

    affected_population = round(
        population * affected_ratio
    )

    if affected_population >= population * 0.60:
        impact_level = "CRITICAL"
    elif affected_population >= population * 0.30:
        impact_level = "HIGH"
    elif affected_population >= population * 0.10:
        impact_level = "MEDIUM"
    else:
        impact_level = "LOW"

    return {
        "status": "IMPACT_ESTIMATED",
        "population": round(population, 2),
        "inundation_area_km2": round(inundation_area_km2, 4),
        "estimated_affected_population": affected_population,
        "impact_percentage": round(
            affected_ratio * 100, 2
        ),
        "impact_level": impact_level,
        "method": "WorldPop population + DEM inundation impact estimation"
    }
