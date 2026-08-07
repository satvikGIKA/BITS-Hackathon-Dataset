"""Tests for bidintel.sql_guard."""

import pytest

from bidintel.sql_guard import extract_sql, validate_sql


def test_extract_sql_from_markdown():
    raw = "```sql\nSELECT COUNT(*) FROM works\n```"
    assert extract_sql(raw) == "SELECT COUNT(*) FROM works"


def test_extract_sql_plain():
    assert extract_sql("SELECT 1") == "SELECT 1"


def test_validate_rejects_insert():
    with pytest.raises(ValueError):
        validate_sql("INSERT INTO works VALUES (1)")


def test_validate_rejects_drop_in_select():
    with pytest.raises(ValueError, match="forbidden"):
        validate_sql("SELECT 1; DROP TABLE works")


def test_validate_accepts_select():
    validate_sql("SELECT COUNT(*) FROM works WHERE client = 'X'")
