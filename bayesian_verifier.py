"""
bayesian_verifier.py — Module 4: Multi-Sensor Bayesian Verifier

Genuine Bayesian evidence fusion (Naive Bayes / likelihood-ratio
combination) across independent signals - water level anomaly, seismic
activity, satellite lake-area change, and weather (heavy
rainfall/storm) - to compute the posterior probability that an alert
is a real event rather than a single noisy sensor (the "Cry Wolf"
effect this module is meant to fix).

Each evidence source has a prior sensitivity/specificity (true-positive
and false-positive rate), sourced here from reasonable engineering
defaults rather than a fitted model (we don't have labelled
historical alarm outcomes to fit on) - but the combination math itself
is real Bayesian inference, not a rule threshold.
"""

from typing import Dict

# (true_positive_rate, false_positive_rate) per evidence source.
# i.e. P(signal fires | real event) and P(signal fires | no event).
EVIDENCE_RELIABILITY: Dict[str, tuple] = {
    "sensor_anomaly": (0.85, 0.15),
    "seismic_spike": (0.75, 0.10),
    "satellite_area_change": (0.80, 0.05),
    "severe_weather": (0.55, 0.20),
    "crowd_report": (0.60, 0.25),
}

PRIOR_PROBABILITY_REAL_EVENT = 0.05  # base rate before any evidence


def verify_alarm(evidence: Dict[str, bool]):
    """
    evidence: dict mapping source name -> bool (did that source fire?)
    e.g. {"sensor_anomaly": True, "seismic_spike": False, ...}

    Returns the posterior probability of a real event, combining all
    supplied evidence via sequential Bayesian updating.
    """
    posterior_odds = PRIOR_PROBABILITY_REAL_EVENT / (
        1 - PRIOR_PROBABILITY_REAL_EVENT
    )

    used_sources = []

    for source, fired in evidence.items():
        if source not in EVIDENCE_RELIABILITY:
            continue

        tpr, fpr = EVIDENCE_RELIABILITY[source]

        if fired:
            likelihood_ratio = tpr / max(fpr, 1e-6)
        else:
            likelihood_ratio = (1 - tpr) / max(1 - fpr, 1e-6)

        posterior_odds *= likelihood_ratio
        used_sources.append({
            "source": source,
            "fired": fired,
            "likelihood_ratio": round(likelihood_ratio, 3),
        })

    posterior_probability = posterior_odds / (1 + posterior_odds)
    posterior_probability = min(max(posterior_probability, 0.0), 1.0)

    if posterior_probability >= 0.90:
        verdict = "CONFIRMED_REAL_EVENT"
    elif posterior_probability >= 0.60:
        verdict = "LIKELY_REAL_EVENT"
    elif posterior_probability >= 0.30:
        verdict = "UNCERTAIN"
    else:
        verdict = "LIKELY_FALSE_ALARM"

    return {
        "status": "VERIFIED",
        "method": (
            "Sequential Bayesian evidence fusion (Naive Bayes "
            "likelihood-ratio combination across independent sensors)"
        ),
        "prior_probability": PRIOR_PROBABILITY_REAL_EVENT,
        "posterior_probability": round(posterior_probability, 4),
        "verdict": verdict,
        "evidence_breakdown": used_sources,
    }
