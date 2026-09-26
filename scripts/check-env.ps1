# Verifica as ferramentas de desenvolvimento (Windows PowerShell 5.1+ / PowerShell 7).
# Nao instala nada e nao altera o sistema.
$ErrorActionPreference = 'Continue'
$failed = $false

function Write-Ok([string]$Name, [string]$Detail) { Write-Host ("  [ok]    {0,-16} {1}" -f $Name, $Detail) }
function Write-Missing([string]$Name, [string]$Hint) {
    Write-Host ("  [FALTA] {0,-16} {1}" -f $Name, $Hint) -ForegroundColor Red
    $script:failed = $true
}
function Write-Optional([string]$Name) { Write-Host ("  [--]    {0,-16} opcional nesta sprint" -f $Name) }

function Test-Tool {
    param([string]$Name, [bool]$Required, [string]$Exe, [string[]]$VersionArgs, [string]$Hint = 'obrigatorio')
    if (Get-Command $Exe -ErrorAction SilentlyContinue) {
        $v = (& $Exe @VersionArgs 2>&1 | Where-Object { "$_".Trim() -ne '' -and "$_" -notmatch '^\s*WARNING' } | Select-Object -First 1)
        Write-Ok $Name "$v"
        return $true
    }
    if ($Required) { Write-Missing $Name $Hint } else { Write-Optional $Name }
    return $false
}

Write-Host 'Guardiao Financeiro BR - verificacao de ambiente'
[void](Test-Tool 'git' $true 'git' @('--version'))

if (Test-Tool 'docker' $true 'docker' @('--version') 'instale o Docker Desktop') {
    [void](Test-Tool 'docker compose' $true 'docker' @('compose', 'version'))
    # O CLI pode existir com o engine parado: verificar o daemon de fato.
    $server = (& docker info --format '{{.ServerVersion}}' 2>$null)
    if ($LASTEXITCODE -eq 0 -and $server) { Write-Ok 'docker engine' "em execucao ($server)" }
    else { Write-Missing 'docker engine' 'parado: abra o Docker Desktop e aguarde "Engine running"' }
}

[void](Test-Tool 'uv' $true 'uv' @('--version') 'instale: winget install --id=astral-sh.uv -e  (depois abra um novo terminal)')
[void](Test-Tool 'node' $false 'node' @('--version'))
[void](Test-Tool 'npm' $false 'npm' @('--version'))
[void](Test-Tool 'az (Azure CLI)' $false 'az' @('--version'))
[void](Test-Tool 'gh' $false 'gh' @('--version'))

if (Test-Path '.env') {
    Write-Ok '.env' 'presente (nao versionado)'
    if (Select-String -Path '.env' -Pattern '^POSTGRES_PASSWORD=(troque-esta-senha-local)?\s*$' -Quiet) {
        Write-Host '  [aviso] POSTGRES_PASSWORD ainda e o placeholder/vazio: defina um valor local' -ForegroundColor Yellow
    }
}
else { Write-Host '  [--]    .env ausente: Copy-Item .env.example .env' }

if ($failed) { exit 1 } else { exit 0 }
