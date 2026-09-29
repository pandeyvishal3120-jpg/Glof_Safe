def analyze_climate_trend(
    years,
    lake_area_km2,
    water_level_m=None
):
    years = list(years)
    areas = [float(x) for x in lake_area_km2]

    if len(years) != len(areas) or len(areas) < 2:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": "At least two matching observations are required."
        }

    first_area = areas[0]
    latest_area = areas[-1]

    area_change_km2 = latest_area - first_area

    if first_area != 0:
        area_change_percent = (area_change_km2 / first_area) * 100
    else:
        area_change_percent = 0

    if area_change_percent >= 10:
        trend = "STRONGLY_INCREASING"
    elif area_change_percent >= 5:
        trend = "INCREASING"
    elif area_change_percent <= -5:
        trend = "DECREASING"
    else:
        trend = "STABLE"

    result = {
        "status": "TREND_ANALYZED",
        "years": years,
        "lake_area_km2": areas,
        "initial_area_km2": round(first_area, 4),
        "latest_area_km2": round(latest_area, 4),
        "area_change_km2": round(area_change_km2, 4),
        "area_change_percent": round(area_change_percent, 2),
        "trend": trend,
        "method": "Historical lake-area trend analysis"
    }

    if water_level_m:
        levels = [float(x) for x in water_level_m]

        if len(levels) == len(years):
            result["water_level_m"] = levels
            result["water_level_change_m"] = round(
                levels[-1] - levels[0], 4
            )

    return result


def generate_climate_summary(
    years,
    lake_area_km2,
    water_level_m=None
):
    analysis = analyze_climate_trend(
        years=years,
        lake_area_km2=lake_area_km2,
        water_level_m=water_level_m
    )

    if analysis.get("status") != "TREND_ANALYZED":
        return analysis

    trend = analysis["trend"]

    if trend in ("STRONGLY_INCREASING", "INCREASING"):
        interpretation = (
            "Lake area is increasing and should receive closer monitoring."
        )
    elif trend == "DECREASING":
        interpretation = (
            "Lake area is decreasing compared with the initial observation."
        )
    else:
        interpretation = (
            "Lake area is relatively stable across the available observations."
        )

    analysis["interpretation"] = interpretation

    return analysis
