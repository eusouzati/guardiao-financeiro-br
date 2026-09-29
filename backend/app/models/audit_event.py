from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.audit import ActorType, AuditEventType
from app.models.base import Base, UUIDPrimaryKeyMixin, utc_now

_EVENT_TYPES = ", ".join(f"'{e.value}'" for e in AuditEventType)
_ACTOR_TYPES = ", ".join(f"'{a.value}'" for a in ActorType)


class AuditEvent(UUIDPrimaryKeyMixin, Base):
    """Trilha de auditoria append-only (ADR-015). UPDATE/DELETE/TRUNCATE bloqueados por trigger."""

    __tablename__ = "audit_event"
    __table_args__ = (
        CheckConstraint(f"event_type IN ({_EVENT_TYPES})", name="event_type_valid"),
        CheckConstraint(f"actor_type IN ({_ACTOR_TYPES})", name="actor_type_valid"),
        Index("ix_audit_event_org_occurred_at", "organization_id", "occurred_at"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organization.id"))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now()
    )
    event_type: Mapped[str] = mapped_column(String(50))
    actor_type: Mapped[str] = mapped_column(String(20))
    actor_id: Mapped[str] = mapped_column(String(200))
    request_id: Mapped[str | None] = mapped_column(String(64))
    target_type: Mapped[str | None] = mapped_column(String(50))
    target_id: Mapped[str | None] = mapped_column(String(100))
    details: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb")
    )
