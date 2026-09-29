import numpy as np
import rasterio
import pystac_client
import planetary_computer

from datetime import datetime, timedelta, timezone
from rasterio.windows import Window
from rasterio.warp import transform


STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"


def search_scene(lat, lon, start_date, end_date):
    d = 0.05

    try:
        catalog = pystac_client.Client.open(STAC_URL)

        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=[lon - d, lat - d, lon + d, lat + d],
            datetime=f"{start_date.isoformat()}/{end_date.isoformat()}",
            query={"eo:cloud_cover": {"lt": 30}},
            max_items=20,
            sortby=[{"field": "datetime", "direction": "desc"}]
        )

        items = list(search.items())

    except Exception as error:
        return {
            "status": "SATELLITE_UNAVAILABLE",
            "error": str(error)
        }

    if not items:
        return None

    return items[0]


def ndwi_from_scene(scene, lat, lon):

    try:
        green_asset = scene.assets.get("B03")
        nir_asset = scene.assets.get("B08")

        if not green_asset or not nir_asset:
            return {
                "status": "BANDS_NOT_AVAILABLE",
                "scene_id": scene.id
            }

        green_url = planetary_computer.sign(
            green_asset
        ).href

        nir_url = planetary_computer.sign(
            nir_asset
        ).href

        with rasterio.Env(
            GDAL_HTTP_MULTIRANGE="YES",
            GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
            GDAL_HTTP_VERSION="2"
        ):

            with rasterio.open(green_url) as src:

                # Convert WGS84 lake coordinate into the
                # Sentinel-2 raster CRS.
                x, y = transform(
                    "EPSG:4326",
                    src.crs,
                    [lon],
                    [lat]
                )

                lake_x = x[0]
                lake_y = y[0]

                row, col = src.index(
                    lake_x,
                    lake_y
                )

                # Larger AOI: approximately 5.12 km x 5.12 km
                # for a 10 m Sentinel-2 band.
                size = 128

                col_start = max(
                    0,
                    col - size // 2
                )

                row_start = max(
                    0,
                    row - size // 2
                )

                width = min(
                    size,
                    src.width - col_start
                )

                height = min(
                    size,
                    src.height - row_start
                )

                if width <= 0 or height <= 0:
                    return {
                        "status": "AOI_OUTSIDE_RASTER",
                        "scene_id": scene.id
                    }

                window = Window(
                    col_start,
                    row_start,
                    width,
                    height
                )

                green_data = src.read(
                    1,
                    window=window
                ).astype("float32")

                transform_window = src.window_transform(
                    window
                )

            with rasterio.open(nir_url) as src:

                nir_data = src.read(
                    1,
                    window=window
                ).astype("float32")

        denominator = green_data + nir_data

        ndwi = np.divide(
            green_data - nir_data,
            denominator,
            out=np.zeros_like(green_data),
            where=denominator != 0
        )

        # Sentinel-2 water detection threshold.
        water_mask = ndwi > 0.10

        water_pixels = int(
            np.sum(water_mask)
        )

        pixel_area_m2 = abs(
            transform_window.a *
            transform_window.e
        )

        water_area_km2 = (
            water_pixels *
            pixel_area_m2
        ) / 1_000_000

        return {
            "status": "SUCCESS",
            "scene_id": scene.id,
            "acquisition_date": scene.properties.get(
                "datetime"
            ),
            "cloud_cover": scene.properties.get(
                "eo:cloud_cover"
            ),
            "water_pixels": water_pixels,
            "water_area_km2": round(
                water_area_km2,
                6
            ),
            "aoi_pixels": int(
                width * height
            ),
            "pixel_area_m2": round(
                pixel_area_m2,
                4
            )
        }

    except Exception as error:

        return {
            "status": "PROCESSING_ERROR",
            "scene_id": scene.id,
            "error": str(error)
        }


def satellite_damage_assessment(
    lat,
    lon,
    event_date=None,
    before_days=180,
    after_days=30
):

    try:
        # -------------------------------------------------
        # AUTOMATIC MODE
        # No event date -> use latest available scene
        # as POST-EVENT and previous scene as PRE-EVENT.
        # -------------------------------------------------
        if event_date is None:

            now = datetime.now(timezone.utc)

            latest_scene = search_scene(
                lat,
                lon,
                now - timedelta(days=180),
                now
            )

            if isinstance(latest_scene, dict):
                return latest_scene

            if not latest_scene:
                return {
                    "status": "NO_LATEST_SATELLITE_SCENE"
                }

            event_date = latest_scene.datetime

            post_scene = latest_scene

            # Search only before the latest scene.
            pre_scene = search_scene(
                lat,
                lon,
                event_date - timedelta(days=before_days),
                event_date - timedelta(seconds=1)
            )

        # -------------------------------------------------
        # MANUAL DATE MODE
        # -------------------------------------------------
        else:

            try:
                event_date = datetime.fromisoformat(
                    event_date.replace("Z", "+00:00")
                )

            except Exception as error:
                return {
                    "status": "INVALID_EVENT_DATE",
                    "error": str(error)
                }

            if event_date.tzinfo is None:
                event_date = event_date.replace(
                    tzinfo=timezone.utc
                )

            pre_start = event_date - timedelta(
                days=before_days
            )

            pre_scene = search_scene(
                lat,
                lon,
                pre_start,
                event_date - timedelta(seconds=1)
            )

            if isinstance(pre_scene, dict):
                return pre_scene

            post_end = event_date + timedelta(
                days=after_days
            )

            post_scene = search_scene(
                lat,
                lon,
                event_date,
                post_end
            )

    except Exception as error:
        return {
            "status": "SATELLITE_DAMAGE_PROCESSING_ERROR",
            "error": str(error)
        }

    if isinstance(pre_scene, dict):
        return pre_scene

    if not pre_scene:
        return {
            "status": "NO_PRE_EVENT_SCENE"
        }

    if isinstance(post_scene, dict):
        return post_scene

    if not post_scene:
        return {
            "status": "NO_POST_EVENT_SCENE"
        }

    # -------------------------------------------------
    # NDWI
    # -------------------------------------------------

    pre = ndwi_from_scene(
        pre_scene,
        lat,
        lon
    )

    if pre.get("status") != "SUCCESS":
        return pre

    post = ndwi_from_scene(
        post_scene,
        lat,
        lon
    )

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

        "pre_event_area_km2": round(pre_area, 4),
        "post_event_area_km2": round(post_area, 4),
        "change_area_km2": round(area_change, 4),
        "change_percent": round(change_percent, 2),
        "damage_level": damage_level
    }
