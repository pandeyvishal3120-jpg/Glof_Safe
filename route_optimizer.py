import requests


OSRM_URL = "https://router.project-osrm.org"


def get_nearest_roads(latitude, longitude, number=5):
    url = f"{OSRM_URL}/nearest/v1/driving/{longitude},{latitude}"

    response = requests.get(
        url,
        params={"number": number},
        timeout=15
    )
    response.raise_for_status()

    data = response.json()

    if data.get("code") != "Ok":
        return []

    return data.get("waypoints", [])


def get_route(start_lon, start_lat, end_lon, end_lat):
    url = (
        f"{OSRM_URL}/route/v1/driving/"
        f"{start_lon},{start_lat};"
        f"{end_lon},{end_lat}"
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
        return None

    routes = data.get("routes", [])

    if not routes:
        return None

    return routes[0]


def calculate_route(
    latitude: float,
    longitude: float,
    risk_level: str = "LOW"
):
    risk = str(risk_level).upper()

    if risk == "CRITICAL":
        priority = "IMMEDIATE EVACUATION"
    elif risk == "HIGH":
        priority = "URGENT EVACUATION"
    elif risk == "MEDIUM":
        priority = "PREPARE FOR EVACUATION"
    else:
        priority = "MONITOR"

    try:
        roads = get_nearest_roads(
            latitude=latitude,
            longitude=longitude,
            number=5
        )

        if not roads:
            return {
                "status": "ROUTE_UNAVAILABLE",
                "priority": priority,
                "risk_level": risk,
                "message": "No nearby routable road found."
            }

        # Select the nearest routable road point.
        nearest = min(
            roads,
            key=lambda point: point.get("distance", float("inf"))
        )

        road_lon, road_lat = nearest["location"]
        road_distance_km = nearest.get("distance", 0) / 1000

        # The nearest road is a routing point, NOT a shelter.
        # The lake itself is off-road, so direct lake-to-road routing
        # can collapse to 0 km after OSRM snapping.
        # Use two distinct routable road points instead.

        if road_distance_km <= 0:
            return {
                "status": "ROUTE_UNAVAILABLE",
                "priority": priority,
                "risk_level": risk,
                "message": "Lake location could not be mapped to a usable road point."
            }

        farther = None

        for candidate in roads:
            candidate_lon, candidate_lat = candidate["location"]

            if (
                abs(candidate_lon - road_lon) > 0.001
                or abs(candidate_lat - road_lat) > 0.001
            ):
                farther = candidate
                break

        if farther is None:
            return {
                "status": "ROUTE_UNAVAILABLE",
                "priority": priority,
                "risk_level": risk,
                "message": "No distinct evacuation road segment found."
            }

        destination_lon, destination_lat = farther["location"]

        route = get_route(
            start_lon=road_lon,
            start_lat=road_lat,
            end_lon=destination_lon,
            end_lat=destination_lat
        )

        if not route:
            return {
                "status": "ROUTE_UNAVAILABLE",
                "priority": priority,
                "risk_level": risk,
                "message": "Road route could not be generated."
            }

        distance_km = route["distance"] / 1000
        duration_min = route["duration"] / 60

        return {
            "status": "REAL_ROAD_ROUTE_GENERATED",
            "priority": priority,
            "safe_zone": "Routable Evacuation Road Segment",
            "safe_zone_latitude": round(destination_lat, 6),
            "safe_zone_longitude": round(destination_lon, 6),
            "distance_km": round(distance_km, 2),
            "estimated_time_min": round(duration_min, 1),
            "road_distance_from_lake_km": round(
                road_distance_km, 2
            ),
            "risk_level": risk,
            "method": "OpenStreetMap OSRM nearest-road routing",
            "note": "Road point is not a verified emergency shelter. Real shelter integration pending."
        }

    except Exception as error:
        return {
            "status": "ROUTE_ERROR",
            "priority": priority,
            "risk_level": risk,
            "message": str(error)
        }
