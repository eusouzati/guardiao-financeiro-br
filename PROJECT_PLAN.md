# Plano do projeto — Guardião Financeiro BR

> Fonte do escopo: prompt mestre consolidado (Cloud-First) mantido pelo responsável, fora
> do repositório. Decisões derivadas dele estão nas ADRs e nesta documentação.
> Ambiente único: **MVP** ([ADR-001](docs/decisions/ADR-001-mvp-cloud-first.md)).
> Roadmap resumido: [`docs/roadmap.md`](docs/roadmap.md).

## 1. Governança

- Execução **exclusivamente em sprints**; cada sprint termina com relatório e **parada**
  até aprovação explícita do mantenedor.
- Exigem aprovação prévia: custo relevante, redução de segurança, mudança significativa de
  arquitetura, uso de credenciais, criação de recurso cloud, remoção de dados, mudança de
  autenticação, ampliação de permissões Azure/Microsoft 365, exposição de informação,
  `git push`, publicação de release.
- O primeiro deploy do MVP exige a frase **"AUTORIZAR DEPLOY MVP DA SPRINT 0"**.
- Nunca automático: excluir grupo de recursos ou PostgreSQL, `DROP DATABASE`, purge do Key
  Vault, excluir caixa, App Registration ou Service Principal, apagar blobs, reescrever o
  histórico do Git ([`docs/teardown-mvp.md`](docs/teardown-mvp.md)).
- Não criar ambientes de homologação, produção ou equivalentes.
- Repositório público no GitHub antecipado por decisão do responsável em 2026-09-29. A
  revisão de histórico, dados e documentação da Sprint 10 continua obrigatória antes da
  release `v0.1.0`.
- Dúvidas não bloqueantes: solução mais simples e segura + registro em `docs/decisions/`.

### Fluxo de cada sprint

1. Inspecionar o repositório e executar `git status` → 2. validar contexto Azure (e
   Microsoft 365 quando aplicável) → 3. apresentar plano → 4. identificar custos →
2. implementar → 6. testar → 7. validar no ambiente MVP → 8. atualizar documentação →
3. relatório → **PARAR**.

### Definição de pronto (todas as sprints)

Funcionalidade implementada · testes relevantes existem e passam · lint e type check
passam · erros tratados · documentação atualizada · sem segredos · segurança considerada ·
critérios de aceite verificados · **funcionalidade que depende da nuvem validada no MVP
Azure** (não vale funcionar só localmente, com banco local, arquivo local como storage ou
segredo guardado no computador).

## 2. Sprints

| #   | Sprint                                          | Critérios de aceite resumidos                                                                                                                                                                                                                 | Status                           |
| --- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| 0   | MVP Cloud Foundation & Microsoft 365 Foundation | Bicep válido; recursos Azure do MVP criados e verificados; API e frontend de bootstrap no Container Apps com health check; Shared Mailbox, App Registrations e escopo de e-mail validados; nenhum segredo versionado; documentação e teardown | Concluída — aguardando aprovação |
| 1   | Core Platform no MVP Azure                      | Aplicação conectada ao PostgreSQL do Azure e ao Key Vault; autenticação base Entra; layout, navegação e páginas; deploy no MVP                                                                                                                | Planejada                        |
| 2   | Fiscal Document Engine                          | Upload seguro para Blob, SHA-256, NF-e e NFS-e nacional, XML seguro, normalização, fila PostgreSQL                                                                                                                                            | Planejada                        |
| 3   | Suppliers, Orders & Receipts                    | Cadastros e importação CSV/XLSX com templates e relatório, persistidos no MVP                                                                                                                                                                 | Planejada                        |
| 4   | Matching & Rule Engine                          | Regras com testes independentes, three-way match, tolerâncias, explicabilidade, versionamento (sem IA)                                                                                                                                        | Planejada                        |
| 5   | Exception Workbench                             | Dashboard, fila, filtros, detalhe, comparação, revisão, justificativa, resolução, auditoria; deploy no MVP                                                                                                                                    | Planejada                        |
| 6   | Microsoft 365 Mail Ingestion                    | Polling da Shared Mailbox via Graph, anexos, deduplicação, retry, última sincronização; teste ponta a ponta e-mail → resultado                                                                                                                | Planejada                        |
| 7   | Identity, RBAC, LGPD & Security Hardening       | Entra completo, autorização no backend, escopo por organização, retenção, headers, rate limiting, testes de segurança, revisão de permissões Azure/M365                                                                                       | Planejada                        |
| 8   | Reliability & Cloud Hardening do MVP            | Backup e restore testados, proteção de blobs, alertas, escala, custos, rede, runbooks                                                                                                                                                         | Planejada                        |
| 9   | GitHub Actions & DevSecOps                      | `ci.yml`, `security.yml`, `deploy-mvp.yml`, CodeQL, Trivy, OIDC com Azure                                                                                                                                                                     | Planejada                        |
| 10  | Open Source Release                             | Revisão de histórico, segredos, dados de tenant e documentação; `v0.1.0` somente com autorização                                                                                                                                              | Planejada                        |

