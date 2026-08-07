#!/usr/bin/env python3
"""Run answer-all and print detailed per-question evaluation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bidintel.env import load_dotenv

load_dotenv()


def score_one(gold, got):
    if got is None:
        return 0.0
    try:
        gold, got = float(gold), float(got)
    except (TypeError, ValueError):
        return 0.0
    if abs(gold) < 100:
        if got == gold:
            return 1.0
        return 0.3 if abs(got - gold) <= 1 else 0.0
    err = abs(got - gold) / abs(gold)
    if err <= 0.005:
        return 1.0
    if err <= 0.02:
        return 0.7
    if err <= 0.10:
        return 0.3
    return 0.0


def main() -> None:
    db = ROOT / "data" / "kb.sqlite"
    questions = ROOT / "sample_questions.json"
    out = ROOT / "my_answers.jsonl"
    log = ROOT / "answer_log.txt"

    if not db.exists():
        subprocess.check_call(
            [sys.executable, "-m", "bidintel", "build-kb", "--documents", str(ROOT / "documents"), "--out", str(db)],
            cwd=ROOT,
        )

    with log.open("w") as lf:
        proc = subprocess.run(
            [sys.executable, "-m", "bidintel", "answer-all", "--db", str(db), "--questions", str(questions), "--out", str(out), "-v"],
            cwd=ROOT,
            stderr=lf,
            stdout=lf,
            text=True,
        )
    if proc.returncode != 0:
        print(log.read_text())
        sys.exit(proc.returncode)

    gold = {q["qid"]: q for q in json.loads(questions.read_text())["questions"]}
    got = {}
    for line in out.read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            got[rec["qid"]] = rec.get("answer")

    log_text = log.read_text()
    sql_by_qid = {}
    for line in log_text.splitlines():
        if line.startswith("HS-IC-"):
            parts = line.split(" sql=", 1)
            if parts:
                qid = parts[0].split(":")[0].strip()
                sql_part = parts[1].strip() if len(parts) > 1 else None
                if sql_part:
                    sql_by_qid[qid] = sql_part

    rows = []
    by_shape: dict[str, list[float]] = {}
    for qid in sorted(gold):
        q = gold[qid]
        g = q["answer"]
        a = got.get(qid)
        s = score_one(g, a)
        shape = q.get("shape", "?")
        by_shape.setdefault(shape, []).append(s)
        rows.append((qid, shape, g, a, s, q["question"]))

    print("=" * 80)
    print("BID INTELLIGENCE — OpenRouter evaluation (openrouter/free)")
    print("=" * 80)
    print()
    print(f"{'QID':<14} {'Shape':<24} {'Score':>5}  {'Gold':>14}  {'Got':>14}")
    print("-" * 80)
    for qid, shape, g, a, s, _ in rows:
        mark = "OK " if s == 1.0 else f"{s:.1f}"
        print(f"{qid:<14} {shape:<24} {mark:>5}  {g:>14}  {a!s:>14}")

    total = sum(r[4] for r in rows)
    print("-" * 80)
    print(f"TOTAL: {total:.1f} / {len(rows)} = {total / len(rows):.1%}")
    print()
    print("By shape:")
    for shape, scores in sorted(by_shape.items(), key=lambda kv: -sum(kv[1]) / len(kv[1])):
        t = sum(scores)
        print(f"  {shape:<26} {t:5.1f} / {len(scores)}  ({t / len(scores):.0%})")

    print()
    print("SQL / errors (from answer_log.txt):")
    print("-" * 80)
    for line in log_text.splitlines():
        if line.strip():
            print(line)

    perfect = [r for r in rows if r[4] == 1.0]
    partial = [r for r in rows if 0 < r[4] < 1.0]
    failed = [r for r in rows if r[4] == 0.0]
    print()
    print(f"Perfect: {len(perfect)}  Partial credit: {len(partial)}  Zero: {len(failed)}")


if __name__ == "__main__":
    main()
