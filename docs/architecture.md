# Arquitetura — Guardião Financeiro BR

> Documento vivo. Visão geral resumida em [`../ARCHITECTURE.md`](../ARCHITECTURE.md).
> Decisões em [`decisions/`](decisions/README.md).

## 1. Objetivo arquitetural

Conferir automaticamente documentos de contas a pagar (NF-e, NFS-e) contra pedidos e
recebimentos, **processando sozinhos os casos normais e encaminhando apenas exceções**
para análise humana — com explicabilidade, auditoria e segurança desde o início.

Restrições que moldam a arquitetura:

- **Cloud-First:** um único ambiente de nuvem, o **MVP** (Azure + Microsoft 365), desde a
  Sprint 0 ([ADR-001](decisions/ADR-001-mvp-cloud-first.md),
  [`cloud-architecture.md`](cloud-architecture.md)). A máquina local serve para
  desenvolvimento e testes, não como ambiente oficial.
- **Sem qualquer LLM** nas decisões de conferência.
- Não é ERP, não paga, não escritura, não afirma correção fiscal/jurídica.
- Simplicidade primeiro: monólito modular, fila em PostgreSQL, sem broker (ADR-018, ADR-004).

## 2. Contexto (C4 — nível 1)

```mermaid
flowchart LR
    analyst([Analista / Aprovador / Auditor / Admin])
    m365[(Microsoft 365<br/>caixa contas a pagar)]
    entra[Microsoft Entra ID]
    erp[ERP / planilhas<br/>pedidos, recebimentos]
    gfb[[Guardião Financeiro BR]]

    analyst -- navegador, pt-BR --> gfb
    gfb -- OIDC --> entra
    gfb -- Graph API, escopo de 1 caixa --> m365
    erp -- CSV / XLSX --> gfb
```

## 3. Containers (C4 — nível 2)

```mermaid
flowchart TB
    subgraph browser[Navegador]
        spa[Frontend SPA<br/>React + TS + Vite + Tailwind]
    end
    subgraph runtime[Azure Container Apps — MVP]
        api[API<br/>FastAPI /api/v1]
        worker[Worker<br/>mesmo código do backend]
    end
    db[(PostgreSQL 18<br/>metadados, fila, auditoria)]
    blob[(Azure Blob Storage<br/>documentos)]
    kv[(Azure Key Vault)]
    obs[(App Insights / OpenTelemetry)]

    spa -- HTTPS + JWT --> api
    api --> db
    worker --> db
    api --> blob
    worker --> blob
    api -. segredos via Managed Identity .-> kv
    worker -. segredos .-> kv
    api -. telemetria sem documentos .-> obs
    worker -. telemetria .-> obs
```

| Container  | Responsabilidade                                                 | MVP (Azure, oficial)                              | Desenvolvimento local         |
| ---------- | ---------------------------------------------------------------- | ------------------------------------------------- | ----------------------------- |
| Frontend   | UI pt-BR, experiência; nenhuma decisão de autorização ou cálculo | Container App `ca-gfbr-web-mvp`                   | Vite dev server / Nginx       |
| API        | REST versionada, authN/authZ, orquestração                       | Container App `ca-gfbr-api-mvp` (ingress interno) | Uvicorn                       |
| Worker     | parsing, matching, ingestão de e-mail, jobs                      | Container App / Job (Sprint 2+)                   | processo Python               |
| PostgreSQL | metadados, fila `processing_job`, auditoria                      | Flexible Server 18, `guardiao_financeiro`         | Docker                        |
| Storage    | arquivos originais e derivados, por hash                         | Blob Storage privado                              | diretório temporário (testes) |

> **Estado (Sprint 0 do plano Cloud-First):** API, frontend (Nginx) e job de migração
> prontos para o MVP; sondas `GET /health` e `GET /ready` (também em `/api/health/*`) e
> página pública `/status`. O worker entra com o processamento assíncrono (Sprint 2).

## 4. Backend — camadas (C4 — nível 3)

```text
backend/app/
├── api/           # Rotas FastAPI /api/v1, dependências de auth, DTOs de entrada/saída
├── schemas/       # Modelos Pydantic da API (request/response)
├── services/      # Casos de uso: orquestram domínio, repositórios, storage e fila
├── domain/        # Núcleo puro: entidades de valor, Money, FiscalId, enums, erros
├── parsers/       # FiscalDocumentParser: XML → estrutura normalizada (puro)
├── rules/         # Regras determinísticas versionadas (puras)
├── matching/      # Three-way match: seleção de candidatos + agregação de status (puro)
├── models/        # ORM SQLAlchemy (tabelas)
├── repositories/  # Acesso a dados, sempre com escopo de organization_id
├── integrations/  # Adapters externos: storage, Microsoft Graph, Key Vault
├── security/      # Autenticação, permissões, sanitização de upload
├── audit/         # Emissão de eventos de auditoria
└── config/        # Settings (pydantic-settings), validação de ambiente
```

