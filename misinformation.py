def verify_claim(claim: str):
    text = str(claim).strip()

    if not text:
        return {
            "status": "INVALID",
            "recommendation": "Enter a disaster-related claim."
        }

    lower = text.lower()

    emergency_words = [
        "glof",
        "flood",
        "evacuation",
        "dam break",
        "glacial lake",
        "warning",
        "alert",
        "landslide"
    ]

    matched = [
        word for word in emergency_words
        if word in lower
    ]

    if not matched:
        return {
            "status": "UNVERIFIED",
            "recommendation": (
                "The claim does not contain enough disaster-related "
                "context for automated verification."
            ),
            "matched_terms": []
        }

    urgent_words = [
        "immediate",
        "critical",
        "burst",
        "bursting",
        "destroyed",
        "danger",
        "evacuate now"
    ]

    urgent_matches = [
        word for word in urgent_words
        if word in lower
    ]

    if urgent_matches:
        status = "REQUIRES_VERIFICATION"
        recommendation = (
            "Treat this claim as unverified and cross-check it with "
            "official disaster-management or sensor data before sharing."
        )
    else:
        status = "POTENTIALLY_RELEVANT"
        recommendation = (
            "The claim is disaster-related. Cross-check with official "
            "GLOF-SAFE observations and authorized authorities."
        )

    return {
        "status": status,
        "recommendation": recommendation,
        "matched_terms": matched,
        "urgency_terms": urgent_matches,
        "method": "Rule-based disaster claim screening"
    }
