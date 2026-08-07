"""One-shot SQL safety checks."""

from __future__ import annotations

import re

_FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|ATTACH|PRAGMA|REPLACE|CREATE|TRUNCATE)\b",
    re.IGNORECASE,
)


def extract_sql(raw: str) -> str:
    """Pull a single SELECT from model output."""
    text = raw.strip()
    # Strip markdown fences
    if "```" in text:
        parts = re.findall(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if parts:
            text = parts[-1].strip()
    # Take last line that looks like SELECT
    for line in reversed(text.splitlines()):
        line = line.strip()
        if line.upper().startswith("SELECT"):
            text = line
            break
    # Remove trailing semicolon
    text = text.rstrip().rstrip(";").strip()
    return text


def validate_sql(sql: str) -> None:
    if not sql:
        raise ValueError("empty SQL")
    if not sql.upper().startswith("SELECT"):
        raise ValueError("only SELECT allowed")
    if _FORBIDDEN.search(sql):
        raise ValueError("forbidden SQL keyword")
    # Reject multiple statements
    remainder = sql.rstrip(";").split(";")
    if len([p for p in remainder if p.strip()]) > 1:
        raise ValueError("multiple statements not allowed")
