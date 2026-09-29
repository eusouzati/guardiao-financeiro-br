"""Leitura da identidade do Easy Auth (ADR-006)."""

from __future__ import annotations

import base64
import json

import pytest
from pydantic import ValidationError

from app.config.settings import AppEnv, Settings
from app.domain.errors import NotAuthenticatedError
from app.domain.identity import Role
from app.security.easy_auth import MAX_HEADER_BYTES, parse_client_principal

TENANT = "11111111-2222-4333-8444-555555555555"  # fictício
OID = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"  # fictício


def encode(payload: object) -> str:
    return base64.b64encode(json.dumps(payload).encode()).decode()


def principal(*, tenant: str = TENANT, roles: tuple[str, ...] = ("ADMIN",)) -> str:
    claims = [
        {"typ": "http://schemas.microsoft.com/identity/claims/objectidentifier", "val": OID},
        {"typ": "http://schemas.microsoft.com/identity/claims/tenantid", "val": tenant},
        {"typ": "name", "val": "Pessoa Exemplo"},
        *({"typ": "roles", "val": role} for role in roles),
    ]
    return encode({"auth_typ": "aad", "claims": claims, "role_typ": "roles"})


def test_valid_principal_maps_identity_and_app_roles() -> None:
    identity = parse_client_principal(
        principal(roles=("ANALYST", "auditor", "IGNORADO")), idp="aad", expected_tenant_id=TENANT
    )
    assert identity.object_id == OID
    assert identity.display_name == "Pessoa Exemplo"
    assert identity.roles == frozenset({Role.ANALYST, Role.AUDITOR})


def test_user_without_app_roles_has_no_roles() -> None:
    identity = parse_client_principal(principal(roles=()), idp="aad", expected_tenant_id=TENANT)
    assert identity.roles == frozenset()


@pytest.mark.parametrize(
    ("header", "idp"),
    [
        (None, "aad"),
        ("", "aad"),
        ("não-é-base64!!", "aad"),
        (encode(["lista"]), "aad"),
        (encode({"claims": "x"}), "aad"),
        (encode({"claims": [{"typ": "name", "val": "Sem OID"}]}), "aad"),
        (principal(), "google"),
        (principal(tenant="99999999-2222-4333-8444-555555555555"), "aad"),
        ("A" * (MAX_HEADER_BYTES + 1), "aad"),
    ],
)
def test_invalid_or_foreign_principals_are_rejected(header: str | None, idp: str) -> None:
    with pytest.raises(NotAuthenticatedError):
        parse_client_principal(header, idp=idp, expected_tenant_id=TENANT)


def test_easy_auth_requires_cloud_environment() -> None:
    with pytest.raises(ValidationError, match="EASY_AUTH_ENABLED=true só é permitido"):
        Settings(app_env=AppEnv.LOCAL, easy_auth_enabled=True, entra_tenant_id=TENANT)
    with pytest.raises(ValidationError, match="EASY_AUTH_ENABLED=true só é permitido"):
        Settings(app_env=AppEnv.TEST, easy_auth_enabled=True, entra_tenant_id=TENANT)


def test_easy_auth_requires_tenant() -> None:
    with pytest.raises(ValidationError, match="ENTRA_TENANT_ID"):
        Settings(app_env=AppEnv.MVP, easy_auth_enabled=True)


def test_easy_auth_and_dev_auth_are_mutually_exclusive() -> None:
    with pytest.raises(ValidationError):
        Settings(
            app_env=AppEnv.MVP,
            easy_auth_enabled=True,
            entra_tenant_id=TENANT,
            dev_auth_enabled=True,
        )


def test_easy_auth_allowed_in_mvp() -> None:
    settings = Settings(app_env=AppEnv.MVP, easy_auth_enabled=True, entra_tenant_id=TENANT)
    assert settings.easy_auth_enabled
