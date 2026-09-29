"""Dependências FastAPI: configuração, sessão de banco, identidade e autorização."""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session, sessionmaker

from app.config.logging import organization_id_var
from app.config.settings import AppEnv, Settings
from app.domain.errors import NotAuthenticatedError, PermissionDeniedError
from app.security.easy_auth import IDP_HEADER, PRINCIPAL_HEADER, parse_client_principal
from app.security.permissions import Permission
from app.security.principal import AuthMethod, Principal
from app.services.organizations import get_current_organization

logger = logging.getLogger(__name__)


def get_settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


def get_session(request: Request) -> Iterator[Session]:
    factory: sessionmaker[Session] = request.app.state.session_factory
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[Session, Depends(get_session)]


def get_current_principal(
    request: Request, settings: SettingsDep, session: SessionDep
) -> Principal:
    """Resolve a identidade da requisição.

    - Autenticação DEV: somente quando ``APP_ENV=local`` e ``DEV_AUTH_ENABLED=true``
      (a combinação é validada na carga das configurações; conferida de novo aqui).
    - Easy Auth (Entra ID + App Roles): ``EASY_AUTH_ENABLED=true`` no ambiente MVP,
      atrás do sidecar do Container Apps (ADR-018).
    - Validação JWT direta do Entra ID: Sprint 7.
    Sem nenhum dos modos, toda rota protegida retorna 401.
    """
    if settings.easy_auth_enabled and settings.entra_tenant_id:
        identity = parse_client_principal(
            request.headers.get(PRINCIPAL_HEADER),
            idp=request.headers.get(IDP_HEADER),
            expected_tenant_id=settings.entra_tenant_id,
        )
        organization = get_current_organization(session)
        organization_id_var.set(str(organization.id))
        return Principal(
            user_id=identity.object_id,
            display_name=identity.display_name,
            roles=identity.roles,
            organization_id=organization.id,
            auth_method=AuthMethod.EASY_AUTH,
        )
    if settings.dev_auth_enabled and settings.app_env is AppEnv.LOCAL:
        organization = get_current_organization(session)
        organization_id_var.set(str(organization.id))
        return Principal(
            user_id="dev-user",
            display_name=settings.dev_auth_user_name,
            roles=settings.dev_auth_roles,
            organization_id=organization.id,
            auth_method=AuthMethod.DEV,
        )
    raise NotAuthenticatedError()


PrincipalDep = Annotated[Principal, Depends(get_current_principal)]


def require(permission: Permission) -> Callable[[Principal], Principal]:
    """Cria dependência que exige ``permission`` do usuário autenticado."""

    def _checker(principal: PrincipalDep) -> Principal:
        if not principal.can(permission):
            logger.info(
                "Acesso negado",
                extra={"ctx": {"user_id": principal.user_id, "permission": permission.value}},
            )
            raise PermissionDeniedError()
        return principal

    return _checker
