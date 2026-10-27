$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$statePath = Join-Path $repoRoot '.demo-state.json'
if (!(Test-Path -LiteralPath $statePath)) { Write-Host 'No recorded demo processes.'; return }
$records = @(Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json)
foreach ($record in $records) {
    $process = Get-Process -Id $record.id -ErrorAction SilentlyContinue
    if ($process -and $process.Path -eq $record.path -and $process.StartTime.ToUniversalTime().ToString('o') -eq $record.started) {
        Stop-Process -Id $process.Id
    }
}
Remove-Item -LiteralPath $statePath
Write-Host 'Recorded demo services stopped. Demo data and logs were preserved.'
