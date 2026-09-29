def simulate_flood(water_level_increase, population=10000):
    affected_area = round(water_level_increase * 2.5, 2)
    affected_population = round(
        min(population, affected_area * 1200)
    )

    if water_level_increase >= 5:
        severity = "CRITICAL"
    elif water_level_increase >= 3:
        severity = "HIGH"
    elif water_level_increase >= 1.5:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    return {
        "water_level_increase_m": water_level_increase,
        "estimated_inundation_km2": affected_area,
        "estimated_affected_population": affected_population,
        "severity": severity
    }
