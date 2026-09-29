// Log Analytics (retenção econômica e limite diário de ingestão) + Application Insights
// baseado em workspace. Nunca enviar conteúdo de documentos fiscais para telemetria.
param resourcePrefix string
param environment string
param location string
param tags object
param retentionInDays int
@description('Limite diário de ingestão em GB (string decimal, ex.: "0.2").')
param dailyQuotaGb string

resource workspace 'Microsoft.OperationalInsights/workspaces@2025-07-01' = {
  name: 'log-${resourcePrefix}-${environment}'
  location: location
  tags: tags
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: retentionInDays
    workspaceCapping: { dailyQuotaGb: json(dailyQuotaGb) }
    features: { enableLogAccessUsingOnlyResourcePermissions: true }
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-${resourcePrefix}-${environment}'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspace.id
    IngestionMode: 'LogAnalytics'
    DisableIpMasking: false
  }
}

output workspaceName string = workspace.name
output appInsightsConnectionString string = appInsights.properties.ConnectionString
