// =============================================================================
// Guardião Financeiro BR — fundação Azure do MVP (Sprint 0)
//
// ADR-001 (MVP cloud-first), ADR-011 (rede), ADR-019 (IaC).
//
// Escopo de assinatura: cria o grupo de recursos e os recursos do único ambiente
// existente (MVP). Duas fases (ver scripts/azure/deploy-mvp.ps1):
//   1. deployApps=false → fundação: rede, monitoramento, identidades, ACR, Key Vault,
//      Storage, PostgreSQL, ambiente do Container Apps e orçamento.
//   2. deployApps=true  → aplicações de bootstrap (api, web) e job de migração, depois
//      que as imagens estiverem no ACR.
// =============================================================================
targetScope = 'subscription'

import { skuConfig } from 'types.bicep'

@description('Nome do ambiente. Hoje existe somente o MVP (ADR-001); ampliar a lista é decisão explícita do responsável pelo projeto.')
@allowed(['mvp'])
param environment string = 'mvp'

@description('Região dos recursos. Confirmada pelo responsável antes do deploy.')
param location string = 'brazilsouth'

@description('Prefixo curto do projeto usado nos nomes dos recursos.')
@minLength(2)
@maxLength(6)
param resourcePrefix string = 'gfbr'

@description('Responsável pelo projeto (tag owner). Não use e-mail pessoal real em arquivos versionados.')
@minLength(1)
param owner string

@description('Tags adicionais, mescladas às tags padrão.')
param tags object = {}

@description('SKUs e dimensionamento (ver types.bicep).')
param sku skuConfig = {
  registry: 'Basic'
  storage: 'Standard_LRS'
  postgres: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
    storageGB: 32
    backupRetentionDays: 7
  }
  logRetentionDays: 30
  logDailyQuotaGb: '0.2'
}

@description('Rede privada para PostgreSQL e Container Apps (ADR-011). false = endpoint público restrito.')
param enablePrivateNetwork bool = true

@description('Espaço de endereços da VNet (usado somente com enablePrivateNetwork=true).')
param vnetAddressPrefix string = '10.60.0.0/22'

@description('Sub-rede do ambiente do Container Apps (mínimo /27 para workload profiles).')
param containerAppsSubnetPrefix string = '10.60.0.0/24'

@description('Sub-rede delegada ao PostgreSQL Flexible Server.')
param postgresSubnetPrefix string = '10.60.1.0/28'

@description('Object ID (Entra) de quem executa o deploy: recebe AcrPush e Key Vault Secrets Officer.')
param deployerObjectId string

@secure()
@description('Senha do administrador do PostgreSQL (bootstrap). Gerada pelo script e guardada somente no Key Vault.')
param postgresAdminPassword string

@description('Fase 2: publica as aplicações de bootstrap.')
param deployApps bool = false

@description('Tag das imagens no ACR (obrigatória quando deployApps=true).')
param imageTag string = ''

@description('Valor mensal do orçamento, na moeda da cobrança da assinatura.')
param budgetAmount int = 50

@description('Início do orçamento (AAAA-MM-01). Fixado no primeiro deploy para que reexecuções não o alterem.')
param budgetStartDate string

@description('E-mails de alerta do orçamento. Vazio = orçamento não é criado (passo manual documentado).')
param budgetContactEmails array = []

var baseName = '${resourcePrefix}-${environment}'
// Sufixo estável por assinatura para nomes globalmente únicos (ACR, Key Vault, Storage).
var suffix = take(uniqueString(subscription().id, resourcePrefix, environment), 6)
var allTags = union(
  {
    project: 'guardiao-financeiro-br'
    environment: environment
    'managed-by': 'bicep'
    owner: owner
    'data-classification': 'business'
  },
  tags
)

resource rg 'Microsoft.Resources/resourceGroups@2025-04-01' = {
  name: 'rg-${baseName}'
  location: location
  tags: allTags
}

module network 'modules/network.bicep' = if (enablePrivateNetwork) {
  name: 'network'
  scope: rg
  params: {
    resourcePrefix: resourcePrefix
    environment: environment
    location: location
    tags: allTags
    addressPrefix: vnetAddressPrefix
    containerAppsSubnetPrefix: containerAppsSubnetPrefix
    postgresSubnetPrefix: postgresSubnetPrefix
  }
}

module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  scope: rg
  params: {
    resourcePrefix: resourcePrefix
    environment: environment
    location: location
    tags: allTags
    retentionInDays: sku.logRetentionDays
    dailyQuotaGb: sku.logDailyQuotaGb
  }
}

