// Identidades gerenciadas das aplicações (menor privilégio; sem Owner/Contributor).
//
// - api: AcrPull, Key Vault Secrets User e Storage Blob Data Contributor (atribuídos nos
//        módulos de cada recurso).
// - web: somente AcrPull (Nginx + SPA não acessa dados).
//
// A identidade do worker será criada na sprint que introduzir o worker (ADR-004); a de
// deploy (GitHub OIDC) na Sprint 9.
param resourcePrefix string
param environment string
param location string
param tags object

resource api 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: 'id-${resourcePrefix}-api-${environment}'
  location: location
  tags: tags
}

resource web 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: 'id-${resourcePrefix}-web-${environment}'
  location: location
  tags: tags
}

output apiId string = api.id
output apiPrincipalId string = api.properties.principalId
output apiClientId string = api.properties.clientId
output webId string = web.id
output webPrincipalId string = web.properties.principalId
