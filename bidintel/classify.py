"""Deterministic question shape classification."""

from __future__ import annotations

import re

from bidintel.shapes import SHAPES


def classify(question: str) -> tuple[str | None, float]:
    q = question.lower()

    scores: dict[str, int] = {shape: 0 for shape in SHAPES}

    if re.search(r"reference letter", q) and re.search(
        r"no |lack|without|unreferenced|actually lack", q
    ):
        scores["absence"] += 5
    if re.search(r"how many.*reference letter", q):
        scores["absence"] += 4

    if re.search(r"days passed|number of days|exact interval|days between", q):
        scores["date_span"] += 5
    if re.search(r"issuance to finish|issuance to completion|from issuance", q):
        scores["date_span"] += 4

    if re.search(r"distinct|different categories|distinct work classifications", q):
        scores["distinct_count"] += 5

    if re.search(r"average size|mean size|defensible average", q):
        scores["avg_work_size"] += 5

    if re.search(r"excluding|exclude", q):
        scores["exclusion_aggregate"] += 5

    if re.search(r"additional work|reach our credential target|reach.*target", q):
        scores["gap_to_threshold"] += 5

    if re.search(r"largest.*second|second largest|difference between the largest", q):
        scores["rank_value"] += 5

    if re.search(r"out of one hundred|whole number out of one hundred|number out of one hundred", q):
        scores["referenced_share"] += 5
    if re.search(r"share of completed.*reference|formal verification on file", q):
        scores["referenced_share"] += 4

    if re.search(r"\bas prime\b", q):
        scores["role_split"] += 5

    if re.search(r"crossing the|crossing|hitting the|hitting|above inr|>=", q) and re.search(
        r"crore|mark|line", q
    ):
        scores["threshold_aggregate"] += 5

    if re.search(r"wrapped up after|completed after.*pmp|after that date|after her pmp", q):
        scores["temporal_chain"] += 5
    if re.search(r"after.*issued", q) and re.search(r"combined value|total value", q):
        scores["temporal_chain"] += 3

    if re.search(r"graded|marked satisfactory|marked excellent", q) and re.search(
        r"sum|total amount|contract amounts", q
    ):
        scores["doc_filtered_aggregate"] += 5
    if re.search(r"excellent|satisfactory", q) and re.search(
        r"completion certificates|so graded|those entries", q
    ):
        scores["doc_filtered_aggregate"] += 4

    if re.search(r"combined value|total value|aggregate value|defensible aggregate", q):
        if re.search(r"delivered for|for the commissioning client|for that client", q):
            scores["hop_aggregate"] += 4
        if re.search(r"starting from|reference point|referencing her", q):
            scores["hop_aggregate"] += 3
        if re.search(r"pmp.*project", q) and re.search(r"pkg-", q):
            scores["hop_aggregate"] += 2

    best_shape = max(scores, key=scores.get)
    best_score = scores[best_shape]
    if best_score == 0:
        return None, 0.0

    sorted_scores = sorted(scores.values(), reverse=True)
    if len(sorted_scores) > 1 and sorted_scores[0] == sorted_scores[1]:
        return None, 0.0

    return best_shape, min(1.0, best_score / 5.0)
