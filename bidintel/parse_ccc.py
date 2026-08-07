"""Parse company completion certificates (DOC-CCC-*.pdf)."""

from __future__ import annotations

from dataclasses import dataclass

from bidintel.money import parse_money
from bidintel.parse_common import extract_grade, field_after, normalize_client, parse_date


@dataclass
class WorkRecord:
    work_id: int
    name: str
    client: str
    category: str
    value_inr: int
    completion_date: str
    project_manager: str
    grade: str | None = None


def parse_ccc_text(work_id: int, text: str) -> WorkRecord | None:
    lines = text.split("\n")
    name = field_after(lines, "Project Name", "Work")
    client = normalize_client(field_after(lines, "Client"))
    category = field_after(lines, "Work Category", "Category")
    value_raw = field_after(lines, "Contract Value", "Executed Value")
    date_raw = field_after(lines, "Completion Date", "Completion")
    pm = field_after(lines, "Project Manager", "Project Lead")
    value_inr = parse_money(value_raw)
    completion_date = parse_date(date_raw)
    grade = extract_grade(text)

    if not all([name, client, category, value_inr, completion_date, pm]):
        return None

    return WorkRecord(
        work_id=work_id,
        name=name,
        client=client,
        category=category,
        value_inr=value_inr,
        completion_date=completion_date,
        project_manager=pm,
        grade=grade,
    )
