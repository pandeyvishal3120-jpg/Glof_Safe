import time
import json
import requests

from shapely.geometry import shape, mapping
from shapely.ops import transform
from pyproj import Transformer


WORLDPOP_STATS_URL = "https://api.worldpop.org/v1/services/stats"
WORLDPOP_TASK_URL = "https://api.worldpop.org/v1/tasks"

# Real lake dataset CRS -> WGS84
CRS_TRANSFORMER = Transformer.from_crs(
    "EPSG:7755",
    "EPSG:4326",
    always_xy=True
)


def _to_wgs84(geometry):
    return transform(
        CRS_TRANSFORMER.transform,
        geometry
    )


def _submit_polygon(polygon, year):
    polygon_geojson = mapping(polygon)

    params = {
        "dataset": "wpgppop",
        "year": year,
        "geojson": json.dumps(
            polygon_geojson,
            separators=(",", ":")
        ),
        "runasync": "true"
    }

    response = requests.get(
        WORLDPOP_STATS_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    if result.get("error"):
        raise RuntimeError(
            result.get("error_message") or "WorldPop request failed"
        )

    task_id = result.get("taskid")

    if not task_id:
        raise RuntimeError("WorldPop task ID not returned")

    return task_id


def _wait_for_task(task_id, timeout=90):
    start = time.time()

    while time.time() - start < timeout:
        response = requests.get(
            f"{WORLDPOP_TASK_URL}/{task_id}",
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        if result.get("status") == "finished":

            if result.get("error"):
                raise RuntimeError(
                    result.get("error_message")
                    or "WorldPop task failed"
                )

            data = result.get("data", {})
            population = data.get("total_population")

            if population is None:
                raise RuntimeError(
                    "WorldPop result does not contain total_population"
                )

            return float(population)

        time.sleep(2)

    raise TimeoutError(
        f"WorldPop task timed out: {task_id}"
    )


def get_population_for_polygon(geojson, year=2020, timeout=90):
    """
    Get WorldPop population for Polygon or MultiPolygon GeoJSON.

    The GLOF-SAFE lake dataset uses EPSG:7755.
    Geometry is converted to WGS84 before sending to WorldPop.
    """

    geometry = shape(geojson)

    # Convert real lake geometry from EPSG:7755 to EPSG:4326
    geometry = _to_wgs84(geometry)

    if geometry.geom_type == "Polygon":
        polygons = [geometry]

    elif geometry.geom_type == "MultiPolygon":
        polygons = list(geometry.geoms)

    else:
        raise ValueError(
            f"Unsupported geometry type: {geometry.geom_type}"
        )

    total_population = 0.0
    task_ids = []

    for polygon in polygons:

        if polygon.is_empty:
            continue

        task_id = _submit_polygon(
            polygon,
            year
        )

        task_ids.append(task_id)

        population = _wait_for_task(
            task_id,
            timeout=timeout
        )

        total_population += population

    return {
        "status": "WORLDPOP_SUCCESS",
        "dataset": "wpgppop",
        "year": year,
        "total_population": round(
            total_population,
            2
        ),
        "polygon_count": len(polygons),
        "taskids": task_ids
    }
