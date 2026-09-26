"""Travas de configuração da autenticação DEV (ADR-004)."""

from __future__ import annotations

import pytest
from pydantic import SecretStr, ValidationError

from app.config.settings import AppEnv, Settings
from app.domain.identity import Role
from app.repositories.database import build_database_url


@pytest.mark.parametrize("env", [AppEnv.TEST, AppEnv.HOMOLOGATION, AppEnv.PRODUCTION])
def test_dev_auth_is_rejected_outside_local(env: AppEnv) -> None:
    with pytest.raises(ValidationError, match="DEV_AUTH_ENABLED=true só é permitido"):
        Settings(app_env=env, dev_auth_enabled=True)


def test_dev_auth_is_rejected_from_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEV_AUTH_ENABLED", "true")
    with pytest.raises(ValidationError):
        Settings()


def test_dev_auth_is_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEV_AUTH_ENABLED", raising=False)
    assert Settings().dev_auth_enabled is False


def test_dev_auth_allowed_only_in_local() -> None:
    settings = Settings(app_env=AppEnv.LOCAL, dev_auth_enabled=True)
    assert settings.dev_auth_enabled is True


def test_dev_auth_roles_parsed_from_comma_separated_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEV_AUTH_ROLES", "analyst, auditor")
    assert Settings().dev_auth_roles == frozenset({Role.ANALYST, Role.AUDITOR})


def test_unknown_dev_role_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEV_AUTH_ROLES", "SUPERUSER")
    with pytest.raises(ValidationError):
        Settings()


def test_database_url_takes_precedence_and_uses_psycopg() -> None:
    settings = Settings(database_url=SecretStr("postgresql://u:p@db:5432/x"))
    url = build_database_url(settings)
    assert url.drivername == "postgresql+psycopg"
    assert url.host == "db"


def test_database_url_built_from_components() -> None:
    settings = Settings(
        postgres_host="db", postgres_db="guardiao", postgres_password=SecretStr("segredo")
    )
    url = build_database_url(settings)
    assert (url.host, url.database, url.password) == ("db", "guardiao", "segredo")


def test_secrets_are_not_exposed_in_repr() -> None:
    settings = Settings(postgres_password=SecretStr("segredo-local"))
    assert "segredo-local" not in repr(settings)
