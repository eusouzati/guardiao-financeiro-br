// Key Vault com RBAC, soft delete e purge protection.
// A API lê segredos (Secrets User); quem executa o deploy administra (Secrets Officer).
// Único segredo nesta sprint: senha administrativa do PostgreSQL (bootstrap, ADR-003).
param name string
param location string
param tags object
param vaultReaderPrincipalId string
param vaultAdminPrincipalId string
@secure()
param postgresAdminPassword string

// IDs públicos de papéis internos do Azure: Key Vault Secrets User e Key Vault Secrets Officer.
var vaultReaderRoleId = '4633458b-17de-408a-b874-0445c86b69e6'
var vaultAdminRoleId = 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7'

resource vault 'Microsoft.KeyVault/vaults@2026-02-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    tenantId: tenant().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    // Impede purge acidental durante a retenção (docs/teardown-mvp.md explica o efeito).
    enablePurgeProtection: true
    publicNetworkAccess: 'Enabled'
    networkAcls: { defaultAction: 'Allow', bypass: 'AzureServices' }
  }
}

resource postgresSecret 'Microsoft.KeyVault/vaults/secrets@2026-02-01' = {
  parent: vault
  name: 'postgres-admin-password'
  properties: {
    value: postgresAdminPassword
    contentType: 'text/plain'
  }
}

resource secretsUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(vault.id, vaultReaderPrincipalId, vaultReaderRoleId)
  scope: vault
  properties: {
    principalId: vaultReaderPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', vaultReaderRoleId)
  }
}

resource secretsOfficer 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(vault.id, vaultAdminPrincipalId, vaultAdminRoleId)
  scope: vault
  properties: {
    principalId: vaultAdminPrincipalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', vaultAdminRoleId)
  }
}

output name string = vault.name
output uri string = vault.properties.vaultUri
