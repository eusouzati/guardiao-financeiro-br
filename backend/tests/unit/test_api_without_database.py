"""Comportamento HTTP que não depende do banco: auth, erros, headers, OpenAPI."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

import pytest
from fastapi import FastAPI, Query
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.domain.errors import ErrorCode
from app.main import create_app
from tests.conftest import make_settings


def _boom() -> None:
    raise RuntimeError("detalhe interno: /srv/segredo SELECT * FROM x")


def _count(n: Annotated[int, Query(ge=1)]) -> dict[str, int]:
    return {"n": n}


@pytest.fixture
def app() -> FastAPI:
    unreachable = SecretStr("postgresql://nobody@127.0.0.1:1/test_unreachable")
    application = create_app(make_settings(database_url=unreachable, db_connect_timeout_seconds=1))
    application.add_api_route("/api/v1/_test/boom", _boom)
    application.add_api_route("/api/v1/_test/count", _count)
    return application


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.mark.parametrize("path", ["/health", "/api/health/live"])
def test_liveness_does_not_need_database(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("path", ["/ready", "/api/health/ready"])
def test_readiness_reports_unavailable_database(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 503
    body = response.json()
    assert body["database"] == "unavailable"
    assert "segredo" not in response.text


@pytest.mark.parametrize("path", ["/api/v1/me", "/api/v1/configurations", "/api/v1/audit/events"])
def test_protected_routes_require_authentication_without_dev_auth(
    client: TestClient, path: str
) -> None:
    response = client.get(path)
    assert response.status_code == 401
    assert response.json()["code"] == ErrorCode.NOT_AUTHENTICATED.value
    assert response.headers["www-authenticate"] == "Bearer"


def test_request_id_is_generated_and_echoed(client: TestClient) -> None:
    generated = client.get("/api/health/live").headers["x-request-id"]
    assert len(generated) >= 8
    echoed = client.get("/api/health/live", headers={"X-Request-ID": "abc-12345678"})
    assert echoed.headers["x-request-id"] == "abc-12345678"


def test_malicious_request_id_is_replaced(client: TestClient) -> None:
    response = client.get("/api/health/live", headers={"X-Request-ID": 'x"; DROP TABLE y'})
    assert response.headers["x-request-id"] != 'x"; DROP TABLE y'


def test_security_headers_are_present(client: TestClient) -> None:
    headers = client.get("/api/health/live").headers
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"
    assert headers["referrer-policy"] == "no-referrer"
    assert "frame-ancestors 'none'" in headers["content-security-policy"]


def test_unknown_route_returns_standard_error(client: TestClient) -> None:
    response = client.get("/api/v1/nao-existe")
    assert response.status_code == 404
    body = response.json()
    assert body["code"] == ErrorCode.NOT_FOUND.value
    assert body["request_id"] == response.headers["x-request-id"]


def test_validation_errors_are_in_portuguese(client: TestClient) -> None:
    response = client.get("/api/v1/_test/count", params={"n": "0"})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == ErrorCode.VALIDATION_ERROR.value
    assert body["message"] == "Dados da requisição inválidos."
    assert body["details"] == [{"field": "n", "message": "Deve ser maior ou igual a 1."}]


def test_unhandled_error_hides_internal_details(client: TestClient) -> None:
    response = client.get("/api/v1/_test/boom")
    assert response.status_code == 500
    body = response.json()
    assert body["code"] == ErrorCode.INTERNAL_ERROR.value
    assert "segredo" not in response.text
    assert "SELECT" not in response.text
    assert "Traceback" not in response.text


def test_openapi_is_published_under_versioned_path(client: TestClient) -> None:
    schema = client.get("/api/v1/openapi.json").json()
    assert schema["info"]["title"].startswith("Guardião Financeiro BR")
    assert "/api/v1/configurations" in schema["paths"]
