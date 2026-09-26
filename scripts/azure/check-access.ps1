# Guardiao Financeiro BR - diagnostico de acesso ao Azure (SOMENTE LEITURA).
#
# Nao cria, altera nem apaga nada. Nao exibe segredos.
# Uso:   az login
#        ./scripts/azure/check-access.ps1 [-Location brazilsouth]
#
# A saida contem IDs de assinatura/tenant: nao sao segredos, mas nao os
# versione no repositorio publico.
param([string]$Location = 'brazilsouth')

$ErrorActionPreference = 'Continue'
function Section([string]$t) { Write-Host ''; Write-Host "== $t" -ForegroundColor Cyan }
function Ok([string]$t) { Write-Host "  [ok]    $t" }
function Warn([string]$t) { Write-Host "  [aviso] $t" -ForegroundColor Yellow }
function Fail([string]$t) { Write-Host "  [FALTA] $t" -ForegroundColor Red }

if (-not (Get-Command az -ErrorAction SilentlyContinue)) { Fail 'Azure CLI nao encontrada'; exit 1 }

Section 'Azure CLI e Bicep'
$cli = (az version -o json 2>$null | ConvertFrom-Json).'azure-cli'
Ok "azure-cli $cli"
$bicep = (az bicep version 2>&1 | Where-Object { "$_" -match 'Bicep CLI version' } | Select-Object -First 1)
if ($bicep) { Ok "$bicep" } else { Warn 'Bicep nao instalado: rode  az bicep install' }

Section 'Sessao e assinatura'
$acct = az account show -o json 2>$null | ConvertFrom-Json
if (-not $acct) { Fail 'Sem sessao ativa: rode  az login'; exit 1 }
Ok ("Usuario:     {0} ({1})" -f $acct.user.name, $acct.user.type)
Ok ("Assinatura:  {0}" -f $acct.name)
Ok ("Sub ID:      {0}" -f $acct.id)
Ok ("Tenant ID:   {0}" -f $acct.tenantId)
Ok ("Estado:      {0}" -f $acct.state)
$offer = az rest --method get --url "https://management.azure.com/subscriptions/$($acct.id)?api-version=2022-12-01" --query 'subscriptionPolicies.quotaId' -o tsv 2>$null
if ($offer) { Ok "Tipo (quotaId): $offer" }
Write-Host '  Assinaturas visiveis:'
az account list --query '[].{Nome:name, Estado:state, Padrao:isDefault}' -o table

Section 'Papeis (RBAC) do usuario nesta assinatura'
$oid = az ad signed-in-user show --query id -o tsv 2>$null
if (-not $oid) {
    Warn 'Nao foi possivel obter o object ID do usuario (conta convidada ou sem permissao no Graph).'
} else {
    $roles = az role assignment list --assignee $oid --all --include-inherited --include-groups `
        --query '[].{Papel:roleDefinitionName, Escopo:scope}' -o json 2>$null | ConvertFrom-Json
    if (-not $roles) { Warn 'Nenhuma atribuicao de papel encontrada (ou sem permissao para listar).' }
    else { $roles | Format-Table -AutoSize | Out-String | Write-Host }
    $names = @($roles | ForEach-Object { $_.Papel })
    if ($names -contains 'Owner') { Ok 'Owner encontrado: suficiente para a Sprint 1A.' }
    elseif (($names -contains 'Contributor') -and (($names -contains 'User Access Administrator') -or ($names -contains 'Role Based Access Control Administrator'))) {
        Ok 'Contributor + administracao de RBAC: suficiente para a Sprint 1A.'
    } elseif ($names -contains 'Contributor') {
        Warn 'Somente Contributor: cria recursos, mas NAO atribui papeis as Managed Identities (AcrPull, Key Vault, Blob).'
    } else { Fail 'Permissao insuficiente para criar recursos.' }
}

Section 'Resource providers necessarios'
$providers = 'Microsoft.App','Microsoft.ContainerRegistry','Microsoft.DBforPostgreSQL','Microsoft.Storage',
             'Microsoft.KeyVault','Microsoft.OperationalInsights','Microsoft.Insights','Microsoft.ManagedIdentity'
foreach ($p in $providers) {
    $state = az provider show -n $p --query registrationState -o tsv 2>$null
    if ($state -eq 'Registered') { Ok "$p" } else { Warn "$p = $state  (registro e gratuito: az provider register -n $p)" }
}

Section "Disponibilidade na regiao '$Location'"
$appLocs = az provider show -n Microsoft.App --query "resourceTypes[?resourceType=='managedEnvironments'].locations | [0]" -o tsv 2>$null
$locName = az account list-locations --query "[?name=='$Location'].displayName | [0]" -o tsv 2>$null
if (-not $locName) { Fail "Regiao '$Location' nao encontrada" }
elseif ("$appLocs" -match [regex]::Escape($locName)) { Ok "Container Apps disponivel em $locName" }
else { Warn "Container Apps nao listado em $locName" }
az postgres flexible-server list-skus --location $Location -o none 2>$null
if ($LASTEXITCODE -eq 0) { Ok "PostgreSQL Flexible Server consultavel em $locName (restricoes de SKU/cota aparecem no what-if)" }
else { Warn "Nao foi possivel consultar SKUs do PostgreSQL Flexible em $Location (pode haver restricao para esta assinatura)" }

Section 'Entra ID (apenas se optarmos por Easy Auth na Sprint 1A)'
$canCreate = az rest --method get --url 'https://graph.microsoft.com/v1.0/policies/authorizationPolicy' `
    --query 'defaultUserRolePermissions.allowedToCreateApps' -o tsv 2>$null
if ($canCreate -eq 'true') { Ok 'Usuarios podem registrar aplicativos no tenant.' }
elseif ($canCreate -eq 'false') { Warn 'Registro de apps restrito: seria preciso o papel Application Developer.' }
else { Warn 'Nao foi possivel verificar a politica de registro de apps (normal sem permissao de leitura de politicas).' }

Section 'Grupos de recursos existentes com prefixo rg-guardiao'
az group list --query "[?starts_with(name,'rg-guardiao')].{Nome:name, Regiao:location}" -o table

Write-Host ''
Write-Host 'Diagnostico concluido. Nada foi criado ou alterado.' -ForegroundColor Green
