# ADR-004 — Fila de processamento em tabela PostgreSQL

- **Status:** PROPOSED
- **Data:** 2026-09-29
- **Sprint:** 0 (implementação: Sprints 2, 4 e 6)
- **Histórico:** decisão equivalente aprovada pelo mantenedor em 2026-09-26 no plano
  anterior (com critérios); campos e estados alinhados ao plano Cloud-First.

## Contexto

Parsing de documentos, conferência (matching) e ingestão de e-mail podem demorar, falhar
temporariamente e precisar de nova tentativa. O plano proíbe Redis, RabbitMQ, Kafka ou
Azure Service Bus sem necessidade comprovada e exige evitar processamento concorrente
inconsistente do mesmo documento.

## Decisão

- Fila em **tabela PostgreSQL** (`processing_job`), consumida por um processo **worker**
  do próprio backend com `SELECT … FOR UPDATE SKIP LOCKED` em transação curta.
- Campos:

| Campo               | Uso                                                                       |
| ------------------- | ------------------------------------------------------------------------- |
| `id`                | UUID                                                                      |
| `organization_id`   | isolamento por organização ([ADR-013](ADR-013-multitenancy.md))           |
| `job_type`          | ex.: `PARSE_DOCUMENT`, `RUN_MATCHING`, `POLL_MAILBOX`                     |
| `payload_reference` | somente referências (IDs); **nunca** o conteúdo de documentos             |
| `idempotency_key`   | única por organização; reenfileirar a mesma chave devolve o job existente |
| `status`            | `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`, `DEAD`                    |
| `priority`          | menor valor = maior prioridade                                            |
| `attempt_count`     | tentativas já feitas                                                      |
| `max_attempts`      | limite; ao esgotar → `DEAD` (dead-letter lógico, visível na UI)           |
| `available_at`      | quando pode ser executado (backoff exponencial com jitter)                |
| `locked_at`         | início da reserva                                                         |
| `locked_by`         | identificação do worker                                                   |
| `last_error`        | código e mensagem sanitizados (sem segredos nem dados pessoais)           |
| `created_at`        | UTC                                                                       |
| `updated_at`        | UTC                                                                       |
| `completed_at`      | UTC                                                                       |

- Semântica dos estados: `FAILED` = falhou e ainda será tentado de novo (volta a ser
  elegível em `available_at`); `DEAD` = falha definitiva ou tentativas esgotadas.
- **Jobs órfãos:** um job `PROCESSING` com `locked_at` mais antigo que o tempo limite do
  tipo volta a ser elegível (o worker morreu). Handlers são idempotentes.
- **Concorrência por documento:** o matching de um documento executa sob
  `pg_advisory_xact_lock` do documento e com controle de versão nas entidades revisáveis.
- Interface `JobQueue` isola o mecanismo, permitindo substituição futura sem alterar o
  domínio.
- Observabilidade: métricas de jobs pendentes, retries e jobs mortos; `processing_job_id`
  nos logs.
- No MVP, o worker roda como Container App (ou job agendado) com a mesma imagem do
  backend e identidade própria (`id-gfbr-worker-mvp`), criada na sprint que o introduzir.

## Alternativas consideradas

- **Celery + Redis** — dois componentes a mais; rejeitado no MVP.
- **FastAPI BackgroundTasks** — sem persistência nem retry.
- **Azure Service Bus** — adequado em escala; custo e complexidade sem necessidade atual.

## Consequências

- Nenhuma infraestrutura adicional no Azure para filas.
- Throughput limitado pelo banco — suficiente para o volume de PMEs.

## Riscos

- Contenção no PostgreSQL com muitos workers: mitigado por índices parciais em
  (`status`, `available_at`, `priority`) e poucos workers.
- Job preso em `PROCESSING`: mitigado pela recuperação de órfãos e por alerta de fila
  parada.

## Possibilidade de revisão

Quando o volume ou a latência exigirem mensageria dedicada; a troca é feita atrás de
`JobQueue` por nova ADR.
