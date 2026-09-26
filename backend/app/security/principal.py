"""Identidade autenticada de uma requisição."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID

from app.domain.identity import Role
from app.security.permissions import Permission, permissions_for


class AuthMethod(StrEnum):
    DEV = "DEV"  # autenticação simulada — somente APP_ENV=local (ADR-004)
    ENTRA_ID = "ENTRA_ID"  # Sprint 7


@dataclass(frozen=True, slots=True)
class Principal:
    user_id: str
    display_name: str
    roles: frozenset[Role]
    organization_id: UUID
    auth_method: AuthMethod
    permissions: frozenset[Permission] = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "permissions", permissions_for(self.roles))

    def can(self, permission: Permission) -> bool:
        return permission in self.permissions
