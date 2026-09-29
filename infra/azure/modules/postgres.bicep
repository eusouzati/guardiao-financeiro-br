// PostgreSQL 18 Flexible Server do MVP (ADR-003, ADR-011).
//
// - SKU econômica, sem alta disponibilidade, backup local com retenção configurável.
// - TLS obrigatório (require_secure_transport = on, padrão do serviço).
// - Rede privada (usePrivateNetwork=true): sem endpoint público.
//   Sem rede privada: endpoint público liberado somente para serviços do Azure — nenhum IP
//   externo e nunca 0.0.0.0/0.
// - Autenticação Entra habilitada junto com senha. A senha administrativa é usada apenas no
//   bootstrap e fica somente no Key Vault (débito técnico: migrar a aplicação para
//   identidade gerenciada — docs/sprint-0/README.md).
param name string
param location string
param tags object
param skuName string
param skuTier string
param storageSizeGB int
param backupRetentionDays int
@secure()
param administratorPassword string
param administratorLogin string = 'gfbradmin'
param databaseName string = 'guardiao_financeiro'
@description('true = integração à VNet, sem endpoint público (ADR-011). Definido em tempo de compilação.')
param usePrivateNetwork bool
@description('Sub-rede delegada (obrigatória com usePrivateNetwork=true).')
param delegatedSubnetId string = ''
param privateDnsZoneId string = ''


resource server 'Microsoft.DBforPostgreSQL/flexibleServers@2025-08-01' = {
  name: name
  location: location
  tags: tags
  sku: { name: skuName, tier: skuTier }
  properties: {
    version: '18'
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorPassword
    authConfig: {
      activeDirectoryAuth: 'Enabled'
      passwordAuth: 'Enabled'
      tenantId: tenant().tenantId
    }
    storage: { storageSizeGB: storageSizeGB, autoGrow: 'Disabled' }
    backup: { backupRetentionDays: backupRetentionDays, geoRedundantBackup: 'Disabled' }
    highAvailability: { mode: 'Disabled' }
    network: usePrivateNetwork
      ? {
          delegatedSubnetResourceId: delegatedSubnetId
          privateDnsZoneArmResourceId: privateDnsZoneId
          publicNetworkAccess: 'Disabled'
        }
      : { publicNetworkAccess: 'Enabled' }
  }
}

resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2025-08-01' = {
  parent: server
  name: databaseName
  properties: { charset: 'UTF8', collation: 'en_US.utf8' }
}

// Somente sem rede privada: a regra especial 0.0.0.0–0.0.0.0 libera apenas serviços
// hospedados no Azure (não é 0.0.0.0/0). Senha forte e TLS continuam obrigatórios.
resource allowAzureServices 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2025-08-01' = if (!usePrivateNetwork) {
  parent: server
  name: 'AllowAllAzureServicesAndResourcesWithinAzureIps'
  properties: { startIpAddress: '0.0.0.0', endIpAddress: '0.0.0.0' }
  dependsOn: [database]
}

output name string = server.name
output fqdn string = server.properties.fullyQualifiedDomainName
output administratorLogin string = administratorLogin
output databaseName string = database.name
