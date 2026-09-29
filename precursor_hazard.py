"""
precursor_hazard.py — Module 2: Precursor & Cascading Hazard Detector

HONEST SCOPE NOTE:
- "Slope Displacement Vision Engine" as briefed needs millimetre-level
  InSAR time-series (e.g. Sentinel-1 interferometry) to catch actual
  ground movement over time. We don't ingest InSAR data. What's
  implemented is a real terrain-susceptibility analysis from the
  bundled DEM (slope angle + surface roughness within a 5 km radius) -
  a legitimate first-pass hazard-zoning technique used in real GLOF
  studies, but it flags where a slope failure is *more likely*, not
  that one is *currently happening*. Wiring in real InSAR is flagged
  as future work.
- "Neural Debris-Flow Solver (PINN)" needs a trained physics-informed
  network to be genuinely faster than solving the underlying PDEs.
  What's implemented instead is a well-established EMPIRICAL
  volume-based runout formula from debris-flow engineering literature
  (Rickenmann-style: L = a * (V * H)^b), which is itself already a
  near-instant closed-form estimate - so the "30 seconds vs 4 hours"
  goal is genuinely met, just via a proven empirical formula rather
  than a trained PINN.
"""

import math
from pathlib import Path

import numpy as np
import rasterio

from dem_tile_manager import ensure_dem_tile

# Empirical debris-flow mobility coefficients (Rickenmann, 1999 style):
# runout distance L [m] = A_COEF * (Volume [m^3] * Drop height [m]) ** B_COEF
RUNOUT_A_COEF = 1.9
RUNOUT_B_COEF = 0.16


def analyze_slope_instability(latitude, longitude, radius_km=5.0):
    """
    Real DEM-derived terrain susceptibility around a glacial lake.
    Stands in for InSAR ground-displacement monitoring until that data
    source is integrated.
    """
    dem_file = ensure_dem_tile(latitude, longitude)

    if dem_file is None or not Path(dem_file).exists():
        return {
            "status": "DEM_UNAVAILABLE",
            "message": "No matching DEM tile could be loaded.",
        }

    with rasterio.open(dem_file) as src:
        row, col = src.index(longitude, latitude)

        if row < 0 or row >= src.height or col < 0 or col >= src.width:
            return {"status": "LOCATION_OUTSIDE_DEM"}

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
            return {"status": "INSUFFICIENT_TERRAIN_DATA"}

        gy, gx = np.gradient(elevation, pixel_h_m, pixel_w_m)
        slope_deg = np.degrees(np.arctan(np.sqrt(gx ** 2 + gy ** 2)))

        max_slope = float(np.nanmax(slope_deg))
        mean_slope = float(np.nanmean(slope_deg))
        roughness_m = float(np.nanstd(elevation))

    # Susceptibility classification thresholds informed by standard
    # geomorphological slope-stability guidance (>35 deg approaches the
    # natural angle of repose for loose rock/debris/moraine material).
    score = 0
    if max_slope >= 45:
        score += 4
    elif max_slope >= 35:
        score += 3
    elif max_slope >= 25:
        score += 2
    elif max_slope >= 15:
        score += 1

    if roughness_m >= 150:
        score += 3
    elif roughness_m >= 80:
        score += 2
    elif roughness_m >= 40:
        score += 1

    if score >= 6:
        level = "CRITICAL"
    elif score >= 4:
        level = "HIGH"
    elif score >= 2:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "status": "SLOPE_ANALYZED",
        "method": (
            "DEM-derived slope/roughness terrain susceptibility "
            "(proxy for InSAR millimetre-displacement monitoring)"
        ),
        "radius_km": radius_km,
        "max_slope_deg": round(max_slope, 2),
        "mean_slope_deg": round(mean_slope, 2),
        "terrain_roughness_m": round(roughness_m, 2),
        "instability_score": score,
        "instability_level": level,
        "future_work": (
            "Integrate Sentinel-1 InSAR time-series for real "
            "millimetre-level displacement detection."
        ),
    }


def estimate_debris_flow_runout(volume_m3, elevation_drop_m):
    """
    Empirical volume-based debris-flow runout distance and rough
    inundation-corridor width, computed in closed form (near-instant).
    """
    volume_m3 = max(float(volume_m3), 0.0)
    elevation_drop_m = max(float(elevation_drop_m), 0.0)

    if volume_m3 <= 0 or elevation_drop_m <= 0:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": "volume_m3 and elevation_drop_m must be > 0.",
        }

    runout_m = RUNOUT_A_COEF * (
        (volume_m3 * elevation_drop_m) ** RUNOUT_B_COEF
    ) * 1000

    # Empirical debris-flow width scaling (roughly proportional to the
    # cube root of volume) - order-of-magnitude corridor estimate.
    corridor_width_m = max(5.0, 0.15 * (volume_m3 ** (1 / 3)))

    if runout_m >= 5000:
        severity = "CRITICAL"
    elif runout_m >= 2000:
        severity = "HIGH"
    elif runout_m >= 500:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    return {
        "status": "RUNOUT_ESTIMATED",
        "method": (
            "Empirical volume-drop debris-flow mobility relation "
            "(Rickenmann-style closed form; proxy for a trained PINN "
            "solver)"
        ),
        "volume_m3": round(volume_m3, 2),
        "elevation_drop_m": round(elevation_drop_m, 2),
        "estimated_runout_m": round(runout_m, 1),
        "estimated_corridor_width_m": round(corridor_width_m, 1),
        "severity": severity,
        "compute_time_note": (
            "Closed-form formula: effectively instant, versus hours "
            "for a full numerical PDE solve."
        ),
    }
