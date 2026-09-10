import os
from dataclasses import dataclass


PROVIDER_DISABLED = "disabled"
PROVIDER_OPENAI = "openai"
PROVIDER_CHATGPT = "chatgpt"
PROVIDER_GOOGLE = "google"
PROVIDER_LOCAL = "local"

VALID_PROVIDERS = {
    PROVIDER_DISABLED,
    PROVIDER_OPENAI,
    PROVIDER_CHATGPT,
    PROVIDER_GOOGLE,
    PROVIDER_LOCAL,
}


@dataclass(frozen=True)
class LlmSettings:
    provider: str
    model: str
    api_key: str
    base_url: str
    timeout_seconds: int

    @property
    def enabled(self):
        return self.provider != PROVIDER_DISABLED

    @property
    def provider_label(self):
        if self.provider in {PROVIDER_OPENAI, PROVIDER_CHATGPT}:
            return "OpenAI"

        return self.provider.title()

    def public_dict(self):
        return {
            "enabled": self.enabled,
            "provider": self.provider,
            "providerLabel": self.provider_label,
            "model": self.model,
            "baseUrl": self.base_url,
            "hasApiKey": bool(self.api_key),
        }


def _read_timeout():
    try:
        return max(int(os.getenv("LLM_TIMEOUT_SECONDS", "45")), 5)
    except ValueError:
        return 45


def _normalize_provider(value):
    provider = (value or PROVIDER_DISABLED).strip().lower()

    if provider not in VALID_PROVIDERS:
        return PROVIDER_DISABLED

    return provider


def get_llm_settings():
    provider = _normalize_provider(os.getenv("LLM_PROVIDER", PROVIDER_DISABLED))
    common_model = os.getenv("LLM_MODEL", "").strip()

    if provider in {PROVIDER_OPENAI, PROVIDER_CHATGPT}:
        return LlmSettings(
            provider=provider,
            model=os.getenv("OPENAI_MODEL", common_model or "gpt-5-mini").strip(),
            api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
            timeout_seconds=_read_timeout(),
        )

    if provider == PROVIDER_GOOGLE:
        return LlmSettings(
            provider=provider,
            model=os.getenv("GOOGLE_LLM_MODEL", common_model or "gemini-3.7-flash").strip(),
            api_key=(
                os.getenv("GOOGLE_API_KEY", "").strip()
                or os.getenv("GEMINI_API_KEY", "").strip()
            ),
            base_url=os.getenv(
                "GOOGLE_LLM_BASE_URL",
                "https://generativelanguage.googleapis.com/v1beta",
            ).rstrip("/"),
            timeout_seconds=_read_timeout(),
        )

    if provider == PROVIDER_LOCAL:
        return LlmSettings(
            provider=provider,
            model=os.getenv("LOCAL_LLM_MODEL", common_model or "llama3.1").strip(),
            api_key=os.getenv("LOCAL_LLM_API_KEY", "local").strip(),
            base_url=os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:11434/v1").rstrip("/"),
            timeout_seconds=_read_timeout(),
        )

    return LlmSettings(
        provider=PROVIDER_DISABLED,
        model="",
        api_key="",
        base_url="",
        timeout_seconds=_read_timeout(),
    )
