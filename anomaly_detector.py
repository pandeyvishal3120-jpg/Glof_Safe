"""
anomaly_detector.py

Simple statistical anomaly detector for glacial lake sensor readings.

Flags a reading as anomalous when the water level jumps abnormally fast
between two consecutive readings, or when seismic activity spikes at the
same time - the classic early-warning combination for a possible moraine
or ice-dam failure event. This is intentionally simple (threshold + delta
based) so it runs instantly with no training data, which suits a live
demo; it can be swapped for a trained model later without changing the
function signature main.py relies on.
"""

from typing import Dict, Union

Number = Union[int, float]

# Thresholds tuned for demo purposes.
WATER_JUMP_WARNING_M = 1.0
WATER_JUMP_CRITICAL_M = 2.5
SEISMIC_WARNING = 3.0
SEISMIC_CRITICAL = 4.0


def detect_anomaly(
    water_level: Number,
    previous_water_level: Number,
    seismic_value: Number,
) -> Dict[str, object]:
    """
    Compare the current sensor reading against the previous one and flag
    anomalies caused by a sudden water-level jump and/or a seismic spike.
    """

    water_level_delta = round(water_level - previous_water_level, 3)
    abs_delta = abs(water_level_delta)

    reasons = []
    severity = "NONE"

    if abs_delta >= WATER_JUMP_CRITICAL_M:
        reasons.append("Sudden large change in water level")
        severity = "CRITICAL"
    elif abs_delta >= WATER_JUMP_WARNING_M:
        reasons.append("Unusually fast change in water level")
        severity = "WARNING"

    if seismic_value >= SEISMIC_CRITICAL:
        reasons.append("Severe seismic activity detected")
        severity = "CRITICAL"
    elif seismic_value >= SEISMIC_WARNING:
        reasons.append("Elevated seismic activity detected")
        if severity == "NONE":
            severity = "WARNING"

    is_anomaly = severity != "NONE"

    return {
        "is_anomaly": is_anomaly,
        "severity": severity,
        "water_level": water_level,
        "previous_water_level": previous_water_level,
        "water_level_delta": water_level_delta,
        "seismic_value": seismic_value,
        "reasons": reasons,
        "model": "GLOF-SAFE statistical anomaly detector v0.1",
    }
