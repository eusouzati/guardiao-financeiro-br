// Ambiente do Azure Container Apps com workload profiles, somente perfil Consumption
// (escala a zero, sem custo fixo de perfil dedicado). Logs no Log Analytics.
// Com sub-rede informada, o ambiente fica na VNet do MVP e alcança o PostgreSQL privado.
param name string
param location string
param tags object
param logAnalyticsWorkspaceName string
@description('true = ambiente na VNet do MVP (ADR-011). Definido em tempo de compilação.')
param useVnet bool
@description('Sub-rede delegada a Microsoft.App/environments (obrigatória com useVnet=true).')
param infrastructureSubnetId string = ''
@description('Grupo de recursos gerenciado pela plataforma (somente com VNet).')
param infrastructureResourceGroupName string


resource workspace 'Microsoft.OperationalInsights/workspaces@2025-07-01' existing = {
  name: logAnalyticsWorkspaceName
}

resource environment 'Microsoft.App/managedEnvironments@2026-01-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
    vnetConfiguration: useVnet
      ? {
          infrastructureSubnetId: infrastructureSubnetId
          internal: false // o frontend é público; a API tem ingress interno
        }
      : null
    infrastructureResourceGroup: useVnet ? infrastructureResourceGroupName : null
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: workspace.properties.customerId
        sharedKey: workspace.listKeys().primarySharedKey
      }
    }
    // Criptografa o tráfego entre aplicações dentro do ambiente (web → api).
    peerTrafficConfiguration: { encryption: { enabled: true } }
    zoneRedundant: false
  }
}

output id string = environment.id
output name string = environment.name
output defaultDomain string = environment.properties.defaultDomain
