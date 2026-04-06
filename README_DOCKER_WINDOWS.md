# ASML Pipeline - Windows + Docker (Mounted Models, All Videos in Folder)

This bundle is tailored for:
- Windows host
- Docker Desktop
- CPU-first execution
- models mounted from the host
- all videos in `input/`

## Expected folders

```text
project/
├─ Dockerfile
├─ requirements.txt
├─ run_pipeline.ps1
├─ build_image.ps1
├─ models/
│  ├─ whisper/
│  │  └─ medium.en/
│  └─ llm/
│     └─ model.gguf
├─ input/
├─ Data/
├─ scripts/
└─ docker/
```

## Build

Open PowerShell in the project root:

```powershell
.uild_image.ps1
```

## Run (CPU)

Put all test videos inside `input/`, then run:

```powershell
.un_pipeline.ps1
```

## Run (try GPU passthrough if host has NVIDIA)

```powershell
.un_pipeline.ps1 -UseGpu
```

## Notes

- The image is CPU-first and works offline.
- `models/` is mounted, so the image stays smaller and you can swap models without rebuilding.
- Output goes to `Data/`.
