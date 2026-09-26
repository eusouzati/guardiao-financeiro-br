"""Verificações de sanidade do pacote."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import app


def test_version_is_pep440() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+(\.dev\d+)?", app.__version__)


def test_version_matches_pyproject() -> None:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    assert data["project"]["version"] == app.__version__
