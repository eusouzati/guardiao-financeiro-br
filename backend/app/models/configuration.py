from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin, utc_now


class ConfigurationEntry(UUIDPrimaryKeyMixin, Base):
    """Sobrescrita versionada de uma política por organização.

    Append-only: cada alteração cria nova versão (trigger no banco impede UPDATE/DELETE).
    O valor efetivo é a maior versão de cada chave; ausência = padrão do domínio.
    """

    __tablename__ = "configuration"
    __table_args__ = (
        UniqueConstraint("organization_id", "key", "version"),
        CheckConstraint("version >= 1", name="version_positive"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organization.id"))
    key: Mapped[str] = mapped_column(String(100))
    value: Mapped[Any] = mapped_column(JSONB)
    version: Mapped[int]
    changed_by: Mapped[str] = mapped_column(String(200))
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now()
    )
