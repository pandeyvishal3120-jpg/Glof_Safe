from datetime import datetime


def create_alert(
    risk_level: str,
    lake_name: str = "Glacial Lake"
):
    risk = str(risk_level).upper()

    messages = {
        "CRITICAL": (
            "CRITICAL GLOF WARNING: Immediate evacuation is recommended."
        ),
        "HIGH": (
            "HIGH GLOF RISK: Move to the designated safe zone immediately."
        ),
        "MEDIUM": (
            "MODERATE GLOF RISK: Stay alert and prepare for evacuation."
        ),
        "LOW": (
            "LOW GLOF RISK: Continue monitoring the lake conditions."
        )
    }

    priorities = {
        "CRITICAL": "EMERGENCY",
        "HIGH": "URGENT",
        "MEDIUM": "WARNING",
        "LOW": "ADVISORY"
    }

    return {
        "status": "ALERT_GENERATED",
        "lake_name": lake_name,
        "risk_level": risk,
        "priority": priorities.get(risk, "ADVISORY"),
        "message": messages.get(
            risk,
            "Monitor the glacial lake and follow official instructions."
        ),
        "languages": ["English", "Hindi"],
        "timestamp": datetime.utcnow().isoformat(),
        "recommended_action": (
            "Evacuate immediately"
            if risk in ("HIGH", "CRITICAL")
            else "Continue monitoring"
        )
    }
