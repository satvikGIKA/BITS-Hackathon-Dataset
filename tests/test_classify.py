"""Tests for shape classification."""

import json
from pathlib import Path

from bidintel.classify import classify

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS = json.loads((ROOT / "sample_questions.json").read_text())["questions"]


def test_all_sample_shapes_classified():
    mismatches = []
    for q in QUESTIONS:
        shape, _ = classify(q["question"])
        if shape != q["shape"]:
            mismatches.append((q["qid"], q["shape"], shape))
    assert not mismatches, f"shape mismatches: {mismatches}"
