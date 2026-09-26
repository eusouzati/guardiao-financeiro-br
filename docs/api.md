# API — visão geral

- Base: `/api/v1/` (versionada). Documentação OpenAPI interativa em `/api/docs`
  (especificação em `/api/v1/openapi.json`).
- Formato: JSON; valores decimais como **string** (`"15780.00"`); datas ISO 8601 em UTC.
- Autorização sempre no backend; erros no formato de [`error-codes.md`](error-codes.md).
- Listas sempre paginadas (`page`, `page_size` ≤ 100).

## Endpoints disponíveis (Sprint 1)

| Método | Rota                     | Autenticação | Permissão            | Descrição                                                  |
| ------ | ------------------------ | ------------ | -------------------- | ---------------------------------------------------------- |
| GET    | `/api/health/live`       | não          | —                    | Processo em execução.                                      |
| GET    | `/api/health/ready`      | não          | —                    | Banco acessível e migrado (503 se não).                    |
| GET    | `/api/v1/me`             | sim          | —                    | Usuário atual, perfis, permissões e organização.           |
| GET    | `/api/v1/configurations` | sim          | `CONFIGURATION_READ` | Políticas efetivas (padrão + sobrescritas da organização). |
| GET    | `/api/v1/audit/events`   | sim          | `AUDIT_READ`         | Trilha de auditoria paginada.                              |

Não existem endpoints simulados: recursos de documentos, fornecedores, pedidos,
recebimentos, exceções, revisões e importações entram nas sprints correspondentes.

## Autenticação até a Sprint 7

Sem Entra ID, as rotas protegidas retornam `401` — exceto em ambiente local com
`APP_ENV=local` e `DEV_AUTH_ENABLED=true`, quando toda requisição é tratada como o usuário
de desenvolvimento com os perfis de `DEV_AUTH_ROLES` (ADR-004).
