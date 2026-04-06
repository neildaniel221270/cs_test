Yes — you can make this pipeline run **fully inside Docker** so the tester only needs **VS Code + Docker**, with **no LM Studio / Ollama / other desktop AI apps**. The main thing you need to replace is the current **LM Studio dependency** in your structuring/boundary steps with a **local OpenAI-compatible server running inside the container**. Your current scripts are already close to this:

*   `transcribe_batch.py` already accepts a `--model` argument and passes it directly into `WhisperModel(...)`, so you can point it to a **local Whisper model folder** instead of downloading at runtime. (transcribe_batch.py)
*   `semantic_segmentation.py` already works **offline** and even falls back to **TF-IDF** if `sentence-transformers` is unavailable, so an embeddings model is **optional**. (semantic_segmentation.py)
*   The only real external-app blocker is that your structuring/boundary scripts currently call an **LM Studio-compatible `/chat/completions` endpoint**. (structure_batch.py), (structure_batch_2.py), (clean_transcript.py)
*   `extract_audio.py` depends on `ffmpeg`/`ffprobe`, so those must be installed in the Docker image. (extract_audio.py)

***

# Recommended offline design

## Use only **2 local models**

That is enough for your pipeline:

1.  **Whisper model** for transcription  
    Recommended:
    *   **CPU-safe**: `medium.en` (good accuracy/speed tradeoff)
    *   **GPU if available**: `large-v3`

2.  **Local LLM model** for structuring + boundary detection  
    Recommended:
    *   **Better quality**: a **7B instruct GGUF**
    *   **Safer on CPU/RAM**: a **3B–4B instruct GGUF**

## Do **not** require an embeddings model

Because your `semantic_segmentation.py` already falls back to TF-IDF, you can skip a third model completely. (semantic_segmentation.py)

***

# What I recommend you change

## Keep these scripts as they are

These already fit the offline plan:

*   `extract_audio.py` (extract_audio.py)
*   `transcribe_batch.py` (transcribe_batch.py)
*   `clean_transcript.py` (but **do not** use its internal `--structure` option anymore; use the batch structuring script instead) (clean_transcript.py)
*   `semantic_segmentation.py` (semantic_segmentation.py)
*   `timestamp_alignment.py` (timestamp_alignment.py)
*   `compare_reports.py` (compare_reports.py)

## Use this script for LLM work

Use **`structure_batch_2.py`** for both:

*   `--mode structure`
*   `--mode boundary`  
    because it already supports both modes via one OpenAI-compatible endpoint. (structure_batch_2.py)

***

# Final folder structure

Put your project like this:

```text
project/
├─ scripts/
│  ├─ boundary_detection.py
│  ├─ clean_transcript.py
│  ├─ compare_reports.py
│  ├─ extract_audio.py
│  ├─ prompts.py
│  ├─ prompts_2.py
│  ├─ semantic_segmentation.py
│  ├─ structure_batch.py
│  ├─ structure_batch_2.py
│  ├─ timestamp_alignment.py
│  └─ transcribe_batch.py
├─ docker/
│  ├─ entrypoint.sh
│  ├─ start_local_llm.sh
│  └─ run_full_pipeline.sh
├─ models/
│  ├─ whisper/
│  │  └─ medium.en/              # local faster-whisper / CTranslate2 model folder
│  └─ llm/
│     └─ model.gguf              # local GGUF instruct model
├─ input/                        # tester drops videos here
├─ Data/                         # pipeline output
├─ requirements.txt
└─ Dockerfile
```

***

# Step-by-step implementation

***

## STEP 1 — Move your uploaded Python files into `scripts/`

Create a folder called `scripts/` and place all your current `.py` files there.  
That matches how your imports are already written (`sys.path.insert(...)` etc.). (structure_batch.py), (structure_batch_2.py)

***

## STEP 2 — Create `requirements.txt`

Create a file named **`requirements.txt`**:

```txt
faster-whisper==1.1.0
numpy==1.26.4
scikit-learn==1.5.2
llama-cpp-python[server]==0.2.90
```

