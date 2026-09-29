import random

def get_sensor_data():
    water_level = round(random.uniform(50, 70), 2)
    water_change = round(random.uniform(-1, 4), 2)
    seismic = round(random.uniform(0.5, 5.0), 2)

    anomaly = (
        water_change > 3
        or seismic > 4
        or water_level > 65
    )

    return {
        "water_level_m": water_level,
        "water_change_m": water_change,
        "seismic_activity": seismic,
        "anomaly": anomaly,
        "status": "ANOMALY" if anomaly else "NORMAL"
    }
