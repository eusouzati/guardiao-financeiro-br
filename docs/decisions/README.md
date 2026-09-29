# Architecture Decision Records (ADRs)

Registro das decisões arquiteturais relevantes do Guardião Financeiro BR.

## Como usar

- Copie [`ADR-000-template.md`](ADR-000-template.md) para `ADR-NNN-titulo-curto.md`.
- Toda ADR contém: **contexto, decisão, alternativas, consequências, riscos e
  possibilidade de revisão**.
- ADRs não são apagadas. Uma decisão revista gera nova ADR e a anterior passa a
  `SUPERSEDED`.
- Não existem ADRs de ambientes futuros: o projeto tem um único ambiente, o MVP
  ([ADR-001](ADR-001-mvp-cloud-first.md)).

## Status

| Status         | Significado                                      |
| -------------- | ------------------------------------------------ |
| **PROPOSED**   | Apresentada, aguardando aprovação do responsável |
| **ACCEPTED**   | Aprovada pelo responsável pelo projeto           |
| **SUPERSEDED** | Substituída por ADR posterior                    |

## Índice

ADRs mínimas do plano Cloud-First (001–011) e decisões complementares (012–020).

| ADR                                      | Título                                                    | Status   |
| ---------------------------------------- | --------------------------------------------------------- | -------- |
| [001](ADR-001-mvp-cloud-first.md)        | MVP Cloud-First com um único ambiente                     | PROPOSED |
| [002](ADR-002-stack.md)                  | Stack tecnológica e ferramentas                           | PROPOSED |
| [003](ADR-003-postgresql-18.md)          | PostgreSQL 18 como banco de metadados                     | PROPOSED |
| [004](ADR-004-processing-queue.md)       | Fila de processamento em tabela PostgreSQL                | PROPOSED |
| [005](ADR-005-storage.md)                | Armazenamento de documentos em Azure Blob Storage         | PROPOSED |
| [006](ADR-006-authentication.md)         | Autenticação e autorização                                | PROPOSED |
| [007](ADR-007-microsoft-365-mailbox.md)  | Caixa de e-mail do MVP no Microsoft 365 com escopo mínimo | PROPOSED |
| [008](ADR-008-mail-polling.md)           | Polling da caixa de e-mail do MVP                         | PROPOSED |
| [009](ADR-009-numeric-precision.md)      | Precisão numérica de valores monetários e quantidades     | PROPOSED |
| [010](ADR-010-language-strategy.md)      | Estratégia de idiomas                                     | PROPOSED |
| [011](ADR-011-mvp-networking.md)         | Rede do MVP                                               | ACCEPTED |
| [012](ADR-012-fiscal-identifier.md)      | Identificador fiscal (CNPJ) como string e alfanumérico    | PROPOSED |
| [013](ADR-013-multitenancy.md)           | Prontidão para multi-tenancy via `organization_id`        | PROPOSED |
| [014](ADR-014-idempotency-dedup.md)      | Idempotência e deduplicação                               | PROPOSED |
| [015](ADR-015-audit-log.md)              | Trilha de auditoria append-only                           | PROPOSED |
| [016](ADR-016-rule-engine.md)            | Motor de regras determinístico e versionado               | PROPOSED |
| [017](ADR-017-fiscal-parsers.md)         | Parsers fiscais versionados e XML seguro                  | PROPOSED |
| [018](ADR-018-monorepo-layers.md)        | Monorepo e monólito modular em camadas                    | PROPOSED |
| [019](ADR-019-infrastructure-as-code.md) | Infraestrutura como código com Bicep                      | PROPOSED |
| [020](ADR-020-backend-foundations.md)    | Fundações técnicas do backend e do frontend               | PROPOSED |

## Renumeração de 2026-09-29

Com a mudança para o plano Cloud-First, as ADRs foram renumeradas para seguir a lista
mínima do plano. Correspondência com a numeração anterior (nenhuma havia sido publicada):

| Anterior | Atual | Anterior                                                  | Atual                           |
| -------- | ----- | --------------------------------------------------------- | ------------------------------- |
| 001      | 002   | 010                                                       | 013                             |
| 002      | 003   | 011                                                       | 014                             |
| 003      | 005   | 012                                                       | 015                             |
| 004      | 006   | 013                                                       | 010                             |
| 005      | 016   | 014                                                       | 019                             |
| 006      | 018   | 015                                                       | 007 e 008                       |
| 007      | 009   | 016                                                       | 017                             |
| 008      | 012   | 018                                                       | 020                             |
| 009      | 004   | 017 (`dev` antecipado) e 019 (rede/autenticação do `dev`) | substituídas por 001, 006 e 011 |
