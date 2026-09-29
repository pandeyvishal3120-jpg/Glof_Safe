"""
transboundary_discharge.py — Module 3: Non-Intrusive Transboundary Tracker

HONEST SCOPE NOTE:
The brief calls for satellite altimetry (e.g. Sentinel-6/ICESat-2 water
surface elevation) combined with SAR-derived river width to infer
discharge without any ground station in the upstream country. We don't
have a live altimetry/SAR-width feed wired in here. What's implemented
is the real hydraulic-engineering technique used when direct gauge data
is unavailable: Manning's equation, driven by a real DEM-derived
channel slope at the point of interest plus a river width (either
measured/estimated from imagery and passed in, or a conservative
default). This produces a genuine, checkable discharge estimate in
m^3/s - it's just not yet fed by live satellite width/altimetry
measurements, which is flagged as the integration point for future
work.

Manning's equation: Q = (1/n) * A_cross * R^(2/3) * S^(1/2)
  n = Manning roughness coefficient
  A_cross = cross-sectional flow area (width * depth)
  R = hydraulic radius (approximated as depth for a wide, shallow channel)
  S = channel bed slope (dimensionless, from real DEM data)
"""

import math
from pathlib import Path

import numpy as np
import rasterio

from dem_tile_manager import ensure_dem_tile

DEFAULT_MANNING_N = 0.035  # natural gravel/cobble river channel
DEFAULT_RIVER_WIDTH_M = 25.0
DEFAULT_FLOW_DEPTH_M = 1.5


def _channel_slope(latitude, longitude, sample_offset_deg=0.002):
    """Real bed slope from the bundled DEM: elevation drop over a short
    downstream sample distance."""
    dem_file = ensure_dem_tile(latitude, longitude)

    if dem_file is None or not Path(dem_file).exists():
        return None

    with rasterio.open(dem_file) as src:
        row1, col1 = src.index(longitude, latitude)
        row2, col2 = src.index(
            longitude + sample_offset_deg, latitude - sample_offset_deg
        )

        if not (0 <= row1 < src.height and 0 <= col1 < src.width):
            return None
        if not (0 <= row2 < src.height and 0 <= col2 < src.width):
            row2, col2 = row1, col1

        elev1 = float(src.read(1)[row1, col1])
        elev2 = float(src.read(1)[row2, col2])

        lat_rad = math.radians(latitude)
        horizontal_m = sample_offset_deg * 111320.0 * math.sqrt(
            1 + math.cos(lat_rad) ** 2
        )

        if horizontal_m <= 0:
            return None

        drop_m = elev1 - elev2
        slope = abs(drop_m) / horizontal_m

        return {
            "slope": max(slope, 0.0001),
            "elevation_m": elev1,
            "sample_drop_m": round(drop_m, 2),
        }


def estimate_discharge(
    latitude,
    longitude,
    river_width_m=None,
    flow_depth_m=None,
    manning_n=DEFAULT_MANNING_N,
):
    """
    Estimate cross-border river discharge (m^3/s) at a point using
    Manning's equation, driven by real DEM channel slope.
    """
    river_width_m = river_width_m or DEFAULT_RIVER_WIDTH_M
    flow_depth_m = flow_depth_m or DEFAULT_FLOW_DEPTH_M

    slope_info = _channel_slope(latitude, longitude)

    if slope_info is None:
        return {
            "status": "DEM_UNAVAILABLE",
            "message": "Could not derive channel slope for this point.",
        }

    slope = slope_info["slope"]

    cross_section_area = river_width_m * flow_depth_m
    hydraulic_radius = (
        cross_section_area / (river_width_m + 2 * flow_depth_m)
    )

    discharge_m3s = (
        (1 / manning_n)
        * cross_section_area
        * (hydraulic_radius ** (2 / 3))
        * (slope ** 0.5)
    )

    return {
        "status": "DISCHARGE_ESTIMATED",
        "method": (
            "Manning's equation with DEM-derived channel slope "
            "(proxy for satellite altimetry + SAR river-width fusion)"
        ),
        "latitude": latitude,
        "longitude": longitude,
        "assumed_river_width_m": river_width_m,
        "assumed_flow_depth_m": flow_depth_m,
        "manning_roughness_n": manning_n,
        "channel_slope": round(slope, 5),
        "estimated_discharge_m3_per_s": round(discharge_m3s, 2),
        "future_work": (
            "Feed river_width_m from Sentinel-1 SAR water-extent "
            "measurements and flow_depth_m from satellite altimetry "
            "(e.g. Sentinel-6/ICESat-2) instead of assumed defaults."
        ),
    }


def detect_upstream_release(discharge_series_m3s):
    """
    Statistical spike detection (z-score) over a short discharge time
    series to flag a sudden upstream dam release or ice-dam burst
    without needing any upstream ground station.
    """
    values = [float(v) for v in discharge_series_m3s if v is not None]

    if len(values) < 4:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": "Need at least 4 discharge readings.",
        }

    latest = values[-1]
    history = values[:-1]

    mean = sum(history) / len(history)
    variance = sum((v - mean) ** 2 for v in history) / len(history)
    std_dev = math.sqrt(variance) if variance > 0 else 1e-6

    z_score = (latest - mean) / std_dev

    if z_score >= 4:
        severity = "CRITICAL"
    elif z_score >= 3:
        severity = "HIGH"
    elif z_score >= 2:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    return {
        "status": "ANALYZED",
        "method": "Z-score anomaly detection on discharge time series",
        "latest_discharge_m3s": round(latest, 2),
        "baseline_mean_m3s": round(mean, 2),
        "baseline_std_m3s": round(std_dev, 2),
        "z_score": round(z_score, 2),
        "is_sudden_release": z_score >= 2,
        "severity": severity,
    }
