# ADR-015 — Trilha de auditoria append-only

- **Status:** PROPOSED
- **Data:** 2026-09-29
- **Sprint:** 0 (implementação: Sprints 1/5/7)
- **Histórico:** decisão aprovada pelo mantenedor em 2026-09-26 no plano anterior; reapresentada no plano Cloud-First.

## Decisão

- Tabela `audit_event` só recebe `INSERT`. O papel de banco da aplicação **não** tem
  `UPDATE`/`DELETE` nessa tabela (grants configurados em migration) e um trigger rejeita
  alterações como segunda barreira.
- Campos: id, `organization_id`, `occurred_at` (UTC), `event_type`, ator (usuário/sistema),
  `request_id`, entidade alvo (tipo + id), `before`/`after` resumidos (sem documento
  completo nem dados pessoais desnecessários), IP (quando aplicável).
- `ReviewDecision` também é append-only: nova decisão = nova linha com estado anterior e
  novo; nada é sobrescrito.
- Eventos iniciais: `DOCUMENT_UPLOADED`, `DOCUMENT_PARSED`, `DOCUMENT_MATCHED`,
  `EXCEPTION_CREATED`, `EXCEPTION_RESOLVED`, `DOCUMENT_REVIEWED`, `CONFIGURATION_CHANGED`,
  `IMPORT_STARTED`, `IMPORT_COMPLETED`, `LOGIN_SUCCESS`, `LOGIN_FAILURE`.
- Retenção da auditoria segue política própria, independente da retenção de documentos.

## Alternativas consideradas

- **Somente logs de aplicação** — não são consultáveis pelo auditor nem garantem retenção.
- **Hash encadeado (tamper-evident)** — interessante; fica no roadmap pós-MVP.

## Consequências

- A remoção por LGPD de dados pessoais em eventos antigos é feita por pseudonimização
  controlada via procedimento administrativo documentado, não por UPDATE da aplicação.

## Riscos

- Volume da trilha crescer além do esperado: índices por organização/data e política
  de retenção documentada na Sprint 7.

## Possibilidade de revisão

Na Sprint 7 (LGPD e retenção) ou se for exigida trilha imutável externa.
