# =============================================================================
# setup_models.ps1 — Windows helper to download models
# =============================================================================
# Run this ONCE on a machine with internet access to HuggingFace.
#
# Usage:
#   .\setup_models.ps1                     # Download all models
#   .\setup_models.ps1 -SkipLLM            # Skip LLM (already have it)
#   .\setup_models.ps1 -SkipWhisper        # Skip Whisper
#   .\setup_models.ps1 -WhisperSize large-v3
#   .\setup_models.ps1 -VerifyOnly         # Just check if models exist
# =============================================================================
param(
    [switch]$SkipLLM,
    [switch]$SkipWhisper,
    [switch]$SkipEmbedding,
    [switch]$VerifyOnly,
    [string]$WhisperSize = "medium.en",
    [string]$ModelsDir = "models"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ASML Pipeline — Model Setup (Windows)     " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python is available
try {
    $pyVersion = python --version 2>&1
    Write-Host "[OK] Python: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Install Python 3.10+ first." -ForegroundColor Red
    exit 1
}

# Install huggingface_hub if not present
Write-Host "Checking huggingface_hub..." -ForegroundColor Cyan
pip install huggingface_hub --quiet 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install huggingface_hub" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] huggingface_hub installed" -ForegroundColor Green

# Build the command
$args_list = @("setup_models.py", "--models_dir", $ModelsDir, "--whisper_size", $WhisperSize)

if ($SkipLLM)       { $args_list += "--skip_llm" }
if ($SkipWhisper)   { $args_list += "--skip_whisper" }
if ($SkipEmbedding) { $args_list += "--skip_embedding" }
if ($VerifyOnly)    { $args_list += "--verify_only" }

Write-Host ""
Write-Host "Running: python $($args_list -join ' ')" -ForegroundColor Cyan
Write-Host ""

python @args_list

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Model setup failed. See errors above." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Model setup complete!                     " -ForegroundColor Green
Write-Host "  Next: docker compose up                   " -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
