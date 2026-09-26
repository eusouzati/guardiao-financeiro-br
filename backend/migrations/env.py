"""Ambiente Alembic: usa a mesma configuração (variáveis de ambiente) da aplicação."""

from __future__ import annotations

from alembic import context
from sqlalchemy import Connection

from app.config.settings import get_settings
from app.models import Base
from app.repositories.database import create_db_engine

target_metadata = Base.metadata


def _configure(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        transaction_per_migration=True,
    )


def run_migrations_online() -> None:
    external: Connection | None = context.config.attributes.get("connection")
    if external is not None:  # usado pelos testes de integração
        _configure(external)
        with context.begin_transaction():
            context.run_migrations()
        return
    engine = create_db_engine(get_settings())
    try:
        with engine.connect() as connection:
            _configure(connection)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    raise SystemExit("Modo offline não suportado: execute as migrations contra um banco.")
run_migrations_online()
