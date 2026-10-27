$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot
$env:DJANGO_DEBUG = 'true'
$env:DB_NAME = Join-Path $repoRoot ('e2e-' + [guid]::NewGuid().ToString('N') + '.sqlite3')
$env:CAMPUS_DEMO_PASSWORD = 'demo-' + [guid]::NewGuid().ToString('N')
$pythonPath = Join-Path $repoRoot '.venv\Scripts\python.exe'
& $pythonPath manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'Database migration failed' }
& $pythonPath manage.py seed_recommendation_demo
if ($LASTEXITCODE -ne 0) { throw 'Demo data creation failed' }
$env:CAMPUS_PYTHON_COMMAND = '..\.venv\Scripts\python ..\manage.py runserver 127.0.0.1:8001 --noreload'
Set-Location -LiteralPath (Join-Path $repoRoot 'frontend')
try {
    npx playwright test --config playwright.real.config.js
    if ($LASTEXITCODE -ne 0) { throw 'Real integration test failed' }
} finally {
    Set-Location -LiteralPath $repoRoot
    Remove-Item Env:CAMPUS_DEMO_PASSWORD -ErrorAction SilentlyContinue
    Remove-Item Env:DB_NAME -ErrorAction SilentlyContinue
    Remove-Item Env:CAMPUS_PYTHON_COMMAND -ErrorAction SilentlyContinue
}
