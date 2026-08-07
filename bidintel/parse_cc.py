"""Parse client completion certificates (DOC-CC-*.pdf) for grade / PM fill."""

from __future__ import annotations

import re
from dataclasses import dataclass

from bidintel.money import parse_money
from bidintel.parse_common import extract_grade, field_after, parse_date


@dataclass
class CCExtras:
    work_id: int
    grade: str | None
    project_manager: str | None
    value_inr: int | None


def parse_cc_text(work_id: int, text: str) -> CCExtras:
    lines = text.split("\n")
    grade = extract_grade(text)
    pm = field_after(lines, "Contractor's Project Manager")
    if not pm:
        m = re.search(
            r"supervised on the contractor's side by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            text,
        )
        if m:
            pm = m.group(1).strip()

    value_inr = None
    val_raw = field_after(lines, "Contract Value (Original)")
    if val_raw:
        value_inr = parse_money(val_raw)
    if value_inr is None:
        m = re.search(r"gross executed value of\s+([^\(]+)", text, re.IGNORECASE)
        if m:
            value_inr = parse_money(m.group(1))

    return CCExtras(
        work_id=work_id,
        grade=grade,
        project_manager=pm,
        value_inr=value_inr,
    )
