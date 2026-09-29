<#
.SYNOPSIS
  Deploy da fundacao Azure do MVP do Guardiao Financeiro BR (Sprint 0).

.DESCRIPTION
  Unico ambiente do projeto: MVP (ADR-001). Nenhum outro ambiente e criado.

  Fase "base": grupo de recursos, VNet (ADR-011), Log Analytics/Application Insights,
  identidades gerenciadas, ACR, Key Vault, Storage (containers privados), PostgreSQL 18
  com o database guardiao_financeiro, ambiente do Container Apps e orcamento.
  Fase "apps": build e push das imagens de bootstrap, aplicacoes api/web e job de
  migracao (executado ao final).

  Antes de qualquer acao o script confirma assinatura, tenant e usuario (secao 11 do
  plano) e PARA se nao corresponderem ao esperado.

  -WhatIf executa somente "az deployment sub what-if": nada e criado.
  Sem -WhatIf o script exige digitar CONFIRMAR antes de criar/alterar recursos.

  Nenhum segredo e exibido, versionado ou passado na linha de comando: a senha do
  PostgreSQL e gerada aqui, enviada ao Bicep por variavel de ambiente da sessao e
  guardada somente no Key Vault.

.EXAMPLE
  . ./.azure/mvp.env.ps1   # valores locais (ignorado pelo Git); ver docs/deployment-azure.md
  ./scripts/azure/deploy-mvp.ps1 -Phase base -ProjectOwner '<responsavel>' -WhatIf
  ./scripts/azure/deploy-mvp.ps1 -Phase base -ProjectOwner '<responsavel>' -BudgetEmails 'alertas@<dominio>'
  ./scripts/azure/deploy-mvp.ps1 -Phase apps -ProjectOwner '<responsavel>' -WhatIf
  ./scripts/azure/deploy-mvp.ps1 -Phase apps -ProjectOwner '<responsavel>'
