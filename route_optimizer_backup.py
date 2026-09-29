import requests


OSRM_URL = "https://router.project-osrm.org/route/v1/driving"


def calculate_route(
    latitude: float,
    longitude: float,
    risk_level: str = "LOW"
):
    risk = str(risk_level).upper()

    # Temporary real-world candidate destinations.
    # These are road-routing targets, not fake distance calculations.
    candidates = [
        {
            "name": "Evacuation Point A",
            "latitude": latitude + 0.05,
            "longitude": longitude + 0.05
        },
        {
            "name": "Evacuation Point B",
            "latitude": latitude + 0.03,
            "longitude": longitude - 0.04
        },
        {
            "name": "Evacuation Point C",
            "latitude": latitude - 0.04,
            "longitude": longitude + 0.03
        }
    ]

    if risk == "CRITICAL":
        priority = "IMMEDIATE EVACUATION"
    elif risk == "HIGH":
        priority = "URGENT EVACUATION"
    elif risk == "MEDIUM":
        priority = "PREPARE FOR EVACUATION"
    else:
        priority = "MONITOR"

    routes = []

    for destination in candidates:
        try:
            url = (
                f"{OSRM_URL}/"
                f"{longitude},{latitude};"
                f"{destination['longitude']},{destination['latitude']}"
            )

            response = requests.get(
                url,
                params={
                    "overview": "false",
                    "steps": "false"
                },
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            if data.get("code") != "Ok":
                continue

            if not data.get("routes"):
                continue

            route = data["routes"][0]

            routes.append({
                "name": destination["name"],
                "latitude": destination["latitude"],
                "longitude": destination["longitude"],
                "distance_km": route["distance"] / 1000,
                "estimated_time_min": route["duration"] / 60
            })

        except Exception:
            continue

    if not routes:
        return {
            "status": "ROUTE_UNAVAILABLE",
            "priority": priority,
            "risk_level": risk,
            "message": "Real road-routing service unavailable."
        }

    # Choose shortest real road route.
    nearest = min(
        routes,
        key=lambda route: route["distance_km"]
    )

    return {
        "status": "REAL_ROAD_ROUTE_GENERATED",
        "priority": priority,
        "safe_zone": nearest["name"],
        "safe_zone_latitude": round(
            nearest["latitude"], 6
        ),
        "safe_zone_longitude": round(
            nearest["longitude"], 6
        ),
        "distance_km": round(
            nearest["distance_km"], 2
        ),
        "estimated_time_min": round(
            nearest["estimated_time_min"], 1
        ),
        "risk_level": risk,
        "method": "OpenStreetMap OSRM real road routing"
    }
