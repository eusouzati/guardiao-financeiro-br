# API — visão geral

- Base: `/api/v1/` (versionada). Documentação OpenAPI interativa em `/api/docs`
  (especificação em `/api/v1/openapi.json`).
- Formato: JSON; valores decimais como **string** (`"15780.00"`); datas ISO 8601 em UTC.
- Autorização sempre no backend; erros no formato de [`error-codes.md`](error-codes.md).
- Listas sempre paginadas (`page`, `page_size` ≤ 100).

## Endpoints disponíveis

| Método | Rota                     | Autenticação | Permissão            | Descrição                                                  |
| ------ | ------------------------ | ------------ | -------------------- | ---------------------------------------------------------- |
| GET    | `/health`                | não          | —                    | Liveness (sonda do Container Apps).                        |
| GET    | `/ready`                 | não          | —                    | Readiness: banco acessível e migrado (503 se não).         |
| GET    | `/api/health/live`       | não          | —                    | Processo em execução.                                      |
| GET    | `/api/health/ready`      | não          | —                    | Banco acessível e migrado (503 se não).                    |
| GET    | `/api/v1/me`             | sim          | —                    | Usuário atual, perfis, permissões e organização.           |
| GET    | `/api/v1/configurations` | sim          | `CONFIGURATION_READ` | Políticas efetivas (padrão + sobrescritas da organização). |
| GET    | `/api/v1/audit/events`   | sim          | `AUDIT_READ`         | Trilha de auditoria paginada.                              |

Não existem endpoints simulados: recursos de documentos, fornecedores, pedidos,
recebimentos, exceções, revisões e importações entram nas sprints correspondentes.

`/health` e `/ready` são chamados diretamente no container da API (sem ingress público no
MVP); `/api/health/*` são as mesmas verificações alcançáveis pelo frontend.

## Autenticação

No MVP, sem o login Entra ligado (Sprint 1), as rotas protegidas retornam `401`. Com
`EASY_AUTH_ENABLED=true` (somente `APP_ENV=mvp`), a identidade vem do Easy Auth do
Container Apps (ADR-006). Localmente, sem Entra ID, as rotas protegidas retornam `401` — exceto com
`APP_ENV=local` e `DEV_AUTH_ENABLED=true`, quando toda requisição é tratada como o usuário
de desenvolvimento com os perfis de `DEV_AUTH_ROLES` (ADR-006).
