import json


DASHBOARD_INSIGHT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"},
        "drivers": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 4,
        },
        "risks": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 4,
        },
        "actions": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 4,
        },
        "caveats": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 3,
        },
    },
    "required": ["summary", "drivers", "risks", "actions", "caveats"],
}


def build_dashboard_insight_prompts(summary):
    system_prompt = (
        "You are an analytics copilot for an energy customer portfolio dashboard. "
        "Use only the supplied JSON metrics. Do not invent data, causal claims, "
        "forecasts, benchmark comparisons, or customer facts that are not present. "
        "Write concise executive language for operations, retention, and commercial "
        "leaders. Return only valid JSON matching the requested schema."
    )
    user_prompt = (
        "Generate dashboard insights from this metric payload. Keep the summary under "
        "55 words. Each driver, risk, action, and caveat must be one sentence and must "
        "include specific metric values when relevant.\n\n"
        f"{json.dumps(summary, sort_keys=True)}"
    )

    return system_prompt, user_prompt
