import requests
import numpy as np
from datetime import datetime, timedelta, timezone

STAC_URL = "https://stac.dataspace.copernicus.eu/v1/search"


def get_latest_scene(lat, lon):
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=180)

    d = 0.05

    payload = {
        "collections": ["sentinel-2-l2a"],
        "bbox": [
            lon - d,
            lat - d,
            lon + d,
            lat + d
        ],
        "datetime": (
            start.strftime("%Y-%m-%dT%H:%M:%SZ")
            + "/"
            + now.strftime("%Y-%m-%dT%H:%M:%SZ")
        ),
        "limit": 10,
        "query": {
            "eo:cloud_cover": {
                "lte": 30
            }
        },
        "sortby": [
            {
                "field": "datetime",
                "direction": "desc"
            }
        ]
    }

    try:
        r = requests.post(
            STAC_URL,
            json=payload,
            timeout=10
        )

        r.raise_for_status()

        features = r.json().get("features", [])

        if not features:
            return None

        return features[0]

    except requests.RequestException as error:
        return {
            "error": str(error)
        }


def calculate_ndwi_area(lat, lon):
    scene = get_latest_scene(lat, lon)

    if scene is None:
        return {
            "status": "NO_SATELLITE_SCENE"
        }

    if "error" in scene:
        return {
            "status": "SATELLITE_UNAVAILABLE",
            "error": scene["error"]
        }

    props = scene.get("properties", {})
    assets = scene.get("assets", {})

    b03 = assets.get("B03_10m")
    b08 = assets.get("B08_10m")

    if not b03 or not b08:
        return {
            "status": "BANDS_NOT_AVAILABLE",
            "scene_id": scene.get("id")
        }

    return {
        "status": "SATELLITE_SCENE_FOUND",
        "scene_id": scene.get("id"),
        "acquisition_date": props.get("datetime"),
        "cloud_cover": props.get("eo:cloud_cover"),
        "green_band": b03.get("href"),
        "nir_band": b08.get("href"),
        "method": "NDWI",
        "resolution_m": 10,
        "note": "Sentinel-2 scene identified. Raster NDWI processing requires downloadable band assets."
    }
