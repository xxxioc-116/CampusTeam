$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$originalLocation = (Get-Location).Path
$demoDbPath = [IO.Path]::GetFullPath((Join-Path $repoRoot ('e2e-' + [guid]::NewGuid().ToString('N') + '.sqlite3')))
if ([IO.Path]::GetDirectoryName($demoDbPath) -ne $repoRoot -or [IO.Path]::GetFileName($demoDbPath) -notmatch '^e2e-[0-9a-f]{32}\.sqlite3$') {
    throw 'Unexpected temporary database path'
}
$pythonPath = Join-Path $repoRoot '.venv\Scripts\python.exe'
$playwrightPath = Join-Path $repoRoot 'frontend\node_modules\@playwright\test\cli.js'
$variableNames = @('DJANGO_DEBUG', 'DB_NAME', 'CAMPUS_DEMO_PASSWORD', 'CAMPUS_PYTHON_COMMAND')
$originalEnvironment = @{}
foreach ($name in $variableNames) {
    $originalEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
}
try {
    if (!(Test-Path -LiteralPath $pythonPath) -or !(Test-Path -LiteralPath $playwrightPath)) {
        throw 'Install the Python and locked frontend dependencies before running this test'
    }
    Set-Location -LiteralPath $repoRoot
    $env:DJANGO_DEBUG = 'true'
    $env:DB_NAME = $demoDbPath
    $env:CAMPUS_DEMO_PASSWORD = 'demo-' + [guid]::NewGuid().ToString('N')
    & $pythonPath manage.py migrate --noinput
    if ($LASTEXITCODE -ne 0) { throw 'Database migration failed' }
    & $pythonPath manage.py seed_recommendation_demo
    if ($LASTEXITCODE -ne 0) { throw 'Demo data creation failed' }
    $env:CAMPUS_PYTHON_COMMAND = '..\.venv\Scripts\python ..\manage.py runserver 127.0.0.1:8001 --noreload'
    Set-Location -LiteralPath (Join-Path $repoRoot 'frontend')
    & node $playwrightPath test --config playwright.real.config.js
    if ($LASTEXITCODE -ne 0) { throw 'Real integration test failed' }
} finally {
    Set-Location -LiteralPath $originalLocation
    foreach ($name in $variableNames) {
        if ($null -eq $originalEnvironment[$name]) {
            Remove-Item -LiteralPath ("Env:" + $name) -ErrorAction SilentlyContinue
        } else {
            [Environment]::SetEnvironmentVariable($name, $originalEnvironment[$name], 'Process')
        }
    }
    foreach ($suffix in @('', '-wal', '-shm', '-journal')) {
        $temporaryPath = [IO.Path]::GetFullPath($demoDbPath + $suffix)
        if ([IO.Path]::GetDirectoryName($temporaryPath) -ne $repoRoot) { throw 'Unsafe cleanup target' }
        if (Test-Path -LiteralPath $temporaryPath) { Remove-Item -LiteralPath $temporaryPath -ErrorAction Stop }
    }
}