### Why this is enough

*   `faster-whisper` → ASR
*   `llama-cpp-python[server]` → local OpenAI-compatible LLM server inside container
*   `scikit-learn` + `numpy` → semantic segmentation TF-IDF fallback

> I am **intentionally not adding `sentence-transformers`** so the image stays lighter and fully offline. Your segmentation script will still work using TF-IDF fallback.(semantic_segmentation.py)

***

## STEP 3 — Create the Dockerfile

Create **`Dockerfile`**:

```dockerfile
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    XDG_CACHE_HOME=/app/.cache

WORKDIR /app

# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    build-essential \
    cmake \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && \
    CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" \
    pip install -r /app/requirements.txt

# Copy scripts + docker helpers
COPY scripts/ /app/scripts/
COPY docker/ /app/docker/

RUN chmod +x /app/docker/*.sh

# Default locations
RUN mkdir -p /app/models /workspace/input /workspace/Data

ENTRYPOINT ["/app/docker/entrypoint.sh"]
```

***

## STEP 4 — Create the script that starts the local LLM server

Create **`docker/start_local_llm.sh`**:

```bash
#!/usr/bin/env bash
set -euo pipefail

LLM_MODEL_PATH="${LLM_MODEL_PATH:-/app/models/llm/model.gguf}"
LLM_PORT="${LLM_PORT:-8000}"
LLM_CTX="${LLM_CTX:-8192}"
LLM_ALIAS="${LLM_ALIAS:-local-llm}"
LLM_THREADS="${LLM_THREADS:-8}"
LLM_N_GPU_LAYERS="${LLM_N_GPU_LAYERS:-0}"

if [ ! -f "$LLM_MODEL_PATH" ]; then
  echo "[ERROR] LLM model not found: $LLM_MODEL_PATH"
  exit 1
fi

echo "[INFO] Starting local LLM server..."
python -m llama_cpp.server \
  --model "$LLM_MODEL_PATH" \
  --host 0.0.0.0 \
  --port "$LLM_PORT" \
  --n_ctx "$LLM_CTX" \
  --model_alias "$LLM_ALIAS" \
  --n_threads "$LLM_THREADS" \
  --n_gpu_layers "$LLM_N_GPU_LAYERS" \
  >/tmp/llm_server.log 2>&1 &

LLM_PID=$!
echo "$LLM_PID" >/tmp/llm_server.pid

echo "[INFO] Waiting for LLM server to become ready..."
for i in $(seq 1 120); do
  if curl -s "http://127.0.0.1:${LLM_PORT}/v1/models" >/dev/null 2>&1; then
    echo "[INFO] LLM server is ready."
    exit 0
  fi
  sleep 2
done

echo "[ERROR] LLM server did not start in time."
echo "----- llama.cpp server log -----"
cat /tmp/llm_server.log || true
exit 1
```

***

## STEP 5 — Create the full pipeline runner

Create **`docker/run_full_pipeline.sh`**:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT_DIR="${INPUT_DIR:-/workspace/input}"
DATA_DIR="${DATA_DIR:-/workspace/Data}"

WHISPER_MODEL_PATH="${WHISPER_MODEL_PATH:-/app/models/whisper/medium.en}"
WHISPER_DEVICE="${WHISPER_DEVICE:-cpu}"
WHISPER_COMPUTE_TYPE="${WHISPER_COMPUTE_TYPE:-int8}"
WHISPER_LANGUAGE="${WHISPER_LANGUAGE:-en}"

LLM_BASE_URL="${LLM_BASE_URL:-http://127.0.0.1:8000/v1}"
LLM_MODEL_NAME="${LLM_MODEL_NAME:-local-llm}"
LLM_TIMEOUT="${LLM_TIMEOUT:-600}"

mkdir -p \
  "${DATA_DIR}/processed/audio_wav" \
  "${DATA_DIR}/processed/subtitles" \
  "${DATA_DIR}/transcripts_raw" \
  "${DATA_DIR}/transcripts_clean" \
  "${DATA_DIR}/transcripts_structured" \
  "${DATA_DIR}/transcripts_boundaries" \
  "${DATA_DIR}/transcripts_segmented" \
  "${DATA_DIR}/transcripts_aligned" \
  "${DATA_DIR}/reports"

