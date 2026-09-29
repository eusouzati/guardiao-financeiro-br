<#
.SYNOPSIS
  Cria (ou confere) as App Registrations e Service Principals do MVP no Microsoft Entra ID.

.DESCRIPTION
  Idempotente e sem segredos: nenhuma credencial (client secret ou certificado) e criada
  nesta sprint. Nunca apaga App Registrations nem Service Principals.

  guardiao-financeiro-web-mvp  (autenticacao da aplicacao web)
    - single-tenant (AzureADMyOrg);
    - App Roles ADMIN, ANALYST, APPROVER, AUDITOR (ADR-006);
    - atribuicao obrigatoria no Service Principal (so usuarios com papel entram);
    - redirect URI do Easy Auth quando -WebRedirectUri for informado;
    - nenhuma permissao do Microsoft Graph solicitada.

  guardiao-financeiro-mail-mvp  (ingestao de e-mail, separada da autenticacao)
    - single-tenant, sem App Roles e SEM permissoes de API no Entra ID;
    - o acesso a caixa do MVP e concedido somente pelo Exchange RBAC for Applications
      (Set-ExchangeAppRbac.ps1). Consentimento de Mail.* no Entra anularia o escopo;
      por isso o script PARA se encontrar permissao de aplicacao do Graph concedida.

  IDs gerados (nao sao segredos) ficam em .azure/m365-mvp.json, ignorado pelo Git.

