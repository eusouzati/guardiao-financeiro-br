"""Garante as regras de dependência entre camadas do backend (ADR-018).

O teste analisa estaticamente (AST) os imports de cada módulo em ``app/`` e falha se uma
camada importar outra que lhe é proibida — por exemplo, ``parsers`` importando ``models``
ou SQLAlchemy.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parents[2] / "app"
APP_PACKAGE = "app"

LAYERS: frozenset[str] = frozenset(
    {
        "api",
        "audit",
        "config",
        "domain",
        "integrations",
        "matching",
        "models",
        "parsers",
        "repositories",
        "rules",
        "schemas",
        "security",
        "services",
    }
)

_INFRA_LIBS = frozenset({"sqlalchemy", "alembic", "fastapi", "starlette", "psycopg"})
_PURE_FORBIDDEN_LAYERS = frozenset(
    {"api", "services", "models", "repositories", "integrations", "audit", "security"}
)

# camada -> camadas internas proibidas
FORBIDDEN_LAYERS: dict[str, frozenset[str]] = {
    "domain": LAYERS - {"domain"},
    "parsers": _PURE_FORBIDDEN_LAYERS | {"schemas", "config"},
    "rules": _PURE_FORBIDDEN_LAYERS | {"schemas", "parsers"},
    "matching": _PURE_FORBIDDEN_LAYERS | {"schemas", "parsers"},
    "models": frozenset({"api", "services", "schemas"}),
    "repositories": frozenset({"api", "services", "schemas"}),
    "api": frozenset({"models", "repositories"}),
}

# camada -> bibliotecas de infraestrutura proibidas
FORBIDDEN_LIBS: dict[str, frozenset[str]] = {
    "domain": _INFRA_LIBS,
    "parsers": _INFRA_LIBS,
    "rules": _INFRA_LIBS,
    "matching": _INFRA_LIBS,
}


@dataclass(frozen=True)
class Violation:
    module: str
    imported: str
    reason: str

    def __str__(self) -> str:
        return f"{self.module} importa {self.imported!r}: {self.reason}"


def _imported_names(tree: ast.AST, module_parts: tuple[str, ...]) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # import relativo -> resolve para absoluto
                base = module_parts[: len(module_parts) - node.level]
                prefix = ".".join(base)
                target = f"{prefix}.{node.module}" if node.module else prefix
                if node.module is None:
                    names.extend(f"{target}.{alias.name}" for alias in node.names)
                else:
                    names.append(target)
            elif node.module:
                names.append(node.module)
    return names


def find_violations(source: str, module: str) -> list[Violation]:
    """Retorna as violações de camada de um módulo (``module`` no formato ``app.x.y``)."""
    parts = tuple(module.split("."))
    if len(parts) < 2 or parts[0] != APP_PACKAGE:
        return []
    layer = parts[1]
    tree = ast.parse(source)
    violations: list[Violation] = []
    for imported in _imported_names(tree, parts):
        top = imported.split(".")
        if top[0] == APP_PACKAGE and len(top) > 1:
            target_layer = top[1]
            if target_layer in FORBIDDEN_LAYERS.get(layer, frozenset()):
                reason = f"camada '{layer}' não pode depender de '{target_layer}'"
                violations.append(Violation(module, imported, reason))
        elif top[0] in FORBIDDEN_LIBS.get(layer, frozenset()):
            violations.append(
                Violation(module, imported, f"camada '{layer}' deve ser pura (sem '{top[0]}')")
            )
    return violations


def _iter_modules() -> list[tuple[str, Path]]:
    modules: list[tuple[str, Path]] = []
    for path in sorted(APP_DIR.rglob("*.py")):
        rel = path.relative_to(APP_DIR.parent).with_suffix("")
        parts = list(rel.parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        modules.append((".".join(parts), path))
    return modules


def test_every_layer_directory_is_classified() -> None:
    directories = {p.name for p in APP_DIR.iterdir() if p.is_dir() and p.name != "__pycache__"}
    assert directories == LAYERS, (
        "Toda nova camada em app/ precisa ser classificada em LAYERS "
        "e ter regras de dependência avaliadas (ADR-018)."
    )


def test_app_has_no_forbidden_dependencies() -> None:
    violations = [
        v
        for module, path in _iter_modules()
        for v in find_violations(path.read_text(encoding="utf-8"), module)
    ]
    assert not violations, "\n".join(str(v) for v in violations)


@pytest.mark.parametrize(
    ("module", "source"),
    [
        ("app.parsers.nfe", "from app.models.fiscal_document import FiscalDocument\n"),
        ("app.parsers.nfe", "import sqlalchemy\n"),
        ("app.rules.duplicates", "from ..repositories import documents\n"),
        ("app.domain.money", "from app.config import settings\n"),
        ("app.matching.engine", "from fastapi import Depends\n"),
        ("app.api.documents", "from app.repositories.documents import DocumentRepository\n"),
    ],
)
def test_checker_detects_forbidden_imports(module: str, source: str) -> None:
    assert find_violations(source, module), f"violação não detectada em {module}"


@pytest.mark.parametrize(
    ("module", "source"),
    [
        ("app.parsers.nfe", "from app.domain.fiscal_id import FiscalId\n"),
        ("app.rules.duplicates", "from app.domain import money\n"),
        ("app.services.documents", "from app.repositories.documents import DocumentRepository\n"),
        ("app.api.documents", "from app.services.documents import upload_document\n"),
        ("app.domain.money", "from decimal import Decimal\n"),
    ],
)
def test_checker_allows_permitted_imports(module: str, source: str) -> None:
    assert find_violations(source, module) == []
