<#
.SYNOPSIS
  Estimativa de custo do ambiente MVP a partir da API publica de precos do Azure
  (https://prices.azure.com). Somente leitura; nao exige login.

.DESCRIPTION
  Considera a configuracao de infra/azure (PostgreSQL B1ms 32 GB, ACR Basic, Log Analytics
  com limite diario, Container Apps Consumption com escala a zero, VNet e zona DNS privada).
  Nao aplica creditos nem servicos gratuitos da conta; o valor real tende a ser menor.
  Precos de varejo em USD. Detalhes e classificacao: docs/cost-management.md.

.EXAMPLE
  ./scripts/azure/estimate-cost.ps1 -Days 26
#>
[CmdletBinding()]
param(
    [string]$Region = 'brazilsouth',
    [int]$Days = 30,
    [double]$LogGbPerDay = 0.2
)

$ErrorActionPreference = 'Stop'

function Get-RetailPrices([string]$Filter) {
    $items = @()
    $url = 'https://prices.azure.com/api/retail/prices?$filter=' + [uri]::EscapeDataString($Filter)
    while ($url) {
        $page = Invoke-RestMethod -Uri $url -Method Get
        $items += $page.Items
        $url = $page.NextPageLink
    }
    return $items | Where-Object { $_.type -eq 'Consumption' -and $_.currencyCode -eq 'USD' }
}

function Find-Price($Items, [scriptblock]$Where, [string]$Label) {
    $match = $Items | Where-Object $Where | Sort-Object retailPrice | Select-Object -First 1
    if (-not $match) { Write-Warning "Preco nao encontrado: $Label"; return $null }
    return $match
}

$hoursPerMonth = 730
$lines = New-Object System.Collections.Generic.List[object]

$pg = Get-RetailPrices "serviceName eq 'Azure Database for PostgreSQL' and armRegionName eq '$Region'"
$compute = Find-Price $pg { $_.productName -like '*Flexible Server*Burstable*' -and $_.skuName -like '*B1ms*' -and $_.unitOfMeasure -eq '1 Hour' } 'PostgreSQL B1ms'
if ($compute) { $lines.Add([pscustomobject]@{ Item = 'PostgreSQL B1ms (computacao)'; Unit = "$($compute.retailPrice)/h"; Monthly = $compute.retailPrice * $hoursPerMonth }) }
$storage = Find-Price $pg { $_.productName -like '*Flexible Server Storage*' -and $_.meterName -like '*Storage Data Stored*' } 'PostgreSQL storage'
if ($storage) { $lines.Add([pscustomobject]@{ Item = 'PostgreSQL storage 32 GB'; Unit = "$($storage.retailPrice)/GB-mes"; Monthly = $storage.retailPrice * 32 }) }

$acr = Get-RetailPrices "serviceName eq 'Container Registry' and armRegionName eq '$Region'"
$basic = Find-Price $acr { $_.skuName -eq 'Basic' -and $_.meterName -like '*Registry Unit*' } 'ACR Basic'
if ($basic) { $lines.Add([pscustomobject]@{ Item = 'Container Registry Basic'; Unit = "$($basic.retailPrice)/dia"; Monthly = $basic.retailPrice * 30 }) }

$la = Get-RetailPrices "serviceName eq 'Log Analytics' and armRegionName eq '$Region'"
$ingest = Find-Price $la { $_.meterName -like '*Data Ingestion*' -and $_.retailPrice -gt 0 } 'Log Analytics ingestao'
if ($ingest) {
    # 5 GB/mes gratuitos por conta de cobranca.
    $gb = [math]::Max(0, $LogGbPerDay * 30 - 5)
    $lines.Add([pscustomobject]@{ Item = "Log Analytics (ate $LogGbPerDay GB/dia)"; Unit = "$($ingest.retailPrice)/GB"; Monthly = $ingest.retailPrice * $gb })
}

$dns = Get-RetailPrices "serviceName eq 'Azure DNS' and priceType eq 'Consumption'"
$zone = Find-Price $dns { $_.meterName -like '*Private Zone*' -and $_.retailPrice -gt 0 } 'Zona DNS privada'
if ($zone) { $lines.Add([pscustomobject]@{ Item = 'Zona DNS privada do PostgreSQL'; Unit = "$($zone.retailPrice)/zona-mes"; Monthly = $zone.retailPrice }) }

$lines.Add([pscustomobject]@{ Item = 'VNet e sub-redes (sem custo direto)'; Unit = '-'; Monthly = 0 })
$lines.Add([pscustomobject]@{ Item = 'Container Apps Consumption (escala a zero, dentro da cota gratuita mensal)'; Unit = '-'; Monthly = 0 })
$lines.Add([pscustomobject]@{ Item = 'Key Vault, Storage, App Insights (uso minimo)'; Unit = '-'; Monthly = 1 })

$lines | Format-Table Item, Unit, @{ Label = 'USD/mes'; Expression = { '{0:N2}' -f $_.Monthly } } -AutoSize
$monthly = ($lines | Measure-Object -Property Monthly -Sum).Sum
Write-Host ('Total estimado: USD {0:N2}/mes | USD {1:N2} em {2} dias' -f $monthly, ($monthly * $Days / 30), $Days) -ForegroundColor Cyan
Write-Host 'Precos de varejo sem creditos/servicos gratuitos. Confira tambem Cost Management no portal.'
