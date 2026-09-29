from pathlib import Path
import math

import numpy as np
import rasterio

from dem_tile_manager import ensure_dem_tile


DEM_DIR = Path(__file__).resolve().parent / "data" / "dem"


def find_dem_for_location(latitude, longitude):
    try:
        return ensure_dem_tile(latitude, longitude)
    except Exception:
        return None


def terrain_inundation(
    latitude: float,
    longitude: float,
    water_level_increase_m: float = 0.0,
    dem_path: str | None = None,
    radius_km: float = 5.0
):
    dem_file = Path(dem_path) if dem_path else find_dem_for_location(
        latitude,
        longitude
    )

    if dem_file is None or not dem_file.exists():
        return {
            "status": "DEM_UNAVAILABLE",
            "method": "Terrain-aware DEM threshold inundation",
            "message": "No matching DEM tile could be loaded."
        }

    try:
        with rasterio.open(dem_file) as src:
            elevation = src.read(1).astype("float32")
            transform = src.transform
            nodata = src.nodata

            row, col = src.index(longitude, latitude)

            if (
                row < 0 or row >= src.height or
                col < 0 or col >= src.width
            ):
                return {
                    "status": "LOCATION_OUTSIDE_DEM",
                    "dem_file": str(dem_file)
                }

            lake_elevation = float(elevation[row, col])

        if nodata is not None and lake_elevation == nodata:
            return {
                "status": "INVALID_LAKE_ELEVATION",
                "dem_file": str(dem_file)
            }

        water_level_increase_m = max(
            float(water_level_increase_m),
            0.0
        )

        water_surface_elevation = (
            lake_elevation + water_level_increase_m
        )

        pixel_width_deg = abs(transform.a)
        pixel_height_deg = abs(transform.e)

        lat_rad = math.radians(latitude)

        meters_per_degree_lat = 111320.0
        meters_per_degree_lon = 111320.0 * math.cos(lat_rad)

        pixel_width_m = (
            pixel_width_deg * meters_per_degree_lon
        )
        pixel_height_m = (
            pixel_height_deg * meters_per_degree_lat
        )

        radius_lat = radius_km / 111.32
        radius_lon = radius_km / (
            111.32 * max(math.cos(lat_rad), 0.01)
        )

        min_lon = longitude - radius_lon
        max_lon = longitude + radius_lon
        min_lat = latitude - radius_lat
        max_lat = latitude + radius_lat

        row_top, col_left = src.index(min_lon, max_lat)
        row_bottom, col_right = src.index(max_lon, min_lat)

        top = max(0, min(row_top, row_bottom))
        bottom = min(src.height, max(row_top, row_bottom) + 1)
        left = max(0, min(col_left, col_right))
        right = min(src.width, max(col_left, col_right) + 1)

        if top >= bottom or left >= right:
            return {
                "status": "LOCAL_DEM_WINDOW_EMPTY",
                "dem_file": str(dem_file)
            }

        with rasterio.open(dem_file) as src:
            local = src.read(
                1,
                window=((top, bottom), (left, right))
            ).astype("float32")

        if nodata is not None:
            valid = local != nodata
        else:
            valid = np.isfinite(local)

        flooded = valid & (
            local <= water_surface_elevation
        )

        flooded_pixels = int(np.sum(flooded))

        pixel_area_m2 = (
            pixel_width_m * pixel_height_m
        )

        inundation_area_km2 = (
            flooded_pixels * pixel_area_m2
        ) / 1_000_000

        valid_values = local[valid]

        return {
            "status": "DEM_INUNDATION_CALCULATED",
            "method": "Terrain-aware DEM threshold inundation",
            "dem_file": str(dem_file),
            "latitude": round(float(latitude), 6),
            "longitude": round(float(longitude), 6),
            "lake_elevation_m": round(lake_elevation, 2),
            "water_level_increase_m": round(
                water_level_increase_m, 2
            ),
            "water_surface_elevation_m": round(
                water_surface_elevation, 2
            ),
            "analysis_radius_km": radius_km,
            "flooded_pixels": flooded_pixels,
            "pixel_size_m": [
                round(pixel_width_m, 2),
                round(pixel_height_m, 2)
            ],
            "estimated_inundation_area_km2": round(
                inundation_area_km2, 6
            ),
            "local_min_elevation_m": round(
                float(np.min(valid_values)),
                2
            ) if valid_values.size else None,
            "local_max_elevation_m": round(
                float(np.max(valid_values)),
                2
            ) if valid_values.size else None
        }

    except Exception as error:
        return {
            "status": "DEM_PROCESSING_ERROR",
            "error": str(error)
        }
