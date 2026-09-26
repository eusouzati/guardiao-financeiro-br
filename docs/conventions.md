# Convenções do projeto

## 1. Estrutura do monorepo

```text
guardiao-financeiro-br/
├── backend/        # API FastAPI + worker (Python 3.13, uv)
├── frontend/       # SPA React + TypeScript + Vite + Tailwind (Node 24, npm)
├── infra/          # Bicep (Sprint 8)
├── docs/           # Documentação técnica e ADRs
├── scripts/        # Scripts de desenvolvimento e verificação
└── .github/        # Templates, workflows (Sprint 9), Dependabot
```

## 2. Estratégia de branches

- `main`: sempre estável e implantável; protegida (PR obrigatório, CI verde, 1 revisão
  quando houver mais de um mantenedor; sem force push).
- Branches curtas a partir de `main`:
  `feat/<escopo>-<descricao>`, `fix/…`, `docs/…`, `chore/…`, `ci/…`, `security/…`,
  `refactor/…`, `test/…`. Ex.: `feat/sprint-1-core-platform`.
- Uma branch por sprint (ou por entrega dentro da sprint), integrada via PR com
  squash merge.
- Releases por tag SemVer anotada (`v0.1.0`); `CHANGELOG.md` no formato Keep a Changelog.
- **Nenhum push, merge ou release sem autorização explícita do mantenedor.**

## 3. Commits — Conventional Commits

```text
<tipo>(<escopo opcional>): <descrição no imperativo>

[corpo opcional: o quê e por quê]

[rodapé: BREAKING CHANGE:, Refs: #123]
```

Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`, `security`, `perf`, `build`.
Escopos sugeridos: `backend`, `frontend`, `infra`, `parser`, `rules`, `matching`, `m365`,
`auth`, `audit`, `docs`, `deps`.

Exemplos:

```text
chore: estrutura inicial do monorepo (Sprint 0)
feat(parser): adiciona NFeParser para layout 4.00
security(upload): valida tipo real do arquivo por magic bytes
```

Commits pequenos e coesos; nunca versionar `.env`, segredos, documentos reais, backups
ou saídas locais.

## 4. Código Python

- Ruff (lint + format), linha de 100 colunas; mypy `strict`.
- Tipagem obrigatória em código de produção.
- `Decimal` para dinheiro/quantidade; nunca `float` (ADR-007).
- Nada de `print`; usar logger estruturado.
- Exceções de domínio com código estável (`GFB-XXXX`).
- Testes em `backend/tests/` espelhando `app/`; nome `test_<comportamento>`.
- Datas: `datetime` sempre _aware_ em UTC.

## 5. Código TypeScript/React (Sprint 1)

- `strict: true`; ESLint (flat config) + Prettier.
- Componentes funcionais; nenhuma regra de negócio decisória no frontend.
- Formatação pt-BR via `Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })`
  e `Intl.DateTimeFormat('pt-BR')`.
- Textos de UI centralizados; acessibilidade (labels, foco visível, contraste, status
  com ícone + texto, não só cor).

## 6. API

- REST sob `/api/v1/`; recursos no plural e kebab-case (`/purchase-orders`).
- Paginação obrigatória em listas (`page`, `page_size`, máximo definido).
- Valores monetários como string decimal; datas ISO 8601 com `Z`.
- Erros no formato `{ "code": "GFB-1001", "message": "…", "request_id": "…" }`.
- OpenAPI automático.

## 7. Banco

- Tabelas e colunas `snake_case`, singular (`purchase_order`).
- Migrations Alembic revisadas; nunca editar migration já aplicada em ambiente compartilhado.
- Constraints e índices nomeados explicitamente (convenção de nomes do SQLAlchemy).

## 8. Documentação

- Toda decisão arquitetural relevante → ADR.
- Toda sprint atualiza `CHANGELOG.md`, `PROJECT_PLAN.md` e docs afetadas.
- Markdown formatado por Prettier.

## 9. Versionamento

- Aplicação: SemVer (`0.x` até estabilizar).
- Regras e ruleset: SemVer próprio (ADR-005).
- Parsers: versão do leiaute suportado explícita.
