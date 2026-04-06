Param(
    [string]$ImageName = "asml-pipeline-offline:latest"
)

$ErrorActionPreference = "Stop"
docker build -t $ImageName .
