$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$backend = Start-Process -FilePath "python" `
    -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8765 --reload" `
    -WorkingDirectory $PSScriptRoot `
    -PassThru

$frontend = Start-Process -FilePath "npm.cmd" `
    -ArgumentList "run dev" `
    -WorkingDirectory (Join-Path $PSScriptRoot "jarvis-frontend") `
    -PassThru

Write-Host "Backend:  http://127.0.0.1:8765/api/health"
Write-Host "Frontend: http://localhost:1420"
Write-Host "Press Ctrl+C to stop this launcher."

try {
    Wait-Process -Id $backend.Id, $frontend.Id
}
finally {
    foreach ($process in @($backend, $frontend)) {
        if (!$process.HasExited) {
            Stop-Process -Id $process.Id -Force
        }
    }
}
