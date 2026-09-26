"""Verificações de sanidade do pacote na Sprint 0."""

from __future__ import annotations

import re

import app


def test_version_is_semver() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", app.__version__)
