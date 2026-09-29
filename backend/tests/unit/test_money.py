"""Representação monetária: Decimal sempre, nunca float (ADR-009)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.errors import InvalidMonetaryValueError
from app.domain.money import MONEY_SCALE, QUANTITY_SCALE, fits_scale, quantize, to_decimal


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("15780.00", Decimal("15780.00")),
        (" 0.1 ", Decimal("0.1")),
        (42, Decimal(42)),
        (Decimal("1.2345678901"), Decimal("1.2345678901")),
    ],
)
def test_to_decimal_accepts_text_int_decimal(raw: str | int | Decimal, expected: Decimal) -> None:
    assert to_decimal(raw) == expected


@pytest.mark.parametrize("raw", [0.1, True, "", "abc", "NaN", "Infinity"])
def test_to_decimal_rejects_float_bool_and_invalid(raw: object) -> None:
    with pytest.raises(InvalidMonetaryValueError):
        to_decimal(raw)  # type: ignore[arg-type]


def test_decimal_arithmetic_is_exact() -> None:
    assert to_decimal("0.1") + to_decimal("0.2") == Decimal("0.3")


def test_original_precision_is_preserved() -> None:
    value = to_decimal("12.3456789012")
    assert str(value) == "12.3456789012"


@pytest.mark.parametrize(
    ("raw", "scale", "fits"),
    [
        ("10.12", MONEY_SCALE, True),
        ("10.123", MONEY_SCALE, False),
        ("1.1200", MONEY_SCALE, True),
        ("3.1415", QUANTITY_SCALE, True),
        ("3.14159", QUANTITY_SCALE, False),
        ("100", 0, True),
    ],
)
def test_fits_scale(raw: str, scale: int, fits: bool) -> None:
    assert fits_scale(Decimal(raw), scale) is fits


@pytest.mark.parametrize(
    ("raw", "expected"), [("2.345", "2.34"), ("2.355", "2.36"), ("-2.345", "-2.34")]
)
def test_quantize_uses_round_half_even(raw: str, expected: str) -> None:
    assert quantize(Decimal(raw), MONEY_SCALE) == Decimal(expected)
