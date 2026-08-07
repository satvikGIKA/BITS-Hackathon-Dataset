"""Shared parsing helpers."""

from __future__ import annotations

import datetime
import re


def field_after(lines: list[str], *labels: str) -> str | None:
    label_set = {lab.strip() for lab in labels}
    for i, line in enumerate(lines):
        if line.strip() in label_set and i + 1 < len(lines):
            return lines[i + 1].strip()
    return None


def normalize_client(raw: str | None) -> str | None:
    if not raw:
        return None
    s = re.sub(
        r"\s*\((government|psu|private)\)\s*$",
        "",
        raw.strip(),
        flags=re.IGNORECASE,
    )
    return re.sub(r"\s+", " ", s).strip()


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_date(text: str | None) -> str | None:
    if not text:
        return None
    s = text.strip()
    formats = (
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d %b %Y",
        "%d %B %Y",
        "%B %d, %Y",
        "%d %b %Y",
    )
    for fmt in formats:
        try:
            return datetime.datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    # "10 Mar 2021" without leading zero
    m = re.match(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", s)
    if m:
        try:
            return datetime.datetime.strptime(
                f"{m.group(1)} {m.group(2)} {m.group(3)}", "%d %b %Y"
            ).date().isoformat()
        except ValueError:
            pass
    return None


def extract_grade(text: str) -> str | None:
    m = re.search(r"graded\s+([A-Za-z ]+?)\.", text)
    if m:
        return m.group(1).strip()
    m = re.search(r"assessed the completed work as\s+([A-Za-z ]+?)[\.,]", text)
    if m:
        return m.group(1).strip()
    return None
