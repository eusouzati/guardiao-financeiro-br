# Implantação no Azure — ambiente MVP

> Único ambiente do projeto: **MVP** ([ADR-001](decisions/ADR-001-mvp-cloud-first.md)).
> Nenhum recurso é criado sem `what-if`, estimativa de custo e a autorização
> **"AUTORIZAR DEPLOY MVP DA SPRINT 0"**. Arquitetura: [`cloud-architecture.md`](cloud-architecture.md).

## 1. Variáveis obrigatórias

Informadas na sessão do PowerShell de quem faz o deploy — **nunca** versionadas.

| Variável                   | Uso                                            | Sugestão                    |
| -------------------------- | ---------------------------------------------- | --------------------------- |
| `AZURE_SUBSCRIPTION_ID`    | Assinatura esperada (o script para se diferir) | —                           |
| `AZURE_TENANT_ID`          | Tenant esperado (o script para se diferir)     | —                           |
| `AZURE_REGION`             | Região dos recursos                            | `brazilsouth`               |
| `RESOURCE_PREFIX`          | Prefixo dos nomes                              | `gfbr`                      |
| `PROJECT_OWNER`            | Tag `owner`                                    | nome ou apelido, sem e-mail |
| `M365_TENANT_DOMAIN`       | Domínio do Microsoft 365                       | —                           |
| `MVP_SHARED_MAILBOX_ALIAS` | Alias da Shared Mailbox                        | `guardiao-financeiro-mvp`   |
| `MVP_ADMIN_USER`           | Administrador que executa os scripts M365      | —                           |

Orçamento: `MVP_BUDGET_AMOUNT` (ou `-BudgetAmount`; padrão 50, na **moeda de cobrança**
da assinatura) e `MVP_BUDGET_EMAILS` (ou `-BudgetEmails`; lista separada por vírgula). Sem
e-mails, o orçamento não é criado e o passo manual de
[`cost-management.md`](cost-management.md) se aplica.

Recomendação: manter esses valores num arquivo local `.azure/mvp.env.ps1` (a pasta
`.azure/` é ignorada pelo Git) com linhas `$env:NOME = 'valor'` e carregá-lo na sessão com
`. ./.azure/mvp.env.ps1`.

## 2. Acessos necessários

Diagnóstico somente leitura: `./scripts/azure/check-access.ps1` (após `az login`).

| Acesso                                                                               | Por quê                                                                                                                                                        |
| ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Owner` na assinatura (ou `Contributor` + `Role Based Access Control Administrator`) | Criar recursos e atribuir papéis às identidades gerenciadas                                                                                                    |
| Resource providers registrados                                                       | `Microsoft.App`, `ContainerRegistry`, `DBforPostgreSQL`, `Storage`, `KeyVault`, `OperationalInsights`, `Insights`, `ManagedIdentity`, `Network`, `Consumption` |
| Docker Desktop em execução                                                           | Build das imagens de bootstrap na fase `apps`                                                                                                                  |
| Registro de aplicativos no Entra ID                                                  | App Registrations do MVP ([`microsoft-365.md`](microsoft-365.md))                                                                                              |
| Exchange Administrator                                                               | Shared Mailbox e RBAC for Applications                                                                                                                         |

## 3. Recursos

Naming: `<tipo>-<prefixo>-<ambiente>`; nomes globais recebem um sufixo estável de 6
caracteres derivado da assinatura (`uniqueString`).

| Recurso                    | Nome                                           | Configuração                                                                                                                                                                |
| -------------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Grupo de recursos          | `rg-gfbr-mvp`                                  | tags `project`, `environment`, `managed-by`, `owner`, `data-classification`                                                                                                 |
| VNet (ADR-011, opção A)    | `vnet-gfbr-mvp`                                | `10.60.0.0/22`; sub-redes `snet-container-apps` (/24) e `snet-postgres` (/28)                                                                                               |
| Zona DNS privada           | `gfbr-mvp.private.postgres.database.azure.com` | vinculada à VNet                                                                                                                                                            |
| Log Analytics              | `log-gfbr-mvp`                                 | retenção 30 dias, limite de 0,2 GB/dia                                                                                                                                      |
| Application Insights       | `appi-gfbr-mvp`                                | baseado no workspace                                                                                                                                                        |
| Identidades gerenciadas    | `id-gfbr-api-mvp`, `id-gfbr-web-mvp`           | api: AcrPull, Key Vault Secrets User, Storage Blob Data Contributor; web: AcrPull                                                                                           |
| Container Registry         | `acrgfbrmvp<sufixo>`                           | Basic, sem admin user, sem pull anônimo                                                                                                                                     |
| Key Vault                  | `kv-gfbr-mvp-<sufixo>`                         | RBAC, soft delete 7 dias, purge protection                                                                                                                                  |
| Storage Account            | `stgfbrmvp<sufixo>`                            | Standard LRS, HTTPS/TLS 1.2, sem acesso público, sem chave compartilhada, versionamento, soft delete; containers `documents-raw`, `documents-derived`, `imports`, `exports` |
| PostgreSQL Flexible Server | `psql-gfbr-mvp-<sufixo>`                       | v18, Burstable B1ms, 32 GB, backup 7 dias, sem HA, TLS, sem acesso público (VNet), database `guardiao_financeiro`                                                           |
| Container Apps environment | `cae-gfbr-mvp`                                 | workload profiles, perfil Consumption; grupo gerenciado `rg-gfbr-mvp-cae-infra`                                                                                             |
| Container App (API)        | `ca-gfbr-api-mvp`                              | ingress interno; `/health` e `/ready`; 0,25 vCPU / 0,5 GiB; escala 0–1                                                                                                      |
| Container App (frontend)   | `ca-gfbr-web-mvp`                              | ingress externo HTTPS; página pública `/status`; escala 0–1                                                                                                                 |
| Container Apps job         | `caj-gfbr-migrate-mvp`                         | manual: `alembic upgrade head`                                                                                                                                              |
| Orçamento                  | `budget-gfbr-mvp`                              | mensal no grupo de recursos; alertas 50/80/100% real e 100% previsto                                                                                                        |

## 4. Procedimento

Pré-requisitos: Azure CLI com Bicep, PowerShell, Docker Desktop, `az login --tenant <tenant>`.

```powershell
$env:AZURE_SUBSCRIPTION_ID = '<assinatura>'
$env:AZURE_TENANT_ID       = '<tenant>'
$owner = '<responsavel>'

