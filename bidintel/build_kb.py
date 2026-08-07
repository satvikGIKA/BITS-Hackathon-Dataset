"""Build SQLite knowledge base from documents/."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pymupdf

from bidintel.parse_cc import parse_cc_text
from bidintel.parse_ccc import parse_ccc_text
from bidintel.parse_pcert import parse_pcert_file
from bidintel.parse_ppp import parse_ppp_roles
from bidintel.parse_ref import match_reference_works


def _pdf_text(path: Path) -> str:
    doc = pymupdf.open(path)
    return "\n".join(page.get_text() for page in doc)


def build_kb(documents_dir: Path, out_path: Path) -> sqlite3.Connection:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()

    conn = sqlite3.connect(out_path)
    schema = (Path(__file__).parent / "schema.sql").read_text()
    conn.executescript(schema)

    ccc_dir = documents_dir / "company_completion_certificate"
    cc_dir = documents_dir / "completion_certificate"
    ppp_path = documents_dir / "past_performance_portfolio" / "DOC-PPP-001.pdf"
    ref_dir = documents_dir / "reference_letter"
    pcert_dir = documents_dir / "personnel_certificate"

    works: dict[int, dict] = {}

    for ccc_path in sorted(ccc_dir.glob("DOC-CCC-*.pdf")):
        work_id = int(ccc_path.stem.split("-")[-1])
        rec = parse_ccc_text(work_id, _pdf_text(ccc_path))
        if rec is None:
            print(f"WARN: failed to parse CCC {ccc_path.name}")
            continue
        works[work_id] = {
            "work_id": rec.work_id,
            "name": rec.name,
            "client": rec.client,
            "category": rec.category,
            "value_inr": rec.value_inr,
            "completion_date": rec.completion_date,
            "project_manager": rec.project_manager,
            "grade": rec.grade,
            "role": None,
            "has_reference_letter": 0,
        }

    for cc_path in sorted(cc_dir.glob("DOC-CC-*.pdf")):
        work_id = int(cc_path.stem.split("-")[-1])
        extras = parse_cc_text(work_id, _pdf_text(cc_path))
        if work_id not in works:
            continue
        w = works[work_id]
        if extras.grade and not w["grade"]:
            w["grade"] = extras.grade
        if extras.project_manager and not w["project_manager"]:
            w["project_manager"] = extras.project_manager
        if w["value_inr"] is None and extras.value_inr is not None:
            w["value_inr"] = extras.value_inr

    if ppp_path.exists():
        roles = parse_ppp_roles(ppp_path)
        for wid, role in roles.items():
            if wid in works:
                works[wid]["role"] = role

    name_map = {wid: w["name"] for wid, w in works.items()}
    ref_ids = match_reference_works(ref_dir, name_map)
    for wid in ref_ids:
        if wid in works:
            works[wid]["has_reference_letter"] = 1

    for w in works.values():
        conn.execute(
            """
            INSERT INTO works (
                work_id, name, client, category, value_inr, completion_date,
                project_manager, grade, role, has_reference_letter
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                w["work_id"],
                w["name"],
                w["client"],
                w["category"],
                w["value_inr"],
                w["completion_date"],
                w["project_manager"],
                w["grade"],
                w["role"],
                w["has_reference_letter"],
            ),
        )

    for pcert_path in sorted(pcert_dir.glob("DOC-PCERT-*.pdf")):
        cert = parse_pcert_file(pcert_path)
        if cert is None:
            print(f"WARN: failed to parse {pcert_path.name}")
            continue
        conn.execute(
            """
            INSERT INTO personnel_certs (
                doc_id, person_name, credential_type, credential_id, issued_date
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                cert.doc_id,
                cert.person_name,
                cert.credential_type,
                cert.credential_id,
                cert.issued_date,
            ),
        )

    conn.commit()
    _print_validation(conn)
    return conn


def _print_validation(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    n_works = cur.execute("SELECT COUNT(*) FROM works").fetchone()[0]
    n_certs = cur.execute("SELECT COUNT(*) FROM personnel_certs").fetchone()[0]
    missing_value = cur.execute(
        "SELECT COUNT(*) FROM works WHERE value_inr IS NULL"
    ).fetchone()[0]
    missing_client = cur.execute(
        "SELECT COUNT(*) FROM works WHERE client IS NULL OR client = ''"
    ).fetchone()[0]
    missing_role = cur.execute(
        "SELECT COUNT(*) FROM works WHERE role IS NULL"
    ).fetchone()[0]
    missing_grade = cur.execute(
        "SELECT COUNT(*) FROM works WHERE grade IS NULL"
    ).fetchone()[0]
    total_inr = cur.execute("SELECT SUM(value_inr) FROM works").fetchone()[0]
    total_cr = total_inr / 1e7 if total_inr else 0

    print(f"works: {n_works} (expect 155)")
    print(f"personnel_certs: {n_certs} (expect 48)")
    print(f"missing value_inr: {missing_value}")
    print(f"missing client: {missing_client}")
    print(f"missing role: {missing_role}")
    print(f"missing grade: {missing_grade}")
    print(f"total value: {total_cr:.1f} Cr (expect ~5530.4)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build SQLite KB from documents/")
    ap.add_argument(
        "--documents",
        type=Path,
        default=Path("documents"),
        help="Path to documents directory",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("data/kb.sqlite"),
        help="Output SQLite path",
    )
    args = ap.parse_args()
    build_kb(args.documents, args.out)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
