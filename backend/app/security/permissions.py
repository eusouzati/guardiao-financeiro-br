"""Matriz perfil x permissão (docs/security.md §3, ADR-004).

A autorização é sempre decidida no backend. O frontend recebe a lista de permissões
apenas para adaptar a experiência visual.
"""

from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum

from app.domain.identity import Role


class Permission(StrEnum):
    DASHBOARD_READ = "DASHBOARD_READ"
    DOCUMENT_READ = "DOCUMENT_READ"
    DOCUMENT_UPLOAD = "DOCUMENT_UPLOAD"
    IMPORT_RUN = "IMPORT_RUN"
    EXCEPTION_DECIDE_WARNING = "EXCEPTION_DECIDE_WARNING"
    EXCEPTION_DECIDE_CRITICAL = "EXCEPTION_DECIDE_CRITICAL"
    REANALYSIS_REQUEST = "REANALYSIS_REQUEST"
    CONFIGURATION_READ = "CONFIGURATION_READ"
    CONFIGURATION_MANAGE = "CONFIGURATION_MANAGE"
    MAILBOX_MANAGE = "MAILBOX_MANAGE"
    AUDIT_READ = "AUDIT_READ"


_READ = frozenset(
    {Permission.DASHBOARD_READ, Permission.DOCUMENT_READ, Permission.CONFIGURATION_READ}
)

ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(Permission),
    Role.ANALYST: _READ
    | {
        Permission.DOCUMENT_UPLOAD,
        Permission.IMPORT_RUN,
        Permission.EXCEPTION_DECIDE_WARNING,
        Permission.REANALYSIS_REQUEST,
    },
    Role.APPROVER: _READ
    | {
        Permission.EXCEPTION_DECIDE_WARNING,
        Permission.EXCEPTION_DECIDE_CRITICAL,
        Permission.REANALYSIS_REQUEST,
    },
    Role.AUDITOR: _READ | {Permission.AUDIT_READ},
}


def permissions_for(roles: Iterable[Role]) -> frozenset[Permission]:
    granted: set[Permission] = set()
    for role in roles:
        granted |= ROLE_PERMISSIONS[role]
    return frozenset(granted)
