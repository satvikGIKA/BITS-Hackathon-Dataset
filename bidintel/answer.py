"""Answer questions via shape templates (B) with LLM SQL fallback (A)."""

from __future__ import annotations

import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

from bidintel.classify import classify
from bidintel.env import load_dotenv
from bidintel.openrouter_client import chat
from bidintel.schema_prompt import build_schema_prompt, build_user_prompt
from bidintel.shapes import render_template, slots_complete
from bidintel.slots import extract_slots
from bidintel.sql_guard import extract_sql, validate_sql

load_dotenv()


@dataclass
class AnswerResult:
    question: str
    sql: str | None
    answer: float
    method: str = "template"
    shape: str | None = None
    error: str | None = None


def execute_scalar(conn: sqlite3.Connection, sql: str) -> float:
    cur = conn.execute(sql)
    row = cur.fetchone()
    if row is None or row[0] is None:
        return 0.0
    return float(row[0])


def answer_via_llm(
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
        return AnswerResult(
            question=question,
            sql=sql,
            answer=value,
            method="llm",
        )
    except Exception as exc:
        if verbose:
            print(f"ERROR: {exc}", file=sys.stderr)
        return AnswerResult(
            question=question,
            sql=None,
            answer=0.0,
            method="llm",
            error=str(exc),
        )


def answer_question(
    conn: sqlite3.Connection,
    question: str,
    *,
    verbose: bool = False,
    llm_fallback: bool = True,
) -> AnswerResult:
    shape, _conf = classify(question)
    if shape:
        slots = extract_slots(conn, question, shape)
        if slots_complete(shape, slots):
            try:
                sql = render_template(shape, slots)
                validate_sql(sql)
                if verbose:
                    print(f"shape={shape} method=template", file=sys.stderr)
                    print(f"SQL: {sql}", file=sys.stderr)
                value = execute_scalar(conn, sql)
                return AnswerResult(
                    question=question,
                    sql=sql,
                    answer=value,
                    method="template",
                    shape=shape,
                )
            except Exception as exc:
                if verbose:
                    print(f"template ERROR: {exc}", file=sys.stderr)
                if not llm_fallback:
                    return AnswerResult(
                        question=question,
                        sql=None,
                        answer=0.0,
                        method="template",
                        shape=shape,
                        error=str(exc),
                    )

    if not llm_fallback:
        return AnswerResult(
            question=question,
            sql=None,
            answer=0.0,
            method="template",
            shape=shape,
            error="template path incomplete",
        )

    if verbose and shape:
        print(f"shape={shape} falling back to llm", file=sys.stderr)
    result = answer_via_llm(conn, question, verbose=verbose)
    result.shape = shape
    return result


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Answer one question")
    ap.add_argument("--db", type=Path, default=Path("data/kb.sqlite"))
    ap.add_argument("--question", required=True)
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument(
        "--no-llm-fallback",
        action="store_true",
        help="Use template path only",
    )
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    result = answer_question(
        conn,
        args.question,
        verbose=args.verbose,
        llm_fallback=not args.no_llm_fallback,
    )
    print(result.answer)
    if result.error:
        sys.exit(1)


if __name__ == "__main__":
    main()
