"""Tests for bidintel.money."""

import pytest

from bidintel.money import parse_money


@pytest.mark.parametrize(
    "text,expected",
    [
        ("INR 33.38 Cr", 333_800_000),
        ("Rs. 57.37 Crore", 573_700_000),
        ("INR 20.92 Cr", 209_200_000),
        ("Rs. 65.46 Lakh", 6_546_000),
        ("INR 81,44,00,000/-", 814_400_000),
        ("INR 57,37,00,000/-", 573_700_000),
        ("3,338.00 Lakh", 333_800_000),
        ("333800000", 333_800_000),
        (None, None),
        ("", None),
    ],
)
def test_parse_money(text, expected):
    assert parse_money(text) == expected
