# LDM local dev — no venv activate required
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    python -m venv .venv
    & $py -m pip install -r requirements.txt
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

$env:LLM_MOCK = "1"
if (-not $env:DATABASE_URL) {
    $env:DATABASE_URL = "sqlite:///instance/ldm.db"
}

& $py manage.py init-db
& $py manage.py seed --force
Write-Host "Starting Flask on http://localhost:5000"
& $py app.py
