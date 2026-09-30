# Sprint 0 — MVP Cloud Foundation & Microsoft 365 Foundation

> Evidências da Sprint 0. **Sem segredos:** nenhum valor de senha, token, client secret,
> ID de assinatura/tenant/aplicativo ou domínio real é registrado aqui. Deploy autorizado
> pelo responsável em 2026-09-29 ("AUTORIZAR DEPLOY MVP DA SPRINT 0") e executado na mesma data.

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

## 5. Recursos criados (2026-09-29)

### Azure — grupo `rg-gfbr-mvp` (`brazilsouth`)

| Recurso                       | Nome                                                   |
| ----------------------------- | ------------------------------------------------------ |
| VNet                          | `vnet-gfbr-mvp`                                        |
| Zona DNS privada + link       | `gfbr-mvp.private.postgres.database.azure.com`         |
| Log Analytics                 | `log-gfbr-mvp`                                         |
| Application Insights          | `appi-gfbr-mvp`                                        |
| Identidades gerenciadas       | `id-gfbr-api-mvp`, `id-gfbr-web-mvp`                   |
| Container Registry            | `acrgfbrmvpi75ffu`                                     |
| Key Vault                     | `kv-gfbr-mvp-i75ffu`                                   |
| Storage Account               | `stgfbrmvpi75ffu` (4 containers privados)              |
| PostgreSQL Flexible Server 18 | `psql-gfbr-mvp-i75ffu`, database `guardiao_financeiro` |
| Container Apps environment    | `cae-gfbr-mvp`                                         |
| Container Apps                | `ca-gfbr-api-mvp`, `ca-gfbr-web-mvp`                   |
| Container Apps job            | `caj-gfbr-migrate-mvp`                                 |
| Orçamento                     | `budget-gfbr-mvp`                                      |

O grupo `rg-gfbr-mvp-cae-infra` é criado e gerenciado pela plataforma.

### Microsoft 365 — tenant do responsável

| Recurso                         | Nome / valor                                                                                                                   |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Shared Mailbox                  | `guardiao-financeiro-mvp@<domínio>`, `SharedMailbox`, `CustomAttribute1 = guardiao-financeiro-mvp`, login interativo bloqueado |
| App Registration web + SP       | `guardiao-financeiro-web-mvp` (App Roles, atribuição obrigatória, redirect do Easy Auth)                                       |
| App Registration de e-mail + SP | `guardiao-financeiro-mail-mvp` (sem permissões no Entra)                                                                       |
| Service principal no Exchange   | `guardiao-financeiro-mail-mvp`                                                                                                 |
| Personalização da organização   | `Enable-OrganizationCustomization` (autorizada em 2026-09-29)                                                                  |
| Management Scope                | `gfbr-mvp-mailbox-scope` (`CustomAttribute1 -eq 'guardiao-financeiro-mvp'`)                                                    |
| Atribuição de papel             | `gfbr-mvp-Mail-Read` — `Application Mail.Read` no escopo acima                                                                 |

### Resultado de `scripts/azure/test-mvp.ps1`

```text
Container Registry   [ok] admin desabilitado · [ok] pull anônimo desabilitado
Storage              [ok] sem acesso público · [ok] sem chave compartilhada · [ok] somente HTTPS
                     [ok] TLS 1.2 · [ok] documents-raw, documents-derived, imports, exports privados
Key Vault            [ok] RBAC · [ok] soft delete · [ok] purge protection · [ok] somente postgres-admin-password
PostgreSQL           [ok] versão 18 · [ok] sem HA · [ok] backup 7 dias · [ok] require_secure_transport=on
                     [ok] sem acesso público · [ok] database guardiao_financeiro
Container Apps       [ok] API sem ingress externo · [ok] web com HTTPS obrigatório
Aplicação            [ok] API pronta (0.1.0.dev1, ambiente mvp, schema 0001)
                     [ok] /status responde · [ok] Content-Security-Policy · [ok] rota protegida → 401
Todas as verificações passaram.
```

### Resultado de `infra/m365/Test-MailboxAccess.ps1`

