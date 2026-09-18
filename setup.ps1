$ErrorActionPreference = 'Stop'
# Repair only this process when an automation host omits executable extensions.
if ($env:PATHEXT -notmatch '(?i)(^|;)\.EXE(;|$)') { $env:PATHEXT = '.COM;.EXE;.BAT;.CMD;' + $env:PATHEXT }
Set-Location -LiteralPath $PSScriptRoot
$candidates = @()
$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pyLauncher) { $candidates += $pyLauncher.Source }
if ($pythonCommand) { $candidates += $pythonCommand.Source }
$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (Test-Path -LiteralPath $bundledPython) { $candidates += $bundledPython }
$labPython = $null
foreach ($candidate in $candidates) {
    try {
        & $candidate -c "import sys; sys.exit(0 if sys.version_info[:2] == (3,12) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) { $labPython = $candidate; break }
    } catch { }
}
if (-not $labPython) { throw 'Install Python 3.12 from python.org (Add python.exe to PATH), then retry.' }
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    & $labPython -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'venv creation failed' }
}
& '.\.venv\Scripts\python.exe' -m pip install -r requirements-lock.txt
if ($LASTEXITCODE -ne 0) { throw 'dependency installation failed' }
& '.\.venv\Scripts\python.exe' -X utf8 scripts\verify_environment.py
if ($LASTEXITCODE -ne 0) { throw 'verification failed; read outputs/environment_report.json' }
Write-Host 'SETUP PASS. Open demo.cmd to begin.' -ForegroundColor Green
