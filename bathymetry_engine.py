"""
bathymetry_engine.py — Module 1: Physics-Guided Bathymetry Estimator

HONEST SCOPE NOTE:
The brief describes a deep-learning model trained on terrain/slope/bed
topography. Training a real network needs labelled bathymetric survey
data we don't have. What's implemented here instead is the real
technique glaciology studies actually use when no survey exists:
an empirical area-volume scaling relation (Huggel et al., 2002 /
O'Connor et al. lake-volume literature: V ≈ c * A^d for
moraine/ice-dammed lakes), corrected by real DEM-derived terrain
steepness around the lake (steeper surrounding walls -> a deeper
basin for the same surface area; flatter terrain -> shallower).
No field survey is needed - it only needs lake area (already in the
DB) and the bundled DEM tiles.
"""

import math
from pathlib import Path

import numpy as np
import rasterio

from dem_tile_manager import ensure_dem_tile

DEM_DIR = Path(__file__).resolve().parent / "data" / "dem"

# Empirical area-volume coefficients (Huggel et al. 2002 style scaling
# for moraine-dammed glacial lakes): V [m^3] = C * (A [m^2])^D
EMPIRICAL_C = 0.104
EMPIRICAL_D = 1.42


def _surrounding_slope_stats(latitude, longitude, radius_km=1.0):
    """Real terrain steepness around the lake, computed from the bundled
    DEM tiles (numpy gradient over the elevation raster)."""
    dem_file = ensure_dem_tile(latitude, longitude)

    if dem_file is None or not Path(dem_file).exists():
        return None

    with rasterio.open(dem_file) as src:
        row, col = src.index(longitude, latitude)

        if row < 0 or row >= src.height or col < 0 or col >= src.width:
            return None

        lat_rad = math.radians(latitude)
        meters_per_deg_lat = 111320.0
        meters_per_deg_lon = 111320.0 * math.cos(lat_rad)

        pixel_h_m = abs(src.transform.e) * meters_per_deg_lat
        pixel_w_m = abs(src.transform.a) * meters_per_deg_lon

        half_px_rows = max(1, int((radius_km * 1000) / max(pixel_h_m, 1)))
        half_px_cols = max(1, int((radius_km * 1000) / max(pixel_w_m, 1)))

        row_start = max(0, row - half_px_rows)
        row_stop = min(src.height, row + half_px_rows)
        col_start = max(0, col - half_px_cols)
        col_stop = min(src.width, col + half_px_cols)

        window = rasterio.windows.Window(
            col_start, row_start,
            col_stop - col_start, row_stop - row_start
        )
        elevation = src.read(1, window=window).astype("float32")

        nodata = src.nodata
        if nodata is not None:
            elevation = np.where(elevation == nodata, np.nan, elevation)

        if np.all(np.isnan(elevation)) or elevation.size < 4:
            return None

        gy, gx = np.gradient(elevation, pixel_h_m, pixel_w_m)
        slope_deg = np.degrees(np.arctan(np.sqrt(gx ** 2 + gy ** 2)))

        return {
            "mean_slope_deg": float(np.nanmean(slope_deg)),
            "max_slope_deg": float(np.nanmax(slope_deg)),
            "elevation_range_m": float(
                np.nanmax(elevation) - np.nanmin(elevation)
            ),
            "dem_file": str(dem_file),
        }


def estimate_bathymetry(latitude, longitude, area_km2):
    """
    Estimate glacial lake depth/volume without a field survey.

    Returns mean depth (m), estimated volume (m^3 and million m^3),
    and the terrain-based correction factor applied, with the DEM
    evidence used so the number is explainable rather than a black box.
    """
    area_km2 = max(float(area_km2), 0.0)

    if area_km2 <= 0:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": "Lake area must be greater than zero.",
        }

    area_m2 = area_km2 * 1_000_000

    base_volume_m3 = EMPIRICAL_C * (area_m2 ** EMPIRICAL_D)

    terrain = _surrounding_slope_stats(latitude, longitude)

    if terrain is not None:
        # Steeper surrounding basin walls -> deeper basin for the same
        # surface area. Correction factor is a bounded, monotonic
        # function of mean slope so it never runs away to absurd values.
        slope = terrain["mean_slope_deg"]
        correction = 1.0 + min(max(slope - 15.0, -10.0), 25.0) / 100.0
        correction = max(0.5, min(correction, 1.6))
    else:
        correction = 1.0

    volume_m3 = base_volume_m3 * correction
    mean_depth_m = volume_m3 / area_m2

    return {
        "status": "BATHYMETRY_ESTIMATED",
        "method": (
            "Empirical area-volume scaling (V = C * A^D, "
            "moraine-dammed lake calibration) corrected by "
            "DEM-derived surrounding slope"
        ),
        "area_km2": round(area_km2, 4),
        "estimated_mean_depth_m": round(mean_depth_m, 2),
        "estimated_volume_million_m3": round(volume_m3 / 1_000_000, 4),
        "terrain_correction_factor": round(correction, 3),
        "terrain_evidence": terrain,
        "disclaimer": (
            "Estimate only - no field bathymetric survey performed. "
            "Suitable for triage/prioritisation, not engineering design."
        ),
    }
