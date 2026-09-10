import json
import socket
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import PROVIDER_CHATGPT, PROVIDER_GOOGLE, PROVIDER_LOCAL, PROVIDER_OPENAI


class LlmClientError(RuntimeError):
    """Raised when an LLM provider cannot return a usable response."""


def _post_json(url, payload, headers, timeout_seconds):
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise LlmClientError(f"LLM provider returned HTTP {error.code}: {details}") from error
    except URLError as error:
        raise LlmClientError(f"Unable to reach LLM provider: {error.reason}") from error
    except (TimeoutError, socket.timeout) as error:
        raise LlmClientError("LLM provider request timed out.") from error
    except json.JSONDecodeError as error:
        raise LlmClientError("LLM provider returned invalid JSON.") from error


def _extract_json_object(text):
    cleaned = (text or "").strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise LlmClientError("LLM response did not contain a JSON object.")

        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as error:
            raise LlmClientError("LLM response JSON could not be parsed.") from error


def _message_text_from_chat_response(response):
    choices = response.get("choices") or []
    if not choices:
        raise LlmClientError("LLM provider returned no choices.")

    message = choices[0].get("message") or {}
    content = message.get("content")

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "\n".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") in {"text", "output_text"}
        )

    raise LlmClientError("LLM provider returned an unsupported message shape.")


def _text_from_google_response(response):
    candidates = response.get("candidates") or []
    if not candidates:
        raise LlmClientError("Google LLM provider returned no candidates.")

    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    text = "\n".join(part.get("text", "") for part in parts if isinstance(part, dict))

    if not text.strip():
        raise LlmClientError("Google LLM provider returned an empty response.")

    return text


def _openai_compatible_response(settings, system_prompt, user_prompt, response_schema):
    response_format = {"type": "json_object"}

    if settings.provider in {PROVIDER_OPENAI, PROVIDER_CHATGPT, PROVIDER_LOCAL}:
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "decision_analytics_insights",
                "strict": True,
                "schema": response_schema,
            },
        }

    payload = {
        "model": settings.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": response_format,
    }
    headers = {}

    if settings.provider in {PROVIDER_OPENAI, PROVIDER_CHATGPT}:
        if not settings.api_key:
            raise LlmClientError("OPENAI_API_KEY is required for the OpenAI provider.")
        headers["Authorization"] = f"Bearer {settings.api_key}"
    elif settings.provider == PROVIDER_LOCAL and settings.api_key:
        headers["Authorization"] = f"Bearer {settings.api_key}"

    response = _post_json(
        f"{settings.base_url}/chat/completions",
        payload,
        headers,
        settings.timeout_seconds,
    )
    return _extract_json_object(_message_text_from_chat_response(response))


def _google_response(settings, system_prompt, user_prompt, response_schema):
    if not settings.api_key:
        raise LlmClientError("GOOGLE_API_KEY or GEMINI_API_KEY is required for the Google provider.")

    payload = {
        "systemInstruction": {
            "parts": [{"text": system_prompt}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        },
    }
    response = _post_json(
        f"{settings.base_url}/models/{settings.model}:generateContent",
        payload,
        {"x-goog-api-key": settings.api_key},
        settings.timeout_seconds,
    )
    return _extract_json_object(_text_from_google_response(response))


def generate_structured_json(settings, system_prompt, user_prompt, response_schema):
    if settings.provider in {PROVIDER_OPENAI, PROVIDER_CHATGPT, PROVIDER_LOCAL}:
        return _openai_compatible_response(
            settings,
            system_prompt,
            user_prompt,
            response_schema,
        )

    if settings.provider == PROVIDER_GOOGLE:
        return _google_response(settings, system_prompt, user_prompt, response_schema)

    raise LlmClientError("LLM provider is disabled.")
