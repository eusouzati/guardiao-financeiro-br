// Storage Account para documentos: privada, somente HTTPS/TLS 1.2+, sem chave compartilhada
// (acesso por Entra ID/RBAC), soft delete e versionamento de blobs (ADR-005).
param name string
param location string
param tags object
param skuName string
param blobDataPrincipalId string

var blobDataContributorRoleId = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
var containers = ['documents-raw', 'documents-derived', 'imports', 'exports']

resource account 'Microsoft.Storage/storageAccounts@2026-04-01' = {
  name: name
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: { name: skuName }
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    allowCrossTenantReplication: false
    defaultToOAuthAuthentication: true
    publicNetworkAccess: 'Enabled'
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2026-04-01' = {
  parent: account
  name: 'default'
  properties: {
    isVersioningEnabled: true
    deleteRetentionPolicy: { enabled: true, days: 7 }
    containerDeleteRetentionPolicy: { enabled: true, days: 7 }
  }
}

resource blobContainers 'Microsoft.Storage/storageAccounts/blobServices/containers@2026-04-01' = [
  for containerName in containers: {
    parent: blobService
    name: containerName
    properties: { publicAccess: 'None' }
  }
]

resource blobDataContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(account.id, blobDataPrincipalId, blobDataContributorRoleId)
  scope: account
  properties: {
    principalId: blobDataPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', blobDataContributorRoleId)
  }
}

output name string = account.name
output blobEndpoint string = account.properties.primaryEndpoints.blob
