"""
climate_projection.py — Module 9: Spatio-Temporal Climate Transformer

HONEST SCOPE NOTE:
Training a Vision Transformer + time-series model on 30 years of
satellite retreat data, permafrost thaw rates, and IPCC projections
needs a large curated dataset and training infrastructure this
project doesn't have. What's implemented instead is a genuine
statistical time-series forecast: polynomial regression (numpy
polyfit) over whatever historical (year, lake area) observations are
available, extrapolated out to a target year, with an honestly
reported confidence band derived from the fit's own residuals rather
than a fabricated number. It's a real, working forecast - just a
classical statistical model standing in for a transformer until a
proper training dataset exists.
"""

import numpy as np


def project_lake_growth(years, lake_area_km2, target_year=2035):
    """
    Fit a degree-2 polynomial to historical (year, area) observations
    and extrapolate to target_year, with a residual-based confidence
    band.
    """
    years = np.array([float(y) for y in years])
    areas = np.array([float(a) for a in lake_area_km2])

    if len(years) < 3:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": "Need at least 3 historical (year, area) points to fit a trend.",
        }

    degree = 2 if len(years) >= 4 else 1

    coeffs = np.polyfit(years, areas, degree)
    poly = np.poly1d(coeffs)

    fitted = poly(years)
    residuals = areas - fitted
    residual_std = float(np.std(residuals)) if len(residuals) > 1 else 0.0

    projected_area = float(poly(target_year))
    years_ahead = target_year - float(years[-1])

    # Confidence band widens with extrapolation distance - a simple,
    # honest way to signal growing uncertainty the further out we project.
    band_width = residual_std * (1 + 0.15 * max(years_ahead, 0))

    baseline_area = float(areas[-1])
    growth_percent = (
        ((projected_area - baseline_area) / baseline_area) * 100
        if baseline_area > 0 else 0
    )

    if growth_percent >= 30:
        outlook = "MAJOR_EXPANSION_EXPECTED"
    elif growth_percent >= 10:
        outlook = "MODERATE_EXPANSION_EXPECTED"
    elif growth_percent <= -10:
        outlook = "CONTRACTION_EXPECTED"
    else:
        outlook = "RELATIVELY_STABLE"

    return {
        "status": "PROJECTION_GENERATED",
        "method": (
            f"Degree-{degree} polynomial regression on historical "
            "lake-area observations (statistical proxy for a trained "
            "Spatio-Temporal Transformer)"
        ),
        "historical_years": years.tolist(),
        "historical_area_km2": areas.tolist(),
        "target_year": target_year,
        "projected_area_km2": round(projected_area, 4),
        "projected_area_lower_km2": round(projected_area - band_width, 4),
        "projected_area_upper_km2": round(projected_area + band_width, 4),
        "growth_percent_vs_latest_observation": round(growth_percent, 2),
        "outlook": outlook,
        "future_work": (
            "Replace with a Vision Transformer + time-series model "
            "trained on 30 years of satellite retreat data, permafrost "
            "thaw rates, and IPCC projections once that dataset is "
            "assembled."
        ),
    }
