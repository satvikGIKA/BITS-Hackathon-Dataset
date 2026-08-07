"""OpenRouter chat completions client (OpenAI-compatible API)."""

from __future__ import annotations

import os

import httpx

DEFAULT_BASE = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openrouter/free"


def _api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Add it to your .env file."
        )
    return key


def chat(
    system: str,
    user: str,
    *,
    model: str | None = None,
    base_url: str | None = None,
) -> str:
    model = model or os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
    base_url = (base_url or os.environ.get("OPENROUTER_BASE_URL", DEFAULT_BASE)).rstrip("/")
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.environ.get("OPENROUTER_REFERER", "https://github.com/bits-hackathon"),
        "X-Title": os.environ.get("OPENROUTER_TITLE", "Bid Intelligence"),
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0,
    }
    resp = httpx.post(url, json=payload, headers=headers, timeout=180.0)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]
