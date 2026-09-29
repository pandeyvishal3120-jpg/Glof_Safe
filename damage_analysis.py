def assess_damage(
    pre_event_area_km2: float,
    post_event_area_km2: float,
    damaged_roads: int = 0,
    damaged_bridges: int = 0,
    damaged_buildings: int = 0
):
    pre_event_area_km2 = max(float(pre_event_area_km2), 0.0)
    post_event_area_km2 = max(float(post_event_area_km2), 0.0)

    damaged_roads = max(int(damaged_roads), 0)
    damaged_bridges = max(int(damaged_bridges), 0)
    damaged_buildings = max(int(damaged_buildings), 0)

    area_change = abs(post_event_area_km2 - pre_event_area_km2)

    if pre_event_area_km2 > 0:
        change_percent = (
            area_change / pre_event_area_km2
        ) * 100
    else:
        change_percent = 0

    damage_points = 0

    if change_percent >= 50:
        damage_points += 4
    elif change_percent >= 25:
        damage_points += 3
    elif change_percent >= 10:
        damage_points += 2
    elif change_percent > 0:
        damage_points += 1

    damage_points += min(damaged_roads, 3)
    damage_points += min(damaged_bridges * 2, 4)
    damage_points += min(damaged_buildings // 10, 4)

    if damage_points >= 10:
        damage_level = "CRITICAL"
    elif damage_points >= 7:
        damage_level = "HIGH"
    elif damage_points >= 4:
        damage_level = "MEDIUM"
    else:
        damage_level = "LOW"

    confidence = min(
        0.98,
        0.50
        + (0.10 if pre_event_area_km2 > 0 else 0)
        + min(damage_points * 0.03, 0.30)
    )

    return {
        "status": "DAMAGE_ASSESSED",
        "pre_event_area_km2": round(pre_event_area_km2, 4),
        "post_event_area_km2": round(post_event_area_km2, 4),
        "change_area_km2": round(area_change, 4),
        "change_percent": round(change_percent, 2),
        "damaged_roads": damaged_roads,
        "damaged_bridges": damaged_bridges,
        "damaged_buildings": damaged_buildings,
        "damage_score": damage_points,
        "damage_level": damage_level,
        "confidence": round(confidence, 2),
        "method": "Post-disaster multi-indicator damage assessment"
    }
