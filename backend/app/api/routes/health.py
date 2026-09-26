"""Health checks (sem autenticação; sem dados sensíveis)."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

import app as app_package
from app.api.deps import SessionDep, SettingsDep
from app.schemas.health import LivenessResponse, ReadinessResponse
from app.services.health import check_database

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/live", response_model=LivenessResponse, summary="Processo em execução")
def live() -> LivenessResponse:
    return LivenessResponse(status="ok")


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Pronto para receber tráfego (banco acessível e migrado)",
    responses={503: {"model": ReadinessResponse}},
)
def ready(settings: SettingsDep, session: SessionDep) -> ReadinessResponse | JSONResponse:
    db = check_database(session)
    ok = db.reachable and db.schema_revision is not None
    body = ReadinessResponse(
        status="ok" if ok else "unavailable",
        version=app_package.__version__,
        environment=settings.app_env.value,
        database="ok" if db.reachable else "unavailable",
        schema_revision=db.schema_revision,
    )
    if ok:
        return body
    return JSONResponse(status_code=503, content=body.model_dump(mode="json"))
