"""Comando de inicialização (python -m app.cli bootstrap) em banco descartável."""

from __future__ import annotations

import pytest
from alembic import command
from sqlalchemy import Engine, func, select

from app.cli import main
from app.config.settings import get_settings
from app.models import AuditEvent, Organization
from tests.conftest import alembic_config
from tests.integration.test_migrations import scratch_engine

pytestmark = pytest.mark.integration

__all__ = ["scratch_engine"]  # fixture reutilizada


def test_bootstrap_command_is_idempotent(
    scratch_engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    with scratch_engine.begin() as conn:
        command.upgrade(alembic_config(conn), "head")
    monkeypatch.setenv("DATABASE_URL", scratch_engine.url.render_as_string(hide_password=False))
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DEV_AUTH_ENABLED", "false")
    get_settings.cache_clear()
    try:
        assert main(["bootstrap"]) == 0
        assert main(["bootstrap"]) == 0
    finally:
        get_settings.cache_clear()

    with scratch_engine.connect() as conn:
        organizations = conn.scalar(select(func.count()).select_from(Organization))
        events = conn.scalar(select(func.count()).select_from(AuditEvent))
    assert (organizations, events) == (1, 1)
