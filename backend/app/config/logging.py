"""Logs estruturados (JSON) com correlation IDs e redação de dados sensíveis.

Nunca registrar tokens, senhas, segredos, documentos completos ou dados pessoais
desnecessários (seção 27 do escopo). Campos extras são aceitos apenas via ``ctx`` e
chaves com nomes sensíveis são substituídas por ``[REDACTED]``.
"""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
organization_id_var: ContextVar[str | None] = ContextVar("organization_id", default=None)

_SENSITIVE_MARKERS = (
    "password",
    "senha",
    "secret",
    "token",
    "authorization",
    "cookie",
    "api_key",
    "apikey",
    "connection_string",
    "database_url",
    "cpf",
)
REDACTED = "[REDACTED]"


def redact(value: Any, _depth: int = 0) -> Any:
    """Remove recursivamente valores de chaves sensíveis."""
    if _depth > 5:  # noqa: PLR2004 - limite de profundidade defensivo
        return "[TRUNCATED]"
    if isinstance(value, dict):
        return {
            str(k): (
                REDACTED
                if any(marker in str(k).lower() for marker in _SENSITIVE_MARKERS)
                else redact(v, _depth + 1)
            )
            for k, v in value.items()
        }
    if isinstance(value, list | tuple):
        return [redact(v, _depth + 1) for v in value]
    return value


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if (request_id := request_id_var.get()) is not None:
            payload["request_id"] = request_id
        if (organization_id := organization_id_var.get()) is not None:
            payload["organization_id"] = organization_id
        ctx = getattr(record, "ctx", None)
        if isinstance(ctx, dict):
            payload.update(redact(ctx))
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = f"{record.levelname:<8} {record.name}: {record.getMessage()}"
        if (request_id := request_id_var.get()) is not None:
            base += f" [request_id={request_id}]"
        ctx = getattr(record, "ctx", None)
        if isinstance(ctx, dict):
            base += f" {redact(ctx)}"
        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)
        return base


def configure_logging(level: str = "INFO", fmt: str = "json") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter() if fmt == "json" else ConsoleFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
    # Logs de acesso são emitidos pelo middleware da aplicação (com request_id).
    logging.getLogger("uvicorn.access").disabled = True
    for name in ("uvicorn", "uvicorn.error"):
        logging.getLogger(name).handlers[:] = []
        logging.getLogger(name).propagate = True
