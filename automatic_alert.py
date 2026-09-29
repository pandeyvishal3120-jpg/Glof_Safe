from alert_service import create_alert
from recipient_service import get_recipients
from notification_service import send_notification

def automatic_alert_check(lake_name, risk_level):

    risk_level = str(risk_level).upper()

    if risk_level not in ["HIGH", "CRITICAL"]:
        return {
            "status": "NO_ALERT",
            "risk_level": risk_level,
            "notifications_sent": 0
        }

    alert = create_alert(
        risk_level=risk_level,
        lake_name=lake_name
    )

    recipients = [
        r for r in get_recipients()
        if r.get("active", True)
    ]

    notifications = []

    for recipient in recipients:
        notifications.append(
            send_notification(
                recipient=recipient,
                message=alert["message"],
                risk_level=risk_level
            )
        )

    return {
        "status": "AUTOMATIC_ALERT_TRIGGERED",
        "lake_name": lake_name,
        "risk_level": risk_level,
        "alert": alert,
        "recipient_count": len(recipients),
        "notifications": notifications
    }
