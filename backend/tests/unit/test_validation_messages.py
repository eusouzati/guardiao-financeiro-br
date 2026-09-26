"""Mensagens de validação traduzidas e sem eco do valor recebido."""

from __future__ import annotations

from app.api.errors import translate_validation_error


def test_known_error_types_are_translated_with_context() -> None:
    message = translate_validation_error({"type": "greater_than_equal", "ctx": {"ge": 1}})
    assert message == "Deve ser maior ou igual a 1."


def test_unknown_error_type_uses_generic_message() -> None:
    assert translate_validation_error({"type": "algo_novo"}) == "Valor inválido."


def test_input_value_is_never_echoed() -> None:
    message = translate_validation_error(
        {"type": "int_parsing", "input": "<script>alert(1)</script>"}
    )
    assert "<script>" not in message
