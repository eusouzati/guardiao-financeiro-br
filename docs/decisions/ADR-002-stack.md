# ADR-002 — Stack tecnológica e ferramentas

- **Status:** PROPOSED
- **Data:** 2026-09-29
- **Sprint:** 0
- **Histórico:** decisão equivalente aprovada pelo mantenedor em 2026-09-26 no plano anterior; reapresentada no plano Cloud-First.

## Contexto

O plano define a stack: React + TypeScript + Vite + Tailwind CSS no frontend; Python 3.13 +
FastAPI + Pydantic + SQLAlchemy + Alembic no backend; `uv` com lockfile; PostgreSQL 18;
pytest, Vitest e Playwright. Faltava fixar versões de runtime, ferramentas e o type
checker Python. A base já implementada usa React 19, React Router 8, Vite 8, Tailwind 4,
TypeScript 6 e ESLint 9 (ver [ADR-020](ADR-020-backend-foundations.md) e
[`dependencies.md`](../dependencies.md)).

## Decisão

| Item                 | Escolha                                     | Motivo                                                                                    |
| -------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Python               | **3.13** (`.python-version`)                | Estável, suportado por FastAPI/SQLAlchemy/psycopg; 3.14 ainda recente para o ecossistema. |
| Gerenciador Python   | **uv** com `uv.lock`                        | Resolução rápida, lockfile reprodutível com hashes, gerencia a versão do Python.          |
| Type checker         | **mypy** (modo `strict`)                    | Maduro, integração com Pydantic via plugin. Pyright fica como alternativa no editor.      |
| Lint/format Python   | **Ruff** (lint + formatter)                 | Uma ferramenta substitui flake8/isort/black.                                              |
| Node.js              | **24 LTS** (`.nvmrc`)                       | Linha LTS ativa.                                                                          |
| Gerenciador JS       | **npm** com `package-lock.json`             | Já vem com o Node; evita dependência extra.                                               |
| Testes               | pytest, Vitest, Playwright                  | Definidos no escopo.                                                                      |
| Format/lint frontend | Prettier; ESLint 9 (flat config) + jsx-a11y | ESLint 10 ainda sem suporte do plugin de acessibilidade.                                  |
| Hooks locais         | pre-commit (opcional para o dev)            | Mesmas verificações do CI rodando antes do commit.                                        |

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

- Contribuidores precisam de `uv` e Node 24 (ou apenas Docker para subir a aplicação).
- As imagens de container usam a mesma stack no MVP (Azure Container Apps).
- Upgrades de runtime passam por nova ADR ou atualização desta.

## Riscos

- Versões muito recentes (TypeScript 6, Vite 8) podem ter incompatibilidades com plugins;
  mitigado por lockfiles e pela checagem em CI (Sprint 9).
- Dependências abandonadas ou com licença incompatível: revisão em `dependencies.md`.

## Possibilidade de revisão

- Ao surgir incompatibilidade relevante de ecossistema, ou quando Python 3.14 tiver
  suporte estável de todas as dependências.
