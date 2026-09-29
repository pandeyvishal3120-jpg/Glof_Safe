"""
crowd_intel_gateway.py — Module 5: Multimodal Local Intelligence Gateway

HONEST SCOPE NOTE:
The brief describes NLP + Large Multimodal Models parsing voice notes,
photos, and text. Running a real LMM needs a model/API key this
project doesn't have configured. What's implemented is a genuine,
working rule-based NLP classifier: it scans free-text reports (which
in production would be the output of a speech-to-text step on a voice
note, or a caption on a photo) for hazard-indicating keywords across
weighted categories, scores severity, and stores the result as a
GPS-tagged point ready to plot on the GIS map (`/lakes`-style data).
This is real, tested code - just rule-based instead of a trained LMM.
Swapping in an actual LMM (e.g. via the Anthropic API) for richer
photo/voice understanding is flagged as the natural upgrade path.
"""

from datetime import datetime

from database import SessionLocal
from models import CrowdReport

HAZARD_KEYWORDS = {
    "water_discoloration": {
        "weight": 3,
        "terms": ["discolor", "muddy", "brown water", "murky", "dirty water"],
    },
    "loud_noise": {
        "weight": 3,
        "terms": ["loud noise", "rumbling", "roaring", "explosion sound", "cracking sound"],
    },
    "ground_movement": {
        "weight": 4,
        "terms": ["ground shaking", "landslide", "rockfall", "avalanche", "crack in ground"],
    },
    "rising_water": {
        "weight": 4,
        "terms": ["water rising", "flooding", "flood", "water level rising", "overflow"],
    },
    "ice_lake_change": {
        "weight": 3,
        "terms": ["ice breaking", "lake growing", "glacier moving", "ice melting fast"],
    },
    "distress": {
        "weight": 2,
        "terms": ["help", "emergency", "danger", "evacuate", "scared"],
    },
}


def parse_crowd_report(message: str, latitude: float, longitude: float, has_photo: bool = False):
    """
    Classify a free-text crowd report (transcribed voice note, SMS,
    or photo caption) into hazard categories and a severity score,
    then persist it as a GPS-tagged point.
    """
    text = (message or "").lower()

    matched_tags = []
    score = 0

    for category, config in HAZARD_KEYWORDS.items():
        for term in config["terms"]:
            if term in text:
                matched_tags.append(category)
                score += config["weight"]
                break  # count each category once

    if has_photo:
        score += 2  # visual evidence increases confidence

    if score >= 8:
        severity_level = "CRITICAL"
    elif score >= 5:
        severity_level = "HIGH"
    elif score >= 2:
        severity_level = "MEDIUM"
    else:
        severity_level = "LOW"

    db = SessionLocal()
    try:
        report = CrowdReport(
            latitude=latitude,
            longitude=longitude,
            message=message,
            has_photo=1 if has_photo else 0,
            hazard_tags=",".join(sorted(set(matched_tags))),
            severity_score=float(score),
            severity_level=severity_level,
            timestamp=datetime.utcnow(),
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        report_id = report.id
    finally:
        db.close()

    return {
        "status": "REPORT_PARSED",
        "method": (
            "Rule-based keyword NLP classifier over weighted hazard "
            "categories (proxy for an LMM voice/photo pipeline)"
        ),
        "report_id": report_id,
        "latitude": latitude,
        "longitude": longitude,
        "matched_hazard_tags": sorted(set(matched_tags)),
        "severity_score": score,
        "severity_level": severity_level,
        "future_work": (
            "Route voice notes through speech-to-text and photos "
            "through a vision-capable LMM for richer classification "
            "than keyword matching."
        ),
    }


def get_recent_reports(limit: int = 50):
    db = SessionLocal()
    try:
        reports = (
            db.query(CrowdReport)
            .order_by(CrowdReport.timestamp.desc())
            .limit(limit)
            .all()
        )
    finally:
        db.close()

    return [
        {
            "id": r.id,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "message": r.message,
            "has_photo": bool(r.has_photo),
            "hazard_tags": r.hazard_tags.split(",") if r.hazard_tags else [],
            "severity_score": r.severity_score,
            "severity_level": r.severity_level,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
        }
        for r in reports
    ]
