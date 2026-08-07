"""End-to-end template answering against sample questions."""

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

from bidintel.answer import answer_question
from evaluate import score_one

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "kb.sqlite"
QUESTIONS = json.loads((ROOT / "sample_questions.json").read_text())["questions"]


def _ensure_kb() -> None:
    if DB.exists():
        return
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "bidintel",
            "build-kb",
            "--documents",
            str(ROOT / "documents"),
            "--out",
            str(DB),
        ],
        cwd=ROOT,
    )


def test_all_sample_questions_score_full():
    _ensure_kb()
    conn = sqlite3.connect(DB)
    failures = []
    total = 0.0
    for q in QUESTIONS:
        result = answer_question(conn, q["question"], llm_fallback=False)
        score = score_one(q["answer"], result.answer)
        total += score
        if score < 1.0:
            failures.append(
                {
                    "qid": q["qid"],
                    "gold": q["answer"],
                    "got": result.answer,
                    "shape": result.shape,
                    "sql": result.sql,
                }
            )
    assert not failures, f"failures={failures} total={total}"
    assert total == len(QUESTIONS)


def test_jal_nigam_satisfactory_sum_gate():
    _ensure_kb()
    conn = sqlite3.connect(DB)
    total = conn.execute(
        "SELECT SUM(value_inr) FROM works "
        "WHERE client = 'Jal Nigam, Jharkhand' AND grade = 'Satisfactory'"
    ).fetchone()[0]
    assert total == 883600000
