"""Políticas configuráveis por organização (seção 45 do escopo, docs/data-model.md §4).

As definições (tipo, padrão, limites) ficam aqui, no domínio. O banco guarda apenas
sobrescritas versionadas por organização; o valor efetivo é padrão + sobrescrita.
Nada disso é decidido no frontend.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from app.domain.errors import InvalidConfigurationValueError
from app.domain.money import to_decimal


class Severity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class PolicyType(StrEnum):
    BOOLEAN = "BOOLEAN"
    INTEGER = "INTEGER"
    DECIMAL = "DECIMAL"
    SEVERITY = "SEVERITY"


type PolicyValue = bool | int | Decimal | Severity


@dataclass(frozen=True, slots=True)
class PolicyDefinition:
    key: str
    type: PolicyType
    default: PolicyValue
    label: str
    description: str
    unit: str | None = None
    minimum: Decimal | None = None
    maximum: Decimal | None = None
    allowed: tuple[Severity, ...] = ()

    def parse(self, raw: object) -> PolicyValue:
        """Valida e converte um valor bruto (ex.: vindo de JSON) para o tipo da política."""
        match self.type:
            case PolicyType.BOOLEAN:
                if isinstance(raw, bool):
                    return raw
            case PolicyType.INTEGER:
                if isinstance(raw, int) and not isinstance(raw, bool):
                    self._check_range(Decimal(raw))
                    return raw
            case PolicyType.DECIMAL:
                if isinstance(raw, str | int | Decimal) and not isinstance(raw, bool):
                    value = to_decimal(raw)
                    self._check_range(value)
                    return value
            case PolicyType.SEVERITY:
                if isinstance(raw, str) and raw in {s.value for s in self.allowed}:
                    return Severity(raw)
        raise InvalidConfigurationValueError(f"Valor inválido para a política '{self.key}'.")

    def _check_range(self, value: Decimal) -> None:
        if self.minimum is not None and value < self.minimum:
            raise InvalidConfigurationValueError(
                f"'{self.key}' deve ser maior ou igual a {self.minimum}."
            )
        if self.maximum is not None and value > self.maximum:
            raise InvalidConfigurationValueError(
                f"'{self.key}' deve ser menor ou igual a {self.maximum}."
            )


def serialize_policy_value(value: PolicyValue) -> bool | int | str:
    """Representação JSON segura: Decimal vira string, nunca float (ADR-007)."""
    if isinstance(value, bool | int):
        return value
    return str(value)


POLICIES: tuple[PolicyDefinition, ...] = (
    PolicyDefinition(
        key="purchase_order_required",
        type=PolicyType.BOOLEAN,
        default=True,
        label="Exigir pedido de compra",
        description="Documentos sem pedido associado geram exceção.",
    ),
    PolicyDefinition(
        key="purchase_order_missing_severity",
        type=PolicyType.SEVERITY,
        default=Severity.CRITICAL,
        label="Severidade de pedido ausente",
        description="Severidade da exceção quando o pedido é exigido e não foi encontrado.",
        allowed=(Severity.WARNING, Severity.CRITICAL),
    ),
    PolicyDefinition(
        key="receipt_required",
        type=PolicyType.BOOLEAN,
        default=True,
        label="Exigir recebimento",
        description="Pedido sem confirmação de recebimento gera exceção.",
    ),
    PolicyDefinition(
        key="amount_tolerance_absolute",
        type=PolicyType.DECIMAL,
        default=Decimal("0.05"),
        label="Tolerância de valor (R$)",
        description="Diferença absoluta aceita entre documento e pedido.",
        unit="BRL",
        minimum=Decimal("0"),
        maximum=Decimal("1000000"),
    ),
    PolicyDefinition(
        key="amount_tolerance_percentage",
        type=PolicyType.DECIMAL,
        default=Decimal("0.50"),
        label="Tolerância de valor (%)",
        description="Diferença percentual aceita entre documento e pedido.",
        unit="PERCENT",
        minimum=Decimal("0"),
        maximum=Decimal("100"),
    ),
    PolicyDefinition(
        key="duplicate_window_days",
        type=PolicyType.INTEGER,
        default=30,
        label="Janela de possível duplicidade (dias)",
        description="Período para comparar fornecedor e valor iguais.",
        unit="DAYS",
        minimum=Decimal("1"),
        maximum=Decimal("3650"),
    ),
    PolicyDefinition(
        key="old_document_threshold_days",
        type=PolicyType.INTEGER,
        default=90,
        label="Documento antigo a partir de (dias)",
        description="Emissões anteriores a este limite geram alerta.",
        unit="DAYS",
        minimum=Decimal("1"),
        maximum=Decimal("3650"),
    ),
    PolicyDefinition(
        key="future_date_tolerance_minutes",
        type=PolicyType.INTEGER,
        default=10,
        label="Tolerância para data futura (minutos)",
        description="Margem para relógios dessincronizados antes de alertar data futura.",
        unit="MINUTES",
        minimum=Decimal("0"),
        maximum=Decimal("1440"),
    ),
)

POLICIES_BY_KEY: dict[str, PolicyDefinition] = {p.key: p for p in POLICIES}


class PolicySource(StrEnum):
    DEFAULT = "DEFAULT"
    ORGANIZATION = "ORGANIZATION"


@dataclass(frozen=True, slots=True)
class StoredPolicyOverride:
    key: str
    raw_value: object
    version: int
    changed_by: str
    changed_at: datetime


@dataclass(frozen=True, slots=True)
class EffectivePolicy:
    definition: PolicyDefinition
    value: PolicyValue
    source: PolicySource
    version: int | None
    changed_by: str | None
    changed_at: datetime | None


def resolve_policies(overrides: dict[str, StoredPolicyOverride]) -> list[EffectivePolicy]:
    """Combina padrões e sobrescritas. Sobrescritas inválidas ou desconhecidas são rejeitadas."""
    unknown = set(overrides) - set(POLICIES_BY_KEY)
    if unknown:
        raise InvalidConfigurationValueError(
            f"Políticas desconhecidas armazenadas: {', '.join(sorted(unknown))}."
        )
    result: list[EffectivePolicy] = []
    for definition in POLICIES:
        override = overrides.get(definition.key)
        if override is None:
            result.append(
                EffectivePolicy(
                    definition, definition.default, PolicySource.DEFAULT, None, None, None
                )
            )
        else:
            result.append(
                EffectivePolicy(
                    definition,
                    definition.parse(override.raw_value),
                    PolicySource.ORGANIZATION,
                    override.version,
                    override.changed_by,
                    override.changed_at,
                )
            )
    return result
