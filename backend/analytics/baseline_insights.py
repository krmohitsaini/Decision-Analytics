def build_dashboard_baseline_insights(summary):
    kpis = summary.get("kpis", {})
    mixes = summary.get("mixes", {})
    outcomes = mixes.get("outcomes", [])
    channels = mixes.get("channels", [])
    top_outcome = outcomes[0]["label"] if outcomes else "the leading outcome"
    top_channel = channels[0]["label"] if channels else "the leading channel"

    return {
        "summary": (
            f"Portfolio health is anchored by a {kpis.get('activeSiteRate', 0)}% active site "
            f"rate, with churn at {kpis.get('churnRate', 0)}% and digital adoption at "
            f"{kpis.get('digitalAdoptionRate', 0)}%."
        ),
        "drivers": [
            f"{top_channel} is the largest visible channel in the selected view.",
            f"{top_outcome} is the largest visible contract outcome in the selected view.",
            f"Digital adoption is {kpis.get('digitalAdoptionRate', 0)}% across distinct business partners.",
        ],
        "risks": [
            f"Churn is {kpis.get('churnRate', 0)}% of closed contract episodes.",
            f"Leakage is {kpis.get('leakageRate', 0)}% of selected contract episodes.",
        ],
        "actions": [
            "Prioritize churn review by channel before renewal planning.",
            "Inspect leakage cases by same-day and early-life drops.",
            "Target non-digital business partners for portal adoption campaigns.",
        ],
        "caveats": [
            "These baseline insights are deterministic and do not use an LLM.",
        ],
    }
