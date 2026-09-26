"""Middleware ASGI: correlation ID, log de acesso e cabeçalhos de segurança básicos.

O endurecimento completo de cabeçalhos (CSP da SPA, HSTS etc.) é da Sprint 7.
"""

from __future__ import annotations

import logging
import re
import time
import uuid

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.config.logging import request_id_var

logger = logging.getLogger("app.access")

REQUEST_ID_HEADER = "x-request-id"
_VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")
_DOCS_PATHS = ("/api/docs", "/api/v1/openapi.json")

_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
    "Cache-Control": "no-store",
}
_API_CSP = "default-src 'none'; frame-ancestors 'none'"


def _incoming_request_id(scope: Scope) -> str:
    for name, value in scope.get("headers", []):
        if name == REQUEST_ID_HEADER.encode():
            candidate: str = value.decode("latin-1")
            if _VALID_REQUEST_ID.fullmatch(candidate):
                return candidate
            break
    return uuid.uuid4().hex


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = _incoming_request_id(scope)
        request_id_var.set(request_id)
        path: str = scope.get("path", "")
        started = time.perf_counter()
        status_holder: dict[str, int] = {"status": 500}

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                status_holder["status"] = message["status"]
                headers = MutableHeaders(scope=message)
                headers[REQUEST_ID_HEADER] = request_id
                for key, value in _SECURITY_HEADERS.items():
                    headers.setdefault(key, value)
                if not path.startswith(_DOCS_PATHS):
                    headers.setdefault("Content-Security-Policy", _API_CSP)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Só método, caminho (sem query string, que pode conter dados) e status.
            logger.info(
                "request",
                extra={
                    "ctx": {
                        "method": scope.get("method"),
                        "path": path,
                        "status": status_holder["status"],
                        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                    }
                },
            )
