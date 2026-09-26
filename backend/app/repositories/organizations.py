from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.organization import OrganizationInfo
from app.models.organization import Organization


def _to_info(org: Organization) -> OrganizationInfo:
    return OrganizationInfo(id=org.id, legal_name=org.legal_name, tax_id=org.tax_id)


class OrganizationRepository:
    """Organizações. No MVP há uma por implantação: a organização ativa mais antiga."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_default(self) -> OrganizationInfo | None:
        stmt = (
            select(Organization)
            .where(Organization.status == "ACTIVE")
            .order_by(Organization.created_at, Organization.id)
            .limit(1)
        )
        org = self._session.scalars(stmt).first()
        return _to_info(org) if org else None

    def create(self, legal_name: str, tax_id: str | None = None) -> OrganizationInfo:
        org = Organization(legal_name=legal_name, tax_id=tax_id)
        self._session.add(org)
        self._session.flush()
        return _to_info(org)