echo "============================================================"
echo "1) Extract audio / subtitles"
echo "============================================================"
python /app/scripts/extract_audio.py \
  --input "${INPUT_DIR}" \
  --out_audio_dir "${DATA_DIR}/processed/audio_wav" \
  --out_sub_dir "${DATA_DIR}/processed/subtitles" \
  --manifest "${DATA_DIR}/processed/manifest.jsonl"

echo "============================================================"
echo "2) Transcribe audio"
echo "============================================================"
python /app/scripts/transcribe_batch.py \
  --manifest "${DATA_DIR}/processed/manifest.jsonl" \
  --out_dir "${DATA_DIR}/transcripts_raw" \
  --model "${WHISPER_MODEL_PATH}" \
  --device "${WHISPER_DEVICE}" \
  --compute_type "${WHISPER_COMPUTE_TYPE}" \
  --language "${WHISPER_LANGUAGE}" \
  --limit 999999

echo "============================================================"
echo "3) Clean transcripts"
echo "============================================================"
for f in "${DATA_DIR}"/transcripts_raw/*.raw.json; do
  [ -e "$f" ] || continue
  base="$(basename "$f" .raw.json)"
  python /app/scripts/clean_transcript.py \
    --in_raw_json "$f" \
    --out_clean_json "${DATA_DIR}/transcripts_clean/${base}.clean.json"
done

echo "============================================================"
echo "4) Structure transcripts with local LLM"
echo "============================================================"
python /app/scripts/structure_batch_2.py \
  --mode structure \
  --in_dir "${DATA_DIR}/transcripts_clean" \
  --out_dir "${DATA_DIR}/transcripts_structured" \
  --model "${LLM_MODEL_NAME}" \
  --base_url "${LLM_BASE_URL}" \
  --timeout "${LLM_TIMEOUT}" \
  --force

echo "============================================================"
echo "5) Detect boundaries with local LLM"
echo "============================================================"
python /app/scripts/structure_batch_2.py \
  --mode boundary \
  --in_dir "${DATA_DIR}/transcripts_clean" \
  --out_dir "${DATA_DIR}/transcripts_boundaries" \
  --model "${LLM_MODEL_NAME}" \
  --base_url "${LLM_BASE_URL}" \
  --timeout "${LLM_TIMEOUT}" \
  --force

echo "============================================================"
echo "6) Semantic segmentation"
echo "============================================================"
for f in "${DATA_DIR}"/transcripts_clean/*.clean.json; do
  [ -e "$f" ] || continue
  base="$(basename "$f" .clean.json)"
  python /app/scripts/semantic_segmentation.py \
    --in_json "$f" \
    --out_json "${DATA_DIR}/transcripts_segmented/${base}.segmented.json"
done

echo "============================================================"
echo "7) Timestamp alignment"
echo "============================================================"
for f in "${DATA_DIR}"/transcripts_structured/*.structured.json; do
  [ -e "$f" ] || continue
  base="$(basename "$f" .structured.json)"
  python /app/scripts/timestamp_alignment.py \
    --in_structured_json "$f" \
    --out_aligned_json "${DATA_DIR}/transcripts_aligned/${base}.aligned.json"
done

echo "============================================================"
echo "8) Compare reports"
echo "============================================================"
for f in "${DATA_DIR}"/transcripts_aligned/*.aligned.json; do
  [ -e "$f" ] || continue
  base="$(basename "$f" .aligned.json)"
  b="${DATA_DIR}/transcripts_boundaries/${base}.boundaries.json"
  s="${DATA_DIR}/transcripts_segmented/${base}.segmented.json"
  if [ -f "$b" ] && [ -f "$s" ]; then
    python /app/scripts/compare_reports.py \
      --boundaries_json "$b" \
      --segmented_json "$s" \
      --aligned_json "$f" \
      --out_report "${DATA_DIR}/reports/${base}.comparison.txt"
  fi
done

echo "============================================================"
echo "PIPELINE FINISHED"
echo "Outputs are in: ${DATA_DIR}"
echo "============================================================"
```

***

## STEP 6 — Create the entrypoint

Create **`docker/entrypoint.sh`**:

```bash
#!/usr/bin/env bash
set -euo pipefail

START_LLM_SERVER="${START_LLM_SERVER:-1}"

if [ "${START_LLM_SERVER}" = "1" ]; then
  /app/docker/start_local_llm.sh
fi

if [ "$#" -eq 0 ]; then
  exec /app/docker/run_full_pipeline.sh
else
  exec "$@"
fi
```

This means:

*   If you run the container normally, it will:
    1.  start the local LLM server
    2.  run the whole pipeline
*   If you pass your own command, it will execute that instead

***

# STEP 7 — Prepare the models offline

Because the ASML network cannot access Hugging Face or many AI sites, **do this once on a machine that *does* have internet access**, then bring the files into the repo.  
Do **not** rely on runtime downloads inside Docker.

## Model 1: Whisper

Use a **local faster-whisper / CTranslate2 model directory**.

Recommended:

*   `medium.en` for CPU
*   `large-v3` if GPU exists and speed is acceptable

Put it here:

```text
models/whisper/medium.en/
```

## Model 2: LLM

Use a **GGUF instruct model**.

Recommended options:

*   **CPU lighter**: 3B–4B instruct GGUF
*   **Better quality**: 7B instruct GGUF

Put it here:

```text
models/llm/model.gguf
```

***

# STEP 8 — Build the Docker image

From the project root:

```bash
docker build -t asml-pipeline-offline:latest .
```

***

# STEP 9 — Run the full pipeline

## CPU example

```bash
docker run --rm -it \
  -v "${PWD}/input:/workspace/input" \
  -v "${PWD}/Data:/workspace/Data" \
  -v "${PWD}/models:/app/models" \
  -e WHISPER_DEVICE=cpu \
  -e WHISPER_COMPUTE_TYPE=int8 \
  -e LLM_N_GPU_LAYERS=0 \
  asml-pipeline-offline:latest
```

## NVIDIA GPU example

```bash
docker run --rm -it \
  --gpus all \
  -v "${PWD}/input:/workspace/input" \
  -v "${PWD}/Data:/workspace/Data" \
  -v "${PWD}/models:/app/models" \
  -e WHISPER_DEVICE=cuda \
  -e WHISPER_COMPUTE_TYPE=float16 \
  -e LLM_N_GPU_LAYERS=-1 \
  asml-pipeline-offline:latest
```

***

# STEP 10 — What the tester needs to do

This is the exact tester workflow:

1.  Open project in **VS Code**
2.  Put video files into `input/`
3.  Ensure the `models/` folder is already present
4.  Run:

```bash
docker build -t asml-pipeline-offline:latest .
docker run --rm -it \
  -v "${PWD}/input:/workspace/input" \
  -v "${PWD}/Data:/workspace/Data" \
  -v "${PWD}/models:/app/models" \
  asml-pipeline-offline:latest
```

That’s it.  
No LM Studio.  
No external model download.  
No Python install on host.  
No other app needed.

***

# STEP 11 — Deploy somewhere else (fully offline)

If you want to ship this to another machine **without rebuilding**, do this after a successful test:

## Option A — Ship image + models separately

### Export image

```bash
docker save asml-pipeline-offline:latest -o asml-pipeline-offline.tar
```

### On target machine

```bash
docker load -i asml-pipeline-offline.tar
```

Then run with the same `models/`, `input/`, `Data/` mounts.

***

## Option B — Bake models into the image

If you want **one single deliverable**, modify Dockerfile like this:

```dockerfile
COPY models/ /app/models/
```

Then rebuild:

```bash
docker build -t asml-pipeline-offline:bundle .
docker save asml-pipeline-offline:bundle -o asml-pipeline-offline-bundle.tar
```

Now the target machine only needs:

*   Docker
*   the image tar
*   input videos

This is the **best option for testers** if image size is acceptable.

***

# Why this plan fits your current codebase

Your current pipeline stages already separate nicely:

*   audio extraction from video via ffmpeg/ffprobe (extract_audio.py)
*   Whisper ASR with word timestamps (transcribe_batch.py)
*   transcript cleaning (clean_transcript.py)
*   LLM-based structuring and boundary detection through an OpenAI-like HTTP interface (structure_batch.py), (structure_batch_2.py)
*   semantic segmentation that can run without embeddings model (semantic_segmentation.py)
*   timestamp alignment against Whisper word timestamps (timestamp_alignment.py)
*   report comparison across methods (compare_reports.py)

So instead of rewriting everything, we are just replacing **LM Studio** with a **containerized local server** and forcing every model load to come from **local disk**.

***

# Important practical notes

## 1) Do not use model names that trigger online downloads

For Whisper, **pass the local path**, not `"large-v3"` or `"medium.en"` by name.  
This is already supported by your `transcribe_batch.py` because the `--model` value is passed directly into `WhisperModel(...)`. (transcribe_batch.py)

✅ Good:

```bash
--model /app/models/whisper/medium.en
```

❌ Avoid:

```bash
--model medium.en
```

***

## 2) Prefer `structure_batch_2.py` over `clean_transcript.py --structure`

`clean_transcript.py` can also call the LLM endpoint, but `structure_batch_2.py` is cleaner for your full pipeline because it supports:

*   structure mode
*   boundary mode
*   retries
*   normalized output handling  
    all in one place. (structure_batch_2.py)

***

## 3) CPU-only testing is possible, but choose lighter models

If your tester has no GPU:

*   Whisper `medium.en` or even `small.en`
*   LLM 3B/4B instruct GGUF

If you choose a 7B GGUF + Whisper large-v3 on CPU, it will work, but it may be slow.

***

## 4) You can skip embeddings completely

Because of your TF-IDF fallback. (semantic_segmentation.py)

That is actually a nice advantage for your offline deployment.

***

# My recommended “best practical setup”

If you want the highest chance of success on random tester machines:

## Use this combination

*   **Whisper**: `medium.en` local folder
*   **LLM**: **3B or 4B instruct GGUF**
*   **Segmentation**: TF-IDF fallback only

This gives:

*   no external apps
*   only 2 local models
*   lighter RAM usage
*   easier offline shipping

***

Absolutely — I tailored this for **your exact setup**:

*   **Windows host**
*   **Docker Desktop**
*   **CPU-first**
*   **models mounted from host**
*   **process all videos in one folder**
*   **no external apps required**
*   **optional GPU passthrough hook exposed in the PowerShell runner** (but the bundled image is intentionally CPU-first for maximum portability/offline reliability)

Your current codebase already supports this direction well, because:

*   `extract_audio.py` uses `ffmpeg` / `ffprobe`, so those just need to exist inside the container.(extract_audio.py)
*   `transcribe_batch.py` passes the `--model` argument straight into `WhisperModel(...)`, which means you can point it to a **local Whisper model folder** instead of downloading anything at runtime. (transcribe_batch.py)
*   `structure_batch_2.py` already supports both **`--mode structure`** and **`--mode boundary`** through an OpenAI-compatible local endpoint, so replacing LM Studio with an in-container server is the cleanest fit. (structure_batch_2.py)
*   `semantic_segmentation.py` already falls back to **TF-IDF** if `sentence-transformers` is unavailable, so you do **not** need a third model for segmentation. (semantic_segmentation.py)

***

# Download the tailored bundle

I created a ready-to-use bundle with the Docker/Windows helper files for you here:

[Download the Windows Docker bundle]

It contains:

*   `Dockerfile`
*   `requirements.txt`
*   `.dockerignore`
*   `docker/entrypoint.sh`
*   `docker/start_local_llm.sh`
*   `docker/run_full_pipeline.sh`
*   `build_image.ps1`
*   `run_pipeline.ps1`
*   `README_DOCKER_WINDOWS.md`

***

# What this bundle is designed to do

This bundle is built around your existing pipeline behavior:

1.  extract audio/subtitles from all videos in a folder
2.  transcribe audio using a **local Whisper model path**
3.  clean transcripts
4.  structure transcripts with a **local LLM server inside Docker**
5.  detect boundaries using the same local server
6.  run semantic segmentation offline
7.  run timestamp alignment
8.  generate comparison reports (extract_audio.py, transcribe_batch.py, structure_batch_2.py, semantic_segmentation.py, asml_docker_windows_bundle.zip, timestamp_alignment.py)

***

# Exactly how to use it on your machine

## 1) Put the bundle files in your project root

After downloading the zip, extract it into the **root** of your project.

Your project should end up like this:

```text
project/
├─ Dockerfile
├─ requirements.txt
├─ .dockerignore
├─ build_image.ps1
├─ run_pipeline.ps1
├─ README_DOCKER_WINDOWS.md
├─ docker/
│  ├─ entrypoint.sh
│  ├─ start_local_llm.sh
│  └─ run_full_pipeline.sh
├─ scripts/
│  ├─ boundary_detection.py
│  ├─ clean_transcript.py
│  ├─ compare_reports.py
│  ├─ extract_audio.py
│  ├─ prompts.py
│  ├─ prompts_2.py
│  ├─ semantic_segmentation.py
│  ├─ structure_batch.py
│  ├─ structure_batch_2.py
│  ├─ timestamp_alignment.py
│  └─ transcribe_batch.py
├─ models/
│  ├─ whisper/
│  │  └─ medium.en/
│  └─ llm/
│     └─ model.gguf
├─ input/
└─ Data/
```

> Important: the zip I generated contains the **Docker + PowerShell helper files**.  
> You should copy **your existing Python pipeline scripts** into the `scripts/` folder shown above.

***

## 2) Put your current Python files into `scripts/`

Use the exact scripts you already uploaded:

*   `extract_audio.py`
*   `transcribe_batch.py`
*   `clean_transcript.py`
*   `semantic_segmentation.py`
*   `timestamp_alignment.py`
*   `compare_reports.py`
*   `structure_batch_2.py`
*   `prompts_2.py`
*   and the rest of your current pipeline files

I specifically wired the bundle so that:

*   transcription uses your existing `transcribe_batch.py` local-model support (transcribe_batch.py)
*   structuring + boundary detection use `structure_batch_2.py` because it already supports both modes cleanly (structure_batch_2.py)
*   segmentation remains offline without a separate embeddings model because TF-IDF fallback already exists in your script (semantic_segmentation.py)

***

## 3) Put your models in the mounted `models/` folder

## Whisper model

Place your **offline Whisper / CTranslate2** model here:

```text
models/whisper/medium.en/
```

Because your `transcribe_batch.py` sends the `--model` value directly into `WhisperModel(...)`, this local directory path will work without online download. (transcribe_batch.py)

## LLM model

Place your **offline GGUF instruct model** here:

```text
models/llm/model.gguf
```

This is used by the local OpenAI-compatible server started in the container, which is what `structure_batch_2.py` will call for both structuring and boundary detection. (structure_batch_2.py)

## Recommended model choices for your setup

Since you said **CPU**, I recommend:

*   **Whisper**: `medium.en`
*   **LLM**: a **3B–4B instruct GGUF**

That keeps the system realistic for Windows + Docker Desktop + offline usage.

And because `semantic_segmentation.py` already has TF-IDF fallback, you can keep this to **just 2 local models total**. (semantic_segmentation.py)

***

## 4) Put all input videos into `input/`

Your helper script is already tailored to process **all videos in the folder**, not one-by-one.

That fits your `extract_audio.py`, which accepts a file or directory and can iterate videos recursively. (extract_audio.py)

***

## 5) Build the Docker image

Open **PowerShell** in the project root and run:

```powershell
.\build_image.ps1
```

That script just runs:

```powershell
docker build -t asml-pipeline-offline:latest .
```

***

## 6) Run the full pipeline (CPU)

Still in PowerShell:

```powershell
.\run_pipeline.ps1
```

This will:

*   mount `input/` to `/workspace/input`
*   mount `Data/` to `/workspace/Data`
*   mount `models/` to `/app/models`
*   run in **CPU mode by default**
*   process **all videos** in the folder

The container then runs:

*   extraction → transcription → cleaning → structuring → boundary detection → segmentation → alignment → reporting, based on your existing scripts. (extract_audio.py, transcribe_batch.py, structure_batch_2.py, semantic_segmentation.py, asml_docker_windows_bundle.zip, timestamp_alignment.py)

***

# Optional GPU hook (as requested)

I also added this in the PowerShell wrapper:

```powershell
.\run_pipeline.ps1 -UseGpu
```

### What it does

*   checks whether `nvidia-smi` exists on the Windows host
*   if found, passes `--gpus all` to Docker
*   also sets:
    *   `WHISPER_DEVICE=cuda`
    *   `WHISPER_COMPUTE_TYPE=float16`
    *   `LLM_N_GPU_LAYERS=-1`

### Important caveat

The current bundle is intentionally a **CPU-first image** because you asked for a setup that is most likely to “just work” on Windows + Docker + offline.  
So this GPU switch is mainly a **forward-compatible hook** in the wrapper.

If you later want, I can make you a **real GPU image variant** (CUDA-based) for:

*   faster-whisper GPU
*   llama.cpp GPU offloading

For now, the version I gave you is the safer one for your current requirement.

***

# What the outputs will look like

After the run, everything will be written into `Data/`, including:

```text
Data/
├─ processed/
├─ transcripts_raw/
├─ transcripts_clean/
├─ transcripts_structured/
├─ transcripts_boundaries/
├─ transcripts_segmented/
├─ transcripts_aligned/
└─ reports/
```

That matches the output conventions already present in your scripts:

*   raw transcripts from `transcribe_batch.py` (transcribe_batch.py)
*   cleaned transcripts from `clean_transcript.py` (compare_reports.py)
*   structured and boundary outputs from `structure_batch_2.py` (structure_batch_2.py)
*   segmentation outputs from `semantic_segmentation.py` (semantic_segmentation.py)
*   aligned outputs from `timestamp_alignment.py` 
*   text comparison reports from `compare_reports.py` (timestamp_alignment.py)

***

# Why I tailored it this way for your machine

I chose this specific setup because it best matches your Windows + CPU + mounted-model requirement:

## CPU-first

Most portable for testers using only Docker Desktop.

## Mounted models

You said you want models **mounted**, not baked into image, which is a good choice because:

*   image stays smaller
*   you can swap local models without rebuild
*   you can prepare models once on an internet-enabled machine and move them internally

## All videos in a folder

Your extraction script already supports directory input and manifest-based processing, so the wrapper is built around that. (extract_audio.py), (transcribe_batch.py)

## No third model

Not needed because segmentation already has the offline TF-IDF fallback. (semantic_segmentation.py)

***

# One important recommendation

For this exact setup, I strongly recommend that you use:

*   `models/whisper/medium.en/`
*   `models/llm/model.gguf` as a **3B–4B instruct model**

That will give you the highest chance of success on a typical Windows laptop/desktop under Docker Desktop.

***

# Your exact next steps

## Minimal checklist

1.  Download the bundle: 
2.  Extract into your project root
3.  Copy your current `.py` files into `scripts/`
4.  Place your local models into:
    *   `models/whisper/medium.en/`
    *   `models/llm/model.gguf`
5.  Put all videos into `input/`
6.  Run:
    ```powershell
    .\build_image.ps1
    .\run_pipeline.ps1
    ```

***

If you want, I can do **one more tailored step** for you next:

### Option A — I give you the **exact final folder tree with copy-paste commands**

So you can set it up in 5 minutes.

### Option B — I help you choose the **best 2 offline models**

Based on your likely CPU RAM / speed constraints (for example: “16 GB RAM”, “32 GB RAM”, etc.).
