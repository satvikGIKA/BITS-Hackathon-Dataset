"""Parse personnel certificates."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pymupdf

from bidintel.parse_common import field_after, parse_date


@dataclass
class PersonnelCert:
    doc_id: str
    person_name: str
    credential_type: str
    credential_id: str | None
    issued_date: str | None


def _credential_type(text: str, lines: list[str]) -> str:
    if re.search(r"SIX SIGMA BLACK BELT", text, re.IGNORECASE):
        return "Six Sigma Black Belt"
    cred = field_after(lines, "Credential Type")
    if cred and "six sigma" in cred.lower():
        return "Six Sigma Black Belt"
    return "PMP"


def parse_pcert_text(doc_id: str, text: str) -> PersonnelCert | None:
    lines = text.split("\n")
    name_m = re.search(
        r"(?:This is to certify that|This credential is conferred upon)\n(.+)",
        text,
    )
    if not name_m:
        return None
    person_name = name_m.group(1).strip().split("\n")[0].strip()

    cred_id = None
    id_m = re.search(
        r"(?:Credential ID|Certificate No\.)\n?\s*([A-Z]+-\d+)",
        text,
    )
    if not id_m:
        id_m = re.search(r"\b([A-Z]{2,5}-\d{4,})\b", text)
    if id_m:
        cred_id = id_m.group(1)

    issued = None
    iss_m = re.search(
        r"(?:Issued:|Date of Issue\n|Issued\n)\s*([\d]{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-z]{3}\s+\d{4})",
        text,
    )
    if iss_m:
        issued = parse_date(iss_m.group(1))

    return PersonnelCert(
        doc_id=doc_id,
        person_name=person_name,
        credential_type=_credential_type(text, lines),
        credential_id=cred_id,
        issued_date=issued,
    )


def parse_pcert_file(path: Path) -> PersonnelCert | None:
    doc = pymupdf.open(path)
    text = "\n".join(page.get_text() for page in doc)
    return parse_pcert_text(path.stem, text)
