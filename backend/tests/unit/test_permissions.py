"""Matriz de permissões por perfil (docs/security.md §3)."""

from __future__ import annotations

import uuid

import pytest

from app.domain.identity import Role
from app.security.permissions import Permission, permissions_for
from app.security.principal import AuthMethod, Principal

P = Permission

EXPECTED: dict[Role, set[Permission]] = {
    Role.ADMIN: set(Permission),
    Role.ANALYST: {
        P.DASHBOARD_READ, P.DOCUMENT_READ, P.CONFIGURATION_READ, P.DOCUMENT_UPLOAD,
        P.IMPORT_RUN, P.EXCEPTION_DECIDE_WARNING, P.REANALYSIS_REQUEST,
    },
    Role.APPROVER: {
        P.DASHBOARD_READ, P.DOCUMENT_READ, P.CONFIGURATION_READ, P.EXCEPTION_DECIDE_WARNING,
        P.EXCEPTION_DECIDE_CRITICAL, P.REANALYSIS_REQUEST,
    },
    Role.AUDITOR: {P.DASHBOARD_READ, P.DOCUMENT_READ, P.CONFIGURATION_READ, P.AUDIT_READ},
}  # fmt: skip


@pytest.mark.parametrize("role", list(Role))
def test_role_matrix_matches_documentation(role: Role) -> None:
    assert permissions_for([role]) == EXPECTED[role]


def test_only_admin_and_approver_decide_critical_exceptions() -> None:
    allowed = {r for r in Role if P.EXCEPTION_DECIDE_CRITICAL in permissions_for([r])}
    assert allowed == {Role.ADMIN, Role.APPROVER}


def test_auditor_is_read_only() -> None:
    writes = {
        P.DOCUMENT_UPLOAD, P.IMPORT_RUN, P.EXCEPTION_DECIDE_WARNING, P.EXCEPTION_DECIDE_CRITICAL,
        P.REANALYSIS_REQUEST, P.CONFIGURATION_MANAGE, P.MAILBOX_MANAGE,
    }  # fmt: skip
    assert not permissions_for([Role.AUDITOR]) & writes


def test_permissions_are_union_of_roles() -> None:
    combined = permissions_for([Role.ANALYST, Role.AUDITOR])
    assert P.AUDIT_READ in combined
    assert P.DOCUMENT_UPLOAD in combined


def test_principal_without_roles_has_no_permissions() -> None:
    principal = Principal("u", "U", frozenset(), uuid.uuid4(), AuthMethod.DEV)
    assert not principal.permissions
    assert not principal.can(P.DASHBOARD_READ)
