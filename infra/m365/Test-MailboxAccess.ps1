<#
.SYNOPSIS
  Valida o escopo de acesso do app de ingestao de e-mail (SOMENTE LEITURA).

.DESCRIPTION
  Criterios da Sprint 0:
    mailbox permitida        -> acesso permitido  (InScope = True)
    mailbox fora do escopo   -> acesso negado     (InScope = False)
  E, no Entra ID, o app de e-mail nao pode ter permissao de aplicacao do Microsoft Graph
  (que valeria para todas as caixas).

  Usa Test-ServicePrincipalAuthorization do Exchange Online, que avalia o RBAC for
  Applications sem precisar de credencial do app. Nenhum e-mail e lido.
  A caixa fora do escopo deve ser uma caixa existente do tenant (ex.: a do administrador).

.EXAMPLE
  ./infra/m365/Test-MailboxAccess.ps1 -TenantDomain '<dominio>' -MailboxAlias 'guardiao-financeiro-mvp' `
      -AdminUser '<admin>@<dominio>' -OutOfScopeMailbox '<outra-caixa>@<dominio>'
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$TenantDomain,
    [Parameter(Mandatory)] [string]$MailboxAlias,
    [Parameter(Mandatory)] [string]$AdminUser,
    [Parameter(Mandatory)] [string]$OutOfScopeMailbox,
    [string]$MailAppId,
    [string]$MailServicePrincipalObjectId,
    [switch]$SkipEntraCheck
)

$ErrorActionPreference = 'Stop'

function Write-Step([string]$Message) { Write-Host ''; Write-Host "==> $Message" -ForegroundColor Cyan }
$script:failures = 0
function Check([string]$Label, [bool]$Condition, [string]$Detail = '') {
    if ($Condition) { Write-Host "  [ok]    $Label" }
    else { Write-Host "  [FALHA] $Label $Detail" -ForegroundColor Red; $script:failures++ }
}

$statePath = Join-Path (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path '.azure/m365-mvp.json'
if ((-not $MailAppId -or -not $MailServicePrincipalObjectId) -and (Test-Path $statePath)) {
    $state = Get-Content $statePath -Raw | ConvertFrom-Json
    if (-not $MailAppId) { $MailAppId = $state.mailAppId }
    if (-not $MailServicePrincipalObjectId) { $MailServicePrincipalObjectId = $state.mailServicePrincipalObjectId }
}
if (-not $MailAppId) { throw 'Informe -MailAppId ou execute antes New-AppRegistrations.ps1.' }

$allowed = "$MailboxAlias@$TenantDomain"
if ($OutOfScopeMailbox -eq $allowed) { throw 'A caixa fora do escopo deve ser diferente da caixa do MVP.' }

if (-not $SkipEntraCheck) {
    Write-Step 'Entra ID: permissoes de aplicacao do Microsoft Graph no app de e-mail'
    if (-not $MailServicePrincipalObjectId) { throw 'Informe -MailServicePrincipalObjectId ou use -SkipEntraCheck.' }
    $graphSpId = (& az ad sp show --id '00000003-0000-0000-c000-000000000000' --query id -o tsv).Trim()
    $raw = & az rest --method get --url "https://graph.microsoft.com/v1.0/servicePrincipals/$MailServicePrincipalObjectId/appRoleAssignments" --query value -o json
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao consultar o Microsoft Graph (az login no tenant do M365).' }
    $grants = @($raw | Out-String | ConvertFrom-Json | Where-Object { $_.resourceId -eq $graphSpId })
    Check 'Nenhuma permissao de aplicacao do Graph concedida no Entra ID' ($grants.Count -eq 0) "($($grants.Count) encontrada(s))"
}

if (-not (Get-Module -ListAvailable -Name ExchangeOnlineManagement)) {
    throw 'Modulo ExchangeOnlineManagement nao encontrado. Instalacao (decisao do administrador): Install-Module ExchangeOnlineManagement -Scope CurrentUser'
}
Import-Module ExchangeOnlineManagement

Write-Step "Conectando ao Exchange Online como $AdminUser"
Connect-ExchangeOnline -UserPrincipalName $AdminUser -ShowBanner:$false
try {
    $domains = @(Get-AcceptedDomain | ForEach-Object { "$($_.DomainName)" })
    if ($domains -notcontains $TenantDomain) { throw "PARE: o dominio '$TenantDomain' nao pertence a organizacao conectada." }

    Write-Step "Caixa permitida: $allowed"
    $inScope = @(Test-ServicePrincipalAuthorization -Identity $MailAppId -Resource $allowed)
    $inScope | Select-Object RoleName, GrantedPermissions, AllowedResourceScope, InScope | Format-Table -AutoSize | Out-String | Write-Host
    Check 'Acesso permitido a caixa do MVP' ((@($inScope | Where-Object { $_.InScope -eq $true })).Count -gt 0)

    Write-Step "Caixa fora do escopo: $OutOfScopeMailbox"
    $outScope = @(Test-ServicePrincipalAuthorization -Identity $MailAppId -Resource $OutOfScopeMailbox)
    $outScope | Select-Object RoleName, GrantedPermissions, AllowedResourceScope, InScope | Format-Table -AutoSize | Out-String | Write-Host
    Check 'Acesso negado a caixa fora do escopo' ((@($outScope | Where-Object { $_.InScope -eq $true })).Count -eq 0)
}
finally {
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
}

Write-Host ''
if ($script:failures -eq 0) { Write-Host 'Escopo de acesso ao e-mail validado.' -ForegroundColor Green }
else { Write-Host "$($script:failures) verificacao(oes) falharam. Se o RBAC foi aplicado ha pouco, aguarde a propagacao (ate 2 horas)." -ForegroundColor Red; exit 1 }
