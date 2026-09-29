// Rede do MVP (ADR-011): uma VNet com duas sub-redes delegadas e uma zona DNS privada.
//
// - snet-container-apps: ambiente do Container Apps (workload profiles, perfil Consumption).
// - snet-postgres:       PostgreSQL Flexible Server com integração à VNet (sem endpoint público).
// - Zona DNS privada do PostgreSQL vinculada à VNet.
//
// Sem Private Endpoints, NAT Gateway, Firewall ou peering: nada disso é necessário no MVP.
param resourcePrefix string
param environment string
param location string
param tags object
param addressPrefix string
param containerAppsSubnetPrefix string
param postgresSubnetPrefix string

var baseName = '${resourcePrefix}-${environment}'

resource vnet 'Microsoft.Network/virtualNetworks@2025-05-01' = {
  name: 'vnet-${baseName}'
  location: location
  tags: tags
  properties: {
    addressSpace: { addressPrefixes: [addressPrefix] }
    subnets: [
      {
        name: 'snet-container-apps'
        properties: {
          addressPrefix: containerAppsSubnetPrefix
          delegations: [
            {
              name: 'container-apps'
              properties: { serviceName: 'Microsoft.App/environments' }
            }
          ]
        }
      }
      {
        name: 'snet-postgres'
        properties: {
          addressPrefix: postgresSubnetPrefix
          // O PostgreSQL adiciona este service endpoint ao usar a sub-rede; declará-lo evita
          // que reimplantações o removam (apareceu como remoção no what-if da fase apps).
          serviceEndpoints: [
            { service: 'Microsoft.Storage' }
          ]
          delegations: [
            {
              name: 'postgres-flexible'
              properties: { serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers' }
            }
          ]
        }
      }
    ]
  }
}

// Integração à VNet exige zona terminada em ".postgres.database.azure.com".
resource postgresDnsZone 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: '${baseName}.private.postgres.database.azure.com'
  location: 'global'
  tags: tags
}

resource postgresDnsLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: postgresDnsZone
  name: 'link-${vnet.name}'
  location: 'global'
  tags: tags
  properties: {
    registrationEnabled: false
    virtualNetwork: { id: vnet.id }
  }
}

output vnetName string = vnet.name
output containerAppsSubnetId string = vnet.properties.subnets[0].id
output postgresSubnetId string = vnet.properties.subnets[1].id
output postgresPrivateDnsZoneId string = postgresDnsZone.id
