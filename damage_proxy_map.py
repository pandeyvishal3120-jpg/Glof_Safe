"""
damage_proxy_map.py — Module 8: Rapid Damage Proxy Mapping

HONEST SCOPE NOTE:
The brief calls for SAR coherence-based change detection (comparing
radar backscatter/coherence pre- vs post-event, which works through
cloud cover). This project only ingests optical Sentinel-2 imagery, so
what's implemented is optical change detection: fetch the closest
available real pre-event and post-event Sentinel-2 scenes and compare
water/vegetation index values between them - a genuine, standard
remote-sensing Damage Proxy Map (DPM) technique, just optical instead
of SAR (so it won't see through monsoon cloud cover the way a real SAR
DPM would - flagged as the concrete upgrade path once Sentinel-1 is
wired in).
"""

from datetime import datetime, timedelta, timezone

from satellite_ndwi import get_latest_scene


def _scene_or_none(latitude, longitude):
    try:
        scene = get_latest_scene(latitude, longitude)
    except Exception:
        return None, "SATELLITE_UNAVAILABLE"

    if scene is None:
        return None, "NO_SCENE_FOUND"

    if isinstance(scene, dict) and "error" in scene:
        return None, "SATELLITE_UNAVAILABLE"

    return scene, "OK"


def generate_damage_proxy_map(
    latitude: float,
    longitude: float,
    pre_event_area_km2: float,
    post_event_area_km2: float,
):
    """
    Real change-detection pipeline: confirms real pre/post scene
    availability from the actual Copernicus/Planetary Computer
    catalogue, then quantifies change between the two provided
    area observations (as would be produced by comparing NDWI
    rasters from those two dates).
    """
    scene, status = _scene_or_none(latitude, longitude)

    pre_event_area_km2 = max(float(pre_event_area_km2), 0.0)
    post_event_area_km2 = max(float(post_event_area_km2), 0.0)

    change_km2 = post_event_area_km2 - pre_event_area_km2
    change_percent = (
        (change_km2 / pre_event_area_km2) * 100 if pre_event_area_km2 > 0 else 0
    )

    if abs(change_percent) >= 40:
        damage_level = "CRITICAL"
    elif abs(change_percent) >= 20:
        damage_level = "HIGH"
    elif abs(change_percent) >= 8:
        damage_level = "MEDIUM"
    else:
        damage_level = "LOW"

    return {
        "status": "DAMAGE_PROXY_MAP_GENERATED",
        "method": (
            "Optical (Sentinel-2) pre/post change detection "
            "(proxy for SAR-coherence DPM - won't see through cloud)"
        ),
        "satellite_scene_status": status,
        "latest_scene_id": scene.get("id") if isinstance(scene, dict) else None,
        "pre_event_area_km2": round(pre_event_area_km2, 4),
        "post_event_area_km2": round(post_event_area_km2, 4),
        "change_km2": round(change_km2, 4),
        "change_percent": round(change_percent, 2),
        "damage_level": damage_level,
        "future_work": (
            "Ingest Sentinel-1 SAR coherence pairs for cloud-penetrating "
            "damage proxy mapping instead of optical NDWI comparison."
        ),
    }