Regras de dependência (ADR-018), verificadas por `backend/tests/architecture/`:

| Camada                         | Não pode importar                                                                |
| ------------------------------ | -------------------------------------------------------------------------------- |
| `domain`                       | qualquer outra camada da app, SQLAlchemy, FastAPI                                |
| `parsers`, `rules`, `matching` | `models`, `repositories`, `api`, `services`, `integrations`, SQLAlchemy, FastAPI |
| `models`, `repositories`       | `api`, `services`                                                                |
| `api`                          | `models`, `repositories` (usa `services`)                                        |

## 5. Fluxo principal (alvo do MVP)

```mermaid
sequenceDiagram
    autonumber
    actor U as Analista
    participant API
    participant ST as Storage
    participant DB as PostgreSQL
    participant W as Worker
    U->>API: upload XML (ou chega via e-mail)
    API->>API: valida tamanho, tipo real, nome
    API->>API: SHA-256 em streaming
    API->>DB: Attachment (org, sha256) — idempotente
    API->>ST: grava por hash
    API->>DB: job PARSE_DOCUMENT
    W->>DB: SKIP LOCKED pega job
    W->>ST: lê XML
    W->>W: ParserRegistry → NFeParser (XML seguro)
    W->>DB: FiscalDocument normalizado + DOCUMENT_PARSED
    W->>DB: advisory lock do documento
    W->>W: localiza fornecedor, pedido, recebimento
    W->>W: executa ruleset vX.Y.Z (puro)
    W->>DB: MatchingRun + RuleResults + Exceptions + status
    U->>API: fila de exceções / detalhe lado a lado
    U->>API: decisão (aceitar, rejeitar, justificar…)
    API->>DB: ReviewDecision (append-only) + AuditEvent
```

## 6. Status do three-way match

`MATCHED`, `MATCHED_WITH_WARNINGS`, `NEEDS_REVIEW`, `BLOCKED` — derivados de forma
determinística dos resultados das regras (tabela em [`matching-engine.md`](matching-engine.md)).

## 7. Preocupações transversais

| Tema                     | Abordagem                                                                                                                  | Onde              |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| Dinheiro                 | `Decimal` / `NUMERIC`, tolerâncias configuráveis                                                                           | ADR-009           |
| Identificador fiscal     | Value object único, CNPJ alfanumérico                                                                                      | ADR-012           |
| Idempotência             | hash, IDs externos, constraints, `Idempotency-Key`                                                                         | ADR-014           |
| Concorrência             | advisory lock por documento + optimistic locking                                                                           | ADR-004           |
| Auditoria                | append-only, grants restritos                                                                                              | ADR-015           |
| Multitenancy             | `organization_id` em tudo                                                                                                  | ADR-013           |
| Segurança                | ver [`security.md`](security.md) e [`threat-model.md`](threat-model.md)                                                    | —                 |
| Privacidade              | ver [`lgpd.md`](lgpd.md)                                                                                                   | —                 |
| Logs                     | JSON estruturado, correlation IDs (`request_id`, `document_id`, `matching_run_id`, `organization_id`), sem dados sensíveis | Sprint 1          |
| Observabilidade          | OpenTelemetry → Application Insights; métricas de parser, matching, fila, Graph, storage                                   | Sprint 7/8        |
| Erros                    | códigos estáveis (`GFB-XXXX`), mensagens pt-BR sem traceback/SQL/caminhos                                                  | Sprint 1          |
| Configuração por empresa | tabela `configuration` versionada; snapshot por `MatchingRun`                                                              | Sprint 3/4        |
| Feature flags            | booleanos em `Configuration`/settings; sem plataforma dedicada                                                             | quando necessário |
| Performance              | paginação obrigatória, índices em campos de busca, streaming de arquivos, evitar N+1                                       | contínuo          |

## 8. Portabilidade

- Ambiente oficial: **MVP** no Azure ([`deployment-azure.md`](deployment-azure.md)).
- Desenvolvimento e testes locais: `docker compose up` (PostgreSQL + API + frontend) e
  adapters fake para serviços externos nos testes automatizados.
- Microsoft 365: Shared Mailbox do MVP desde a Sprint 0; ingestão na Sprint 6.
- Nenhum recurso de nuvem é criado sem autorização explícita.

## 9. Evolução prevista

Integrações ERP, OCR/IA assistiva (nunca decisória), Teams, webhooks, SaaS multiempresa —
ver [`roadmap.md`](roadmap.md). A arquitetura acomoda esses itens por meio de adapters
(`integrations/`), parsers versionados e `organization_id`.