.EXAMPLE
  ./infra/m365/New-AppRegistrations.ps1 -TenantId '<tenant-id>' -WhatIf
  ./infra/m365/New-AppRegistrations.ps1 -TenantId '<tenant-id>' `
      -WebRedirectUri 'https://<web-fqdn>/.auth/login/aad/callback'
#>
[CmdletBinding()]
param(
    [string]$TenantId = $env:AZURE_TENANT_ID,
    [string]$WebAppName = 'guardiao-financeiro-web-mvp',
    [string]$MailAppName = 'guardiao-financeiro-mail-mvp',
    [string]$WebRedirectUri = '',
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'

$graphAppId = '00000003-0000-0000-c000-000000000000' # Microsoft Graph (ID publico e fixo)
$roleDefinitions = @(
    @{ value = 'ADMIN'; displayName = 'Administrador'; description = 'Administra configuracoes, usuarios e integracoes.' },
    @{ value = 'ANALYST'; displayName = 'Analista'; description = 'Analisa documentos e trata excecoes.' },
    @{ value = 'APPROVER'; displayName = 'Aprovador'; description = 'Aprova ou rejeita pagamentos com divergencia.' },
    @{ value = 'AUDITOR'; displayName = 'Auditor'; description = 'Consulta a trilha de auditoria (somente leitura).' }
)

function Write-Step([string]$Message) { Write-Host ''; Write-Host "==> $Message" -ForegroundColor Cyan }

function Invoke-AzJson {
    $raw = & az @args -o json
    if ($LASTEXITCODE -ne 0) { throw "Falha ao executar: az $($args[0]) $($args[1]) (codigo $LASTEXITCODE)" }
    if (-not $raw) { return $null }
    return ($raw | Out-String | ConvertFrom-Json)
}

function Get-RepoRoot { return (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path }

function Get-SingleApp([string]$DisplayName) {
    $apps = @(Invoke-AzJson ad app list --display-name $DisplayName --query "[?displayName=='$DisplayName']")
    if ($apps.Count -gt 1) { throw "PARE: existem $($apps.Count) App Registrations chamadas '$DisplayName'. Resolva a duplicidade manualmente." }
    if ($apps.Count -eq 1) { return $apps[0] }
    return $null
}

function Write-TempJson($Value) {
    $path = [System.IO.Path]::GetTempFileName()
    (ConvertTo-Json -InputObject $Value -Depth 10) | Set-Content -Path $path -Encoding ascii
    return $path
}

function Confirm-ServicePrincipal([string]$AppId) {
    $sp = & az ad sp show --id $AppId -o json 2>$null | Out-String | ConvertFrom-Json
    if ($sp) { return $sp }
    if ($WhatIf) { Write-Host "[what-if] az ad sp create --id $AppId"; return $null }
    return (Invoke-AzJson ad sp create --id $AppId)
}

function Confirm-App([string]$DisplayName) {
    $app = Get-SingleApp $DisplayName
    if ($app) { Write-Host "App Registration '$DisplayName' ja existe (appId $($app.appId))."; return $app }
    if ($WhatIf) { Write-Host "[what-if] az ad app create --display-name $DisplayName --sign-in-audience AzureADMyOrg"; return $null }
    Write-Host "Criando App Registration '$DisplayName'."
    return (Invoke-AzJson ad app create --display-name $DisplayName --sign-in-audience AzureADMyOrg)
}

# ---- Contexto --------------------------------------------------------------------------
if (-not $TenantId) { throw 'Informe -TenantId ou $env:AZURE_TENANT_ID.' }
Write-Step 'Validando tenant'
$account = Invoke-AzJson account show
Write-Host ("Tenant: {0} | Usuario: {1}" -f $account.tenantId, $account.user.name)
if ($account.tenantId -ne $TenantId) { throw "PARE: tenant conectado ($($account.tenantId)) diferente do esperado. Nada foi alterado." }

# ---- Web -------------------------------------------------------------------------------
Write-Step "App Registration web: $WebAppName"
$web = Confirm-App $WebAppName
if ($web) {
    if ($web.signInAudience -ne 'AzureADMyOrg') { throw "PARE: '$WebAppName' nao e single-tenant ($($web.signInAudience))." }

    $existingRoles = @($web.appRoles)
    $missing = @($roleDefinitions | Where-Object { $existingRoles.value -notcontains $_.value })
    if ($missing.Count -gt 0) {
        $roles = @($existingRoles | ForEach-Object {
                @{ id = $_.id; value = $_.value; displayName = $_.displayName; description = $_.description
                    allowedMemberTypes = @($_.allowedMemberTypes); isEnabled = $_.isEnabled }
            })
        foreach ($r in $missing) {
            $roles += @{ id = [guid]::NewGuid().ToString(); value = $r.value; displayName = $r.displayName
                description = $r.description; allowedMemberTypes = @('User'); isEnabled = $true }
        }
        if ($WhatIf) { Write-Host "[what-if] Adicionaria App Roles: $(($missing | ForEach-Object { $_.value }) -join ', ')" }
        else {
            $file = Write-TempJson $roles
            try { & az ad app update --id $web.appId --app-roles "@$file"; if ($LASTEXITCODE -ne 0) { throw 'Falha ao definir App Roles.' } }
            finally { Remove-Item $file -ErrorAction SilentlyContinue }
        }
    }
    else { Write-Host 'App Roles ADMIN, ANALYST, APPROVER, AUDITOR presentes.' }

    if ($WebRedirectUri) {
        if ($WebRedirectUri -notmatch '^https://[^/]+/\.auth/login/aad/callback$') {
            throw 'WebRedirectUri deve ser https://<fqdn>/.auth/login/aad/callback'
        }
        $uris = @($web.web.redirectUris)
        if ($uris -notcontains $WebRedirectUri) {
            if ($WhatIf) { Write-Host "[what-if] Adicionaria redirect URI $WebRedirectUri" }
            else {
                & az ad app update --id $web.appId --web-redirect-uris @($uris + $WebRedirectUri) --enable-id-token-issuance true
                if ($LASTEXITCODE -ne 0) { throw 'Falha ao definir redirect URI.' }
            }
        }
    }

    $webSp = Confirm-ServicePrincipal $web.appId
    if ($webSp -and -not $webSp.appRoleAssignmentRequired) {
        if ($WhatIf) { Write-Host '[what-if] Exigiria atribuicao de usuario (appRoleAssignmentRequired=true)' }
        else {
            & az ad sp update --id $web.appId --set appRoleAssignmentRequired=true
            if ($LASTEXITCODE -ne 0) { throw 'Falha ao exigir atribuicao de usuario no Service Principal web.' }
        }
    }
}

# ---- Mail ------------------------------------------------------------------------------
Write-Step "App Registration de ingestao de e-mail: $MailAppName"
$mail = Confirm-App $MailAppName
$mailSp = $null
if ($mail) {
    if ($mail.signInAudience -ne 'AzureADMyOrg') { throw "PARE: '$MailAppName' nao e single-tenant ($($mail.signInAudience))." }
    if (@($mail.requiredResourceAccess).Count -gt 0) {
        Write-Warning "'$MailAppName' declara permissoes de API. O acesso a caixa deve vir somente do RBAC for Applications; revise e remova-as manualmente."
    }
    $mailSp = Confirm-ServicePrincipal $mail.appId
    if ($mailSp) {
        # Permissoes de aplicacao do Graph concedidas no Entra valem para TODAS as caixas.
        $grants = @(Invoke-AzJson rest --method get `
                --url "https://graph.microsoft.com/v1.0/servicePrincipals/$($mailSp.id)/appRoleAssignments" --query value)
        $graphSp = Invoke-AzJson ad sp show --id $graphAppId --query '{id:id}'
        $graphGrants = @($grants | Where-Object { $_.resourceId -eq $graphSp.id })
        if ($graphGrants.Count -gt 0) {
            throw "PARE: '$MailAppName' tem $($graphGrants.Count) permissao(oes) de aplicacao do Microsoft Graph concedidas no Entra ID, o que anularia o escopo por caixa. Remova-as antes de continuar."
        }
        Write-Host 'Sem permissoes de aplicacao do Graph no Entra ID (correto).'
    }
}

# ---- Estado local (sem segredos) -------------------------------------------------------
if (-not $WhatIf) {
    $state = [ordered]@{
        tenantId                     = $TenantId
        webAppName                   = $WebAppName
        webAppId                     = $web.appId
        webServicePrincipalObjectId  = $webSp.id
        mailAppName                  = $MailAppName
        mailAppId                    = $mail.appId
        mailServicePrincipalObjectId = $mailSp.id
    }
    $dir = Join-Path (Get-RepoRoot) '.azure'
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
    ($state | ConvertTo-Json) | Set-Content -Path (Join-Path $dir 'm365-mvp.json') -Encoding ascii
    Write-Step 'Resultado (IDs publicos, sem segredos; salvos em .azure/m365-mvp.json)'
    [pscustomobject]$state | Format-List | Out-String | Write-Host
    Write-Host 'Proximo passo: ./infra/m365/Set-ExchangeAppRbac.ps1'
}
