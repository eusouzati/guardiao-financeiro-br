# ADR-014 — Idempotência e deduplicação

- **Status:** PROPOSED
- **Data:** 2026-09-29
- **Sprint:** 0 (implementação: Sprints 2/4/6)
- **Histórico:** decisão aprovada pelo mantenedor em 2026-09-26 no plano anterior; reapresentada no plano Cloud-First.

## Contexto

Retries, uploads repetidos, reprocessamentos e a mesma mensagem de e-mail não podem criar
registros duplicados. Ao mesmo tempo, **duplicidade fiscal** (mesma NF-e enviada como
arquivo diferente) precisa ser **registrada e sinalizada**, não silenciosamente descartada.

## Decisão

Distinguir dois conceitos:

1. **Mesmo arquivo (idempotência técnica)** — `Attachment` único por
   `(organization_id, sha256)`. Reenvio do mesmo arquivo retorna o registro existente e
   gera evento de auditoria, sem novo processamento.
2. **Mesmo documento fiscal com arquivo diferente (duplicidade de negócio)** — não há
   constraint única em `access_key`; o novo `FiscalDocument` é criado e as regras
   `DUPLICATE_EXACT` e `DUPLICATE_FISCAL` o marcam como `CRITICAL`. Assim a tentativa
   fica auditável.

Outras chaves:

- Ingestão de e-mail: único `(organization_id, mailbox_id, internet_message_id)` e
  `(organization_id, graph_message_id, attachment_id)`.
- Importações CSV/XLSX: `ImportBatch` único por `(organization_id, sha256, import_type)`;
  linhas com chave natural (ex.: `(organization_id, po_number)`) usam upsert controlado e
  relatório explícito.
- Endpoints de criação aceitam cabeçalho `Idempotency-Key` quando fizer sentido.
- Jobs: `idempotency_key` único na tabela `job` (ADR-004).

## Alternativas consideradas

- **Unique em `access_key`** — impediria registrar a tentativa duplicada; rejeitado.

## Consequências

- A regra de duplicidade precisa de índice em `(organization_id, access_key)` e em
  `(organization_id, issuer_tax_id, number, series, model)`.

## Riscos

- Falso positivo de duplicidade bloqueia pagamento legítimo: a decisão final é humana
  (revisão), com justificativa registrada.

## Possibilidade de revisão

Quando surgirem novos tipos de documento ou canais de entrada.
