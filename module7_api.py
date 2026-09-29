from fastapi import APIRouter

from turbidity_forecaster import analyze_turbidity, forecast_sediment_arrival

router = APIRouter(prefix="/module7", tags=["Module 7 - Silt & Turbidity Forecaster"])


@router.get("/turbidity")
def get_turbidity(latitude: float, longitude: float):
    return analyze_turbidity(latitude, longitude)


@router.get("/sediment-lead-time")
def get_sediment_lead_time(
    distance_km: float,
    flow_velocity_m_s: float,
    turbidity_level: str = "HIGH",
):
    return forecast_sediment_arrival(distance_km, flow_velocity_m_s, turbidity_level)
