# Roadmap

> Cada sprint termina com relatório e **parada para aprovação** do mantenedor.
> Status: ✅ concluída · 🟡 em andamento/aguardando aprovação · ⬜ planejada

## MVP (v0.1.0)

| Sprint | Tema                             | Entregas principais                                                                                                    | Status                  |
| ------ | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| 0      | Foundation & Architecture        | Monorepo, docs, ADRs, modelo de domínio, threat model, Docker (DB), convenções, qualidade                              | 🟡 aguardando aprovação |
| 1      | Core Platform                    | FastAPI, React, PostgreSQL, Alembic, health, layout, navegação, páginas iniciais, testes base                          | ⬜                      |
| 1A     | Azure Dev Environment            | Bicep do ambiente `dev`, what-if, estimativa de custo, deploy manual autorizado, barreira de acesso na borda (ADR-017) | ⬜                      |
| 2      | Fiscal Document Engine           | Upload seguro, storage, SHA-256, NF-e, NFS-e nacional, parser versionado, fixtures                                     | ⬜                      |
| 3      | Suppliers, POs & Receipts        | Cadastros, importação CSV/XLSX, templates, relatório de importação                                                     | ⬜                      |
| 4      | Matching & Rule Engine           | 13 regras, three-way match, tolerâncias, explicabilidade, ruleset versionado                                           | ⬜                      |
| 5      | Exception Workbench              | Dashboard operacional, fila, detalhe lado a lado, revisão, histórico, auditoria                                        | ⬜                      |
| 6      | Microsoft 365 Ingestion          | Graph, caixa dedicada, dedup, retry, RBAC for Applications, mock                                                       | ⬜                      |
| 7      | Identity, RBAC, LGPD & Hardening | Entra ID, RBAC, retenção, headers, rate limit, OWASP Top 10                                                            | ⬜                      |
| 8      | Azure Infrastructure             | Bicep `hml`/`prod` reaproveitando módulos da 1A, rede, custos, backup testado — sem criar recursos sem autorização     | ⬜                      |
| 9      | GitHub Actions & DevSecOps       | CI, CodeQL, Trivy, SBOM, OIDC, deploys com aprovação                                                                   | ⬜                      |
| 10     | Open Source Release              | Revisão de segredos/dados/licenças, docs finais, v0.1.0 (sem publicar sem autorização)                                 | ⬜                      |

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
