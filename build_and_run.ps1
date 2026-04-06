# =============================================================================
# build_and_run.ps1 — Build Docker image and run the pipeline
# =============================================================================
# Usage:
#   .\build_and_run.ps1             # Build + run pipeline
#   .\build_and_run.ps1 -BuildOnly  # Build only
#   .\build_and_run.ps1 -RunOnly    # Run only (already built)
# =============================================================================
param(
    [switch]$BuildOnly,
    [switch]$RunOnly
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ASML Pipeline — Build & Run               " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ── Pre-flight checks ────────────────────────────────────────────────────

# Check Docker
try {
    docker info 2>$null | Out-Null
    Write-Host "[OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not running. Start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check models
Write-Host ""
Write-Host "Checking models..." -ForegroundColor Cyan
$llmPath = "models\llm\Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"
$whisperPath = "models\whisper\model.bin"
$embeddingPath = "models\embeddings\all-MiniLM-L6-v2\config.json"

$modelsOk = $true
if (Test-Path $llmPath) {
    Write-Host "  [OK] LLM model found" -ForegroundColor Green
} else {
    Write-Host "  [MISSING] LLM model: $llmPath" -ForegroundColor Red
    $modelsOk = $false
}
if (Test-Path $whisperPath) {
    Write-Host "  [OK] Whisper model found" -ForegroundColor Green
} else {
    Write-Host "  [MISSING] Whisper model: $whisperPath" -ForegroundColor Red
    $modelsOk = $false
}
if (Test-Path $embeddingPath) {
    Write-Host "  [OK] Embedding model found" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Embedding model not found (will use TF-IDF fallback)" -ForegroundColor Yellow
}

if (-not $modelsOk) {
    Write-Host ""
    Write-Host "Required models are missing. Run setup_models.ps1 first:" -ForegroundColor Red
    Write-Host "  .\setup_models.ps1" -ForegroundColor Yellow
    exit 1
}

# Check videos
$videoCount = (Get-ChildItem -Path "Data\raw_videos" -Include "*.mp4","*.mkv","*.mov","*.avi","*.webm" -File -ErrorAction SilentlyContinue).Count
if ($videoCount -eq 0) {
    Write-Host ""
    Write-Host "[WARN] No videos in Data\raw_videos\. Add .mp4 files first." -ForegroundColor Yellow
}
Write-Host "[OK] $videoCount video(s) ready" -ForegroundColor Green

# ── Build ────────────────────────────────────────────────────────────────
if (-not $RunOnly) {
    Write-Host ""
    Write-Host "Building Docker image..." -ForegroundColor Cyan
    docker compose build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Docker build failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Image built successfully" -ForegroundColor Green
}

# ── Run ──────────────────────────────────────────────────────────────────
if (-not $BuildOnly) {
    Write-Host ""
    Write-Host "Starting pipeline..." -ForegroundColor Cyan
    Write-Host "(This may take several minutes per video)" -ForegroundColor Yellow
    Write-Host ""
    docker compose up
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Done! Check Data\ for results.            " -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
