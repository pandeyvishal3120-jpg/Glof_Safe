import numpy as np
import rasterio
import pystac_client
import planetary_computer
from datetime import datetime, timedelta, timezone

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"


def get_latest_scene(lat, lon):
    catalog = pystac_client.Client.open(STAC_URL)

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=180)

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=[lon - 0.02, lat - 0.02, lon + 0.02, lat + 0.02],
        datetime=f"{start.isoformat()}/{now.isoformat()}",
        query={"eo:cloud_cover": {"lt": 30}},
        max_items=10,
        sortby=[{"field": "datetime", "direction": "desc"}],
    )

    items = list(search.items())

    if not items:
        return None

    return items[0]


def calculate_ndwi_area(lat, lon):
    try:
        scene = get_latest_scene(lat, lon)

        if not scene:
            return {
                "status": "NO_SATELLITE_SCENE"
            }

        b03 = scene.assets.get("B03")
        b08 = scene.assets.get("B08")

        if not b03 or not b08:
            return {
                "status": "BANDS_NOT_AVAILABLE",
                "scene_id": scene.id
            }

        green_url = planetary_computer.sign(b03).href
        nir_url = planetary_computer.sign(b08).href

        with rasterio.open(green_url) as green_src:
            green = green_src.read(1).astype("float32")
            transform = green_src.transform

        with rasterio.open(nir_url) as nir_src:
            nir = nir_src.read(1).astype("float32")

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

        return {
            "status": "SUCCESS",
            "scene_id": scene.id,
            "acquisition_date": scene.properties.get("datetime"),
            "cloud_cover": scene.properties.get("eo:cloud_cover"),
            "ndwi_threshold": 0.20,
            "resolution_m": 10,
            "water_pixels": water_pixels,
            "water_area_km2": round(water_area_km2, 6),
            "method": "Sentinel-2 NDWI via Microsoft Planetary Computer",
            "source": "Microsoft Planetary Computer"
        }

    except Exception as error:
        return {
            "status": "SATELLITE_PROCESSING_ERROR",
            "error": str(error)
        }
