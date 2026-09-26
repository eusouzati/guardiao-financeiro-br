"""Fábrica da aplicação FastAPI.

Execução: ``uvicorn app.main:create_app --factory`` (não há instância global, para que a
configuração seja lida e validada somente na inicialização).
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

import app as app_package
from app.api.errors import register_error_handlers
from app.api.middleware import RequestContextMiddleware
from app.api.routes import health, v1
from app.config.logging import configure_logging
from app.config.settings import Settings, get_settings
from app.repositories.database import create_db_engine, create_session_factory

logger = logging.getLogger(__name__)

DEV_AUTH_WARNING = (
    "ATENÇÃO: autenticação DEV simulada ATIVA (APP_ENV=local). Todas as requisições são "
    "tratadas como o usuário de desenvolvimento. Nunca use esta configuração fora do "
    "ambiente local."
)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level, settings.log_format)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = create_db_engine(settings)
        app.state.session_factory = create_session_factory(engine)
        logger.info(
            "Aplicação iniciada",
            extra={"ctx": {"version": app_package.__version__, "env": settings.app_env.value}},
        )
        if settings.dev_auth_enabled:
            logger.warning(DEV_AUTH_WARNING)
        try:
            yield
        finally:
            engine.dispose()

    app = FastAPI(
        title="Guardião Financeiro BR — API",
        version=app_package.__version__,
        description=(
            "Conferência inteligente de contas a pagar. Valores monetários trafegam como "
            "string decimal; datas em ISO 8601 (UTC)."
        ),
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/v1/openapi.json",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.add_middleware(RequestContextMiddleware)
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(v1.router)
    return app
