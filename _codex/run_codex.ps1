param(
    [Parameter(Mandatory = $true)][string]$Brief,
    [Parameter(Mandatory = $true)][string]$Name,
    [ValidateSet('read-only', 'workspace-write')][string]$Sandbox = 'workspace-write'
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$cx = Get-ChildItem "$env:LOCALAPPDATA\OpenAI\Codex\bin\*\codex.exe" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $cx) { throw 'codex.exe de l''application Codex introuvable' }

$dir = Join-Path $PSScriptRoot ("runs\{0}_{1}" -f (Get-Date -Format 'yyyyMMdd_HHmmss'), $Name)
New-Item -ItemType Directory -Force $dir | Out-Null
$briefText = if (Test-Path $Brief) { Get-Content $Brief -Raw -Encoding UTF8 } else { $Brief }
$prompt = (Get-Content (Join-Path $PSScriptRoot 'PREAMBULE.md') -Raw -Encoding UTF8) + "`n`n# Brief`n" + $briefText
[IO.File]::WriteAllText((Join-Path $dir 'brief.md'), $prompt, (New-Object Text.UTF8Encoding $false))

$report = Join-Path $dir 'rapport.md'
$log = Join-Path $dir 'log.txt'
$start = Get-Date
$ErrorActionPreference = 'Continue'
$rel = (Join-Path $dir 'brief.md').Substring($root.Length + 1) -replace '\\', '/'
& $cx.FullName exec --sandbox $Sandbox -C $root -o $report "Lis le fichier $rel, exécute-le et termine par le rapport final au format demandé." *> $log
$code = $LASTEXITCODE
$secs = [int]((Get-Date) - $start).TotalSeconds

"CODEX $Name : code $code, $secs s"
if (Test-Path $report) { Get-Content $report -Encoding UTF8 } else { "pas de rapport ; fin du journal :"; Get-Content $log -Tail 15 }
