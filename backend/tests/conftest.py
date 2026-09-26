"""Fixtures compartilhadas.

Testes de integração exigem ``TEST_DATABASE_URL`` apontando para um banco PostgreSQL cujo
nome contenha ``test`` (proteção contra apagar um banco real). Sem a variável, são pulados.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import Connection, Engine, create_engine, make_url, text
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import AppEnv, Settings
from app.domain.identity import Role
from app.main import create_app

BACKEND_DIR = Path(__file__).resolve().parents[1]
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")


def make_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "app_env": AppEnv.TEST,
        "log_format": "console",
        "database_url": SecretStr(TEST_DATABASE_URL or "postgresql://nobody@127.0.0.1:1/test_none"),
        "dev_auth_enabled": False,
    }
    values.update(overrides)
    return Settings(**values)  # type: ignore[arg-type]


def alembic_config(connection: Connection) -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    cfg.attributes["connection"] = connection
    return cfg


def sqlalchemy_url(url: str) -> str:
    parsed = make_url(url)
    if parsed.drivername in {"postgresql", "postgres"}:
        parsed = parsed.set(drivername="postgresql+psycopg")
    return parsed.render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def migrated_engine() -> Iterator[Engine]:
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL não definido: testes de integração pulados.")
    database = make_url(TEST_DATABASE_URL).database or ""
    if "test" not in database:
        pytest.fail("TEST_DATABASE_URL deve apontar para um banco cujo nome contenha 'test'.")
    engine = create_engine(sqlalchemy_url(TEST_DATABASE_URL))
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    with engine.begin() as conn:
        command.upgrade(alembic_config(conn), "head")
    yield engine
    engine.dispose()


@pytest.fixture
def db_connection(migrated_engine: Engine) -> Iterator[Connection]:
    """Conexão com transação externa desfeita ao final (isola cada teste)."""
    connection = migrated_engine.connect()
    transaction = connection.begin()
    try:
        yield connection
    finally:
        transaction.rollback()
        connection.close()


@pytest.fixture
def session_factory(db_connection: Connection) -> sessionmaker[Session]:
    return sessionmaker(
        bind=db_connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
        autoflush=False,
    )


@pytest.fixture
def db_session(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


type ClientFactory = Callable[..., TestClient]


@pytest.fixture
def client_factory(session_factory: sessionmaker[Session]) -> Iterator[ClientFactory]:
    """Cria TestClient com DEV auth (APP_ENV=local) ligado ao banco transacional do teste."""
    clients: list[TestClient] = []

    def _factory(roles: frozenset[Role] = frozenset({Role.ADMIN})) -> TestClient:
        settings = make_settings(app_env=AppEnv.LOCAL, dev_auth_enabled=True, dev_auth_roles=roles)
        app: FastAPI = create_app(settings)
        client = TestClient(app, raise_server_exceptions=False)
        client.__enter__()
        app.state.session_factory = session_factory  # substitui o criado no lifespan
        clients.append(client)
        return client

    yield _factory
    for client in clients:
        client.__exit__(None, None, None)
