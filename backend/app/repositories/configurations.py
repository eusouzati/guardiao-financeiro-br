from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import distinct_on
from sqlalchemy.orm import Session

from app.domain.configuration import StoredPolicyOverride
from app.models.configuration import ConfigurationEntry


class ConfigurationRepository:
    """Sobrescritas versionadas de políticas, sempre escopadas por organização (ADR-010)."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def latest_overrides(self, organization_id: UUID) -> dict[str, StoredPolicyOverride]:
        stmt = (
            select(ConfigurationEntry)
            .where(ConfigurationEntry.organization_id == organization_id)
            .order_by(ConfigurationEntry.key, ConfigurationEntry.version.desc())
            .ext(distinct_on(ConfigurationEntry.key))
        )
        return {
            entry.key: StoredPolicyOverride(
                key=entry.key,
                raw_value=entry.value,
                version=entry.version,
                changed_by=entry.changed_by,
                changed_at=entry.changed_at,
            )
            for entry in self._session.scalars(stmt)
        }
