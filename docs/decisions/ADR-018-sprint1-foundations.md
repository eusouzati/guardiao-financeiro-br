# ADR-018 — Fundações técnicas da Sprint 1 (bibliotecas e padrões de execução)

- **Status:** Aceita — aprovada pelo mantenedor em 2026-09-26 (aprovação da Sprint 1)
- **Data:** 2026-09-26
- **Sprint:** 1

## Contexto

A Sprint 1 cria a base executável (FastAPI, PostgreSQL, Alembic, React). Várias escolhas de
biblioteca e padrão não estavam definidas no escopo e precisavam ser registradas.

## Decisão

### Backend

| Tema               | Escolha                                                                                                                       | Motivo                                                                                                         |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Acesso a dados     | SQLAlchemy 2 **síncrono** + psycopg 3; endpoints `def` (threadpool)                                                           | Mais simples de testar e depurar; volume de PMEs não exige async. Revisar se houver I/O concorrente relevante. |
| Configuração       | pydantic-settings; `.env` lido pelo Compose/shell, não pela aplicação                                                         | Validação na carga (fail-fast da auth DEV) e nenhum arquivo de segredo lido implicitamente.                    |
| Execução           | `uvicorn app.main:create_app --factory`                                                                                       | Sem instância global: configuração lida e validada somente na inicialização.                                   |
| Logs               | `logging` da biblioteca padrão com formatador JSON próprio e redação de chaves sensíveis                                      | Evita dependência (structlog) para uma necessidade pequena.                                                    |
| Correlation ID     | Middleware ASGI aceita `X-Request-ID` válido ou gera um; devolvido na resposta e nos erros                                    | Rastreabilidade ponta a ponta (Nginx → API → logs).                                                            |
| Erros              | Catálogo `GFB-XXXX` ([`../error-codes.md`](../error-codes.md)); mensagens pt-BR; nada de traceback/SQL/caminhos               | Seção 47 do escopo.                                                                                            |
| Health             | `/api/health/live` (processo) e `/api/health/ready` (banco + revisão Alembic)                                                 | Usados por Compose e, depois, pelo Azure Container Apps.                                                       |
| Migrations         | Alembic com revisões escritas/revisadas à mão e teste `alembic check`                                                         | Garante modelos e migrations sincronizados.                                                                    |
| Append-only        | Trigger `gfb_reject_mutation()` bloqueia UPDATE/DELETE/TRUNCATE em `audit_event` e `configuration`                            | Implementa ADR-012 no próprio banco.                                                                           |
| Organização padrão | Comando idempotente `python -m app.cli bootstrap` (advisory lock), executado pelo serviço `migrate`                           | MVP com uma organização por implantação (ADR-010).                                                             |
| Testes             | pytest; integração contra PostgreSQL real via `TEST_DATABASE_URL` (nome deve conter `test`); cada teste em transação desfeita | Isolamento sem truncar tabelas append-only.                                                                    |
| Cliente de teste   | `httpx2` (exigido pelo `TestClient` do Starlette 1.x)                                                                         | Evita aviso de depreciação.                                                                                    |

### Frontend

| Tema       | Escolha                                                                                | Motivo                                                                                 |
| ---------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Roteamento | React Router 8 (modo biblioteca, `createBrowserRouter`)                                | Padrão de mercado; sem framework de SSR.                                               |
| Estilo     | Tailwind CSS 4 com tokens próprios (`@theme`)                                          | Identidade própria; CSS gerado em arquivo (compatível com CSP estrita).                |
| Dados      | `fetch` + hook próprio `useApiQuery` (cancelamento, erro normalizado)                  | Sem biblioteca de cache até existir necessidade real (paginação/mutações na Sprint 5). |
| Formatação | Formatação de decimais por manipulação de texto, sem `float`; lint proíbe `parseFloat` | ADR-007.                                                                               |
| TypeScript | **6.0** (não 7.0)                                                                      | `typescript-eslint` ainda não suporta TS 7.                                            |
| ESLint     | **9.x** (não 10) + `typescript-eslint` strict type-checked + `jsx-a11y` strict         | `eslint-plugin-jsx-a11y` ainda não suporta ESLint 10; acessibilidade é requisito.      |
| Testes     | Vitest + Testing Library (jsdom); Playwright para E2E contra a stack em execução       | Definido no escopo.                                                                    |
| Ícones     | SVG próprios inline                                                                    | Evita dependência e mantém identidade visual própria.                                  |

### Execução local

- Nginx (imagem oficial, usuário sem privilégios, porta 8080) serve a SPA e faz proxy de
  `/api/` para o backend: **mesma origem, sem CORS**. CSP estrita na SPA
  (`script-src 'self'`, `frame-ancestors 'none'`).
- Serviço `migrate` (Alembic + bootstrap) roda antes do backend; containers com
  `read_only`, `no-new-privileges` e portas somente em `127.0.0.1`.

## Alternativas consideradas

- **SQLAlchemy async + asyncpg** — mais complexo, sem ganho no volume esperado.
- **TanStack Query** — excelente, mas prematuro para leituras simples da Sprint 1.
- **structlog** — adiciona dependência para algo resolvido com ~80 linhas.
- **CORS entre SPA e API** — desnecessário e mais superfície de ataque; proxy na mesma origem.
- **pg8000 (BSD) no lugar de psycopg (LGPL-3.0)** — menos maduro e mais lento. psycopg é
  usado sem modificação, como dependência dinâmica, o que é compatível com a distribuição
  sob Apache-2.0; a licença fica registrada em `docs/dependencies.md`.

## Consequências

- Rever TS 7 e ESLint 10 quando o ecossistema de plugins suportar.
- Endpoints de escrita futuros devem registrar `AuditEvent` na mesma transação.
- O proxy do Nginx aponta para `backend:8000` (nome do serviço no Compose); a Sprint 1A
  parametriza o destino para o Azure Container Apps.
