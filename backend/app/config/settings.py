"""Configuração da aplicação por variáveis de ambiente (pydantic-settings).

Regras de segurança aplicadas na carga (fail-fast, ADR-004):

- ``DEV_AUTH_ENABLED=true`` só é aceito com ``APP_ENV=local``. Em qualquer outro ambiente a
  aplicação **não inicia**.
- O padrão de ``DEV_AUTH_ENABLED`` é ``false``.
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from typing import Annotated, Literal, Self

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from app.domain.identity import Role


class AppEnv(StrEnum):
    LOCAL = "local"
    TEST = "test"
    HOMOLOGATION = "homologation"
    PRODUCTION = "production"


class InsecureConfigurationError(ValueError):
    """Configuração proibida por política de segurança."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,  # o .env é lido pelo Docker Compose / shell, não pela aplicação
        case_sensitive=False,
        extra="ignore",
    )

    app_env: AppEnv = AppEnv.LOCAL
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "console"] = "json"

    # Banco: DATABASE_URL tem precedência; senão, monta a partir de POSTGRES_*.
    database_url: SecretStr | None = None
    postgres_host: str = "localhost"
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_db: str = "guardiao"
    postgres_user: str = "guardiao"
    postgres_password: SecretStr = SecretStr("")
    db_pool_size: int = Field(default=5, ge=1, le=50)
    db_connect_timeout_seconds: int = Field(default=5, ge=1, le=60)

    # Autenticação DEV simulada (ADR-004)
    dev_auth_enabled: bool = False
    dev_auth_roles: Annotated[frozenset[Role], NoDecode] = frozenset({Role.ADMIN})
    dev_auth_user_name: str = "Usuário de desenvolvimento"

    # Inicialização de ambiente (python -m app.cli bootstrap)
    bootstrap_organization_name: str = "Organização Demonstração (fictícia)"

    @field_validator("dev_auth_roles", mode="before")
    @classmethod
    def _parse_roles(cls, value: object) -> object:
        if isinstance(value, str):
            items = [item.strip().upper() for item in value.split(",") if item.strip()]
            return frozenset(Role(item) for item in items)
        return value

    @model_validator(mode="after")
    def _enforce_security_policies(self) -> Self:
        if self.dev_auth_enabled and self.app_env is not AppEnv.LOCAL:
            raise InsecureConfigurationError(
                "DEV_AUTH_ENABLED=true só é permitido com APP_ENV=local "
                f"(APP_ENV atual: {self.app_env.value}). A aplicação não será iniciada."
            )
        if self.dev_auth_enabled and not self.dev_auth_roles:
            raise InsecureConfigurationError("DEV_AUTH_ROLES não pode ser vazio.")
        return self

    @property
    def is_production_like(self) -> bool:
        return self.app_env in {AppEnv.HOMOLOGATION, AppEnv.PRODUCTION}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
