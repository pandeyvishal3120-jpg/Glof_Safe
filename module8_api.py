from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional

from damage_proxy_map import generate_damage_proxy_map
from constrained_route_planner import plan_constrained_route

router = APIRouter(prefix="/module8", tags=["Module 8 - Damage Mapping & Route AI"])


@router.get("/damage-proxy-map")
def get_damage_proxy_map(
    latitude: float,
    longitude: float,
    pre_event_area_km2: float,
    post_event_area_km2: float,
):
    return generate_damage_proxy_map(
        latitude, longitude, pre_event_area_km2, post_event_area_km2
    )


class ConstrainedRouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    blocked_points: Optional[List[Dict[str, float]]] = None


@router.post("/route-replan")
def post_route_replan(payload: ConstrainedRouteRequest):
    return plan_constrained_route(
        payload.start_lat,
        payload.start_lon,
        payload.end_lat,
        payload.end_lon,
        payload.blocked_points,
    )
