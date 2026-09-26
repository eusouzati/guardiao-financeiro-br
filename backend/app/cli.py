"""Comandos administrativos.

Uso::

    python -m app.cli bootstrap   # cria a organização padrão, se não existir (idempotente)
"""

from __future__ import annotations

import argparse
import logging
import sys

from app.config.logging import configure_logging
from app.config.settings import get_settings
from app.repositories.database import create_db_engine, create_session_factory
from app.services.organizations import bootstrap_organization

logger = logging.getLogger("app.cli")


def _bootstrap() -> int:
    settings = get_settings()
    engine = create_db_engine(settings)
    try:
        factory = create_session_factory(engine)
        with factory.begin() as session:
            organization, created = bootstrap_organization(
                session, settings.bootstrap_organization_name
            )
        message = "Organização criada" if created else "Organização já existente"
        logger.info(message, extra={"ctx": {"organization_id": str(organization.id)}})
        return 0
    finally:
        engine.dispose()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("bootstrap", help="Cria a organização padrão, se não existir.")
    args = parser.parse_args(argv)
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_format)
    if args.command == "bootstrap":
        return _bootstrap()
    return 2  # pragma: no cover - argparse já rejeita comandos desconhecidos


if __name__ == "__main__":
    sys.exit(main())
