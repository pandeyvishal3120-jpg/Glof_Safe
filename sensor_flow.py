import sys
from pathlib import Path

ML_PATH = Path(__file__).resolve().parent.parent / "ml"
sys.path.append(str(ML_PATH))

from sensor_simulator import get_sensor_data
from anomaly_detector import detect_anomaly
from risk_engine import calculate_risk


def process_sensor_flow():
    sensor = get_sensor_data()

    previous_water_level = (
        sensor["water_level_m"] - sensor["water_change_m"]
    )

    anomaly = detect_anomaly(
        water_level=sensor["water_level_m"],
        previous_water_level=previous_water_level,
        seismic_value=sensor["seismic_activity"]
    )

    risk = calculate_risk(
        sensor["water_level_m"],
        sensor["water_change_m"],
        sensor["seismic_activity"]
    )

    return {
        "water_level_m": sensor["water_level_m"],
        "water_change_m": sensor["water_change_m"],
        "seismic_activity": sensor["seismic_activity"],
        "anomaly": anomaly.get("anomaly", False),
        "anomaly_status": anomaly.get("severity", "Normal"),
        "risk_score": risk.get("risk_score"),
        "risk_level": risk.get("risk_level")
    }
