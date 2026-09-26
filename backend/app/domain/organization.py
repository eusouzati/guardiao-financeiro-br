"""Visão de domínio da organização (sem dependência de ORM)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class OrganizationInfo:
    id: UUID
    legal_name: str
    tax_id: str | None
