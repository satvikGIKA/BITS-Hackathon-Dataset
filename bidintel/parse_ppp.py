"""Parse past performance portfolio for Prime / JV Partner roles."""

from __future__ import annotations

import re
from pathlib import Path

import pymupdf


def parse_ppp_roles(ppp_path: Path) -> dict[int, str]:
    """Return work_id -> role ('Prime' or 'JV Partner')."""
    doc = pymupdf.open(ppp_path)
    text = "\n".join(page.get_text() for page in doc)
    roles: dict[int, str] = {}

    blocks = re.split(r"\n(?=\d{1,3}\.\s+[A-Za-z])", text)
    for block in blocks:
        ref = re.search(r"Certificate\s+CC/\d+/\d{4}/(\d+)", block)
        role_m = re.search(
            r"Client\n(.+?)\s*\((Prime|JV Partner)\)",
            block,
            re.DOTALL,
        )
        if ref and role_m:
            roles[int(ref.group(1))] = role_m.group(2)
    return roles
