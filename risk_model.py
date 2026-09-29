"""
risk_model.py

Lightweight, explainable GLOF risk-scoring model.

This is a rule-weighted scoring model (not a trained ML model) designed to
give sensible, demo-ready outputs for the GLOF-SAFE prototype. It combines
four signals that matter for glacial lake outburst flood risk:

- water_level          : current lake water level (m)
- lake_area             : lake surface area (km^2) - bigger lakes hold more
                          potential outburst volume
- seismic_value         : recent seismic activity near the lake (0-5 scale)
- water_level_change    : short-term rate of change in water level (m)

Each signal contributes a weighted sub-score; sub-scores are combined into
a 0-100 risk_score and mapped to a risk_level. The function signature and
output shape match what main.py's `/risk-score` endpoint expects.
"""

from typing import Dict, Union

Number = Union[int, float]


def _clamp(value: Number, low: Number, high: Number) -> Number:
    return max(low, min(high, value))


def _score_water_level(water_level: Number) -> float:
    # 0-30 points: higher absolute water level = closer to breach threshold
    if water_level >= 68:
        return 30
    if water_level >= 63:
        return 22
    if water_level >= 58:
        return 14
    if water_level >= 50:
        return 7
    return 2


def _score_lake_area(lake_area: Number) -> float:
    # 0-20 points: larger lakes = larger potential outburst volume
    if lake_area >= 1.5:
        return 20
    if lake_area >= 1.0:
        return 15
    if lake_area >= 0.5:
        return 10
    if lake_area >= 0.2:
        return 5
    return 2


def _score_seismic(seismic_value: Number) -> float:
    # 0-25 points: seismic shocks can trigger moraine/ice-dam failure
    if seismic_value >= 4:
        return 25
    if seismic_value >= 3:
        return 18
    if seismic_value >= 2:
        return 11
    if seismic_value >= 1:
        return 5
    return 0


def _score_water_change(water_level_change: Number) -> float:
    # 0-25 points: rapid rise is the strongest short-term warning sign
    if water_level_change >= 3:
        return 25
    if water_level_change >= 2:
        return 18
    if water_level_change >= 1:
        return 10
    if water_level_change >= 0.3:
        return 4
    return 0


def _risk_level(score: float) -> str:
    if score >= 75:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "MEDIUM"
    return "LOW"


def calculate_risk_score(
    water_level: Number,
    lake_area: Number,
    seismic_value: Number,
    water_level_change: Number,
) -> Dict[str, object]:
    """
    Combine lake and sensor signals into a 0-100 GLOF risk score.

    Returns a dict with the numeric score, the categorical risk level,
    and a breakdown of each contributing factor (useful for the dashboard
    and for explaining the "why" behind a score in a demo).
    """

    water_level_score = _score_water_level(water_level)
    lake_area_score = _score_lake_area(lake_area)
    seismic_score = _score_seismic(seismic_value)
    water_change_score = _score_water_change(water_level_change)

    raw_score = (
        water_level_score
        + lake_area_score
        + seismic_score
        + water_change_score
    )

    risk_score = round(_clamp(raw_score, 0, 100), 2)
    risk_level = _risk_level(risk_score)

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "factors": {
            "water_level_score": water_level_score,
            "lake_area_score": lake_area_score,
            "seismic_score": seismic_score,
            "water_change_score": water_change_score,
        },
        "inputs": {
            "water_level": water_level,
            "lake_area": lake_area,
            "seismic_value": seismic_value,
            "water_level_change": water_level_change,
        },
        "model": "GLOF-SAFE rule-weighted risk model v0.1",
    }
