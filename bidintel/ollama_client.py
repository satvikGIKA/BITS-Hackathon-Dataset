"""Thin Ollama HTTP client."""

from __future__ import annotations

import os

import httpx

DEFAULT_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")


def chat(system: str, user: str, *, host: str | None = None, model: str | None = None) -> str:
    host = host or DEFAULT_HOST
    model = model or DEFAULT_MODEL
    url = f"{host.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "options": {"temperature": 0},
    }
    resp = httpx.post(url, json=payload, timeout=120.0)
    resp.raise_for_status()
    data = resp.json()
    return data["message"]["content"]
