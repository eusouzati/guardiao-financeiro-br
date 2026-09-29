# Workflows

Planejados para a **Sprint 9** (ADR-019): `ci.yml`, `security.yml` e `deploy-mvp.yml`
(único ambiente — ADR-001). Diretrizes:

- Autenticação GitHub → Azure somente por OIDC.
- Actions de terceiros fixadas por SHA; `permissions:` mínimas por job.
- Deploy do MVP via GitHub Environment `mvp`, com aprovação manual.
