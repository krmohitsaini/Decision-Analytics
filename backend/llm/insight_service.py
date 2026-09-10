from .client import LlmClientError, generate_structured_json
from .config import get_llm_settings
from .prompts import DASHBOARD_INSIGHT_SCHEMA, build_dashboard_insight_prompts


REQUIRED_INSIGHT_FIELDS = ("summary", "drivers", "risks", "actions", "caveats")


def _string_items(value):
    if not isinstance(value, list):
        return []

    return [str(item).strip() for item in value if str(item).strip()]


def _normalize_dashboard_insights(value):
    if not isinstance(value, dict):
        raise LlmClientError("LLM response must be a JSON object.")

    missing_fields = [field for field in REQUIRED_INSIGHT_FIELDS if field not in value]
    if missing_fields:
        raise LlmClientError(f"LLM response is missing fields: {', '.join(missing_fields)}")

    normalized = {
        "summary": str(value.get("summary", "")).strip(),
        "drivers": _string_items(value.get("drivers")),
        "risks": _string_items(value.get("risks")),
        "actions": _string_items(value.get("actions")),
        "caveats": _string_items(value.get("caveats")),
    }

    if not normalized["summary"]:
        raise LlmClientError("LLM response summary is empty.")

    return normalized


def _fallback_dashboard_insights(summary):
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
            "This fallback insight is rule-based because no LLM response was used.",
        ],
    }


class LlmInsightService:
    def __init__(self, dashboard_service, settings=None):
        self.dashboard_service = dashboard_service
        self.settings = settings or get_llm_settings()

    def public_config(self):
        return self.settings.public_dict()

    def dashboard_insights(self, scope="current", channel="", commodity="", use_fallback=True):
        summary = self.dashboard_service.load_summary(scope=scope, channel=channel, commodity=commodity)

        if not self.settings.enabled:
            if use_fallback:
                return {
                    "mode": "fallback",
                    "config": self.public_config(),
                    "insights": _fallback_dashboard_insights(summary),
                }
            raise LlmClientError("LLM provider is disabled.")

        system_prompt, user_prompt = build_dashboard_insight_prompts(summary)
        insights = generate_structured_json(
            self.settings,
            system_prompt,
            user_prompt,
            DASHBOARD_INSIGHT_SCHEMA,
        )

        return {
            "mode": "llm",
            "config": self.public_config(),
            "insights": _normalize_dashboard_insights(insights),
        }
