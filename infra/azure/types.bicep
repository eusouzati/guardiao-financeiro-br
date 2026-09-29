// Tipos compartilhados da infraestrutura do MVP.

@export()
@description('SKUs e dimensionamento dos recursos. Padrões econômicos para o MVP (docs/cost-management.md).')
type skuConfig = {
  @description('SKU do Azure Container Registry.')
  registry: 'Basic' | 'Standard' | 'Premium'

  @description('SKU da Storage Account.')
  storage: 'Standard_LRS' | 'Standard_ZRS'

  @description('PostgreSQL Flexible Server.')
  postgres: {
    name: string
    tier: 'Burstable' | 'GeneralPurpose' | 'MemoryOptimized'
    @minValue(32)
    storageGB: int
    @minValue(7)
    @maxValue(35)
    backupRetentionDays: int
  }

  @description('Retenção do Log Analytics, em dias.')
  @minValue(30)
  logRetentionDays: int

  @description('Limite diário de ingestão do Log Analytics, em GB (string decimal, ex.: "0.2").')
  logDailyQuotaGb: string
}
