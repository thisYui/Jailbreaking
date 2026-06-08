from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from dotenv import load_dotenv

from config import PROJECT_ROOT


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "riverflow-v2.5-fast:free"


def _load_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def _api_key() -> str:
    _load_env()
    api_key = os.getenv("OPENROUTER_API")
    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API. Copy .env.example to .env, then add your OpenRouter API key.")
    return api_key


def require_openrouter_config() -> None:
    _api_key()


def _settings() -> tuple[str, float, int]:
    _load_env()
    model = os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)
    temperature = float(os.getenv("OPENROUTER_TEMPERATURE", "0.0"))
    max_output_tokens = int(os.getenv("OPENROUTER_MAX_OUTPUT_TOKENS", "512"))
    return model, temperature, max_output_tokens


def _headers(api_key: str) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    # OpenRouter recommends these headers for attribution, but they are optional.
    referer = os.getenv("OPENROUTER_HTTP_REFERER")
    title = os.getenv("OPENROUTER_APP_TITLE")
    if referer:
        headers["HTTP-Referer"] = referer
    if title:
        headers["X-Title"] = title
    return headers


def _extract_response_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts)
    return str(content) if content else ""


def _extract_finish_reason(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    if not choices:
        return ""
    return str(choices[0].get("finish_reason") or "")


def call_openrouter(prompt: str) -> dict[str, str]:
    model_name, temperature, max_output_tokens = _settings()
    try:
        api_key = _api_key()
        request_payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_output_tokens,
        }
        request = urllib.request.Request(
            OPENROUTER_URL,
            data=json.dumps(request_payload).encode("utf-8"),
            headers=_headers(api_key),
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return {
            "response_text": _extract_response_text(payload),
            "model": model_name,
            "finish_reason": _extract_finish_reason(payload),
            "error": "",
            "raw_response_repr": json.dumps(payload, ensure_ascii=False),
        }
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return {
            "response_text": "",
            "model": model_name,
            "finish_reason": "",
            "error": f"HTTP {exc.code}: {error_body}",
            "raw_response_repr": "",
        }
    except Exception as exc:
        return {
            "response_text": "",
            "model": model_name,
            "finish_reason": "",
            "error": str(exc),
            "raw_response_repr": "",
        }
