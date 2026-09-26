"""Perfis de acesso (ADR-004)."""

from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    """Perfis iniciais. A matriz de permissões fica em ``app.security.permissions``."""

    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    APPROVER = "APPROVER"
    AUDITOR = "AUDITOR"
