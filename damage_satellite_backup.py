import requests
import numpy as np
import rasterio
from io import BytesIO
from datetime import datetime, timedelta, timezone


STAC_URL = "https://stac.dataspace.copernicus.eu/v1/search"


def search_scene(lat, lon, start_date, end_date):
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
            start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            + "/"
            + end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        ),
        "limit": 20,
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
            timeout=30
        )
        r.raise_for_status()
        features = r.json().get("features", [])

    except requests.RequestException as error:
        return {
            "status": "SATELLITE_UNAVAILABLE",
            "error": str(error)
        }

    if not features:
        return None

    return features[0]


def ndwi_from_scene(scene):
    assets = scene.get("assets", {})

    green = assets.get("B03_10m")
    nir = assets.get("B08_10m")

    if not green or not nir:
        return {
            "status": "BANDS_NOT_AVAILABLE",
            "scene_id": scene.get("id")
        }

    try:
        green_response = requests.get(
            green["href"],
            timeout=60
        )
        nir_response = requests.get(
            nir["href"],
            timeout=60
        )

        green_response.raise_for_status()
        nir_response.raise_for_status()

        with rasterio.open(
            BytesIO(green_response.content)
        ) as src:
            green_data = src.read(1).astype("float32")
            transform = src.transform

        with rasterio.open(
            BytesIO(nir_response.content)
        ) as src:
            nir_data = src.read(1).astype("float32")

        denominator = green_data + nir_data

        ndwi = np.divide(
            green_data - nir_data,
            denominator,
            out=np.zeros_like(green_data),
            where=denominator != 0
        )

        water_mask = ndwi > 0.20

        pixel_area_m2 = abs(
            transform.a * transform.e
        )

        water_pixels = int(
            np.sum(water_mask)
        )

        water_area_km2 = (
            water_pixels * pixel_area_m2
        ) / 1_000_000

        return {
            "status": "SUCCESS",
            "scene_id": scene.get("id"),
            "acquisition_date": scene.get(
                "properties", {}
            ).get("datetime"),
            "cloud_cover": scene.get(
                "properties", {}
            ).get("eo:cloud_cover"),
            "water_area_km2": round(
                water_area_km2,
                6
            )
        }

    except Exception as error:
        return {
            "status": "PROCESSING_ERROR",
            "scene_id": scene.get("id"),
            "error": str(error)
        }


def satellite_damage_assessment(
    lat,
    lon,
    event_date,
    before_days=180,
    after_days=30
):
    event_date = datetime.fromisoformat(
        event_date.replace("Z", "+00:00")
    )

    if event_date.tzinfo is None:
        event_date = event_date.replace(
            tzinfo=timezone.utc
        )

    # Pre-event observation
    pre_start = event_date - timedelta(
        days=before_days
    )

    pre_scene = search_scene(
        lat,
        lon,
        pre_start,
        event_date
    )

    if pre_scene and pre_scene.get("status") == "SATELLITE_UNAVAILABLE":
        return pre_scene

    if not pre_scene:
        return {
            "status": "NO_PRE_EVENT_SCENE"
        }

    # Post-event observation
    post_end = event_date + timedelta(
        days=after_days
    )

    post_scene = search_scene(
        lat,
        lon,
        event_date,
        post_end
    )

    if post_scene and post_scene.get("status") == "SATELLITE_UNAVAILABLE":
        return post_scene

    if not post_scene:
        return {
            "status": "NO_POST_EVENT_SCENE"
        }

    pre = ndwi_from_scene(pre_scene)
    post = ndwi_from_scene(post_scene)

    if pre.get("status") != "SUCCESS":
        return pre

    if post.get("status") != "SUCCESS":
        return post

    pre_area = pre["water_area_km2"]
    post_area = post["water_area_km2"]

    area_change = abs(
        post_area - pre_area
    )

    if pre_area > 0:
        change_percent = (
            area_change / pre_area
        ) * 100
    else:
        change_percent = 0

    if change_percent >= 50:
        damage_level = "CRITICAL"
    elif change_percent >= 25:
        damage_level = "HIGH"
    elif change_percent >= 10:
        damage_level = "MEDIUM"
    else:
        damage_level = "LOW"

    return {
        "status": "SATELLITE_DAMAGE_ASSESSED",
        "method": "Sentinel-2 pre/post NDWI comparison",
        "pre_event": pre,
        "post_event": post,
        "pre_event_area_km2": pre_area,
        "post_event_area_km2": post_area,
        "change_area_km2": round(
            area_change,
            6
        ),
        "change_percent": round(
            change_percent,
            2
        ),
        "damage_level": damage_level
    }
