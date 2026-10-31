param(
    [Parameter(Mandatory = $true)][string]$Brief,
    [Parameter(Mandatory = $true)][string]$Name,
    [string]$Model = 'opencode/deepseek-v4.1-flash-free'
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$dir = Join-Path $PSScriptRoot ("runs\{0}_oc_{1}" -f (Get-Date -Format 'yyyyMMdd_HHmmss'), $Name)
New-Item -ItemType Directory -Force $dir | Out-Null
$briefText = if (Test-Path $Brief) { Get-Content $Brief -Raw -Encoding UTF8 } else { $Brief }
$prompt = (Get-Content (Join-Path $PSScriptRoot 'PREAMBULE.md') -Raw -Encoding UTF8) + "`n`n# Brief`n" + $briefText
$briefFile = Join-Path $dir 'brief.md'
[IO.File]::WriteAllText($briefFile, $prompt, (New-Object Text.UTF8Encoding $false))

$log = Join-Path $dir 'log.txt'
$start = Get-Date
$ErrorActionPreference = 'Continue'
& opencode run "Exécute le brief joint (brief.md) et termine par le rapport final au format demandé." -m $Model --dir $root -f $briefFile *> $log
$code = $LASTEXITCODE
$secs = [int]((Get-Date) - $start).TotalSeconds

$lines = Get-Content $log -Encoding UTF8
$i = ($lines | Select-String -Pattern '^\s*STATUT\s*:' | Select-Object -Last 1).LineNumber
$report = if ($i) { $lines[($i - 1)..($lines.Count - 1)] } else { @('pas de rapport ; fin du journal :') + ($lines | Select-Object -Last 15) }
[IO.File]::WriteAllLines((Join-Path $dir 'rapport.md'), [string[]]$report, (New-Object Text.UTF8Encoding $false))
"OPENCODE $Name ($Model) : code $code, $secs s"
$report
