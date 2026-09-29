"""
cap_generator.py — Module 4: Autonomous CAP Generator

Generates a genuinely valid OASIS Common Alerting Protocol (CAP) v1.2
XML alert - the real standard consumed by siren networks, cell
broadcast (IPAWS/NDMA-style) systems, and emergency dashboards. No ML
"agentic" reasoning is needed for this half of the module; the value is
producing a compliant, machine-actionable alert automatically the
moment a risk threshold is breached, instead of waiting on a human to
manually draft one.

The "bypasses human bureaucracy" framing in the brief means: this
function is called directly and automatically from the alerting
pipeline (see automatic_alert.py / alert_service.py) - no manual
sign-off step sits in between threshold breach and CAP generation.
"""

import uuid
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

CAP_NAMESPACE = "urn:oasis:names:tc:emergency:cap:1.2"

RISK_TO_CAP = {
    "LOW": {"urgency": "Past", "severity": "Minor", "certainty": "Possible"},
    "MEDIUM": {"urgency": "Expected", "severity": "Moderate", "certainty": "Likely"},
    "HIGH": {"urgency": "Immediate", "severity": "Severe", "certainty": "Likely"},
    "CRITICAL": {"urgency": "Immediate", "severity": "Extreme", "certainty": "Observed"},
}


def generate_cap_alert(
    lake_name: str,
    latitude: float,
    longitude: float,
    risk_level: str,
    headline: str,
    description: str,
    sender: str = "GLOF-SAFE-AUTOMATED-SYSTEM",
    area_desc: str = None,
    circle_radius_km: float = 10.0,
):
    """
    Build a valid CAP v1.2 XML document for a GLOF hazard alert.
    Returns both the XML string and a parsed summary dict.
    """
    risk_level = str(risk_level).upper()
    cap_fields = RISK_TO_CAP.get(risk_level, RISK_TO_CAP["MEDIUM"])

    identifier = str(uuid.uuid4())
    sent_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    alert = Element("alert", xmlns=CAP_NAMESPACE)
    SubElement(alert, "identifier").text = identifier
    SubElement(alert, "sender").text = sender
    SubElement(alert, "sent").text = sent_time
    SubElement(alert, "status").text = "Actual"
    SubElement(alert, "msgType").text = "Alert"
    SubElement(alert, "scope").text = "Public"

    info = SubElement(alert, "info")
    SubElement(info, "category").text = "Geo"
    SubElement(info, "event").text = "Glacial Lake Outburst Flood (GLOF)"
    SubElement(info, "urgency").text = cap_fields["urgency"]
    SubElement(info, "severity").text = cap_fields["severity"]
    SubElement(info, "certainty").text = cap_fields["certainty"]
    SubElement(info, "headline").text = headline
    SubElement(info, "description").text = description
    SubElement(info, "senderName").text = "GLOF-SAFE Early Warning System"

    area = SubElement(info, "area")
    SubElement(area, "areaDesc").text = area_desc or f"{lake_name} watershed"
    SubElement(area, "circle").text = (
        f"{latitude},{longitude} {circle_radius_km}"
    )

    rough_xml = tostring(alert, encoding="unicode")
    pretty_xml = minidom.parseString(rough_xml).toprettyxml(indent="  ")

    return {
        "status": "CAP_ALERT_GENERATED",
        "identifier": identifier,
        "sent": sent_time,
        "risk_level": risk_level,
        "cap_xml": pretty_xml,
        "dispatch_targets": [
            "Local siren network (via alert_service.py notification pipeline)",
            "Registered authorities/public recipients (recipients.json)",
        ],
        "standard": "OASIS Common Alerting Protocol v1.2",
    }
