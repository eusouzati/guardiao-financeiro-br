<#
.SYNOPSIS
  Restringe o app de ingestao de e-mail a Shared Mailbox do MVP com Exchange Online
  RBAC for Applications.

.DESCRIPTION
  Idempotente. Nunca remove escopos, papeis ou service principals existentes e nunca
  amplia um escopo silenciosamente: se algo existir com configuracao diferente, PARA.

  1. Confere que a Shared Mailbox do MVP existe e tem CustomAttribute1 = <valor de escopo>.
  2. Confere que o filtro do escopo corresponde a EXATAMENTE uma caixa (a do MVP).
  3. Registra o service principal do app de e-mail no Exchange (New-ServicePrincipal).
  4. Cria o Management Scope filtrado por CustomAttribute1.
  5. Atribui somente os papeis informados (padrao: "Application Mail.Read") ao app,
     limitados ao escopo.

  Sem permissao Mail.* no Entra ID (New-AppRegistrations.ps1 verifica): as permissoes do
  Entra e do RBAC for Applications sao somadas. Propagacao: de 30 minutos a 2 horas.

  Os IDs do app vem de .azure/m365-mvp.json (gerado por New-AppRegistrations.ps1) ou dos
  parametros. MailServicePrincipalObjectId e o Object ID do Service Principal (Enterprise
  Application), nao o da App Registration.

