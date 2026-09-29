# ADR-008 — Polling da caixa de e-mail do MVP

- **Status:** PROPOSED
- **Data:** 2026-09-29
- **Sprint:** 0 (decisão) — Sprint 6 (implementação)
- **Histórico:** polling aprovado pelo mantenedor em 2026-09-26 (plano anterior), com a
  exigência de evolução para notificações sem reescrita do domínio.

## Contexto

Novas mensagens da Shared Mailbox do MVP ([ADR-007](ADR-007-microsoft-365-mailbox.md))
precisam ser detectadas e seus anexos processados, com segurança e idempotência.

## Decisão

- **Polling periódico** com Microsoft Graph _delta query_ na pasta de entrada, executado
  como job da fila ([ADR-004](ADR-004-processing-queue.md)) do tipo `POLL_MAILBOX`.
- Requisitos:
  - **idempotência:** `message ID` e `attachment ID` registrados; anexos deduplicados por
    **SHA-256** ([ADR-014](ADR-014-idempotency-dedup.md));
  - **controle de última sincronização:** `deltaLink` persistido por caixa/pasta;
  - **retry** com backoff e **dead-letter lógico** (`DEAD`) visível na UI;
  - **logs** sem conteúdo integral de mensagens ou documentos;
  - **métricas:** mensagens lidas, anexos aceitos/rejeitados, falhas do Graph.
- A detecção de mensagens fica atrás da interface `MailboxChangeSource`
  (`PollingChangeSource` no MVP), entregando eventos ao mesmo serviço de ingestão
  idempotente. Webhooks do Graph **não** são implementados agora.
- Adapter `MailboxClient` com implementação fake para testes, sem tenant real.

## Alternativas consideradas

- **Webhooks (subscriptions) do Graph** — exigem endpoint público de notificação,
  renovação de assinaturas e validação; complexidade sem ganho no volume do MVP.
- **Leitura completa periódica sem delta** — mais chamadas e mais risco de duplicidade.

## Consequências

- Latência de detecção igual ao intervalo de polling (configurável, ex.: 5 minutos).
- Nenhum endpoint público adicional.

## Riscos

- Throttling do Graph: respeitar `Retry-After` e limitar concorrência.
- `deltaLink` expirado: refazer sincronização completa com deduplicação por hash.

## Possibilidade de revisão

Quando a latência exigida for menor que o intervalo de polling ou o volume justificar
notificações; a troca é feita por nova implementação de `MailboxChangeSource`.
