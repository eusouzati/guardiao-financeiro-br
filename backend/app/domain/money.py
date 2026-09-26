"""Regras de representação de valores monetários e decimais (ADR-007).

- Valores são sempre ``Decimal`` construídos a partir de texto ou inteiro — nunca ``float``.
- Nenhum arredondamento implícito: a precisão original é preservada.
- Quando um arredondamento é explicitamente necessário, usa ``ROUND_HALF_EVEN``.
"""

from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation

from app.domain.errors import InvalidMonetaryValueError

MONEY_SCALE = 2
UNIT_PRICE_SCALE = 10
QUANTITY_SCALE = 4
RATE_SCALE = 4


def to_decimal(value: str | int | Decimal) -> Decimal:
    """Converte texto/inteiro/Decimal em ``Decimal`` finito, rejeitando ``float``.

    ``bool`` também é rejeitado (é subclasse de ``int`` em Python).
    """
    if isinstance(value, bool | float):
        raise InvalidMonetaryValueError("Valores decimais não podem ser do tipo float/bool.")
    if isinstance(value, Decimal):
        result = value
    elif isinstance(value, int):
        result = Decimal(value)
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise InvalidMonetaryValueError("Valor decimal vazio.")
        try:
            result = Decimal(text)
        except InvalidOperation as exc:
            raise InvalidMonetaryValueError(f"Valor decimal inválido: {value!r}.") from exc
    else:
        raise InvalidMonetaryValueError("Tipo de valor decimal não suportado.")
    if not result.is_finite():
        raise InvalidMonetaryValueError("Valor decimal deve ser finito.")
    return result


def fits_scale(value: Decimal, scale: int) -> bool:
    """Indica se ``value`` pode ser armazenado com ``scale`` casas sem perda de precisão."""
    exponent = value.normalize().as_tuple().exponent
    return isinstance(exponent, int) and -exponent <= scale


def quantize(value: Decimal, scale: int) -> Decimal:
    """Arredondamento explícito (ROUND_HALF_EVEN / ABNT NBR 5891) para ``scale`` casas."""
    return value.quantize(Decimal(1).scaleb(-scale), rounding=ROUND_HALF_EVEN)
