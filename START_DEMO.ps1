# Run from PowerShell: .\START_DEMO.ps1
$ErrorActionPreference = "Stop"
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $projectDir
if (-not (Test-Path ".venv\Scripts\python.exe")) { Write-Host "Missing .venv. See README setup." -ForegroundColor Red; exit 1 }
$pythonPath = Join-Path $projectDir ".venv\Scripts\python.exe"
$port = 8000
if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) {
    $port = 8011
    Write-Host "Port 8000 is already in use. Starting the fresh demo on port 8011 instead." -ForegroundColor Yellow
}
$url = "http://127.0.0.1:$port"
Write-Host "Starting KrishiMitr at $url" -ForegroundColor Green
$serverCommand = "& '$pythonPath' -m uvicorn main:app --reload --host 127.0.0.1 --port $port"
$server = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", $serverCommand -PassThru
$deadline = (Get-Date).AddSeconds(30)
do {
    Start-Sleep -Milliseconds 500
    try { $ready = (Invoke-WebRequest -UseBasicParsing -Uri "$url/health" -TimeoutSec 2).StatusCode -eq 200 } catch { $ready = $false }
} while (-not $ready -and (Get-Date) -lt $deadline)
if (-not $ready) {
    Write-Host "Server did not start. Check the separate KrishiMitr server window for the error." -ForegroundColor Red
    exit 1
}
Start-Process $url
Write-Host "Website opened. Keep the separate KrishiMitr server window open." -ForegroundColor Yellow
