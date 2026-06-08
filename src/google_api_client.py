from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

from config import PROJECT_ROOT


DEFAULT_MODEL = "gemini-2.5-flash"


def _load_genai_module():
    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError("google-genai is not installed. Install it with: pip install google-genai") from exc
    return genai


def get_gemini_client():
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing GEMINI_API_KEY. Copy .env.example to .env, then add a Google AI Studio API key."
        )
    genai = _load_genai_module()
    return genai.Client(api_key=api_key)


def require_gemini_config() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError(
            "Missing GEMINI_API_KEY. Copy .env.example to .env, then add a Google AI Studio API key."
        )
    _load_genai_module()


def _settings() -> tuple[str, float, int]:
    load_dotenv(PROJECT_ROOT / ".env")
    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.0"))
    max_output_tokens = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "512"))
    return model, temperature, max_output_tokens


def _extract_response_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if text:
        return str(text)
    candidates = getattr(response, "candidates", None) or []
    parts: list[str] = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", None) or []:
            part_text = getattr(part, "text", None)
            if part_text:
                parts.append(str(part_text))
    return "\n".join(parts)


def _extract_finish_reason(response: Any) -> str:
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return ""
    return str(getattr(candidates[0], "finish_reason", "") or "")


def call_gemini(prompt: str) -> dict[str, str]:
    model_name, temperature, max_output_tokens = _settings()
    try:
        client = get_gemini_client()
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_output_tokens,
                },
            )
        except TypeError:
            response = client.models.generate_content(model=model_name, contents=prompt)
        return {
            "response_text": _extract_response_text(response),
            "model": model_name,
            "finish_reason": _extract_finish_reason(response),
            "error": "",
            "raw_response_repr": repr(response),
        }
    except Exception as exc:
        return {
            "response_text": "",
            "model": model_name,
            "finish_reason": "",
            "error": str(exc),
            "raw_response_repr": "",
        }