## 3. Sprint 0 — checklist

Evidências e checklist completo: [`docs/sprint-0/README.md`](docs/sprint-0/README.md).

- [x] Inspeção local, `git status` e verificação de ferramentas
- [x] ADRs 001–011 (e complementares 012–020) com status `PROPOSED`
- [x] Bicep modular (`infra/azure`) com `bicep build` e lint sem avisos
- [x] Scripts Microsoft 365 idempotentes (`infra/m365`)
- [x] Backend mínimo: `GET /health`, `GET /ready`; frontend mínimo: página `/status`
- [x] Documentação: arquitetura cloud, custos, backup/restore, teardown, deploy, M365
- [x] `what-if` executado pelo responsável e revisado
- [x] Autorização "AUTORIZAR DEPLOY MVP DA SPRINT 0"
- [x] Provisionamento Azure (fase base) e publicação do bootstrap (fase apps)
- [x] Microsoft 365: Shared Mailbox, App Registrations, RBAC for Applications e teste de escopo
- [x] Validação de segurança (`scripts/azure/test-mvp.ps1`) e evidências em `docs/sprint-0/`

## 4. Base de código reaproveitada do plano anterior

- [x] Backend FastAPI com configuração validada, logs estruturados, erros padronizados
- [x] PostgreSQL + SQLAlchemy + Alembic (migration 0001, triggers append-only)
- [x] Autenticação DEV com travas (somente local) + autorização no backend
- [x] Suporte a Easy Auth (Entra ID + App Roles) no backend, desligado até a Sprint 1
- [x] Endpoints: `/api/v1/me`, `/api/v1/configurations`, `/api/v1/audit/events`
- [x] Frontend: layout, navegação e 7 páginas iniciais (sem API simulada)
- [x] Docker Compose local (db, migrate, backend, frontend) com health checks
- [x] Testes backend (unitários + integração), frontend (Vitest) e E2E (Playwright)

## 5. Critério final do MVP

Fluxo ponta a ponta: NF-e recebida → XML identificado → fornecedor → hash → duplicidade →
pedido → recebimento → comparação → regras → classificação → exceções → explicação →
análise humana → decisão registrada → auditoria. Demonstração dos cenários A (sem
divergências), B (com exceção) e C (duplicidade).

## 6. Riscos do projeto

| Risco                                                            | Impacto                       | Mitigação                                                                        |
| ---------------------------------------------------------------- | ----------------------------- | -------------------------------------------------------------------------------- |
| Mudanças frequentes de leiaute (NT NF-e/NFS-e, IBS/CBS)          | Parser quebra ou perde campos | Parsers versionados, `unmapped_fields`, erro explícito, acompanhamento de NTs    |
| CNPJ alfanumérico em sistemas legados de clientes                | Falha de matching             | Value object único, testes com CNPJ alfanumérico                                 |
| Escopo crescer para ERP/motor tributário                         | Atraso e risco                | Fora do escopo explícito; roadmap pós-MVP                                        |
| Permissão ampla no M365                                          | Exposição de e-mails          | RBAC for Applications, documentação e teste de escopo                            |
| Dados reais no repositório público                               | Incidente LGPD                | Política de dados fictícios, gitleaks, revisão Sprint 10                         |
| Custo Azure contínuo desde a Sprint 0                            | Financeiro                    | SKUs econômicos, escala a zero, orçamento com alertas, `docs/cost-management.md` |
| Assinatura de avaliação expira                                   | MVP desativado                | Decisão do responsável antes do deploy; Bicep reproduzível em outra assinatura   |
| Mudança direta no único ambiente                                 | Indisponibilidade/perda       | `what-if`, testes locais, backups, soft delete, autorização para destrutivos     |
| Ambiente de desenvolvimento heterogêneo (Windows/WSL/containers) | "Funciona na minha máquina"   | Docker Compose, `.gitattributes` LF, scripts de verificação, CI (Sprint 9)       |
