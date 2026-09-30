# Roadmap

> Plano **Cloud-First** ([ADR-001](decisions/ADR-001-mvp-cloud-first.md)): existe um único
> ambiente, o **MVP**, com recursos reais no Azure e no Microsoft 365 desde a Sprint 0.
> Cada sprint termina com deploy e validação no MVP, relatório e **parada para aprovação**.
> Status: ✅ concluída · 🟡 em andamento/aguardando aprovação · ⬜ planejada

## MVP (v0.1.0)

| Sprint | Tema                                            | Entregas principais                                                                                                                                                                                    | Status                             |
| ------ | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------- |
| 0      | MVP Cloud Foundation & Microsoft 365 Foundation | ADRs, Bicep, fundação Azure (rede, ACR, PostgreSQL 18, Storage, Key Vault, identidades, monitoramento, orçamento), API/frontend de bootstrap, Shared Mailbox, App Registrations, RBAC for Applications | 🟡 concluída, aguardando aprovação |
| 1      | Core Platform no MVP Azure                      | FastAPI, React, SQLAlchemy, Alembic, conexão ao PostgreSQL do Azure, Key Vault, autenticação base Entra, layout, navegação, páginas iniciais                                                           | ⬜ (base de código já existente)   |
| 2      | Fiscal Document Engine                          | Upload, Blob Storage, SHA-256, NF-e, NFS-e nacional inicial, XML seguro, normalização, fila PostgreSQL                                                                                                 | ⬜                                 |
| 3      | Suppliers, Orders & Receipts                    | Fornecedores, pedidos, itens, recebimentos, importação CSV/XLSX, templates, relatório de importação                                                                                                    | ⬜                                 |
| 4      | Matching & Rule Engine                          | Deduplicação, matching de fornecedor/pedido/recebimento, tolerâncias, three-way match, exceções, versionamento, explicabilidade                                                                        | ⬜                                 |
| 5      | Exception Workbench                             | Dashboard, fila, filtros, detalhe, comparação, revisão, justificativa, resolução, auditoria                                                                                                            | ⬜                                 |
| 6      | Microsoft 365 Mail Ingestion                    | Polling via Graph da Shared Mailbox, anexos, deduplicação, retry, última sincronização, histórico; teste ponta a ponta                                                                                 | ⬜                                 |
| 7      | Identity, RBAC, LGPD & Security Hardening       | Entra completo, roles, autorização no backend, escopo por organização, retenção, headers, rate limiting, testes de segurança                                                                           | ⬜                                 |
| 8      | Reliability & Cloud Hardening do MVP            | Backup e teste de restore, proteção de blobs, monitoramento, alertas, escala, custos, rede, runbooks                                                                                                   | ⬜                                 |
| 9      | GitHub Actions & DevSecOps                      | `ci.yml`, `security.yml`, `deploy-mvp.yml`, CodeQL, Trivy, dependency scanning, push ao ACR, OIDC com Azure                                                                                            | ⬜                                 |
| 10     | Open Source Release                             | Revisão de histórico, segredos, fixtures e dados de tenant; documentação; `v0.1.0` somente com autorização                                                                                             | ⬜                                 |

> Novos ambientes poderão ser avaliados futuramente conforme necessidade real do projeto.

### Aproveitamento do trabalho anterior

O plano anterior (local-first) chegou a concluir uma base de código equivalente à Sprint 1
atual (FastAPI, React, PostgreSQL, Alembic, autenticação DEV local, Easy Auth pronto no
backend, testes). Esse código é reaproveitado: a Sprint 0 o publica como bootstrap no MVP
(sem regras de negócio) e a Sprint 1 completa a integração com Key Vault e Entra ID no
Azure.

### Demonstração de aceite do MVP

- Cenário A — documento sem divergências → `MATCHED`.
- Cenário B — divergência clara → exceção e análise humana.
- Cenário C — duplicidade detectada antes de novo fluxo indevido.

## Pós-MVP (sem compromisso de data)

- Parsers NFS-e municipais prioritários; CT-e.
- Verificação de assinatura digital do XML e consulta pontual de situação na SEFAZ.
- Integrações ERP (conectores brasileiros), API de integração e webhooks.
- Notificações e aprovação via Microsoft Teams; workflow de aprovação multinível.
- IA assistiva (nunca decisória): classificação documental, leitura de PDF/OCR,
  normalização semântica de descrições, sugestão de correspondência de itens,
  sumarização de exceções.
- Row-Level Security no PostgreSQL; auditoria com hash encadeado.
- Portal SaaS multiempresa; indicadores financeiros; integração Power BI.
