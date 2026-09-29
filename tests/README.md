# Testes

Mapa dos testes do monorepo. Cada suíte fica junto do código que testa; este diretório
reúne testes que atravessam componentes.

| Suíte                                        | Onde                                | Como executar                                              |
| -------------------------------------------- | ----------------------------------- | ---------------------------------------------------------- |
| Backend (unitários, integração, arquitetura) | `backend/tests/`                    | `cd backend && uv run pytest`                              |
| Frontend (componentes)                       | `frontend/src/**/*.test.ts(x)`      | `cd frontend && npm test`                                  |
| E2E (navegador)                              | `frontend/e2e/`                     | `cd frontend && npm run e2e` (stack no ar)                 |
| Infraestrutura (Bicep)                       | `infra/azure/`                      | `az bicep build --file infra/azure/main.bicep` e `what-if` |
| Validação do ambiente MVP                    | `scripts/azure/test-mvp.ps1`        | após o deploy (somente leitura)                            |
| Escopo de e-mail (Microsoft 365)             | `infra/m365/Test-MailboxAccess.ps1` | após o RBAC for Applications (somente leitura)             |

Testes ponta a ponta com e-mail real (Sprint 6) entrarão em `tests/`. Somente dados
fictícios ([`../docs/synthetic-data-policy.md`](../docs/synthetic-data-policy.md)).
