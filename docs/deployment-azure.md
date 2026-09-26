# Implantação no Azure

> **Status: planejado.** Ambiente `dev` na **Sprint 1A** (ADR-017); `hml`/`prod` na
> **Sprint 8** (ADR-014). Nenhum recurso é criado sem estimativa de custo, `what-if` e
> autorização explícita do mantenedor.

## 1. Arquitetura alvo

| Recurso                                       | Uso                         | Observações                                                                |
| --------------------------------------------- | --------------------------- | -------------------------------------------------------------------------- |
| Azure Container Apps (+ environment)          | API, frontend, worker       | Managed Identity; escala mínima 0/1 conforme ambiente                      |
| Azure Container Registry                      | Imagens                     | Pull via Managed Identity (AcrPull), sem admin user                        |
| Azure Database for PostgreSQL Flexible Server | Metadados                   | PostgreSQL 18; rede privada ou firewall restrito; Entra auth quando viável |
| Storage Account / Blob                        | Documentos originais        | Privado, soft delete, versionamento, sem acesso público                    |
| Azure Key Vault                               | Segredos, certificado Graph | RBAC, soft delete, purge protection                                        |
| Application Insights + Log Analytics          | Observabilidade             | Sem documentos em telemetria; retenção definida                            |
| Microsoft Entra ID                            | Identidade                  | App registrations: SPA, API, ingestão Graph                                |

## 2. Acessos necessários (Sprint 1A)

Diagnóstico somente leitura: `./scripts/azure/check-access.ps1` (após `az login`).

| #   | Acesso                                | Por quê                                                              | Mínimo recomendado                                                                                                                   |
| --- | ------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Assinatura Azure definida             | Onde os recursos `dev` serão criados                                 | Assinatura ativa; preferencialmente dedicada ou, no mínimo, grupo de recursos `rg-guardiao-dev` exclusivo                            |
| 2   | Sessão da Azure CLI do mantenedor     | Executar build/validate/what-if/deploy                               | `az login` na máquina do mantenedor; **nenhuma credencial é compartilhada no chat nem gravada no repositório**                       |
| 3   | Criar recursos                        | Container Apps, ACR, PostgreSQL, Storage, Key Vault, monitoramento   | `Contributor` no grupo de recursos (ou `Owner` da assinatura)                                                                        |
| 4   | Atribuir papéis às Managed Identities | `AcrPull`, `Key Vault Secrets User`, `Storage Blob Data Contributor` | `Role Based Access Control Administrator` no grupo de recursos, idealmente com condição limitando a esses papéis (ou `Owner`)        |
| 5   | Resource providers registrados        | Pré-requisito dos serviços                                           | `Microsoft.App`, `ContainerRegistry`, `DBforPostgreSQL`, `Storage`, `KeyVault`, `OperationalInsights`, `Insights`, `ManagedIdentity` |
| 6   | Orçamento com alerta                  | Evitar surpresa de custo                                             | Budget mensal no grupo de recursos com alertas (ex.: 50/80/100%)                                                                     |
| 7   | Barreira de acesso ao `dev`           | Entra ID completo só na Sprint 7                                     | IP público do mantenedor **ou** permissão para registrar app no Entra (Easy Auth)                                                    |
| 8   | (Sprint 9) GitHub → Azure via OIDC    | CI/CD sem segredo                                                    | App registration/identidade com federated credential, escopo mínimo por environment                                                  |

### 2.1 Situação verificada do ambiente `dev` (2026-09-26)

Diagnóstico `check-access.ps1` executado pelo mantenedor (IDs de assinatura/tenant
**não** são registrados no repositório):

- Assinatura do tipo **Free Trial** (`quotaId FreeTrial_2014-09-01`), estado `Enabled`.
- Usuário com papel **Owner** na assinatura → itens 3 e 4 atendidos.
- Bicep CLI instalado; região **`brazilsouth`** confirmada pelo mantenedor; Container Apps
  e PostgreSQL Flexible consultáveis na região.
- Resource providers necessários **todos registrados** (`Microsoft.App`, `ContainerRegistry`,
  `DBforPostgreSQL` e `KeyVault` registrados pelo mantenedor em 2026-09-26).
- Tenant permite registro de aplicativos (Easy Auth é viável).

### 2.2 Restrições de uma assinatura Free Trial

- Crédito promocional por tempo limitado (30 dias na oferta atual) e limite de gastos:
  ao terminar, sem migração para pay-as-you-go, a assinatura é desativada e os recursos
  param. Para manter os serviços gratuitos de 12 meses é preciso migrar para
  pay-as-you-go dentro do prazo indicado pela Microsoft.
- Cost Management tem suporte limitado para Free Trial; orçamentos podem não estar
  disponíveis — o limite de gastos da conta é a proteção principal enquanto durar.
- Algumas combinações região/SKU (especialmente PostgreSQL Flexible) podem ser
  bloqueadas para assinaturas de avaliação; o `what-if`/deploy revela isso.
- Por isso o Bicep do `dev` usa **somente SKUs mínimos**: PostgreSQL Burstable B1ms sem HA
  e sem backup geo-redundante, Container Apps em consumo com escala a zero, ACR Basic,
  Storage LRS, Log Analytics com limite diário de ingestão e retenção mínima.
- Tudo parametrizado: migrar o `dev` para outra assinatura é trocar parâmetros.

### 2.3 Decisões para o `dev`

- Uso apenas durante o trial (sem pay-as-you-go); ambiente descartável e recriável.
- Barreira de acesso: Easy Auth com Entra ID restrito ao tenant do mantenedor.
- Crédito do trial verificado no portal em 26/09/2026: US$ 199,99 restantes, expirando em
  26 dias (por volta de 22/10/2026). A Sprint 1A precisa ser executada e validada antes disso.

## 3. Parâmetros

- `environment`: `dev` | `hml` | `prod`
- `location`: padrão sugerido `brazilsouth` (parâmetro; ver `lgpd.md` §4)
- SKUs por ambiente (ex.: Burstable em dev/hml).

## 4. Estrutura prevista

```text
infra/
├── main.bicep
├── parameters/
│   ├── dev.bicepparam
│   ├── hml.bicepparam
│   └── prod.bicepparam
└── modules/
    ├── container-app.bicep
    ├── database.bicep
    ├── storage.bicep
    ├── keyvault.bicep
    ├── monitoring.bicep
    └── registry.bicep
```

## 5. A documentar nas Sprints 1A (dev) e 8 (hml/prod)

- Custos recorrentes estimados por ambiente e recursos que podem ser desligados.
- Procedimento de implantação (validate → what-if → aprovação → deploy).
- Backup/restauração testados ([`backup-recovery.md`](backup-recovery.md)).
- Configuração OIDC GitHub → Azure (federated credentials por environment).
