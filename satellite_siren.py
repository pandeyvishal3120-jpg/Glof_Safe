"""
satellite_siren.py — Module 5: Direct-to-Satellite Siren Trigger

HONEST SCOPE NOTE:
This is a hardware/firmware integration (satellite modem + LoRa gateway
+ physical sirens) - not something a backend API can implement on its
own. What's provided here is the software-side dispatch interface a
real hardware bridge would plug into: a well-defined function and
payload shape that a satellite-modem client (e.g. Iridium/Swarm SDK)
or a LoRa gateway daemon would call in production. It's clearly
labelled SIMULATED, consistent with the rest of this codebase's
convention for anything not backed by real hardware/data.
"""

import uuid
from datetime import datetime, timezone


def trigger_satellite_siren(lake_name: str, risk_level: str, target_zone: str):
    """
    Software-side dispatch call for a direct-to-satellite siren
    trigger, used when terrestrial mobile towers are down. Returns the
    dispatch payload that a real satellite/LoRa hardware bridge would
    transmit - simulated here since no physical siren network is
    connected to this backend.
    """
    dispatch_id = str(uuid.uuid4())

    return {
        "status": "DISPATCH_SIMULATED",
        "dispatch_id": dispatch_id,
        "channel": "SATELLITE_TO_LORA_SIREN",
        "lake_name": lake_name,
        "risk_level": str(risk_level).upper(),
        "target_zone": target_zone,
        "dispatched_at": datetime.now(timezone.utc).isoformat(),
        "note": (
            "No physical satellite modem or LoRa siren gateway is "
            "connected. This function defines the payload contract a "
            "real hardware bridge (e.g. Swarm/Iridium SDK + LoRa "
            "gateway daemon) would consume in production."
        ),
    }
