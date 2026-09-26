# Architecture Decision Records (ADRs)

Registro das decisões arquiteturais relevantes do Guardião Financeiro BR.

## Como usar

- Copie [`ADR-000-template.md`](ADR-000-template.md) para `ADR-NNN-titulo-curto.md`.
- Toda ADR contém: **contexto, decisão, alternativas consideradas e consequências**.
- ADRs não são apagadas. Uma decisão revista gera nova ADR e a anterior passa a
  `Substituída por ADR-NNN`.
- Dúvidas não bloqueantes resolvidas durante uma sprint também são registradas aqui
  (protocolo de execução do projeto).

## Status

| Status          | Significado                                                             |
| --------------- | ----------------------------------------------------------------------- |
| **Aceita**      | Decisão determinada pelo escopo do projeto ou aprovada pelo mantenedor. |
| **Proposta**    | Escolha técnica ainda não revisada pelo mantenedor.                     |
| **Substituída** | Revista por ADR posterior.                                              |

## Índice

| ADR                                     | Título                                                 | Status                                     |
| --------------------------------------- | ------------------------------------------------------ | ------------------------------------------ |
| [001](ADR-001-stack.md)                 | Stack tecnológica e ferramentas                        | Aceita                                     |
| [002](ADR-002-postgresql.md)            | PostgreSQL como banco de metadados                     | Aceita                                     |
| [003](ADR-003-storage.md)               | Abstração de armazenamento de documentos               | Aceita                                     |
| [004](ADR-004-authentication.md)        | Autenticação e autorização                             | Aceita                                     |
| [005](ADR-005-rule-engine.md)           | Motor de regras determinístico e versionado            | Aceita                                     |
| [006](ADR-006-monorepo-layers.md)       | Monorepo e monólito modular em camadas                 | Aceita                                     |
| [007](ADR-007-money-and-quantities.md)  | Representação de valores monetários e quantidades      | Aceita (com critérios)                     |
| [008](ADR-008-fiscal-identifier.md)     | Identificador fiscal (CNPJ) como string e alfanumérico | Aceita                                     |
| [009](ADR-009-background-processing.md) | Processamento assíncrono e concorrência sem broker     | Aceita (com critérios)                     |
| [010](ADR-010-multitenancy.md)          | Prontidão para multi-tenancy via `organization_id`     | Aceita                                     |
| [011](ADR-011-idempotency-dedup.md)     | Idempotência e deduplicação                            | Aceita                                     |
| [012](ADR-012-audit-log.md)             | Trilha de auditoria append-only                        | Aceita                                     |
| [013](ADR-013-language.md)              | Idioma de código, documentação e interface             | Aceita (com critérios)                     |
| [014](ADR-014-iac-cicd.md)              | IaC com Bicep e GitHub Actions com OIDC                | Aceita                                     |
| [015](ADR-015-m365-ingestion.md)        | Ingestão Microsoft 365 via Graph com escopo mínimo     | Aceita (com critérios)                     |
| [016](ADR-016-fiscal-parsers.md)        | Parsers fiscais versionados e XML seguro               | Aceita (biblioteca: a decidir na Sprint 2) |
| [017](ADR-017-azure-dev-early.md)       | Antecipar ambiente `dev` no Azure (Sprint 1A)          | Aceita                                     |
| [018](ADR-018-sprint1-foundations.md)   | Fundações técnicas da Sprint 1                         | Aceita                                     |
