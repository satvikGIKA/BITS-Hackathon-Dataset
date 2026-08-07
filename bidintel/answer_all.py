"""Answer all sample questions and write submission.jsonl."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from bidintel.answer import answer_question
from bidintel.env import load_dotenv

load_dotenv()


def answer_all(
    db_path: Path,
    questions_path: Path,
    out_path: Path,
    *,
    verbose: bool = False,
) -> None:
    data = json.loads(questions_path.read_text())
    questions = data["questions"]
    conn = sqlite3.connect(db_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        for q in questions:
            qid = q["qid"]
            text = q["question"]
            result = answer_question(conn, text, verbose=verbose)
            if verbose:
                print(
                    f"{qid}: answer={result.answer} sql={result.sql!r}",
                    file=sys.stderr,
                )
            line = {"qid": qid, "answer": result.answer}
            f.write(json.dumps(line) + "\n")
            f.flush()

    print(f"Wrote {len(questions)} answers to {out_path}", file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser(description="Answer all sample questions")
    ap.add_argument("--db", type=Path, default=Path("data/kb.sqlite"))
    ap.add_argument(
        "--questions",
        type=Path,
        default=Path("sample_questions.json"),
    )
    ap.add_argument("--out", type=Path, default=Path("my_answers.jsonl"))
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    answer_all(args.db, args.questions, args.out, verbose=args.verbose)


if __name__ == "__main__":
    main()
