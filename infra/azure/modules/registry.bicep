// Azure Container Registry sem usuário admin e sem pull anônimo; pull via identidades
// gerenciadas (AcrPull) e push somente por quem executa o deploy (AcrPush).
param name string
param location string
param tags object
param skuName string
param pullPrincipalIds array
@description('Quem publica imagens (usuário do deploy). Vazio = não atribui.')
param pushPrincipalId string

var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'
var acrPushRoleId = '8311e382-0749-4cb8-b61a-304f252e45ec'

resource registry 'Microsoft.ContainerRegistry/registries@2025-11-01' = {
  name: name
  location: location
  tags: tags
  sku: { name: skuName }
  properties: {
    adminUserEnabled: false
    anonymousPullEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

resource pull 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for principalId in pullPrincipalIds: {
    name: guid(registry.id, principalId, acrPullRoleId)
    scope: registry
    properties: {
      principalId: principalId
      principalType: 'ServicePrincipal'
      roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
    }
  }
]

resource push 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(pushPrincipalId)) {
  name: guid(registry.id, pushPrincipalId, acrPushRoleId)
  scope: registry
  properties: {
    principalId: pushPrincipalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPushRoleId)
  }
}

output name string = registry.name
output loginServer string = registry.properties.loginServer
