# Funcoes compartilhadas pelos scripts de Azure do ambiente MVP (unico ambiente do projeto).
# Compativel com Windows PowerShell 5.1 e PowerShell 7. Somente ASCII neste arquivo.


function Get-RepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}

function Write-Step([string]$Message) {
    Write-Host ''
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Invoke-Az {
    # Executa a Azure CLI e falha se o codigo de saida for diferente de zero.
    & az @args
    if ($LASTEXITCODE -ne 0) { throw "Falha ao executar: az $($args[0]) $($args[1]) (codigo $LASTEXITCODE)" }
}

function Invoke-AzJson {
    $raw = & az @args -o json
    if ($LASTEXITCODE -ne 0) { throw "Falha ao executar: az $($args[0]) $($args[1]) (codigo $LASTEXITCODE)" }
    if (-not $raw) { return $null }
    return ($raw | Out-String | ConvertFrom-Json)
}

function Get-MvpStatePath {
    return Join-Path (Get-RepoRoot) '.azure/mvp.json'
}

function Read-MvpState {
    # Estado local (IDs e nomes gerados). Fica em .azure/, ignorado pelo Git.
    $path = Get-MvpStatePath
    $state = @{}
    if (Test-Path $path) {
        $json = Get-Content $path -Raw | ConvertFrom-Json
        foreach ($p in $json.PSObject.Properties) { $state[$p.Name] = $p.Value }
    }
    return $state
}

function Write-MvpState([hashtable]$State) {
    $path = Get-MvpStatePath
    $dir = Split-Path $path -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
    ($State | ConvertTo-Json -Depth 5) | Set-Content -Path $path -Encoding ascii
}

function Assert-AzContext([string]$ExpectedSubscriptionId, [string]$ExpectedTenantId) {
    # Secao 11 do plano: confirma assinatura, tenant e usuario antes de qualquer criacao.
    # Divergencia = PARE (excecao), nunca provisionar no tenant ou assinatura errados.
    if (-not $ExpectedSubscriptionId -or -not $ExpectedTenantId) {
        throw 'Informe a assinatura e o tenant esperados (-SubscriptionId/-TenantId ou $env:AZURE_SUBSCRIPTION_ID/$env:AZURE_TENANT_ID).'
    }
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $account = & az account show -o json 2>$null | Out-String | ConvertFrom-Json }
    finally { $ErrorActionPreference = $previous }
    if (-not $account) { throw 'Sem sessao na Azure CLI. Execute: az login --tenant <tenant>' }
    Write-Host ("Assinatura: {0} ({1})" -f $account.name, $account.id)
    Write-Host ("Tenant:     {0}" -f $account.tenantId)
    Write-Host ("Usuario:    {0}" -f $account.user.name)
    if ($account.id -ne $ExpectedSubscriptionId) {
        throw "PARE: assinatura atual ($($account.id)) diferente da esperada. Use: az account set --subscription <id>"
    }
    if ($account.tenantId -ne $ExpectedTenantId) {
        throw "PARE: tenant atual ($($account.tenantId)) diferente do esperado."
    }
    if ($account.state -ne 'Enabled') { throw "PARE: assinatura no estado '$($account.state)'." }
    return $account
}

function Get-SignedInUserObjectId {
    $oid = & az ad signed-in-user show --query id -o tsv
    if ($LASTEXITCODE -ne 0 -or -not $oid) { throw 'Nao foi possivel obter o object ID do usuario (az ad signed-in-user show).' }
    return $oid.Trim()
}

function Get-KeyVaultSecretOrNull([string]$VaultName, [string]$Name) {
    if (-not $VaultName) { return $null }
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $value = & az keyvault secret show --vault-name $VaultName --name $Name --query value -o tsv 2>$null }
    finally { $ErrorActionPreference = $previous }
    if ($LASTEXITCODE -ne 0 -or -not $value) { return $null }
    return $value.Trim()
}

function New-StrongPassword([int]$Length = 32) {
    # Letras, digitos e simbolos seguros para variaveis de ambiente e URLs.
    $sets = @('ABCDEFGHJKLMNPQRSTUVWXYZ', 'abcdefghijkmnopqrstuvwxyz', '23456789', '-_.~')
    $all = ($sets -join '').ToCharArray()
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $bytes = New-Object byte[] ($Length * 2)
    $rng.GetBytes($bytes)
    $chars = New-Object System.Collections.Generic.List[char]
    for ($i = 0; $i -lt $sets.Count; $i++) { $chars.Add($sets[$i][$bytes[$i] % $sets[$i].Length]) }
    for ($i = $sets.Count; $i -lt $Length; $i++) { $chars.Add($all[$bytes[$i] % $all.Length]) }
    # Embaralha (Fisher-Yates) com os bytes restantes.
    for ($i = $chars.Count - 1; $i -gt 0; $i--) {
        $j = $bytes[$Length + $i] % ($i + 1)
        $tmp = $chars[$i]; $chars[$i] = $chars[$j]; $chars[$j] = $tmp
    }
    return -join $chars
}

function New-ImageTag {
    $sha = (& git -C (Get-RepoRoot) rev-parse --short HEAD 2>$null)
    if (-not $sha) { $sha = 'local' }
    return ('{0}-{1}' -f $sha.Trim(), (Get-Date -Format 'yyyyMMddHHmm'))
}

function Confirm-Action([string]$Message) {
    Write-Host ''
    Write-Host $Message -ForegroundColor Yellow
    $answer = Read-Host 'Digite CONFIRMAR para prosseguir'
    if ($answer -cne 'CONFIRMAR') { throw 'Operacao cancelada pelo usuario.' }
}

function Publish-Images([string]$RegistryLoginServer, [string]$Tag, [string]$Root) {
    $registryName = $RegistryLoginServer.Split('.')[0]
    Write-Step "Login no ACR $registryName"
    Invoke-Az acr login --name $registryName
    foreach ($image in @(
            @{ Name = 'guardiao-backend'; Context = (Join-Path $Root 'backend') },
            @{ Name = 'guardiao-frontend'; Context = (Join-Path $Root 'frontend') })) {
        $ref = "$RegistryLoginServer/$($image.Name):$Tag"
        Write-Step "Build e push de $ref"
        & docker build --pull --platform linux/amd64 -t $ref $image.Context
        if ($LASTEXITCODE -ne 0) { throw "Falha no build de $ref" }
        & docker push $ref
        if ($LASTEXITCODE -ne 0) { throw "Falha no push de $ref" }
    }
}

function Start-MigrationJob([string]$ResourceGroup, [string]$JobName) {
    Write-Step "Executando migrations (job $JobName)"
    $execution = Invoke-AzJson containerapp job start --name $JobName --resource-group $ResourceGroup
    $executionName = $execution.name
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Seconds 10
        $status = & az containerapp job execution show --name $JobName --resource-group $ResourceGroup `
            --job-execution-name $executionName --query properties.status -o tsv
        Write-Host "  status: $status"
        if ($status -eq 'Succeeded') { return }
        if ($status -in @('Failed', 'Stopped', 'Degraded')) {
            throw "Job de migracao terminou com status $status. Veja os logs no Log Analytics."
        }
    }
    throw 'Tempo esgotado aguardando o job de migracao.'
}
