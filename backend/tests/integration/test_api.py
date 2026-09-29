"""API com banco real: health, identidade, configurações, auditoria e autorização."""

from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.domain.errors import ErrorCode
from app.domain.identity import Role
from app.services.organizations import bootstrap_organization
from tests.conftest import ClientFactory

pytestmark = pytest.mark.integration

ORG_NAME = "Empresa Exemplo Alfa (fictícia)"


@pytest.fixture
def organization(db_session: Session) -> None:
    bootstrap_organization(db_session, ORG_NAME)
    db_session.commit()


@pytest.mark.parametrize("path", ["/ready", "/api/health/ready"])
def test_readiness_ok_with_migrated_database(client_factory: ClientFactory, path: str) -> None:
    response = client_factory().get(path)
    assert response.status_code == 200
    body = response.json()
    assert body["database"] == "ok"
    assert body["schema_revision"] == "0001"


def test_me_requires_initialized_organization(client_factory: ClientFactory) -> None:
    response = client_factory().get("/api/v1/me")
    assert response.status_code == 503
    assert response.json()["code"] == ErrorCode.ORGANIZATION_NOT_INITIALIZED.value


@pytest.mark.usefixtures("organization")
def test_me_returns_dev_identity_and_permissions(client_factory: ClientFactory) -> None:
    body = client_factory(frozenset({Role.ANALYST})).get("/api/v1/me").json()
    assert body["auth_method"] == "DEV"
    assert body["roles"] == ["ANALYST"]
    assert "DOCUMENT_UPLOAD" in body["permissions"]
    assert "AUDIT_READ" not in body["permissions"]
    assert body["organization"]["legal_name"] == ORG_NAME


@pytest.mark.usefixtures("organization")
def test_configurations_expose_effective_policies_with_decimal_strings(
    client_factory: ClientFactory,
) -> None:
    response = client_factory(frozenset({Role.AUDITOR})).get("/api/v1/configurations")
    assert response.status_code == 200
    items = {i["key"]: i for i in response.json()["items"]}
    tolerance = items["amount_tolerance_absolute"]
    assert tolerance["value"] == "0.05"  # string, nunca float
    assert tolerance["source"] == "DEFAULT"
    assert items["purchase_order_required"]["value"] is True
    assert items["duplicate_window_days"]["value"] == 30


@pytest.mark.usefixtures("organization")
@pytest.mark.parametrize(
    ("role", "status"),
    [(Role.ADMIN, 200), (Role.AUDITOR, 200), (Role.ANALYST, 403), (Role.APPROVER, 403)],
)
def test_audit_access_is_enforced_by_backend(
    client_factory: ClientFactory, role: Role, status: int
) -> None:
    response = client_factory(frozenset({role})).get("/api/v1/audit/events")
    assert response.status_code == status
    if status == 403:
        assert response.json()["code"] == ErrorCode.PERMISSION_DENIED.value


@pytest.mark.usefixtures("organization")
def test_audit_events_are_paginated(client_factory: ClientFactory) -> None:
    body = client_factory().get("/api/v1/audit/events", params={"page_size": 1}).json()
    assert body["meta"] == {"page": 1, "page_size": 1, "total": 1}
    assert body["items"][0]["event_type"] == "ORGANIZATION_CREATED"


@pytest.mark.usefixtures("organization")
def test_page_size_is_limited(client_factory: ClientFactory) -> None:
    response = client_factory().get("/api/v1/audit/events", params={"page_size": 1000})
    assert response.status_code == 422
