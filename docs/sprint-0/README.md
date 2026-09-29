# Sprint 0 — MVP Cloud Foundation & Microsoft 365 Foundation

> Evidências da Sprint 0. **Sem segredos:** nenhum valor de senha, token, client secret,
> ID de assinatura/tenant ou domínio real é registrado aqui. Seções marcadas com ⏳ são
> preenchidas após a autorização **"AUTORIZAR DEPLOY MVP DA SPRINT 0"**.

## 1. Arquitetura

Visão completa em [`../cloud-architecture.md`](../cloud-architecture.md). Resumo: frontend
público e API interna no Azure Container Apps (workload profiles, Consumption), PostgreSQL
18 sem acesso público na VNet do MVP, Blob Storage e Key Vault acessados por identidade
gerenciada, Log Analytics/Application Insights, orçamento com alertas; no Microsoft 365, uma
Shared Mailbox dedicada, App Registrations web e mail e RBAC for Applications limitado à
caixa.

## 2. Decisões

| Tema                     | Decisão                                                                           | Registro                                      |
| ------------------------ | --------------------------------------------------------------------------------- | --------------------------------------------- |
| Ambiente                 | Único ambiente `mvp`; nada de homologação/produção                                | ADR-001                                       |
| Rede                     | Opção A: VNet + PostgreSQL privado (escolhida em 2026-09-29)                      | ADR-011                                       |
| Autenticação na Sprint 0 | App Registration web criada; Easy Auth ligado na Sprint 1; rotas não-health → 401 | ADR-006                                       |
| Credencial do PostgreSQL | Senha administrativa gerada no deploy, só no Key Vault (débito técnico)           | ADR-003                                       |
| E-mail                   | Shared Mailbox + RBAC for Applications; sem `Mail.*` no Entra; sem processamento  | ADR-007                                       |
| Bootstrap                | Base de código existente, sem regras de negócio; job aplica migrations            | ADR-001                                       |
| Custos                   | ≈ US$ 37–47/mês, dominado pelo PostgreSQL                                         | [`cost-management.md`](../cost-management.md) |

## 3. Validações locais (antes do deploy)

| Verificação                                                  | Resultado (2026-09-29)                                                      |
| ------------------------------------------------------------ | --------------------------------------------------------------------------- |
| Backend: Ruff, formatação, mypy strict                       | sem erros                                                                   |
| Backend: pytest (unitários + integração)                     | 124 testes, cobertura 98%                                                   |
| Frontend: tsc, ESLint, Prettier                              | sem erros                                                                   |
| Frontend: Vitest                                             | 35 testes                                                                   |
| E2E (Playwright, frontend + API locais)                      | 6 testes, incluindo a página `/status`                                      |
| Bicep: `bicep build`, lint, `build-params`                   | sem erros e sem avisos                                                      |
| PowerShell: análise sintática de todos os scripts            | sem erros                                                                   |
| Scripts de deploy e App Registrations com Azure CLI simulada | caminhos de sucesso e de parada (assinatura/tenant divergentes) verificados |
| gitleaks (árvore de trabalho e histórico)                    | nenhum vazamento                                                            |

## 4. Comandos de validação

```powershell
./scripts/check-env.ps1
./scripts/azure/check-access.ps1
./scripts/azure/estimate-cost.ps1
./scripts/azure/deploy-mvp.ps1 -Phase base -ProjectOwner '<responsavel>' -WhatIf
./scripts/azure/deploy-mvp.ps1 -Phase apps -ProjectOwner '<responsavel>' -WhatIf
./scripts/azure/test-mvp.ps1
./infra/m365/Test-MailboxAccess.ps1 -TenantDomain '<dominio>' -MailboxAlias '<alias>' `
    -AdminUser '<admin>' -OutOfScopeMailbox '<outra-caixa>'
```

## 5. Recursos criados ⏳

Preencher com a saída não sensível de `az resource list -g rg-gfbr-mvp -o table` e com o
resultado de `test-mvp.ps1`.

## 6. Outputs não sensíveis ⏳

| Item                         | Valor         |
| ---------------------------- | ------------- |
| Região                       |               |
| Grupo de recursos            | `rg-gfbr-mvp` |
| URL do frontend (`/status`)  |               |
| Versão/tag das imagens       |               |
| Revisão do schema (`/ready`) |               |
| Orçamento criado             |               |

## 7. Limitações e débitos técnicos

- A aplicação usa a credencial administrativa do PostgreSQL (somente no Key Vault) até a
  migração para identidade gerenciada com usuário de menor privilégio.
- Login Entra ainda desligado no ambiente (Sprint 1); a API responde 401 fora dos health
  checks.
- Storage, Key Vault e ACR com endpoints públicos protegidos por Entra ID/RBAC (revisão na
  Sprint 8).
- Sem restauração testada (Sprint 8).
- Administradores não acessam o PostgreSQL diretamente (rede privada); tarefas
  administrativas exigem job na VNet.
- Scripts M365 dependem do módulo `ExchangeOnlineManagement`, instalado pelo responsável.

## 8. Checklist de aceite

### Local

- [x] Estrutura criada (`backend/`, `frontend/`, `infra/azure`, `infra/m365`, `docs/`, `.github/`, `tests/`)
- [x] Git íntegro
- [x] Documentação criada
- [x] Bicep válido

### Azure ⏳

- [ ] Resource Group existe
- [ ] ACR existe (admin desabilitado)
- [ ] PostgreSQL 18 existe; database `guardiao_financeiro` existe
- [ ] Storage existe; containers privados
- [ ] Key Vault existe (RBAC, purge protection)
- [ ] Log Analytics e Application Insights existem
- [ ] Container Apps Environment existe
- [ ] API de bootstrap implantada; frontend de bootstrap implantado
- [ ] Health check funciona (`/api/health/ready` = `ok`)
- [ ] Orçamento criado ou passo manual registrado

### Microsoft 365 ⏳

- [ ] Shared Mailbox existe
- [ ] App Registration Web existe (com Service Principal)
- [ ] App Registration Mail existe (com Service Principal)
- [ ] Escopo de acesso ao e-mail configurado
- [ ] Caixa do MVP → permitido; outra caixa → negado; nenhuma permissão Graph no Entra

### Segurança

- [x] Nenhum segredo versionado (código, docs e parâmetros sem valores reais)
- [x] Managed Identity usada para ACR, Key Vault e Storage (no código de infraestrutura)
- [x] Blobs privados (no código de infraestrutura)
- [ ] Permissões revisadas no ambiente real (`test-mvp.ps1`) ⏳

### Documentação

- [x] Arquitetura cloud
- [x] ADRs
- [x] Custos
- [x] Instruções de acesso ([`deployment-azure.md`](../deployment-azure.md) §5)
- [x] Instruções de teardown ([`teardown-mvp.md`](../teardown-mvp.md))
- [ ] Relatório final ⏳
