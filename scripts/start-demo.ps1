$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot
$pythonPath = Join-Path $repoRoot '.venv\Scripts\python.exe'
$vitePath = Join-Path $repoRoot 'frontend\node_modules\vite\bin\vite.js'
if (!(Test-Path -LiteralPath $pythonPath) -or !(Test-Path -LiteralPath $vitePath)) {
    throw 'Install Python and frontend dependencies first; see docs/local-handoff.md.'
}
$statePath = Join-Path $repoRoot '.demo-state.json'
if (Test-Path -LiteralPath $statePath) { throw 'Run scripts/stop-demo.ps1 before starting another demo.' }
foreach ($port in @(8000, 5173)) {
    if (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue) {
        throw "Port $port is already in use. Stop that service or use the real integration test instead."
    }
}
$env:DJANGO_DEBUG = 'true'
$env:DB_NAME = Join-Path $repoRoot 'local-demo.sqlite3'
$env:CAMPUS_DEMO_PASSWORD = 'demo-' + [guid]::NewGuid().ToString('N')
$demoPassword = $env:CAMPUS_DEMO_PASSWORD
& $pythonPath manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'Database migration failed' }
& $pythonPath manage.py seed_recommendation_demo
if ($LASTEXITCODE -ne 0) { throw 'Demo seeding failed' }
$env:VITE_USE_MOCK = 'false'
$env:API_PROXY_TARGET = 'http://127.0.0.1:8000'
$logDir = Join-Path $repoRoot '.demo-logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$started = @()
try {
    $backend = Start-Process -FilePath $pythonPath -ArgumentList @('manage.py','runserver','127.0.0.1:8000','--noreload') -WorkingDirectory $repoRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logDir 'backend-out.log') -RedirectStandardError (Join-Path $logDir 'backend-error.log')
    $started += $backend
    $nodePath = (Get-Command node -ErrorAction Stop).Source
    $frontend = Start-Process -FilePath $nodePath -ArgumentList @(('"' + $vitePath + '"'),'--host','127.0.0.1','--port','5173','--strictPort') -WorkingDirectory (Join-Path $repoRoot 'frontend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logDir 'frontend-out.log') -RedirectStandardError (Join-Path $logDir 'frontend-error.log')
    $started += $frontend
    foreach ($url in @('http://127.0.0.1:8000/api/v1/health','http://127.0.0.1:5173')) {
        $ready = $false
        for ($attempt = 0; $attempt -lt 30; $attempt++) {
            try {
                $response = Invoke-WebRequest -Uri $url -TimeoutSec 1 -UseBasicParsing
                if ($response.StatusCode -eq 200) { $ready = $true; break }
            } catch { Start-Sleep -Milliseconds 300 }
        }
        if (!$ready) { throw "Service did not start: $url. See .demo-logs." }
    }
    @($started | ForEach-Object { @{ id=$_.Id; started=$_.StartTime.ToUniversalTime().ToString('o'); path=$_.Path } }) | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding utf8
    Write-Host 'Open http://127.0.0.1:5173'
    Write-Host 'Users: rec_leader / rec_candidate (local demo database only)'
    Write-Host "Temporary demo password: $demoPassword"
    Write-Host 'Stop with .\scripts\stop-demo.ps1'
} catch {
    $started | Where-Object { !$_.HasExited } | Stop-Process -ErrorAction SilentlyContinue
    throw
} finally {
    Remove-Item Env:CAMPUS_DEMO_PASSWORD -ErrorAction SilentlyContinue
    Remove-Item Env:DB_NAME -ErrorAction SilentlyContinue
    Remove-Item Env:VITE_USE_MOCK -ErrorAction SilentlyContinue
    Remove-Item Env:API_PROXY_TARGET -ErrorAction SilentlyContinue
}
