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
    return items[0] if items else None


def calculate_ndwi_area(lat, lon):
    try:
        scene = get_latest_scene(lat, lon)

        if not scene:
            return {"status": "NO_SATELLITE_SCENE"}

        b03 = scene.assets.get("B03")
        b08 = scene.assets.get("B08")

        if not b03 or not b08:
            return {
                "status": "BANDS_NOT_AVAILABLE",
                "scene_id": scene.id
            }

        green_url = planetary_computer.sign(b03).href
        nir_url = planetary_computer.sign(b08).href

        with rasterio.Env(
            GDAL_HTTP_MULTIRANGE="YES",
            GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
            GDAL_HTTP_VERSION="2"
        ):
            with rasterio.open(green_url) as src:
                row, col = src.index(lon, lat)
                size = 256

                window = rasterio.windows.Window(
                    max(0, col - size // 2),
                    max(0, row - size // 2),
                    size,
                    size
                )

                green = src.read(1, window=window).astype("float32")
                transform = src.window_transform(window)

            with rasterio.open(nir_url) as src:
                nir = src.read(1, window=window).astype("float32")

        denominator = green + nir

        ndwi = np.divide(
            green - nir,
            denominator,
            out=np.zeros_like(green),
            where=denominator != 0
        )

        water_mask = ndwi > 0.10

        pixel_area_m2 = abs(transform.a * transform.e)
        water_pixels = int(np.sum(water_mask))
        water_area_km2 = (
            water_pixels * pixel_area_m2 / 1_000_000
        )

        return {
            "status": "SUCCESS",
            "scene_id": scene.id,
            "acquisition_date": scene.properties.get("datetime"),
            "cloud_cover": scene.properties.get("eo:cloud_cover"),
            "ndwi_threshold": 0.10,
            "resolution_m": 10,
            "water_pixels": water_pixels,
            "water_area_km2": round(water_area_km2, 6),
            "method": "Sentinel-2 NDWI small-window processing",
            "source": "Microsoft Planetary Computer"
        }

    except Exception as error:
        return {
            "status": "SATELLITE_PROCESSING_ERROR",
            "error": str(error)
        }
