Param(
    [string]$ImageName = "asml-pipeline-offline:latest",
    [string]$InputDir = ".\input",
    [string]$DataDir = ".\Data",
    [string]$ModelsDir = ".\models",
    [switch]$UseGpu
)

$ErrorActionPreference = "Stop"

function Resolve-FullPath([string]$PathValue) {
    $item = Resolve-Path -LiteralPath $PathValue -ErrorAction SilentlyContinue
    if ($item) { return $item.Path }
    $full = [System.IO.Path]::GetFullPath($PathValue)
    return $full
}

$inputFull = Resolve-FullPath $InputDir
$dataFull = Resolve-FullPath $DataDir
$modelsFull = Resolve-FullPath $ModelsDir

if (-not (Test-Path $inputFull)) { New-Item -ItemType Directory -Force -Path $inputFull | Out-Null }
if (-not (Test-Path $dataFull)) { New-Item -ItemType Directory -Force -Path $dataFull | Out-Null }
if (-not (Test-Path $modelsFull)) { throw "Models folder not found: $modelsFull" }

$dockerArgs = @(
    "run", "--rm", "-it",
    "-v", "${inputFull}:/workspace/input",
    "-v", "${dataFull}:/workspace/Data",
    "-v", "${modelsFull}:/app/models",
    "-e", "WHISPER_DEVICE=cpu",
    "-e", "WHISPER_COMPUTE_TYPE=int8",
    "-e", "LLM_N_GPU_LAYERS=0"
)

$gpuAvailable = $false
if ($UseGpu) {
    $nvidia = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if ($nvidia) {
        $gpuAvailable = $true
    }
}

if ($gpuAvailable) {
    Write-Host "GPU requested and detected on host. Passing --gpus all to Docker."
    $dockerArgs += @("--gpus", "all")
    # NOTE: current image is CPU-first. These env vars are exposed so you can reuse the same wrapper
    # with a future GPU image variant.
    $dockerArgs += @("-e", "WHISPER_DEVICE=cuda", "-e", "WHISPER_COMPUTE_TYPE=float16", "-e", "LLM_N_GPU_LAYERS=-1")
}
else {
    Write-Host "Running in CPU mode."
}

$dockerArgs += $ImageName

Write-Host "Executing: docker $($dockerArgs -join ' ')"
& docker @dockerArgs
