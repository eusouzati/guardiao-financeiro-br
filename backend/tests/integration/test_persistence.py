"""Regras de persistência: bootstrap idempotente, append-only e escopo por organização."""

from __future__ import annotations

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from app.domain.errors import OrganizationNotInitializedError
from app.models import AuditEvent, ConfigurationEntry
from app.repositories.configurations import ConfigurationRepository
from app.services.configurations import get_effective_policies
from app.services.organizations import bootstrap_organization, get_current_organization

pytestmark = pytest.mark.integration


def test_current_organization_requires_bootstrap(db_session: Session) -> None:
    with pytest.raises(OrganizationNotInitializedError):
        get_current_organization(db_session)


def test_bootstrap_is_idempotent_and_audited(db_session: Session) -> None:
    first, created_first = bootstrap_organization(db_session, "Empresa Exemplo Alfa (fictícia)")
    second, created_second = bootstrap_organization(db_session, "Outro nome")
    assert (created_first, created_second) == (True, False)
    assert first == second
    events = db_session.scalar(
        select(func.count())
        .select_from(AuditEvent)
        .where(AuditEvent.event_type == "ORGANIZATION_CREATED")
    )
    assert events == 1


def test_audit_event_is_append_only(db_session: Session) -> None:
    bootstrap_organization(db_session, "Empresa Exemplo Alfa (fictícia)")
    db_session.flush()
    with pytest.raises(DBAPIError, match="append-only"), db_session.begin_nested():
        db_session.execute(text("UPDATE audit_event SET actor_id = 'x'"))
    with pytest.raises(DBAPIError, match="append-only"), db_session.begin_nested():
        db_session.execute(text("DELETE FROM audit_event"))
    with pytest.raises(DBAPIError, match="append-only"), db_session.begin_nested():
        db_session.execute(text("TRUNCATE audit_event CASCADE"))


def test_configuration_is_versioned_and_append_only(db_session: Session) -> None:
    org, _ = bootstrap_organization(db_session, "Empresa Exemplo Alfa (fictícia)")
    for version, value in ((1, "0.10"), (2, "0.25")):
        db_session.add(
            ConfigurationEntry(
                organization_id=org.id,
                key="amount_tolerance_absolute",
                value=value,
                version=version,
                changed_by="tester",
            )
        )
    db_session.flush()

    latest = ConfigurationRepository(db_session).latest_overrides(org.id)
    assert latest["amount_tolerance_absolute"].version == 2

    effective = {p.definition.key: p for p in get_effective_policies(db_session, org.id)}
    assert str(effective["amount_tolerance_absolute"].value) == "0.25"

    with pytest.raises(DBAPIError, match="append-only"), db_session.begin_nested():
        db_session.execute(text("UPDATE configuration SET value = '\"9\"'::jsonb"))

    duplicate = ConfigurationEntry(
        organization_id=org.id,
        key="amount_tolerance_absolute",
        value="1.00",
        version=2,  # versão duplicada
        changed_by="tester",
    )
    savepoint = db_session.begin_nested()
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.flush()
    savepoint.rollback()


def test_invalid_tax_id_is_rejected_by_database(db_session: Session) -> None:
    with pytest.raises(IntegrityError), db_session.begin_nested():
        db_session.execute(
            text(
                "INSERT INTO organization (id, legal_name, tax_id) "
                "VALUES (gen_random_uuid(), 'X', '12.345')"
            )
        )
