"""Parse Indian monetary renderings into integer rupees."""

from __future__ import annotations

import re
from decimal import Decimal, ROUND_HALF_UP

_MONEY = re.compile(
    r"(?:INR|Rs\.?|₹)\s*([\d,]+(?:\.\d+)?)\s*(Cr(?:ore)?s?|Lakhs?|L)?\b|"
    r"([\d,]+(?:\.\d+)?)\s*(Cr(?:ore)?s?|Lakhs?)\b",
    re.IGNORECASE,
)


def _to_int_rupees(amount: Decimal) -> int:
    return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def parse_money(text: str | None) -> int | None:
    """Return integer rupees from a money string, or None if unparseable."""
    if not text or not str(text).strip():
        return None
    s = str(text).strip()
    m = _MONEY.search(s)
    if not m:
        # Plain comma-grouped integer (Indian or western grouping)
        digits = re.sub(r"[^\d.]", "", s)
        if not digits:
            return None
        try:
            return _to_int_rupees(Decimal(digits))
        except Exception:
            return None
    num_str = (m.group(1) or m.group(3) or "").replace(",", "")
    unit = (m.group(2) or m.group(4) or "").lower()
    try:
        value = Decimal(num_str)
    except Exception:
        return None
    if unit.startswith("cr"):
        value *= Decimal("10000000")
    elif unit.startswith("l"):
        value *= Decimal("100000")
    return _to_int_rupees(value)
