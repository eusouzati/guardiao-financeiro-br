"""Políticas configuráveis: padrões, validação e resolução."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.configuration import (
    POLICIES_BY_KEY,
    PolicySource,
    Severity,
    StoredPolicyOverride,
    resolve_policies,
    serialize_policy_value,
)
from app.domain.errors import InvalidConfigurationValueError

EXPECTED_KEYS = {
    "purchase_order_required",
    "purchase_order_missing_severity",
    "receipt_required",
    "amount_tolerance_absolute",
    "amount_tolerance_percentage",
    "duplicate_window_days",
    "old_document_threshold_days",
    "future_date_tolerance_minutes",
}


def _override(key: str, raw: object, version: int = 1) -> StoredPolicyOverride:
    return StoredPolicyOverride(key, raw, version, "tester", datetime(2026, 9, 26, tzinfo=UTC))


def test_all_scope_policies_are_defined() -> None:
    assert set(POLICIES_BY_KEY) == EXPECTED_KEYS


def test_defaults_are_used_without_overrides() -> None:
    policies = {p.definition.key: p for p in resolve_policies({})}
    assert all(p.source is PolicySource.DEFAULT for p in policies.values())
    assert policies["amount_tolerance_absolute"].value == Decimal("0.05")
    assert policies["purchase_order_missing_severity"].value is Severity.CRITICAL


def test_override_replaces_default_and_keeps_audit_metadata() -> None:
    overrides = {"amount_tolerance_percentage": _override("amount_tolerance_percentage", "1.25", 3)}
    policy = next(
        p for p in resolve_policies(overrides) if p.definition.key == "amount_tolerance_percentage"
    )
    assert policy.value == Decimal("1.25")
    assert policy.source is PolicySource.ORGANIZATION
    assert policy.version == 3


@pytest.mark.parametrize(
    ("key", "raw"),
    [
        ("purchase_order_required", "true"),  # texto não é booleano
        ("duplicate_window_days", 0),  # abaixo do mínimo
        ("duplicate_window_days", True),  # bool não é inteiro
        ("amount_tolerance_percentage", "101"),  # acima do máximo
        ("amount_tolerance_absolute", 0.05),  # float é proibido
        ("purchase_order_missing_severity", "INFO"),  # não permitido para esta política
    ],
)
def test_invalid_values_are_rejected(key: str, raw: object) -> None:
    with pytest.raises(InvalidConfigurationValueError):
        POLICIES_BY_KEY[key].parse(raw)


def test_unknown_stored_key_is_rejected() -> None:
    with pytest.raises(InvalidConfigurationValueError, match="desconhecidas"):
        resolve_policies({"inexistente": _override("inexistente", True)})


def test_decimal_serialized_as_string_never_float() -> None:
    assert serialize_policy_value(Decimal("0.50")) == "0.50"
    assert serialize_policy_value(True) is True
    assert serialize_policy_value(30) == 30
    assert serialize_policy_value(Severity.WARNING) == "WARNING"
