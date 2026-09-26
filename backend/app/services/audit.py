"""Consulta da trilha de auditoria."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.audit_events import AuditEventRecord, AuditEventRepository


def list_audit_events(
    session: Session, organization_id: UUID, *, page: int, page_size: int
) -> tuple[list[AuditEventRecord], int]:
    return AuditEventRepository(session).list_page(
        organization_id, offset=(page - 1) * page_size, limit=page_size
    )
