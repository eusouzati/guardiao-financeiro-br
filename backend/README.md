# Backend — Guardião Financeiro BR

API FastAPI (Python 3.13, gerenciado com **uv**). Arquitetura em camadas: ver
[`../docs/architecture.md`](../docs/architecture.md) §4 e ADR-006. Endpoints em
[`../docs/api.md`](../docs/api.md); códigos de erro em
[`../docs/error-codes.md`](../docs/error-codes.md).

## Execução

```bash
uv sync
export APP_ENV=local DEV_AUTH_ENABLED=true POSTGRES_PASSWORD=<senha>   # ver .env.example
uv run alembic upgrade head          # migrations
uv run python -m app.cli bootstrap   # organização padrão (idempotente)
uv run uvicorn app.main:create_app --factory --reload --port 8000
```

OpenAPI: <http://localhost:8000/api/docs>.

## Qualidade

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy                     # strict
uv run pytest --cov             # integração exige TEST_DATABASE_URL (banco com "test" no nome)
```

## Estrutura

```text
app/
├── api/           # rotas, dependências (auth/permissões), middleware, tratamento de erros
├── schemas/       # modelos Pydantic da API
├── services/      # casos de uso
├── domain/        # regras puras: dinheiro, políticas, erros, perfis, auditoria
├── models/        # ORM SQLAlchemy
├── repositories/  # acesso a dados (sempre por organization_id)
├── security/      # permissões e identidade
├── config/        # settings e logging
├── parsers/ rules/ matching/ integrations/ audit/   # sprints seguintes
├── main.py        # fábrica da aplicação
└── cli.py         # comandos administrativos
migrations/        # Alembic
tests/             # unit/, integration/, architecture/
```

O teste `tests/architecture/test_layer_dependencies.py` falha se uma camada importar outra
que lhe é proibida — por exemplo, um parser importando o ORM.
