from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.audit import ActorType, AuditEventType
from app.models.audit_event import AuditEvent


@dataclass(frozen=True, slots=True)
class AuditEventRecord:
    id: UUID
    occurred_at: datetime
    event_type: AuditEventType
    actor_type: ActorType
    actor_id: str
    request_id: str | None
    target_type: str | None
    target_id: str | None
    details: dict[str, Any]


class AuditEventRepository:
    """Somente inserção e leitura: a trilha é append-only (ADR-015)."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def append(
        self,
        *,
        organization_id: UUID,
        event_type: AuditEventType,
        actor_type: ActorType,
        actor_id: str,
        request_id: str | None,
        target_type: str | None = None,
        target_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> UUID:
        event = AuditEvent(
            organization_id=organization_id,
            event_type=event_type.value,
            actor_type=actor_type.value,
            actor_id=actor_id,
            request_id=request_id,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
        )
        self._session.add(event)
        self._session.flush()
        return event.id

    def list_page(
        self, organization_id: UUID, *, offset: int, limit: int
    ) -> tuple[list[AuditEventRecord], int]:
        base = select(AuditEvent).where(AuditEvent.organization_id == organization_id)
        total = self._session.scalar(select(func.count()).select_from(base.subquery())) or 0
        rows = self._session.scalars(
            base.order_by(AuditEvent.occurred_at.desc(), AuditEvent.id.desc())
            .offset(offset)
            .limit(limit)
        )
        records = [
            AuditEventRecord(
                id=row.id,
                occurred_at=row.occurred_at,
                event_type=AuditEventType(row.event_type),
                actor_type=ActorType(row.actor_type),
                actor_id=row.actor_id,
                request_id=row.request_id,
                target_type=row.target_type,
                target_id=row.target_id,
                details=row.details,
            )
            for row in rows
        ]
        return records, total
