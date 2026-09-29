def calculate_combined_risk(
    water_level,
    water_change,
    seismic_activity,
    anomaly=False,
    lake_area_km2=0,
    satellite_change_percent=0,
    inundation_area_km2=0,
    affected_population=0
):
    score = 0
    factors = []

    # Water level
    if water_level >= 68:
        score += 4
        factors.append("Very high water level")
    elif water_level >= 63:
        score += 3
        factors.append("High water level")
    elif water_level >= 58:
        score += 2
        factors.append("Elevated water level")
    else:
        score += 1

    # Rapid water-level change
    if water_change >= 3:
        score += 4
        factors.append("Rapid water-level rise")
    elif water_change >= 2:
        score += 3
        factors.append("Significant water-level rise")
    elif water_change >= 1:
        score += 2
        factors.append("Increasing water level")

    # Seismic activity
    if seismic_activity >= 4:
        score += 4
        factors.append("High seismic activity")
    elif seismic_activity >= 3:
        score += 3
        factors.append("Elevated seismic activity")
    elif seismic_activity >= 2:
        score += 2
        factors.append("Moderate seismic activity")

    # Anomaly detector
    if anomaly:
        score += 3
        factors.append("Sensor anomaly detected")

    # Satellite lake-area expansion
    if satellite_change_percent >= 20:
        score += 4
        factors.append("Rapid satellite-observed lake expansion")
    elif satellite_change_percent >= 10:
        score += 3
        factors.append("Satellite-observed lake expansion")
    elif satellite_change_percent >= 5:
        score += 2
        factors.append("Moderate satellite-observed expansion")

    # Inundation impact
    if inundation_area_km2 >= 8:
        score += 4
        factors.append("Large predicted inundation area")
    elif inundation_area_km2 >= 5:
        score += 3
        factors.append("Significant predicted inundation area")
    elif inundation_area_km2 > 0:
        score += 1

    # Population impact
    if affected_population >= 5000:
        score += 4
        factors.append("Very high population impact")
    elif affected_population >= 2000:
        score += 3
        factors.append("High population impact")
    elif affected_population >= 500:
        score += 2
        factors.append("Population impact detected")

    # Final risk level
    if score >= 18:
        level = "CRITICAL"
        action = "Immediate evacuation and emergency response"
    elif score >= 12:
        level = "HIGH"
        action = "Urgent evacuation preparedness"
    elif score >= 7:
        level = "MEDIUM"
        action = "Enhanced monitoring and prepare evacuation"
    else:
        level = "LOW"
        action = "Continue monitoring"

    return {
        "risk_score": score,
        "risk_level": level,
        "risk_factors": factors,
        "recommended_action": action,
        "inputs": {
            "water_level_m": water_level,
            "water_change_m": water_change,
            "seismic_activity": seismic_activity,
            "anomaly": anomaly,
            "lake_area_km2": lake_area_km2,
            "satellite_change_percent": satellite_change_percent,
            "inundation_area_km2": inundation_area_km2,
            "affected_population": affected_population
        },
        "method": "Multi-source GLOF risk assessment"
    }
