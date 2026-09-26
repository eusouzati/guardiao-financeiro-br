# ADR-009 — Processamento assíncrono e concorrência sem broker

- **Status:** Aceita — aprovada pelo mantenedor em 2026-09-26 (com critérios)
- **Data:** 2026-09-26
- **Sprint:** 0 (implementação: Sprints 2/4/6)

## Contexto

Parsing, matching e ingestão de e-mail podem demorar e precisam de retry. O escopo proíbe
introduzir RabbitMQ, Kafka ou Service Bus sem necessidade comprovada, e exige evitar duas
análises simultâneas inconsistentes do mesmo documento.

## Decisão

- **Fila em tabela PostgreSQL** (`job`), consumida por um processo **worker** do próprio
  backend usando `SELECT … FOR UPDATE SKIP LOCKED`. Campos: tipo, payload mínimo (IDs,
  nunca documentos), status, tentativas, `available_at`, `idempotency_key` único, erro.
- Interface `JobQueue` abstrai o mecanismo para trocar por Azure Service Bus no futuro.
- Retry com backoff exponencial e limite de tentativas; falha definitiva vira estado
  visível na UI, nunca silêncio.
- **Concorrência por documento:** matching de um documento executa sob
  `pg_advisory_xact_lock(hash(document_id))` e com checagem de versão
  (`optimistic locking` via coluna `version`) nas entidades revisáveis.
- No Azure, o worker roda como segunda Container App (ou job) com a mesma imagem.

### Critérios do mantenedor (2026-09-26)

Aprovada para o MVP. **Não** introduzir Redis, RabbitMQ, Kafka ou Azure Service Bus neste
momento, nem outros componentes de infraestrutura apenas para antecipar escala inexistente.
A implementação deve ficar desacoplada (interface `JobQueue`) para substituição futura e
prever obrigatoriamente:

| Requisito | Como |
| --- | --- |
| Idempotência | `idempotency_key` com constraint única por organização; reenfileirar a mesma chave retorna o job existente |
| Status | `PENDING`, `RUNNING`, `SUCCEEDED`, `FAILED_RETRYABLE`, `FAILED_PERMANENT`, `CANCELLED` |
| Tentativas/retries | `attempts`, `max_attempts`, backoff exponencial com jitter via `available_at` |
| Timestamps (UTC) | `created_at`, `available_at`, `started_at`, `finished_at`, `updated_at` |
| Locking seguro | `SELECT … FOR UPDATE SKIP LOCKED` para reservar o próximo job, em transação curta |
| Concorrência / worker que morre | `locked_by` + `lock_expires_at` (lease); jobs com lease vencido voltam a ficar disponíveis; handlers idempotentes |
| Erros | `last_error_code` e mensagem sanitizada (sem segredos/dados pessoais) |

## Alternativas consideradas

- **Celery + Redis** — adiciona dois componentes; rejeitado no MVP.
- **FastAPI BackgroundTasks** — sem persistência nem retry; aceitável apenas para
  tarefas triviais e não críticas.
- **Azure Service Bus** — adequado em escala; reavaliar quando houver volume que justifique.

## Consequências

- Sem infraestrutura extra no ambiente local.
- Throughput limitado pelo banco — suficiente para PMEs (centenas a poucos milhares de
  documentos/dia). Métrica de tamanho da fila exposta via OpenTelemetry.
