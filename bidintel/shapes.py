"""SQL templates for each question shape."""

from __future__ import annotations

from typing import Any

SHAPES = (
    "absence",
    "date_span",
    "distinct_count",
    "hop_aggregate",
    "temporal_chain",
    "avg_work_size",
    "doc_filtered_aggregate",
    "exclusion_aggregate",
    "gap_to_threshold",
    "rank_value",
    "referenced_share",
    "role_split",
    "threshold_aggregate",
)

REQUIRED_SLOTS: dict[str, tuple[str, ...]] = {
    "absence": ("client",),
    "date_span": ("person", "work_name", "credential_type"),
    "distinct_count": ("person", "credential_type"),
    "hop_aggregate": ("work_name",),
    "temporal_chain": ("person", "credential_type", "issued_date"),
    "avg_work_size": ("work_name",),
    "doc_filtered_aggregate": ("client", "grade"),
    "exclusion_aggregate": ("client", "exclusion_kind"),
    "gap_to_threshold": ("client", "threshold_inr"),
    "rank_value": ("client",),
    "referenced_share": ("client",),
    "role_split": ("client",),
    "threshold_aggregate": ("client", "threshold_inr"),
}


def slots_complete(shape: str, slots: dict[str, Any]) -> bool:
    if shape not in REQUIRED_SLOTS:
        return False
    return all(slots.get(key) not in (None, "") for key in REQUIRED_SLOTS[shape])


def _sql_literal(value: str | int | float) -> str:
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def render_template(shape: str, slots: dict[str, Any]) -> str:
    client = _sql_literal(slots["client"]) if "client" in slots and slots["client"] else None
    person = _sql_literal(slots["person"]) if slots.get("person") else None
    work_name = _sql_literal(slots["work_name"]) if slots.get("work_name") else None
    cred = _sql_literal(slots.get("credential_type", "PMP"))
    issued = _sql_literal(slots["issued_date"]) if slots.get("issued_date") else None
    grade = _sql_literal(slots["grade"]) if slots.get("grade") else None
    threshold = slots.get("threshold_inr")

    if shape == "absence":
        return (
            f"SELECT COUNT(*) FROM works "
            f"WHERE client = {client} AND has_reference_letter = 0"
        )

    if shape == "date_span":
        cert_filter = f"person_name = {person} AND credential_type = {cred}"
        if slots.get("issued_date"):
            cert_filter += f" AND issued_date = {issued}"
        return (
            f"SELECT julianday((SELECT completion_date FROM works WHERE name = {work_name})) "
            f"- julianday((SELECT issued_date FROM personnel_certs WHERE {cert_filter}))"
        )

    if shape == "distinct_count":
        return (
            f"SELECT COUNT(DISTINCT category) FROM works "
            f"JOIN personnel_certs ON works.project_manager = personnel_certs.person_name "
            f"WHERE personnel_certs.person_name = {person} "
            f"AND personnel_certs.credential_type = {cred}"
        )

    if shape == "hop_aggregate":
        client_sub = f"(SELECT client FROM works WHERE name = {work_name})"
        return (
            f"SELECT COALESCE(SUM(value_inr), 0) FROM works "
            f"WHERE client = {client_sub}"
        )

    if shape == "temporal_chain":
        cert_parts = [
            f"personnel_certs.person_name = {person}",
            f"personnel_certs.credential_type = {cred}",
        ]
        if issued:
            cert_parts.append(f"personnel_certs.issued_date = {issued}")
        cert_where = " AND ".join(cert_parts)
        return (
            f"SELECT COALESCE(SUM(works.value_inr), 0) FROM works "
            f"JOIN personnel_certs ON works.project_manager = personnel_certs.person_name "
            f"WHERE {cert_where} AND works.completion_date > personnel_certs.issued_date"
        )

    if shape == "avg_work_size":
        client_sub = f"(SELECT client FROM works WHERE name = {work_name})"
        return (
            f"SELECT ROUND(AVG(value_inr)) FROM works "
            f"WHERE client = {client_sub}"
        )

    if shape == "doc_filtered_aggregate":
        return (
            f"SELECT COALESCE(SUM(value_inr), 0) FROM works "
            f"WHERE client = {client} AND grade = {grade}"
        )

    if shape == "exclusion_aggregate":
        kind = slots.get("exclusion_kind")
        if kind == "buildings":
            predicate = "category <> 'Buildings'"
        elif kind == "road_maintenance":
            predicate = "LOWER(category) NOT LIKE '%road%maintenance%'"
        else:
            raise ValueError(f"unknown exclusion_kind: {kind}")
        return (
            f"SELECT COALESCE(SUM(value_inr), 0) FROM works "
            f"WHERE client = {client} AND {predicate}"
        )

    if shape == "gap_to_threshold":
        return (
            f"SELECT COALESCE({int(threshold)} - (SELECT SUM(value_inr) FROM works "
            f"WHERE client = {client}), 0)"
        )

    if shape == "rank_value":
        return (
            f"SELECT (SELECT value_inr FROM works WHERE client = {client} "
            f"ORDER BY value_inr DESC LIMIT 1) - "
            f"(SELECT value_inr FROM works WHERE client = {client} "
            f"ORDER BY value_inr DESC LIMIT 1 OFFSET 1)"
        )

    if shape == "referenced_share":
        return (
            f"SELECT ROUND(100.0 * SUM(CASE WHEN has_reference_letter = 1 THEN 1 ELSE 0 END) "
            f"/ COUNT(*), 2) FROM works WHERE client = {client}"
        )

    if shape == "role_split":
        return (
            f"SELECT COALESCE(SUM(value_inr), 0) FROM works "
            f"WHERE client = {client} AND role = 'Prime'"
        )

    if shape == "threshold_aggregate":
        return (
            f"SELECT COALESCE(SUM(value_inr), 0) FROM works "
            f"WHERE client = {client} AND value_inr >= {int(threshold)}"
        )

    raise ValueError(f"unknown shape: {shape}")
