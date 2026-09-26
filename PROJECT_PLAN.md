# Plano do projeto — Guardião Financeiro BR

> Fonte do escopo: especificação de desenvolvimento mantida pelo mantenedor (fora do
> repositório). Decisões derivadas dela estão nas ADRs e nesta documentação.
> Roadmap resumido: [`docs/roadmap.md`](docs/roadmap.md).

## 1. Governança

- Execução **exclusivamente em sprints**; cada sprint termina com relatório e **parada**
  até aprovação explícita do mantenedor.
- Exigem aprovação prévia: custo relevante, redução de segurança, mudança significativa de
  arquitetura, uso de credenciais, criação de recurso cloud, remoção de dados, mudança de
  autenticação, exposição de informação, `git push`, publicação de release.
- Dúvidas não bloqueantes: solução mais simples e segura + registro em `docs/decisions/`.

### Fluxo de cada sprint

1. Analisar estado atual → 2. objetivo → 3. riscos → 4. arquivos previstos →
2. implementar → 6. testar → 7. corrigir → 8. documentar → 9. relatório → **PARAR**.

### Definição de pronto (todas as sprints)

Funcionalidade implementada · testes relevantes existem e passam · lint e type check
passam · erros tratados · documentação atualizada · sem segredos · segurança considerada ·
critérios de aceite verificados.

## 2. Sprints

| #   | Sprint                           | Critérios de aceite resumidos                                                                                                                                                            | Status                           |
| --- | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| 0   | Foundation & Architecture        | Estrutura coerente; ambiente validado; arquitetura e decisões documentadas; nenhum recurso Azure; nenhuma integração ativa; nenhum segredo                                               | Concluída — aguardando aprovação |
| 1   | Core Platform                    | Frontend, backend e banco executam; migrations; health check; testes iniciais passam; sem fake API permanente                                                                            | Planejada                        |
| 1A  | Azure Dev Environment            | Bicep `dev` validado (build/validate/what-if); custo estimado e aprovado; deploy manual autorizado; acesso restrito na borda; procedimento de destruição documentado; só dados fictícios | Planejada                        |
| 2   | Fiscal Document Engine           | Upload seguro, storage, SHA-256, NF-e e NFS-e nacional versionados, XML seguro, fixtures sintéticas, testes de parser                                                                    | Planejada                        |
| 3   | Suppliers, POs & Receipts        | Importação CSV/XLSX com templates e relatório (processadas/importadas/ignoradas/inválidas/erros)                                                                                         | Planejada                        |
| 4   | Matching & Rule Engine           | 13 regras com testes independentes, three-way match, tolerâncias, explicabilidade, ruleset versionado                                                                                    | Planejada                        |
| 5   | Exception Workbench              | Dashboard operacional, fila com filtros/ordenação/paginação, detalhe lado a lado, revisão e histórico                                                                                    | Planejada                        |
| 6   | Microsoft 365 Ingestion          | Graph com caixa escopada, dedup, retry, mock, docs Entra/RBAC for Applications                                                                                                           | Planejada                        |
| 7   | Identity, RBAC, LGPD & Hardening | Entra ID, RBAC no backend, escopo por organização, retenção, headers, rate limit, OWASP                                                                                                  | Planejada                        |
| 8   | Azure Infrastructure             | Bicep hml/prod validado (what-if) sobre os módulos da 1A; custos e backup documentados; sem recursos sem autorização                                                                     | Planejada                        |
| 9   | GitHub Actions & DevSecOps       | CI completo, CodeQL, Trivy, SBOM, OIDC, produção com aprovação manual                                                                                                                    | Planejada                        |
| 10  | Open Source Release              | Revisão de segredos/dados/licenças; docs finais; `v0.1.0` sem publicar sem autorização                                                                                                   | Planejada                        |

## 3. Sprint 0 — checklist

- [x] Analisar diretório, Git e ferramentas
- [x] Estruturar monorepo
- [x] Documentação inicial (README EN/pt-BR, ARCHITECTURE, SECURITY, CONTRIBUTING, CoC, CHANGELOG)
- [x] ADRs (001–017)
- [x] Arquitetura e modelo de domínio inicial
- [x] Threat model inicial
- [x] Roadmap
- [x] Docker (PostgreSQL local com health check)
- [x] Convenções (código, API, banco, docs)
- [x] Ferramentas de qualidade (Ruff, mypy, pytest, Prettier, pre-commit, EditorConfig)
- [x] Estratégia de branches e commits
- [x] Política de dados fictícios
- [x] Decisões do mantenedor aplicadas às ADRs
- [x] Validações executadas

## 4. Critério final do MVP

Fluxo ponta a ponta: NF-e recebida → XML identificado → fornecedor → hash → duplicidade →
pedido → recebimento → comparação → regras → classificação → exceções → explicação →
análise humana → decisão registrada → auditoria. Demonstração dos cenários A (sem
divergências), B (com exceção) e C (duplicidade).

## 5. Riscos do projeto

| Risco                                                            | Impacto                       | Mitigação                                                                     |
| ---------------------------------------------------------------- | ----------------------------- | ----------------------------------------------------------------------------- |
| Mudanças frequentes de leiaute (NT NF-e/NFS-e, IBS/CBS)          | Parser quebra ou perde campos | Parsers versionados, `unmapped_fields`, erro explícito, acompanhamento de NTs |
| CNPJ alfanumérico em sistemas legados de clientes                | Falha de matching             | Value object único, testes com CNPJ alfanumérico                              |
| Escopo crescer para ERP/motor tributário                         | Atraso e risco                | Fora do escopo explícito; roadmap pós-MVP                                     |
| Permissão ampla no M365                                          | Exposição de e-mails          | RBAC for Applications, documentação e teste de escopo                         |
| Dados reais no repositório público                               | Incidente LGPD                | Política de dados fictícios, gitleaks, revisão Sprint 10                      |
| Custo Azure                                                      | Financeiro                    | Nenhum recurso sem autorização; SKUs mínimos; custos documentados na Sprint 8 |
| Ambiente de desenvolvimento heterogêneo (Windows/WSL/containers) | "Funciona na minha máquina"   | Docker Compose, `.gitattributes` LF, scripts de verificação, CI (Sprint 9)    |
