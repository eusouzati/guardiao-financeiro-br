"""Verificações de saúde da aplicação."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DatabaseHealth:
    reachable: bool
    schema_revision: str | None


def check_database(session: Session) -> DatabaseHealth:
    """Confere conexão e revisão de schema (Alembic). Nunca propaga detalhes do erro."""
    try:
        session.execute(text("SELECT 1"))
        revision = session.execute(text("SELECT version_num FROM alembic_version")).scalar()
    except SQLAlchemyError:
        logger.warning("Banco de dados indisponível no health check", exc_info=True)
        session.rollback()
        return DatabaseHealth(reachable=False, schema_revision=None)
    return DatabaseHealth(reachable=True, schema_revision=revision)
