"""Casos de uso da organização."""

from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.audit import ActorType, AuditEventType
from app.domain.errors import OrganizationNotInitializedError
from app.domain.organization import OrganizationInfo
from app.repositories.audit_events import AuditEventRepository
from app.repositories.organizations import OrganizationRepository

logger = logging.getLogger(__name__)

# Chave arbitrária e estável para o lock de bootstrap.
_BOOTSTRAP_LOCK = text("SELECT pg_advisory_xact_lock(7340031001)")


def get_current_organization(session: Session) -> OrganizationInfo:
    organization = OrganizationRepository(session).get_default()
    if organization is None:
        raise OrganizationNotInitializedError()
    return organization


def bootstrap_organization(session: Session, legal_name: str) -> tuple[OrganizationInfo, bool]:
    """Cria a organização padrão se ainda não existir. Idempotente.

    Retorna a organização e ``True`` quando ela foi criada nesta chamada.
    Um advisory lock transacional evita criação duplicada em inicializações concorrentes.
    """
    session.execute(_BOOTSTRAP_LOCK)
    repo = OrganizationRepository(session)
    existing = repo.get_default()
    if existing is not None:
        return existing, False
    created = repo.create(legal_name=legal_name)
    AuditEventRepository(session).append(
        organization_id=created.id,
        event_type=AuditEventType.ORGANIZATION_CREATED,
        actor_type=ActorType.SYSTEM,
        actor_id="bootstrap",
        request_id=None,
        target_type="organization",
        target_id=str(created.id),
        details={"legal_name": created.legal_name},
    )
    logger.info("Organização inicializada", extra={"ctx": {"organization_id": str(created.id)}})
    return created, True
