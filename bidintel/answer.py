"""Answer a single question via LLM-generated SQL."""

from __future__ import annotations

import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

from bidintel.env import load_dotenv
from bidintel.openrouter_client import chat

load_dotenv()
from bidintel.schema_prompt import build_schema_prompt, build_user_prompt
from bidintel.sql_guard import extract_sql, validate_sql


@dataclass
class AnswerResult:
    question: str
    sql: str | None
    answer: float
    error: str | None = None


def execute_scalar(conn: sqlite3.Connection, sql: str) -> float:
    cur = conn.execute(sql)
    row = cur.fetchone()
    if row is None or row[0] is None:
        return 0.0
    return float(row[0])


def answer_question(
    conn: sqlite3.Connection,
    question: str,
    *,
    verbose: bool = False,
) -> AnswerResult:
    system = build_schema_prompt(conn)
    user = build_user_prompt(question)
    try:
        raw = chat(system, user)
        sql = extract_sql(raw)
        validate_sql(sql)
        if verbose:
            print(f"SQL: {sql}", file=sys.stderr)
        value = execute_scalar(conn, sql)
        return AnswerResult(question=question, sql=sql, answer=value)
    except Exception as exc:
        if verbose:
            print(f"ERROR: {exc}", file=sys.stderr)
        return AnswerResult(
            question=question,
            sql=None,
            answer=0.0,
            error=str(exc),
        )


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Answer one question")
    ap.add_argument("--db", type=Path, default=Path("data/kb.sqlite"))
    ap.add_argument("--question", required=True)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    result = answer_question(conn, args.question, verbose=args.verbose)
    print(result.answer)
    if result.error:
        sys.exit(1)


if __name__ == "__main__":
    main()
