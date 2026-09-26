"""API REST versionada /api/v1 — recursos disponíveis na Sprint 1.

Recursos de negócio (documentos, fornecedores, pedidos, recebimentos, exceções...) são
adicionados nas sprints seguintes; não há endpoints simulados.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import PrincipalDep, SessionDep, require
from app.domain.configuration import serialize_policy_value
from app.schemas.audit import AuditEventPage, AuditEventResponse
from app.schemas.common import ErrorResponse, PageMeta
from app.schemas.configuration import ConfigurationResponse, PolicyResponse
from app.schemas.identity import MeResponse, OrganizationResponse
from app.security.permissions import Permission
from app.security.principal import Principal
from app.services.audit import list_audit_events
from app.services.configurations import get_effective_policies
from app.services.organizations import get_current_organization

_ERRORS: dict[int | str, dict[str, object]] = {
    401: {"model": ErrorResponse, "description": "Não autenticado"},
    403: {"model": ErrorResponse, "description": "Sem permissão"},
    503: {"model": ErrorResponse, "description": "Organização não inicializada"},
}

router = APIRouter(prefix="/api/v1", responses=_ERRORS)

MAX_PAGE_SIZE = 100


@router.get("/me", response_model=MeResponse, tags=["identity"], summary="Usuário atual")
def me(principal: PrincipalDep, session: SessionDep) -> MeResponse:
    organization = get_current_organization(session)
    return MeResponse(
        user_id=principal.user_id,
        display_name=principal.display_name,
        auth_method=principal.auth_method.value,
        roles=sorted(r.value for r in principal.roles),
        permissions=sorted(p.value for p in principal.permissions),
        organization=OrganizationResponse(
            id=organization.id, legal_name=organization.legal_name, tax_id=organization.tax_id
        ),
    )


@router.get(
    "/configurations",
    response_model=ConfigurationResponse,
    tags=["configurations"],
    summary="Políticas efetivas da organização",
)
def configurations(
    principal: Annotated[Principal, Depends(require(Permission.CONFIGURATION_READ))],
    session: SessionDep,
) -> ConfigurationResponse:
    items = [
        PolicyResponse(
            key=p.definition.key,
            label=p.definition.label,
            description=p.definition.description,
            type=p.definition.type.value,
            unit=p.definition.unit,
            value=serialize_policy_value(p.value),
            default_value=serialize_policy_value(p.definition.default),
            allowed_values=[s.value for s in p.definition.allowed],
            minimum=str(p.definition.minimum) if p.definition.minimum is not None else None,
            maximum=str(p.definition.maximum) if p.definition.maximum is not None else None,
            source=p.source.value,
            version=p.version,
            changed_by=p.changed_by,
            changed_at=p.changed_at,
        )
        for p in get_effective_policies(session, principal.organization_id)
    ]
    return ConfigurationResponse(items=items)


@router.get(
    "/audit/events",
    response_model=AuditEventPage,
    tags=["audit"],
    summary="Trilha de auditoria (paginada)",
)
def audit_events(
    principal: Annotated[Principal, Depends(require(Permission.AUDIT_READ))],
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = 20,
) -> AuditEventPage:
    records, total = list_audit_events(
        session, principal.organization_id, page=page, page_size=page_size
    )
    return AuditEventPage(
        items=[
            AuditEventResponse(
                id=r.id,
                occurred_at=r.occurred_at,
                event_type=r.event_type.value,
                actor_type=r.actor_type.value,
                actor_id=r.actor_id,
                request_id=r.request_id,
                target_type=r.target_type,
                target_id=r.target_id,
                details=r.details,
            )
            for r in records
        ],
        meta=PageMeta(page=page, page_size=page_size, total=total),
    )