#>
[CmdletBinding()]
param(
    [ValidateSet('base', 'apps')]
    [string]$Phase = 'base',
    [switch]$WhatIf,
    [string]$SubscriptionId = $env:AZURE_SUBSCRIPTION_ID,
    [string]$TenantId = $env:AZURE_TENANT_ID,
    [string]$Region = $(if ($env:AZURE_REGION) { $env:AZURE_REGION } else { 'brazilsouth' }),
    [string]$ResourcePrefix = $(if ($env:RESOURCE_PREFIX) { $env:RESOURCE_PREFIX } else { 'gfbr' }),
    [string]$ProjectOwner = $env:PROJECT_OWNER,
    [bool]$PrivateNetwork = $true,
    [int]$BudgetAmount = $(if ($env:MVP_BUDGET_AMOUNT) { [int]$env:MVP_BUDGET_AMOUNT } else { 50 }),
    [string]$BudgetEmails = $env:MVP_BUDGET_EMAILS,
    [string]$ImageTag
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

if (-not $ProjectOwner) { throw 'Informe -ProjectOwner (tag owner) ou $env:PROJECT_OWNER.' }

$root = Get-RepoRoot
$paramsFile = Join-Path $root 'infra/azure/parameters/mvp.bicepparam'
$state = Read-MvpState

Write-Step 'Validando contexto Azure'
Assert-AzContext -ExpectedSubscriptionId $SubscriptionId -ExpectedTenantId $TenantId | Out-Null

$envNames = @('GFBR_AZURE_REGION', 'GFBR_RESOURCE_PREFIX', 'GFBR_PROJECT_OWNER', 'GFBR_ENABLE_PRIVATE_NETWORK',
    'GFBR_DEPLOYER_OBJECT_ID', 'GFBR_POSTGRES_ADMIN_PASSWORD', 'GFBR_DEPLOY_APPS', 'GFBR_IMAGE_TAG',
    'GFBR_BUDGET_AMOUNT', 'GFBR_BUDGET_EMAILS', 'GFBR_BUDGET_START_DATE')

try {
    $env:GFBR_AZURE_REGION = $Region
    $env:GFBR_RESOURCE_PREFIX = $ResourcePrefix
    $env:GFBR_PROJECT_OWNER = $ProjectOwner
    $env:GFBR_ENABLE_PRIVATE_NETWORK = $PrivateNetwork.ToString().ToLowerInvariant()
    $env:GFBR_DEPLOYER_OBJECT_ID = Get-SignedInUserObjectId
    $env:GFBR_BUDGET_AMOUNT = "$BudgetAmount"
    $env:GFBR_BUDGET_EMAILS = ($BudgetEmails -replace '\s', '')
    # O inicio do orcamento e fixado no primeiro deploy (reexecucoes nao o alteram).
    if (-not $state.budgetStartDate) { $state.budgetStartDate = (Get-Date).ToUniversalTime().ToString('yyyy-MM-01') }
    $env:GFBR_BUDGET_START_DATE = $state.budgetStartDate
    $env:GFBR_DEPLOY_APPS = 'false'
    $env:GFBR_IMAGE_TAG = ''

    # ---- Senha administrativa do PostgreSQL: reutiliza a do Key Vault; gera so na criacao.
    $password = $null
    if ($state.keyVaultName) {
        $password = Get-KeyVaultSecretOrNull -VaultName $state.keyVaultName -Name 'postgres-admin-password'
    }
    if (-not $password) {
        if ($state.keyVaultName -and -not $WhatIf) {
            throw 'Key Vault existe mas a senha do PostgreSQL nao foi lida. Verifique o papel Key Vault Secrets Officer.'
        }
        $password = New-StrongPassword
    }
    $env:GFBR_POSTGRES_ADMIN_PASSWORD = $password

    if ($Phase -eq 'apps') {
        if (-not $state.registryLoginServer) { throw 'Execute antes a fase base (-Phase base).' }
        if (-not $ImageTag) { $ImageTag = New-ImageTag }
        $env:GFBR_DEPLOY_APPS = 'true'
        $env:GFBR_IMAGE_TAG = $ImageTag
        Write-Step "Tag das imagens: $ImageTag"
    }

    $deploymentName = "gfbr-mvp-$Phase-$(Get-Date -Format 'yyyyMMddHHmmss')"

    if ($WhatIf) {
        Write-Step "Simulacao (what-if) da fase '$Phase' - nada sera criado"
        Invoke-Az deployment sub what-if --name $deploymentName --location $Region `
            --parameters $paramsFile
        return
    }

    Confirm-Action ("A fase '{0}' vai CRIAR/ALTERAR recursos do MVP na assinatura {1} (regiao {2}) e gerar custo." -f $Phase, $SubscriptionId, $Region)

    if ($Phase -eq 'apps') {
        Publish-Images -RegistryLoginServer $state.registryLoginServer -Tag $ImageTag -Root $root
    }

    Write-Step "Deploy da fase '$Phase'"
    $outputs = Invoke-AzJson deployment sub create --name $deploymentName --location $Region `
        --parameters $paramsFile --query properties.outputs
    foreach ($key in @('resourceGroupName', 'registryName', 'registryLoginServer', 'keyVaultName', 'storageAccountName',
            'postgresServerName', 'postgresDatabaseName', 'containerAppsEnvironmentName', 'webAppName', 'apiAppName',
            'migrateJobName', 'webUrl', 'budgetCreated')) {
        $state[$key] = $outputs.$key.value
    }
    if ($Phase -eq 'apps') { $state.imageTag = $ImageTag }
    Write-MvpState $state

    if ($Phase -eq 'apps') {
        Start-MigrationJob -ResourceGroup $state.resourceGroupName -JobName $state.migrateJobName
        Write-Step "Aplicacao publicada: $($state.webUrl)/status"
        Write-Host 'Proximo passo: ./scripts/azure/test-mvp.ps1'
    }
    else {
        if (-not $state.budgetCreated) {
            Write-Warning 'Orcamento nao criado (sem -BudgetEmails). Siga o passo manual em docs/cost-management.md.'
        }
        Write-Step 'Fase base concluida. Proximo passo: -Phase apps -WhatIf'
    }
}
finally {
    foreach ($name in $envNames) { Remove-Item "Env:$name" -ErrorAction SilentlyContinue }
}
