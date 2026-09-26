"""Engine e fábrica de sessões SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import URL, Engine, create_engine, make_url
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import Settings


def build_database_url(settings: Settings) -> URL:
    if settings.database_url is not None:
        url = make_url(settings.database_url.get_secret_value())
        if url.drivername in {"postgresql", "postgres"}:
            url = url.set(drivername="postgresql+psycopg")
        return url
    return URL.create(
        drivername="postgresql+psycopg",
        username=settings.postgres_user,
        password=settings.postgres_password.get_secret_value() or None,
        host=settings.postgres_host,
        port=settings.postgres_port,
        database=settings.postgres_db,
    )


def create_db_engine(settings: Settings) -> Engine:
    return create_engine(
        build_database_url(settings),
        pool_size=settings.db_pool_size,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": settings.db_connect_timeout_seconds,
            "application_name": "guardiao-financeiro-br",
            "options": "-c timezone=UTC",
        },
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