```text
[ok] Nenhuma permissão de aplicação do Graph concedida no Entra ID
Caixa do MVP        Application Mail.Read  gfbr-mvp-mailbox-scope  InScope=True   [ok] permitido
Caixa do admin      Application Mail.Read  gfbr-mvp-mailbox-scope  InScope=False  [ok] negado
Escopo de acesso ao e-mail validado.
```

## 6. Outputs não sensíveis

| Item                         | Valor                                                                         |
| ---------------------------- | ----------------------------------------------------------------------------- |
| Região                       | `brazilsouth`                                                                 |
| Grupo de recursos            | `rg-gfbr-mvp`                                                                 |
| URL do frontend (`/status`)  | `https://ca-gfbr-web-mvp.<domínio-do-ambiente>/status` (em `.azure/mvp.json`) |
| Versão / tag das imagens     | `0.1.0.dev1` / tag `<commit>-<data>` gerada pelo script                       |
| Revisão do schema (`/ready`) | `0001`                                                                        |
| Orçamento criado             | sim — 250 na moeda de cobrança, alertas 50/80/100% real e 100% previsto       |

### Problemas encontrados e corrigidos durante o deploy

| Problema                                                                                 | Correção                                                            |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Provider `Microsoft.Network` não registrado                                              | Registrado pelo responsável (sem custo)                             |
| Regra de firewall do PostgreSQL aparecia como "possível" no what-if                      | Modo de rede passou a ser parâmetro de compilação                   |
| Reimplantação removeria o service endpoint `Microsoft.Storage` da sub-rede do PostgreSQL | Endpoint declarado no Bicep                                         |
| Proxy repassava o `Host` público; o ingress interno roteia pelo `Host`                   | Nginx envia o `Host` do destino (`X-Forwarded-Host` com o original) |
| Resolver do Nginx não aplica domínios de busca → 502                                     | Frontend usa o FQDN interno da API                                  |
| Opções curtas da Azure CLI mudaram (`db show -d`)                                        | Validação usa `db list` com filtro                                  |
| Windows PowerShell 5.1 transforma stderr da CLI em exceção                               | Consultas que podem falhar isoladas com `ErrorActionPreference`     |
| Tenant sem RBAC customizado no Exchange (`IsDehydrated`)                                 | `Enable-OrganizationCustomization` com autorização explícita        |

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

### Azure

- [x] Resource Group existe
- [x] ACR existe (admin desabilitado)
- [x] PostgreSQL 18 existe; database `guardiao_financeiro` existe
- [x] Storage existe; containers privados
- [x] Key Vault existe (RBAC, purge protection)
- [x] Log Analytics e Application Insights existem
- [x] Container Apps Environment existe
- [x] API de bootstrap implantada; frontend de bootstrap implantado
- [x] Health check funciona (`/api/health/ready` = `ok`)
- [x] Orçamento criado ou passo manual registrado

### Microsoft 365

- [x] Shared Mailbox existe
- [x] App Registration Web existe (com Service Principal)
- [x] App Registration Mail existe (com Service Principal)
- [x] Escopo de acesso ao e-mail configurado
- [x] Caixa do MVP → permitido; outra caixa → negado; nenhuma permissão Graph no Entra

### Segurança

- [x] Nenhum segredo versionado (código, docs e parâmetros sem valores reais)
- [x] Managed Identity usada para ACR, Key Vault e Storage (no código de infraestrutura)
- [x] Blobs privados (no código de infraestrutura)
- [x] Permissões revisadas no ambiente real (`test-mvp.ps1`, `Test-MailboxAccess.ps1`)

### Documentação

- [x] Arquitetura cloud
- [x] ADRs
- [x] Custos
- [x] Instruções de acesso ([`deployment-azure.md`](../deployment-azure.md) §5)
- [x] Instruções de teardown ([`teardown-mvp.md`](../teardown-mvp.md))
- [x] Relatório final (seção 9)

## 9. Relatório final

Sprint 0 concluída em 2026-09-29 e **aguardando aprovação**. ADRs 001–010 e 012–020
seguem `PROPOSED` até a aprovação; ADR-011 `ACCEPTED`. A Sprint 1 não foi iniciada.
