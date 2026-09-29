import requests
import numpy as np
import rasterio
from datetime import datetime, timedelta, timezone
from io import BytesIO

STAC_URL = "https://stac.dataspace.copernicus.eu/v1/search"


def get_scene(lat, lon):
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

    response = requests.post(
        STAC_URL,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    features = response.json().get("features", [])

    if not features:
        return None

    return features[0]


def calculate_area(lat, lon):
    scene = get_scene(lat, lon)

    if not scene:
        return {
            "status": "NO_SATELLITE_SCENE"
        }

    assets = scene.get("assets", {})
    props = scene.get("properties", {})

    green = assets.get("B03_10m")
    nir = assets.get("B08_10m")

    if not green or not nir:
        return {
            "status": "B03_B08_NOT_AVAILABLE",
            "scene_id": scene.get("id")
        }

    green_url = green.get("href")
    nir_url = nir.get("href")

    try:
        green_response = requests.get(
            green_url,
            timeout=120
        )

        nir_response = requests.get(
            nir_url,
            timeout=120
        )

        green_response.raise_for_status()
        nir_response.raise_for_status()

        with rasterio.open(
            BytesIO(green_response.content)
        ) as green_src:

            green_data = green_src.read(1).astype("float32")
            transform = green_src.transform

        with rasterio.open(
            BytesIO(nir_response.content)
        ) as nir_src:

            nir_data = nir_src.read(1).astype("float32")

        denominator = green_data + nir_data

        ndwi = np.divide(
            green_data - nir_data,
            denominator,
            out=np.zeros_like(green_data),
            where=denominator != 0
        )

        water = ndwi > 0.20

        pixel_width = abs(transform.a)
        pixel_height = abs(transform.e)

        pixel_area_m2 = pixel_width * pixel_height

        water_pixels = int(np.sum(water))

        area_m2 = water_pixels * pixel_area_m2
        area_km2 = area_m2 / 1_000_000

        return {
            "status": "SUCCESS",
            "scene_id": scene.get("id"),
            "acquisition_date": props.get("datetime"),
            "cloud_cover": props.get("eo:cloud_cover"),
            "ndwi_threshold": 0.20,
            "water_pixels": water_pixels,
            "pixel_size_m": [
                pixel_width,
                pixel_height
            ],
            "water_area_m2": round(area_m2, 2),
            "water_area_km2": round(area_km2, 6),
            "method": "Sentinel-2 NDWI",
            "source": "Copernicus Sentinel-2 L2A"
        }

    except Exception as error:

        return {
            "status": "PROCESSING_ERROR",
            "scene_id": scene.get("id"),
            "error": str(error)
        }
