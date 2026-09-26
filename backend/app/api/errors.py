"""Tratamento centralizado de erros: respostas pt-BR sem detalhes internos (seção 47)."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config.logging import request_id_var
from app.domain.errors import AppError, ErrorCode
from app.schemas.common import ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)

STATUS_BY_CODE: dict[ErrorCode, int] = {
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.NOT_AUTHENTICATED: 401,
    ErrorCode.PERMISSION_DENIED: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.INTERNAL_ERROR: 500,
    ErrorCode.SERVICE_UNAVAILABLE: 503,
    ErrorCode.ORGANIZATION_NOT_INITIALIZED: 503,
    ErrorCode.INVALID_CONFIGURATION_VALUE: 422,
    ErrorCode.INVALID_MONETARY_VALUE: 422,
}

_HTTP_MESSAGES: dict[int, tuple[ErrorCode, str]] = {
    404: (ErrorCode.NOT_FOUND, "Recurso não encontrado."),
    405: (ErrorCode.NOT_FOUND, "Operação não suportada para este recurso."),
}


def _response(
    status: int, code: ErrorCode, message: str, details: list[ErrorDetail] | None = None
) -> JSONResponse:
    body = ErrorResponse(
        code=code.value, message=message, request_id=request_id_var.get(), details=details or []
    )
    headers = {"WWW-Authenticate": "Bearer"} if status == 401 else None  # noqa: PLR2004
    return JSONResponse(status_code=status, content=body.model_dump(mode="json"), headers=headers)


async def _app_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)  # noqa: S101 - garantido pelo registro do handler
    status = STATUS_BY_CODE.get(exc.code, 500)
    level = logging.WARNING if status >= 500 else logging.INFO  # noqa: PLR2004
    logger.log(level, "Erro de aplicação", extra={"ctx": {"code": exc.code.value}})
    return _response(status, exc.code, exc.message)


_VALIDATION_MESSAGES: dict[str, str] = {
    "missing": "Campo obrigatório.",
    "int_parsing": "Deve ser um número inteiro.",
    "int_type": "Deve ser um número inteiro.",
    "decimal_parsing": "Deve ser um número decimal.",
    "bool_parsing": "Deve ser verdadeiro ou falso.",
    "string_type": "Deve ser um texto.",
    "string_too_short": "Texto menor que o tamanho mínimo ({min_length}).",
    "string_too_long": "Texto maior que o tamanho máximo ({max_length}).",
    "greater_than": "Deve ser maior que {gt}.",
    "greater_than_equal": "Deve ser maior ou igual a {ge}.",
    "less_than": "Deve ser menor que {lt}.",
    "less_than_equal": "Deve ser menor ou igual a {le}.",
    "uuid_parsing": "Identificador inválido.",
    "enum": "Valor não permitido.",
    "json_invalid": "JSON inválido.",
}


def translate_validation_error(err: Mapping[str, Any]) -> str:
    """Mensagem pt-BR para um erro do Pydantic; nunca expõe o valor recebido."""
    template = _VALIDATION_MESSAGES.get(str(err.get("type", "")), "Valor inválido.")
    context = err.get("ctx") or {}
    try:
        return template.format(**{k: str(v) for k, v in context.items()})
    except (KeyError, IndexError):
        return "Valor inválido."


async def _validation_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)  # noqa: S101
    details = [
        ErrorDetail(
            field=".".join(str(p) for p in err.get("loc", ()) if p not in {"body", "query", "path"})
            or None,
            message=translate_validation_error(err),
        )
        for err in exc.errors()
    ]
    return _response(422, ErrorCode.VALIDATION_ERROR, "Dados da requisição inválidos.", details)


async def _http_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)  # noqa: S101
    code, message = _HTTP_MESSAGES.get(
        exc.status_code, (ErrorCode.INTERNAL_ERROR, "Não foi possível concluir a operação.")
    )
    return _response(exc.status_code, code, message)


async def _unhandled_error(_: Request, exc: Exception) -> JSONResponse:
    logger.error("Erro não tratado", exc_info=exc)
    return _response(
        500,
        ErrorCode.INTERNAL_ERROR,
        "Erro interno. Se o problema persistir, informe o código da requisição ao suporte.",
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(Exception, _unhandled_error)
