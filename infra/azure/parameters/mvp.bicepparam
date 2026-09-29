// Parâmetros do ambiente MVP (único ambiente do projeto — ADR-001).
//
// Nada sensível ou específico do tenant fica neste arquivo: valores dinâmicos chegam por
// variáveis de ambiente definidas por scripts/azure/deploy-mvp.ps1 na sessão do PowerShell.
using '../main.bicep'

param environment = 'mvp'
param location = readEnvironmentVariable('GFBR_AZURE_REGION', 'brazilsouth')
param resourcePrefix = readEnvironmentVariable('GFBR_RESOURCE_PREFIX', 'gfbr')
param owner = readEnvironmentVariable('GFBR_PROJECT_OWNER')
param enablePrivateNetwork = bool(readEnvironmentVariable('GFBR_ENABLE_PRIVATE_NETWORK', 'true'))

param deployerObjectId = readEnvironmentVariable('GFBR_DEPLOYER_OBJECT_ID')
param postgresAdminPassword = readEnvironmentVariable('GFBR_POSTGRES_ADMIN_PASSWORD')
param deployApps = bool(readEnvironmentVariable('GFBR_DEPLOY_APPS', 'false'))
param imageTag = readEnvironmentVariable('GFBR_IMAGE_TAG', '')

param budgetStartDate = readEnvironmentVariable('GFBR_BUDGET_START_DATE')
param budgetAmount = int(readEnvironmentVariable('GFBR_BUDGET_AMOUNT', '50'))
param budgetContactEmails = empty(readEnvironmentVariable('GFBR_BUDGET_EMAILS', ''))
  ? []
  : split(readEnvironmentVariable('GFBR_BUDGET_EMAILS', ''), ',')
