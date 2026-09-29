<#
.SYNOPSIS
  Cria (ou confere) a Shared Mailbox dedicada ao MVP do Guardiao Financeiro BR.

.DESCRIPTION
  Idempotente: se a caixa ja existir, apenas confere o tipo e o atributo de escopo.
  Nunca apaga caixas. Nao usa caixa real do financeiro.

  - Endereco: <MailboxAlias>@<TenantDomain> (ex.: guardiao-financeiro-mvp@<dominio>).
  - Marca CustomAttribute1 = <ScopeAttributeValue>; esse atributo e o filtro do
    Management Scope do Exchange RBAC for Applications (Set-ExchangeAppRbac.ps1).
  - Bloqueia o login interativo da conta da caixa compartilhada (boa pratica), via
    Azure CLI, quando o usuario tiver permissao para isso.

  Pre-requisitos: modulo ExchangeOnlineManagement (o script NAO instala nada), usuario com
  papel Exchange Administrator (ou Organization Management) e Azure CLI no mesmo tenant.
  Nenhum dominio, tenant ou usuario real fica neste arquivo: tudo chega por parametro.

.EXAMPLE
  ./infra/m365/New-MvpMailbox.ps1 -TenantDomain '<dominio>' -MailboxAlias 'guardiao-financeiro-mvp' `
      -AdminUser '<admin>@<dominio>' -WhatIf
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$TenantDomain,
    [Parameter(Mandatory)] [string]$MailboxAlias,
    [Parameter(Mandatory)] [string]$AdminUser,
    [string]$DisplayName = 'Guardiao Financeiro MVP',
    [string]$ScopeAttributeValue = 'guardiao-financeiro-mvp',
    [switch]$SkipBlockSignIn,
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'

function Write-Step([string]$Message) { Write-Host ''; Write-Host "==> $Message" -ForegroundColor Cyan }

if (-not (Get-Module -ListAvailable -Name ExchangeOnlineManagement)) {
    throw 'Modulo ExchangeOnlineManagement nao encontrado. Instalacao (decisao do administrador): Install-Module ExchangeOnlineManagement -Scope CurrentUser'
}
Import-Module ExchangeOnlineManagement

$address = "$MailboxAlias@$TenantDomain"

Write-Step "Conectando ao Exchange Online como $AdminUser"
Connect-ExchangeOnline -UserPrincipalName $AdminUser -ShowBanner:$false
try {
    Write-Step 'Validando a organizacao conectada'
    $org = Get-OrganizationConfig
    Write-Host ("Organizacao: {0}" -f $org.DisplayName)
    $domains = @(Get-AcceptedDomain | ForEach-Object { "$($_.DomainName)" })
    if ($domains -notcontains $TenantDomain) {
        throw "PARE: o dominio '$TenantDomain' nao pertence a organizacao conectada. Nada foi alterado."
    }

    $mailbox = Get-EXOMailbox -Identity $address -Properties CustomAttribute1 -ErrorAction SilentlyContinue
    if ($mailbox) {
        Write-Step "Caixa $address ja existe"
        if ($mailbox.RecipientTypeDetails -ne 'SharedMailbox') {
            throw "PARE: $address existe mas e do tipo $($mailbox.RecipientTypeDetails), nao SharedMailbox. Nada foi alterado."
        }
        if ($mailbox.CustomAttribute1 -ne $ScopeAttributeValue) {
            if ($mailbox.CustomAttribute1) {
                throw "PARE: CustomAttribute1 ja contem '$($mailbox.CustomAttribute1)'. Revise antes de sobrescrever."
            }
            if ($WhatIf) { Write-Host "[what-if] Definiria CustomAttribute1 = $ScopeAttributeValue" }
            else { Set-Mailbox -Identity $address -CustomAttribute1 $ScopeAttributeValue }
        }
    }
    else {
        Write-Step "Criando Shared Mailbox $address"
        if ($WhatIf) {
            Write-Host "[what-if] New-Mailbox -Shared -Name '$DisplayName' -Alias '$MailboxAlias' -PrimarySmtpAddress '$address'"
            Write-Host "[what-if] Set-Mailbox -CustomAttribute1 '$ScopeAttributeValue'"
        }
        else {
            New-Mailbox -Shared -Name $DisplayName -DisplayName $DisplayName -Alias $MailboxAlias `
                -PrimarySmtpAddress $address | Out-Null
            # A caixa recem-criada pode demorar alguns segundos para aceitar alteracoes.
            for ($i = 0; $i -lt 12; $i++) {
                try { Set-Mailbox -Identity $address -CustomAttribute1 $ScopeAttributeValue; break }
                catch { if ($i -eq 11) { throw }; Start-Sleep -Seconds 10 }
            }
        }
    }

    if (-not $SkipBlockSignIn) {
        Write-Step 'Bloqueando login interativo da conta da caixa compartilhada'
        if ($WhatIf) { Write-Host "[what-if] az ad user update --id $address --account-enabled false" }
        else {
            & az ad user update --id $address --account-enabled false 2>$null
            if ($LASTEXITCODE -ne 0) {
                Write-Warning 'Nao foi possivel bloquear o login (permissao de User Administrator ou az login no tenant). Faca manualmente: docs/microsoft-365.md.'
            }
        }
    }

    if (-not $WhatIf) {
        $result = Get-EXOMailbox -Identity $address -Properties CustomAttribute1
        Write-Step 'Resultado'
        $result | Select-Object DisplayName, PrimarySmtpAddress, RecipientTypeDetails, CustomAttribute1 | Format-List | Out-String | Write-Host
    }
}
finally {
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
}
