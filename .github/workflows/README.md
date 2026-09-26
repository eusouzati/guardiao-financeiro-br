# Workflows

Planejados para a **Sprint 9** (ADR-014): `ci.yml`, `security.yml`, `deploy-hml.yml`,
`deploy-prod.yml`. Diretrizes:

- Autenticação GitHub → Azure somente por OIDC.
- Actions de terceiros fixadas por SHA; `permissions:` mínimas por job.
- Produção com aprovação manual via GitHub Environment `production`.
