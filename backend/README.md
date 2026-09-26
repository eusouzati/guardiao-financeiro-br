# Backend — Guardião Financeiro BR

API FastAPI + worker (a partir da Sprint 1). Python 3.13, gerenciado com **uv**.

## Estado (Sprint 0)

Somente estrutura de camadas e ferramentas de qualidade. Nenhuma dependência de runtime.

## Comandos

```bash
uv sync                      # cria .venv com Python 3.13 e ferramentas de dev
uv run ruff check .          # lint
uv run ruff format --check . # formatação
uv run mypy                  # type check (strict)
uv run pytest                # testes (inclui teste de arquitetura)
```

## Camadas

Ver [`../docs/architecture.md`](../docs/architecture.md) §4 e ADR-006. O teste
`tests/architecture/test_layer_dependencies.py` falha se uma camada importar outra que
lhe é proibida — por exemplo, um parser importando o ORM.
