"""Logs estruturados sem dados sensíveis (seção 27)."""

from __future__ import annotations

import json
import logging

from app.config.logging import REDACTED, JsonFormatter, redact, request_id_var


def test_redact_masks_sensitive_keys_recursively() -> None:
    data = {
        "user": "ana",
        "password": "x",
        "nested": {"access_token": "t", "items": [{"client_secret": "s", "ok": 1}]},
        "Authorization": "Bearer abc",
    }
    result = redact(data)
    assert result["user"] == "ana"
    assert result["password"] == REDACTED
    assert result["Authorization"] == REDACTED
    assert result["nested"]["access_token"] == REDACTED
    assert result["nested"]["items"][0] == {"client_secret": REDACTED, "ok": 1}


def test_json_formatter_includes_request_id_and_redacted_context() -> None:
    token = request_id_var.set("req-12345678")
    try:
        record = logging.LogRecord("t", logging.INFO, __file__, 1, "msg", None, None)
        record.ctx = {"path": "/x", "db_password": "segredo"}
        payload = json.loads(JsonFormatter().format(record))
    finally:
        request_id_var.reset(token)
    assert payload["request_id"] == "req-12345678"
    assert payload["path"] == "/x"
    assert payload["db_password"] == REDACTED
    assert "segredo" not in json.dumps(payload)