./scripts/check-env.ps1                          # ferramentas
./scripts/azure/check-access.ps1                 # permissões, providers, região (somente leitura)
./scripts/azure/estimate-cost.ps1                # estimativa (API pública de preços)

# Fase base — fundação (nada é criado com -WhatIf)
./scripts/azure/deploy-mvp.ps1 -Phase base -ProjectOwner $owner -BudgetEmails '<email>' -WhatIf
./scripts/azure/deploy-mvp.ps1 -Phase base -ProjectOwner $owner -BudgetEmails '<email>'

# Fase apps — imagens de bootstrap, aplicações e migrations
./scripts/azure/deploy-mvp.ps1 -Phase apps -ProjectOwner $owner -WhatIf
./scripts/azure/deploy-mvp.ps1 -Phase apps -ProjectOwner $owner

./scripts/azure/test-mvp.ps1                     # validação de segurança e saúde (somente leitura)
```

Em seguida, Microsoft 365: [`../infra/m365/README.md`](../infra/m365/README.md).

- Antes de criar, o script mostra assinatura, tenant e usuário e **para** se não forem os
  esperados; depois exige digitar `CONFIRMAR`.
- A senha administrativa do PostgreSQL é gerada pelo script, passada ao Bicep por variável
  de ambiente da sessão (removida ao final) e guardada somente no Key Vault; nunca aparece
  em tela, arquivo ou linha de comando.
- Estado local (nomes gerados, tag das imagens, início do orçamento) fica em
  `.azure/mvp.json`, ignorado pelo Git.
- Atualizar apenas as aplicações: `deploy-mvp.ps1 -Phase apps` (nova tag de imagem).
- A opção de rede B do ADR-011 é `-PrivateNetwork $false` e só pode ser escolhida **antes**
  de criar o PostgreSQL.

## 5. Como acessar

- Frontend: `https://ca-gfbr-web-mvp.<domínio-do-ambiente>/status` (URL impressa pelo
  script e gravada em `.azure/mvp.json`).
- API: sem endereço público; o frontend a alcança em `/api/*`. Health check público:
  `/api/health/ready` (sem dados sensíveis).
- PostgreSQL: sem acesso a partir da internet (ADR-011). Migrations e tarefas
  administrativas rodam como job dentro do ambiente.
- Logs: Log Analytics `log-gfbr-mvp` (tabelas `ContainerAppConsoleLogs_CL` e
  `ContainerAppSystemLogs_CL`).

## 6. Parâmetros do Bicep

`infra/azure/main.bicep` recebe `environment` (hoje só `mvp`), `location`,
`resourcePrefix`, `owner`, `tags` e `sku` (registro, storage, PostgreSQL e logs — tipo em
`infra/azure/types.bicep`), além de `enablePrivateNetwork`, faixas de rede e orçamento.
Valores dinâmicos chegam por `parameters/mvp.bicepparam` via variáveis `GFBR_*` definidas
pelo script.

## 7. Custos, backup e remoção

- Custos e classificação: [`cost-management.md`](cost-management.md).
- Backup e restauração: [`backup-restore.md`](backup-restore.md).
- Remoção (nunca automática): [`teardown-mvp.md`](teardown-mvp.md).
