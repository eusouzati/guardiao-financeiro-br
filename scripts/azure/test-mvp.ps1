<#
.SYNOPSIS
  Validacao pos-deploy do MVP (Sprint 0, etapa 0.9). SOMENTE LEITURA.

.DESCRIPTION
  Confere os controles de seguranca e a saude da aplicacao de bootstrap e imprime um
  resumo [ok]/[FALHA] que pode ser copiado para docs/sprint-0/ (sem segredos).
  Le os nomes dos recursos de .azure/mvp.json (gerado por deploy-mvp.ps1).

.EXAMPLE
  ./scripts/azure/test-mvp.ps1
#>
[CmdletBinding()]
param(
    [string]$SubscriptionId = $env:AZURE_SUBSCRIPTION_ID,
    [string]$TenantId = $env:AZURE_TENANT_ID
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

$script:failures = 0
function Check([string]$Label, [bool]$Condition, [string]$Detail = '') {
    if ($Condition) { Write-Host "  [ok]    $Label" }
    else { Write-Host "  [FALHA] $Label $Detail" -ForegroundColor Red; $script:failures++ }
}

Assert-AzContext -ExpectedSubscriptionId $SubscriptionId -ExpectedTenantId $TenantId | Out-Null
$s = Read-MvpState
if (-not $s.resourceGroupName) { throw 'Estado .azure/mvp.json ausente. Execute deploy-mvp.ps1 antes.' }
$rg = $s.resourceGroupName

Write-Step "Recursos do grupo $rg"
& az resource list -g $rg --query '[].{Nome:name, Tipo:type}' -o table

Write-Step 'Container Registry'
$acr = Invoke-AzJson acr show -n $s.registryName -g $rg
Check 'Admin user desabilitado' (-not $acr.adminUserEnabled)
Check 'Pull anonimo desabilitado' (-not $acr.anonymousPullEnabled)

Write-Step 'Storage'
$st = Invoke-AzJson storage account show -n $s.storageAccountName -g $rg
Check 'Acesso publico a blobs desabilitado' (-not $st.allowBlobPublicAccess)
Check 'Chave compartilhada desabilitada' ($st.allowSharedKeyAccess -eq $false)
Check 'Somente HTTPS' ($st.enableHttpsTrafficOnly)
Check 'TLS minimo 1.2' ($st.minimumTlsVersion -eq 'TLS1_2')
# Via ARM (plano de controle): nao exige papel de dados no Storage.
$containers = Invoke-AzJson storage container-rm list --storage-account $s.storageAccountName -g $rg --query '[].{n:name, p:publicAccess}'
foreach ($name in @('documents-raw', 'documents-derived', 'imports', 'exports')) {
    $c = $containers | Where-Object { $_.n -eq $name }
    Check "Container $name privado" ($null -ne $c -and (-not $c.p -or $c.p -eq 'None'))
}

Write-Step 'Key Vault'
$kv = Invoke-AzJson keyvault show -n $s.keyVaultName -g $rg
Check 'Autorizacao por RBAC' ($kv.properties.enableRbacAuthorization)
Check 'Soft delete' ($kv.properties.enableSoftDelete)
Check 'Purge protection' ($kv.properties.enablePurgeProtection)
$secretNames = @(Invoke-AzJson keyvault secret list --vault-name $s.keyVaultName --query '[].name')
Check 'Somente o segredo esperado (postgres-admin-password)' (($secretNames.Count -eq 1) -and ($secretNames[0] -eq 'postgres-admin-password')) "encontrados: $($secretNames -join ', ')"

Write-Step 'PostgreSQL'
$pg = Invoke-AzJson postgres flexible-server show -n $s.postgresServerName -g $rg
Check 'Versao 18' ($pg.version -eq '18')
Check 'Sem alta disponibilidade (MVP)' ($pg.highAvailability.mode -eq 'Disabled')
Check "Backup com retencao ($($pg.backup.backupRetentionDays) dias)" ($pg.backup.backupRetentionDays -ge 7)
$tls = & az postgres flexible-server parameter show --resource-group $rg --server-name $s.postgresServerName --name require_secure_transport --query value -o tsv
Check 'TLS obrigatorio (require_secure_transport=on)' ($tls -eq 'on')
if ($pg.network.publicNetworkAccess -eq 'Disabled') {
    Check 'Sem acesso publico (rede privada)' $true
}
else {
    $rules = @(Invoke-AzJson postgres flexible-server firewall-rule list --resource-group $rg --name $s.postgresServerName)
    $open = @($rules | Where-Object { $_.startIpAddress -ne '0.0.0.0' -or $_.endIpAddress -ne '0.0.0.0' })
    Check 'Firewall sem faixas externas (somente servicos do Azure)' ($open.Count -eq 0) "regras: $($rules.name -join ', ')"
}
# Nomes longos das opcoes: a abreviacao (-s/-d) mudou entre versoes da Azure CLI.
$db = & az postgres flexible-server db show --resource-group $rg --server-name $s.postgresServerName `
    --database-name $s.postgresDatabaseName --query name -o tsv 2>$null
Check "Database $($s.postgresDatabaseName) existe" ($db -eq $s.postgresDatabaseName)

Write-Step 'Container Apps'
$api = Invoke-AzJson containerapp show -n $s.apiAppName -g $rg
Check 'API sem ingress externo' (-not $api.properties.configuration.ingress.external)
$web = Invoke-AzJson containerapp show -n $s.webAppName -g $rg
Check 'Web com HTTPS obrigatorio' (-not $web.properties.configuration.ingress.allowInsecure)

Write-Step 'Saude da aplicacao (via frontend publico)'
$base = $s.webUrl
try {
    # Escala a zero: a primeira chamada pode levar alguns segundos.
    $ready = Invoke-RestMethod -Uri "$base/api/health/ready" -TimeoutSec 90
    Check "API pronta (versao $($ready.version), ambiente $($ready.environment), schema $($ready.schema_revision))" ($ready.status -eq 'ok')
}
catch { Check 'API pronta' $false $_.Exception.Message }
try {
    $page = Invoke-WebRequest -Uri "$base/status" -UseBasicParsing -TimeoutSec 60
    Check 'Frontend responde em /status' ($page.StatusCode -eq 200)
    Check 'Cabecalho Content-Security-Policy presente' ([bool]$page.Headers['Content-Security-Policy'])
}
catch { Check 'Frontend responde em /status' $false $_.Exception.Message }
try {
    Invoke-WebRequest -Uri "$base/api/v1/me" -UseBasicParsing -TimeoutSec 60 | Out-Null
    Check 'Rota protegida exige autenticacao' $false '(respondeu sem autenticacao)'
}
catch {
    $code = $null
    if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
    Check 'Rota protegida exige autenticacao (401)' ($code -eq 401) "status: $code"
}

Write-Host ''
if ($script:failures -eq 0) { Write-Host 'Todas as verificacoes passaram.' -ForegroundColor Green }
else { Write-Host "$($script:failures) verificacao(oes) falharam." -ForegroundColor Red; exit 1 }
