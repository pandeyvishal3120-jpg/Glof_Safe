from datetime import datetime

def send_notification(recipient, message, risk_level):
    # Prototype notification sender.
    # Real SMS provider will be connected later.
    return {
        "status": "NOTIFICATION_QUEUED",
        "channel": "SMS",
        "recipient": recipient["phone"],
        "recipient_name": recipient["name"],
        "risk_level": risk_level,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
