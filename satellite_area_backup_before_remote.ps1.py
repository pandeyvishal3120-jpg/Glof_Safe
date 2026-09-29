import requests
import numpy as np
import rasterio
from io import BytesIO
from datetime import datetime, timedelta, timezone

import pystac_client
import planetary_computer

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"


def get_latest_scene(lat, lon):
    catalog = pystac_client.Client.open(STAC_URL)

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=180)

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=[lon - 0.05, lat - 0.05, lon + 0.05, lat + 0.05],
        datetime=f"{start.isoformat()}/{now.isoformat()}",
        query={"eo:cloud_cover": {"lt": 30}},
        max_items=10,
        sortby=[{"field": "datetime", "direction": "desc"}],
    )

    items = list(search.items())

    if not items:
        return None

    return items[0]


def download_band(asset):
    signed = planetary_computer.sign(asset)

    response = requests.get(
        signed.href,
        timeout=120
    )

    response.raise_for_status()

    return response.content


def calculate_ndwi_area(lat, lon):
    try:
        scene = get_latest_scene(lat, lon)

        if not scene:
            return {
                "status": "NO_SATELLITE_SCENE"
            }

        assets = scene.assets

        green_asset = assets.get("B03")
        nir_asset = assets.get("B08")

        if not green_asset or not nir_asset:
            return {
                "status": "BANDS_NOT_AVAILABLE",
                "scene_id": scene.id
            }

        green_bytes = download_band(green_asset)
        nir_bytes = download_band(nir_asset)

        with rasterio.open(BytesIO(green_bytes)) as src:
            green = src.read(1).astype("float32")
            transform = src.transform

        with rasterio.open(BytesIO(nir_bytes)) as src:
            nir = src.read(1).astype("float32")

        denominator = green + nir

        ndwi = np.divide(
            green - nir,
            denominator,
            out=np.zeros_like(green),
            where=denominator != 0
        )

        water_mask = ndwi > 0.20

        pixel_width = abs(transform.a)
        pixel_height = abs(transform.e)

        pixel_area_m2 = pixel_width * pixel_height

        water_pixels = int(np.sum(water_mask))

        water_area_m2 = water_pixels * pixel_area_m2
        water_area_km2 = water_area_m2 / 1_000_000

        props = scene.properties

        return {
            "status": "SUCCESS",
            "scene_id": scene.id,
            "acquisition_date": props.get("datetime"),
            "cloud_cover": props.get("eo:cloud_cover"),
            "method": "Sentinel-2 NDWI via Microsoft Planetary Computer",
            "ndwi_threshold": 0.20,
            "resolution_m": 10,
            "water_pixels": water_pixels,
            "pixel_area_m2": round(pixel_area_m2, 4),
            "water_area_m2": round(water_area_m2, 2),
            "water_area_km2": round(water_area_km2, 6),
            "source": "Microsoft Planetary Computer - Sentinel-2 L2A"
        }

    except requests.RequestException as error:
        return {
            "status": "SATELLITE_DATA_UNAVAILABLE",
            "error": str(error)
        }

    except Exception as error:
        return {
            "status": "PROCESSING_ERROR",
            "error": str(error)
        }
def download_band(asset):
    import rasterio
    signed = planetary_computer.sign(asset)
    return signed.href