.EXAMPLE
  ./infra/m365/Set-ExchangeAppRbac.ps1 -TenantDomain '<dominio>' -MailboxAlias 'guardiao-financeiro-mvp' `
      -AdminUser '<admin>@<dominio>' -WhatIf
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$TenantDomain,
    [Parameter(Mandatory)] [string]$MailboxAlias,
    [Parameter(Mandatory)] [string]$AdminUser,
    [string]$MailAppId,
    [string]$MailServicePrincipalObjectId,
    [string]$MailAppName = 'guardiao-financeiro-mail-mvp',
    [string]$ScopeAttributeValue = 'guardiao-financeiro-mvp',
    [string]$ScopeName = 'gfbr-mvp-mailbox-scope',
    [string[]]$Roles = @('Application Mail.Read'),
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'

function Write-Step([string]$Message) { Write-Host ''; Write-Host "==> $Message" -ForegroundColor Cyan }

$statePath = Join-Path (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path '.azure/m365-mvp.json'
if ((-not $MailAppId -or -not $MailServicePrincipalObjectId) -and (Test-Path $statePath)) {
    $state = Get-Content $statePath -Raw | ConvertFrom-Json
    if (-not $MailAppId) { $MailAppId = $state.mailAppId }
    if (-not $MailServicePrincipalObjectId) { $MailServicePrincipalObjectId = $state.mailServicePrincipalObjectId }
}
if (-not $MailAppId -or -not $MailServicePrincipalObjectId) {
    throw 'Informe -MailAppId e -MailServicePrincipalObjectId ou execute antes New-AppRegistrations.ps1.'
}
if (-not (Get-Module -ListAvailable -Name ExchangeOnlineManagement)) {
    throw 'Modulo ExchangeOnlineManagement nao encontrado. Instalacao (decisao do administrador): Install-Module ExchangeOnlineManagement -Scope CurrentUser'
}
Import-Module ExchangeOnlineManagement

$address = "$MailboxAlias@$TenantDomain"
$filter = "CustomAttribute1 -eq '$ScopeAttributeValue'"

Write-Step "Conectando ao Exchange Online como $AdminUser"
Connect-ExchangeOnline -UserPrincipalName $AdminUser -ShowBanner:$false
try {
    $domains = @(Get-AcceptedDomain | ForEach-Object { "$($_.DomainName)" })
    if ($domains -notcontains $TenantDomain) { throw "PARE: o dominio '$TenantDomain' nao pertence a organizacao conectada." }

    Write-Step 'Conferindo a caixa do MVP e o alcance do filtro'
    $mailbox = Get-EXOMailbox -Identity $address -Properties CustomAttribute1 -ErrorAction SilentlyContinue
    if (-not $mailbox) { throw "PARE: $address nao existe. Execute New-MvpMailbox.ps1." }
    if ($mailbox.RecipientTypeDetails -ne 'SharedMailbox') { throw "PARE: $address nao e SharedMailbox." }
    if ($mailbox.CustomAttribute1 -ne $ScopeAttributeValue) { throw "PARE: CustomAttribute1 de $address difere de '$ScopeAttributeValue'." }
    $inScope = @(Get-Recipient -RecipientPreviewFilter $filter -ResultSize 10)
    if ($inScope.Count -ne 1 -or "$($inScope[0].PrimarySmtpAddress)" -ne $address) {
        throw "PARE: o filtro [$filter] alcanca $($inScope.Count) destinatario(s): $(($inScope | ForEach-Object { $_.PrimarySmtpAddress }) -join ', '). O escopo precisa conter somente $address."
    }
    Write-Host "Filtro [$filter] alcanca somente $address."

    Write-Step 'Service principal do app de e-mail no Exchange'
    $sp = Get-ServicePrincipal -Identity $MailAppId -ErrorAction SilentlyContinue
    if ($sp) { Write-Host "Ja registrado: $($sp.DisplayName)" }
    elseif ($WhatIf) { Write-Host "[what-if] New-ServicePrincipal -AppId $MailAppId -ObjectId $MailServicePrincipalObjectId -DisplayName $MailAppName" }
    else {
        $sp = New-ServicePrincipal -AppId $MailAppId -ObjectId $MailServicePrincipalObjectId -DisplayName $MailAppName
    }

    Write-Step "Management Scope $ScopeName"
    $scope = Get-ManagementScope -Identity $ScopeName -ErrorAction SilentlyContinue
    if ($scope) {
        if ("$($scope.RecipientFilter)" -notmatch [regex]::Escape($ScopeAttributeValue) -or "$($scope.RecipientFilter)" -notmatch 'CustomAttribute1') {
            throw "PARE: o escopo $ScopeName ja existe com outro filtro ($($scope.RecipientFilter)). Nada foi alterado."
        }
        Write-Host "Ja existe com o filtro: $($scope.RecipientFilter)"
    }
    elseif ($WhatIf) { Write-Host "[what-if] New-ManagementScope -Name $ScopeName -RecipientRestrictionFilter `"$filter`"" }
    else { New-ManagementScope -Name $ScopeName -RecipientRestrictionFilter $filter | Out-Null }

    foreach ($role in $Roles) {
        if ($role -notlike 'Application *') { throw "PARE: '$role' nao e um papel de aplicacao do RBAC for Applications." }
        Write-Step "Papel '$role' limitado ao escopo"
        $existing = @()
        if ($sp) {
            $existing = @(Get-ManagementRoleAssignment -RoleAssignee $MailAppId -Role $role -ErrorAction SilentlyContinue)
        }
        $scoped = @($existing | Where-Object { "$($_.CustomResourceScope)" -eq $ScopeName })
        $unscoped = @($existing | Where-Object { "$($_.CustomResourceScope)" -ne $ScopeName })
        if ($unscoped.Count -gt 0) {
            throw "PARE: o app ja possui '$role' fora do escopo do MVP ($(($unscoped | ForEach-Object { $_.Name }) -join ', ')). Revise manualmente."
        }
        if ($scoped.Count -gt 0) { Write-Host "Ja atribuido: $($scoped[0].Name)"; continue }
        $assignmentName = 'gfbr-mvp-' + (($role -replace '^Application\s+', '') -replace '[^A-Za-z0-9]', '-')
        if ($WhatIf) { Write-Host "[what-if] New-ManagementRoleAssignment -Name $assignmentName -App $MailAppId -Role '$role' -CustomResourceScope $ScopeName" }
        else { New-ManagementRoleAssignment -Name $assignmentName -App $MailAppId -Role $role -CustomResourceScope $ScopeName | Out-Null }
    }

    if (-not $WhatIf) {
        Write-Step 'Resultado'
        Get-ManagementRoleAssignment -RoleAssignee $MailAppId |
            Select-Object Name, Role, CustomResourceScope | Format-Table -AutoSize
        Write-Host 'A propagacao leva de 30 minutos a 2 horas. Depois: ./infra/m365/Test-MailboxAccess.ps1'
    }
}
finally {
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
}
