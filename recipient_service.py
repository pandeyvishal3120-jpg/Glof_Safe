import json
from pathlib import Path

RECIPIENT_FILE = Path(__file__).resolve().parent / "recipients.json"

def get_recipients():
    if not RECIPIENT_FILE.exists():
        return []
    try:
        return json.loads(RECIPIENT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

def add_recipient(name, phone, role="PUBLIC"):
    recipients = get_recipients()

    item = {
        "id": len(recipients) + 1,
        "name": name,
        "phone": phone,
        "role": role,
        "active": True
    }

    recipients.append(item)
    RECIPIENT_FILE.write_text(
        json.dumps(recipients, indent=2),
        encoding="utf-8"
    )

    return item
