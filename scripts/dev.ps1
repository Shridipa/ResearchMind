# ResearchMind 2.0 — local development startup
# Requires: Python 3.11, Node.js 20+, Docker (optional, for Postgres/Redis/Celery)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Write-Host "=== ResearchMind 2.0 Dev Startup ===" -ForegroundColor Cyan

# 1. Infrastructure (Docker)
$dockerRunning = $false
try {
    docker info 2>$null | Out-Null
    $dockerRunning = $true
} catch {}

if ($dockerRunning) {
    Write-Host "[infra] Starting Postgres + Redis via Docker Compose..." -ForegroundColor Yellow
    Push-Location $Root
    docker compose up -d postgres redis
    Pop-Location
} else {
    Write-Host "[infra] Docker not running — Postgres/Redis/Celery unavailable." -ForegroundColor DarkYellow
    Write-Host "        Start Docker Desktop for full enterprise features (ingestion queue, WebSockets)." -ForegroundColor DarkYellow
}

# 2. Backend venv
$venvPython = Join-Path $Root "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "[backend] Creating Python 3.11 venv..." -ForegroundColor Yellow
    py -3.11 -m venv (Join-Path $Root "backend\.venv")
    & (Join-Path $Root "backend\.venv\Scripts\pip.exe") install -r (Join-Path $Root "backend\requirements.txt") email-validator bcrypt
}

# 3. Backend
Write-Host "[backend] Starting FastAPI on http://localhost:8000 ..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    param($Root)
    Set-Location (Join-Path $Root "backend")
    $env:LLM_PROVIDER = "mock"
    & (Join-Path $Root "backend\.venv\Scripts\python.exe") -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
} -ArgumentList $Root

# 4. Frontend
Write-Host "[frontend] Starting Next.js on http://localhost:3000 ..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    param($Root)
    Set-Location (Join-Path $Root "frontend")
    if (-not (Test-Path "node_modules")) { npm install }
    npm run dev
} -ArgumentList $Root

Start-Sleep -Seconds 5
Write-Host ""
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000/api/docs" -ForegroundColor White
Write-Host "  Health:    http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop. Jobs: Backend=$($backendJob.Id) Frontend=$($frontendJob.Id)" -ForegroundColor DarkGray

try {
    while ($true) {
        Receive-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_ }
        Start-Sleep -Seconds 2
    }
} finally {
    Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob, $frontendJob -Force -ErrorAction SilentlyContinue
}
