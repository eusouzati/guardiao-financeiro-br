"""Casos de uso de configuração por organização."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.configuration import EffectivePolicy, resolve_policies
from app.repositories.configurations import ConfigurationRepository


def get_effective_policies(session: Session, organization_id: UUID) -> list[EffectivePolicy]:
    overrides = ConfigurationRepository(session).latest_overrides(organization_id)
    return resolve_policies(overrides)
