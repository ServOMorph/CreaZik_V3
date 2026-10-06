param(
    [ValidateSet('start', 'stop', 'restart', 'status')]
    [string]$Action = 'status',
    [string]$Only = ''
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$acePython = 'D:\ServOMorph\ACE-Step-1.5\.venv\Scripts\python.exe'
$gitBash = 'C:\Program Files\Git\bin\bash.exe'

$services = @(
    @{ Name = 'serveur';    Match = 'server\.py';      File = 'python';  Args = @('server.py', '--no-browser') },
    @{ Name = 'analyse';    Match = 'analyze_viz\.py'; File = $acePython; Args = @('analyze_viz.py', '--watch') },
    @{ Name = 'compression'; Match = 'compress_audio\.py'; File = 'python'; Args = @('compress_audio.py', '--watch') },
    @{ Name = 'generation'; Match = 'run_series\.sh';  File = $gitBash;  Args = @('run_series.sh') }
)

function Get-ServiceProcess($match) {
    Get-CimInstance Win32_Process | Where-Object {
        $_.Name -match 'python|bash' -and $_.CommandLine -match $match
    }
}

function Stop-Services {
    foreach ($s in $services) {
        if ($Only -and $s.Name -ne $Only) { continue }
        Get-ServiceProcess $s.Match | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    }
    if (-not $Only -or $Only -eq 'generation') {
        Get-CimInstance Win32_Process | Where-Object {
            $_.Name -match 'python' -and $_.CommandLine -match 'run_rotation\.py|run_queue\.py|ace_worker\.py|generate\.py'
        } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    }
}

function Start-Missing {
    foreach ($s in $services) {
        if ($Only -and $s.Name -ne $Only) { continue }
        if (-not (Get-ServiceProcess $s.Match)) {
            Start-Process -WindowStyle Hidden -FilePath $s.File -ArgumentList $s.Args -WorkingDirectory $root
            Write-Host "demarre : $($s.Name)"
        }
    }
}

switch ($Action) {
    'stop'    { Stop-Services; Write-Host 'arrete. Pensez a relancer : .\services.ps1 start' }
    'start'   { Start-Missing }
    'restart' { Stop-Services; Start-Sleep -Seconds 3; Start-Missing }
    'status'  {
        foreach ($s in $services) {
            $state = if (Get-ServiceProcess $s.Match) { 'actif' } else { 'ARRETE' }
            Write-Host ("{0,-12} {1}" -f $s.Name, $state)
        }
    }
}
