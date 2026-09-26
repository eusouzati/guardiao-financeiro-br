from __future__ import annotations

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Empresa usuária. No MVP há uma organização por implantação (ADR-010)."""

    __tablename__ = "organization"
    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="status_valid"),
        # CNPJ normalizado (ADR-008): 12 posições alfanuméricas + 2 dígitos verificadores.
        CheckConstraint(
            "tax_id IS NULL OR tax_id ~ '^[0-9A-Z]{12}[0-9]{2}$'", name="tax_id_format"
        ),
    )

    legal_name: Mapped[str] = mapped_column(String(200))
    tax_id: Mapped[str | None] = mapped_column(String(14), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", server_default="ACTIVE")