module identities 'modules/identities.bicep' = {
  name: 'identities'
  scope: rg
  params: {
    resourcePrefix: resourcePrefix
    environment: environment
    location: location
    tags: allTags
  }
}

module registry 'modules/registry.bicep' = {
  name: 'registry'
  scope: rg
  params: {
    name: 'acr${resourcePrefix}${environment}${suffix}'
    location: location
    tags: allTags
    skuName: sku.registry
    pullPrincipalIds: [identities.outputs.apiPrincipalId, identities.outputs.webPrincipalId]
    pushPrincipalId: deployerObjectId
  }
}

module keyVault 'modules/keyvault.bicep' = {
  name: 'keyvault'
  scope: rg
  params: {
    name: 'kv-${baseName}-${suffix}'
    location: location
    tags: allTags
    vaultReaderPrincipalId: identities.outputs.apiPrincipalId
    vaultAdminPrincipalId: deployerObjectId
    postgresAdminPassword: postgresAdminPassword
  }
}

module storage 'modules/storage.bicep' = {
  name: 'storage'
  scope: rg
  params: {
    name: 'st${resourcePrefix}${environment}${suffix}'
    location: location
    tags: allTags
    skuName: sku.storage
    blobDataPrincipalId: identities.outputs.apiPrincipalId
  }
}

module postgres 'modules/postgres.bicep' = {
  name: 'postgres'
  scope: rg
  params: {
    name: 'psql-${baseName}-${suffix}'
    location: location
    tags: allTags
    skuName: sku.postgres.name
    skuTier: sku.postgres.tier
    storageSizeGB: sku.postgres.storageGB
    backupRetentionDays: sku.postgres.backupRetentionDays
    administratorPassword: postgresAdminPassword
    delegatedSubnetId: enablePrivateNetwork ? network!.outputs.postgresSubnetId : ''
    privateDnsZoneId: enablePrivateNetwork ? network!.outputs.postgresPrivateDnsZoneId : ''
  }
}

module containerAppsEnvironment 'modules/container-apps-environment.bicep' = {
  name: 'container-apps-environment'
  scope: rg
  params: {
    name: 'cae-${baseName}'
    location: location
    tags: allTags
    logAnalyticsWorkspaceName: monitoring.outputs.workspaceName
    infrastructureSubnetId: enablePrivateNetwork ? network!.outputs.containerAppsSubnetId : ''
    infrastructureResourceGroupName: 'rg-${baseName}-cae-infra'
  }
}

module costManagement 'modules/cost-management.bicep' = if (!empty(budgetContactEmails)) {
  name: 'cost-management'
  scope: rg
  params: {
    name: 'budget-${baseName}'
    amount: budgetAmount
    startDate: budgetStartDate
    contactEmails: budgetContactEmails
  }
}

module apps 'modules/container-apps.bicep' = if (deployApps) {
  name: 'container-apps'
  scope: rg
  params: {
    resourcePrefix: resourcePrefix
    environment: environment
    location: location
    tags: allTags
    environmentId: containerAppsEnvironment.outputs.id
    apiIdentityId: identities.outputs.apiId
    apiIdentityClientId: identities.outputs.apiClientId
    webIdentityId: identities.outputs.webId
    registryLoginServer: registry.outputs.loginServer
    keyVaultUri: keyVault.outputs.uri
    postgresFqdn: postgres.outputs.fqdn
    postgresAdminLogin: postgres.outputs.administratorLogin
    postgresDatabase: postgres.outputs.databaseName
    storageBlobEndpoint: storage.outputs.blobEndpoint
    appInsightsConnectionString: monitoring.outputs.appInsightsConnectionString
    imageTag: imageTag
  }
}

output resourceGroupName string = rg.name
output registryName string = registry.outputs.name
output registryLoginServer string = registry.outputs.loginServer
output keyVaultName string = keyVault.outputs.name
output storageAccountName string = storage.outputs.name
output postgresServerName string = postgres.outputs.name
output postgresDatabaseName string = postgres.outputs.databaseName
output containerAppsEnvironmentName string = containerAppsEnvironment.outputs.name
output webAppName string = 'ca-${resourcePrefix}-web-${environment}'
output apiAppName string = 'ca-${resourcePrefix}-api-${environment}'
output migrateJobName string = 'caj-${resourcePrefix}-migrate-${environment}'
output webUrl string = 'https://ca-${resourcePrefix}-web-${environment}.${containerAppsEnvironment.outputs.defaultDomain}'
output budgetCreated bool = !empty(budgetContactEmails)
