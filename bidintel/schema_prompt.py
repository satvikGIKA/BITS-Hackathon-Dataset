"""Build schema prompt for Ollama SQL generation."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DDL = (Path(__file__).parent / "schema.sql").read_text()


def build_schema_prompt(conn: sqlite3.Connection) -> str:
    clients = [
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT client FROM works ORDER BY client"
        ).fetchall()
    ]
    client_list = "\n".join(f"  - {c}" for c in clients)

    return f"""You are a SQLite query generator for National Infrastructure Corp. Ltd. bid intelligence.

DATABASE SCHEMA:
{DDL}

TABLE NOTES:
- works: 155 completed construction projects. value_inr is integer rupees (not Crore).
- personnel_certs: staff credentials (PMP, Six Sigma Black Belt).
- Join works to personnel_certs on works.project_manager = personnel_certs.person_name.
- has_reference_letter: 1 if client reference letter exists, 0 if missing.
- role: 'Prime' or 'JV Partner' (from portfolio).
- grade: 'Excellent', 'Very Good', 'Good', 'Satisfactory', or NULL if unknown.
- ~41 works have grade IS NULL; do not invent grades.

VALID CLIENT NAMES (use exact strings):
{client_list}

ANSWER RULES:
- Return exactly ONE SQLite SELECT that produces a single numeric cell.
- Money answers: integer rupees (no units, no commas). Example: 2008199999 not 2008.2 Cr.
- Percentages: number out of 100 (e.g. 33.33 not 0.3333).
- Day counts: integer (use julianday for date differences).
- Counts: integer.
- Use has_reference_letter = 0 for "no reference letter on file".
- Use role = 'Prime' for "as Prime" questions.
- Output ONLY the SQL statement. No markdown, no explanation.

EXAMPLES:
Q: How many works for Jal Nigam, Jharkhand have no reference letter?
SQL: SELECT COUNT(*) FROM works WHERE client = 'Jal Nigam, Jharkhand' AND has_reference_letter = 0

Q: Total value of works for Public Health Engineering Dept, Gujarat as Prime?
SQL: SELECT COALESCE(SUM(value_inr), 0) FROM works WHERE client = 'Public Health Engineering Dept, Gujarat' AND role = 'Prime'
"""


def build_user_prompt(question: str) -> str:
    return f"Question: {question}\nSQL:"
