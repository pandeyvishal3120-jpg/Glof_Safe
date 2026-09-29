def calculate_evacuation(risk_level):
    if risk_level == "CRITICAL":
        return {
            "status": "EVACUATE NOW",
            "safe_zone": "High Ground Zone A",
            "route": "Route A → Bridge → High Ground Zone A",
            "estimated_time_min": 12
        }

    if risk_level == "HIGH":
        return {
            "status": "PREPARE TO EVACUATE",
            "safe_zone": "High Ground Zone B",
            "route": "Route B → Main Road → High Ground Zone B",
            "estimated_time_min": 18
        }

    if risk_level == "MEDIUM":
        return {
            "status": "STAY ALERT",
            "safe_zone": "Community Safe Zone",
            "route": "Route C → Community Safe Zone",
            "estimated_time_min": 25
        }

    return {
        "status": "SAFE",
        "safe_zone": "Local Safe Area",
        "route": "No evacuation required",
        "estimated_time_min": 0
    }


def create_alert(risk_level):
    messages = {
        "CRITICAL": "CRITICAL GLOF ALERT: Evacuate immediately to higher ground.",
        "HIGH": "HIGH GLOF RISK: Prepare for evacuation and follow official instructions.",
        "MEDIUM": "GLOF WATCH: Stay alert and monitor official updates.",
        "LOW": "GLOF STATUS: Normal. Continue routine monitoring."
    }

    return {
        "risk_level": risk_level,
        "message": messages.get(risk_level, messages["LOW"]),
        "languages": ["English", "Hindi"]
    }
