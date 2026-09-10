from .client import LlmClientError, generate_structured_json
from .config import get_llm_settings
from .prompts import (
    DASHBOARD_INSIGHT_SCHEMA,
    DASHBOARD_QUESTION_SCHEMA,
    build_dashboard_insight_prompts,
    build_dashboard_question_prompts,
)


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


def _normalize_dashboard_question(value):
    if not isinstance(value, dict):
        raise LlmClientError("LLM response must be a JSON object.")

    missing_fields = [
        field
        for field in ("answer", "supportingMetrics", "caveats", "suggestedFollowUps")
        if field not in value
    ]
    if missing_fields:
        raise LlmClientError(f"LLM response is missing fields: {', '.join(missing_fields)}")

    normalized = {
        "answer": str(value.get("answer", "")).strip(),
        "supportingMetrics": _string_items(value.get("supportingMetrics")),
        "caveats": _string_items(value.get("caveats")),
        "suggestedFollowUps": _string_items(value.get("suggestedFollowUps")),
    }

    if not normalized["answer"]:
        raise LlmClientError("LLM response answer is empty.")

    return normalized


class LlmInsightService:
    def __init__(self, dashboard_service, settings=None):
        self.dashboard_service = dashboard_service
        self.settings = settings or get_llm_settings()

    def public_config(self):
        return self.settings.public_dict()

    def dashboard_insights(self, scope="current", channel="", commodity="", use_fallback=True):
        summary = self.dashboard_service.load_summary(scope=scope, channel=channel, commodity=commodity)

        if not self.settings.enabled:
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

    def ask_dashboard_question(self, question, scope="current", channel="", commodity=""):
        if not self.settings.enabled:
            raise LlmClientError("LLM provider is disabled.")

        normalized_question = (question or "").strip()
        if not normalized_question:
            raise LlmClientError("Question is required.")

        summary = self.dashboard_service.load_summary(
            scope=scope,
            channel=channel,
            commodity=commodity,
        )
        system_prompt, user_prompt = build_dashboard_question_prompts(summary, normalized_question)
        answer = generate_structured_json(
            self.settings,
            system_prompt,
            user_prompt,
            DASHBOARD_QUESTION_SCHEMA,
        )

        return {
            "mode": "llm",
            "config": self.public_config(),
            "answer": _normalize_dashboard_question(answer),
        }
