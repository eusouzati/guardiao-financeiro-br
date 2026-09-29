"""API atrás do Easy Auth (APP_ENV=mvp) com banco real (ADR-018)."""

from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.config.settings import AppEnv
from app.domain.errors import ErrorCode
from app.services.organizations import bootstrap_organization
from tests.conftest import ClientFactory
from tests.unit.test_easy_auth import TENANT, principal

pytestmark = pytest.mark.integration

EASY_AUTH = {
    "app_env": AppEnv.MVP,
    "dev_auth_enabled": False,
    "easy_auth_enabled": True,
    "entra_tenant_id": TENANT,
}


@pytest.fixture(autouse=True)
def organization(db_session: Session) -> None:
    bootstrap_organization(db_session, "Empresa Exemplo Alfa (fictícia)")
    db_session.commit()


def _headers(**kwargs: object) -> dict[str, str]:
    return {
        "X-MS-CLIENT-PRINCIPAL": principal(**kwargs),  # type: ignore[arg-type]
        "X-MS-CLIENT-PRINCIPAL-IDP": "aad",
    }


def test_me_uses_entra_identity_and_app_roles(client_factory: ClientFactory) -> None:
    client = client_factory(**EASY_AUTH)
    body = client.get("/api/v1/me", headers=_headers(roles=("APPROVER",))).json()
    assert body["auth_method"] == "EASY_AUTH"
    assert body["roles"] == ["APPROVER"]
    assert body["display_name"] == "Pessoa Exemplo"
    assert "EXCEPTION_DECIDE_CRITICAL" in body["permissions"]


def test_missing_principal_is_rejected(client_factory: ClientFactory) -> None:
    response = client_factory(**EASY_AUTH).get("/api/v1/me")
    assert response.status_code == 401
    assert response.json()["code"] == ErrorCode.NOT_AUTHENTICATED.value


def test_foreign_tenant_is_rejected(client_factory: ClientFactory) -> None:
    other = "99999999-2222-4333-8444-555555555555"
    response = client_factory(**EASY_AUTH).get("/api/v1/me", headers=_headers(tenant=other))
    assert response.status_code == 401


def test_user_without_app_role_has_no_access(client_factory: ClientFactory) -> None:
    response = client_factory(**EASY_AUTH).get("/api/v1/configurations", headers=_headers(roles=()))
    assert response.status_code == 403


def test_dev_headers_do_not_bypass_easy_auth(client_factory: ClientFactory) -> None:
    """Sem cabeçalho do Easy Auth não há fallback para identidade de desenvolvimento."""
    response = client_factory(**EASY_AUTH).get(
        "/api/v1/audit/events", headers={"X-Request-ID": "tentativa-123456"}
    )
    assert response.status_code == 401
