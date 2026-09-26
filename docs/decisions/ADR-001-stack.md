# ADR-001 — Stack tecnológica e ferramentas

- **Status:** Aceita — aprovada pelo mantenedor em 2026-09-26
- **Data:** 2026-09-26
- **Sprint:** 0

## Contexto

O escopo define a stack: React + TypeScript + Vite + Tailwind CSS no frontend; Python +
FastAPI + Pydantic + SQLAlchemy no backend; PostgreSQL + Alembic; pytest, Vitest,
Playwright; Ruff, mypy/pyright, ESLint e Prettier. Faltava definir versões de runtime,
gerenciador de pacotes e o type checker Python.

## Decisão

| Item                 | Escolha                                    | Motivo                                                                                    |
| -------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------- |
| Python               | **3.13** (`.python-version`)               | Estável, suportado por FastAPI/SQLAlchemy/psycopg; 3.14 ainda recente para o ecossistema. |
| Gerenciador Python   | **uv** com `uv.lock`                       | Resolução rápida, lockfile reprodutível com hashes, gerencia a versão do Python.          |
| Type checker         | **mypy** (modo `strict`)                   | Maduro, integração com Pydantic via plugin. Pyright fica como alternativa no editor.      |
| Lint/format Python   | **Ruff** (lint + formatter)                | Uma ferramenta substitui flake8/isort/black.                                              |
| Node.js              | **24 LTS** (`.nvmrc`)                      | Linha LTS ativa.                                                                          |
| Gerenciador JS       | **npm** com `package-lock.json`            | Já vem com o Node; evita dependência extra.                                               |
| Testes               | pytest, Vitest, Playwright                 | Definidos no escopo.                                                                      |
| Format frontend/docs | Prettier; ESLint (flat config) na Sprint 1 | ESLint depende dos plugins React/TS instalados na Sprint 1.                               |
| Hooks locais         | pre-commit (opcional para o dev)           | Mesmas verificações do CI rodando antes do commit.                                        |

Regras de dependência:

- Nenhuma dependência é adicionada sem função definida; dependências relevantes são
  listadas em `docs/dependencies.md` com finalidade e licença.
- Versões fixadas por lockfile (`uv.lock`, `package-lock.json`).
- Licenças compatíveis com Apache-2.0 (sem GPL/AGPL no runtime distribuído).

## Alternativas consideradas

- **Poetry / pip-tools** — funcionais, porém mais lentos e sem gestão do interpretador.
- **pyright como checker principal** — excelente, mas exige Node no pipeline Python.
- **pnpm** — mais eficiente, porém adiciona ferramenta que a maioria dos contribuidores
  precisaria instalar.
- **Python 3.14** — reavaliar quando todas as dependências publicarem wheels estáveis.

## Consequências

- Contribuidores precisam de `uv` e Node 24 (ou apenas Docker, a partir da Sprint 1).
- Upgrades de runtime passam por nova ADR ou atualização desta.
