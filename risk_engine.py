def calculate_risk(water_level, water_change, seismic_activity):
    score = 0

    if water_level >= 68:
        score += 4
    elif water_level >= 63:
        score += 3
    elif water_level >= 58:
        score += 2
    else:
        score += 1

    if water_change >= 3:
        score += 4
    elif water_change >= 2:
        score += 3
    elif water_change >= 1:
        score += 2

    if seismic_activity >= 4:
        score += 4
    elif seismic_activity >= 3:
        score += 3
    elif seismic_activity >= 2:
        score += 2

    if score >= 10:
        level = "CRITICAL"
    elif score >= 7:
        level = "HIGH"
    elif score >= 4:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "risk_score": score,
        "risk_level": level
    }
