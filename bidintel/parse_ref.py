"""Parse reference letters and map to work names."""

from __future__ import annotations

import re
from pathlib import Path

import pymupdf

from bidintel.parse_common import normalize_ws


def pdf_text(path: Path) -> str:
    doc = pymupdf.open(path)
    return "\n".join(page.get_text() for page in doc)


def match_reference_works(
    ref_dir: Path,
    work_names: dict[int, str],
) -> set[int]:
    """Return work_ids that have a matching reference letter."""
    matched: set[int] = set()
    norm_names = {wid: normalize_ws(name) for wid, name in work_names.items()}

    for ref_path in sorted(ref_dir.glob("DOC-REF-*.pdf")):
        flat = normalize_ws(pdf_text(ref_path))
        hits = [wid for wid, nm in norm_names.items() if nm in flat]
        if len(hits) == 1:
            matched.add(hits[0])
    return matched
