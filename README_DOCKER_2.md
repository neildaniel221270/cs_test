# Docker Setup — ASML Micro-Learning Pipeline

## Overview

This Docker setup runs the **entire pipeline** inside a single container with **no external applications** required. The tester only needs:

- **VS Code** (optional, for viewing code/results)
- **Docker Desktop** (Windows/Mac/Linux)

What runs inside the container:
| Component | What it replaces |
|---|---|
| `llm_server.py` (llama-cpp-python) | LM Studio |
| `faster-whisper` (local model files) | Whisper API / HuggingFace downloads |
| `sentence-transformers` (local model files) | HuggingFace downloads |
| `ffmpeg` | System ffmpeg install |

---

## Prerequisites

- **Docker Desktop** installed and running on Windows
- **Python 3.10+** installed locally (only needed for the one-time model download step)
- **Internet access to HuggingFace** — needed only once, during model download. After that everything runs offline.

---

## Step-by-Step Setup

### Step 1: Clone or copy the project

Make sure you have the full project directory with this structure:

```
project-root/
├── Data/
│   ├── raw_videos/          ← Put your .mp4 files here
│   ├── ASML Glossary.csv
│   └── references/          ← Optional WER reference .txt files
├── models/
│   ├── llm/                 ← GGUF model goes here
│   ├── whisper/             ← Whisper CT2 model goes here
│   └── embeddings/          ← Sentence-transformers model goes here
├── scripts/                 ← All Python pipeline scripts
├── docker/
│   ├── entrypoint.sh
│   ├── run_full_pipeline.sh
│   └── llm_server.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── setup_models.py
└── setup_models.ps1
```

### Step 2: Download models (one-time, requires internet)

> **Important:** This step must be done on a network that can reach `huggingface.co`. If you are on the ASML corporate network and it blocks HuggingFace, do this step at home or on a VPN first.

**Option A: Automatic download (recommended)**

Open a terminal in the project root and run:

```powershell
# Windows (PowerShell)
.\setup_models.ps1

# Or directly with Python (any OS)
pip install huggingface_hub
python setup_models.py
```

This downloads three models into `./models/`:

| Model | Size | Purpose |
|---|---|---|
| `Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf` | ~4 GB | LLM for transcript structuring |
| `Systran/faster-whisper-medium.en` | ~1.5 GB | Speech-to-text transcription |
| `sentence-transformers/all-MiniLM-L6-v2` | ~90 MB | Semantic segmentation embeddings |

**Option B: You already have models downloaded**

If you already have models (you mentioned you have 2), place them as follows:

```
models/
├── llm/
│   └── Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf   ← Your GGUF file
├── whisper/
│   ├── model.bin                                   ← CT2 format required!
│   ├── config.json
│   ├── tokenizer.json
│   ├── vocabulary.txt (or vocab)
│   └── ...
└── embeddings/
    └── all-MiniLM-L6-v2/
        ├── config.json
        ├── model.safetensors (or pytorch_model.bin)
        └── ...
```

> **Critical note about Whisper:** Your `medium.en.pt` file is in PyTorch format. `faster-whisper` needs the **CTranslate2 format** from `Systran/faster-whisper-medium.en`. You must download this — the `.pt` file will not work. Run:
> ```powershell
> python setup_models.py --skip_llm --skip_embedding
> ```

**Option C: Download manually on another machine**

If you can't run Python scripts, manually download from these URLs and place the files:

1. **Whisper CT2 model:** https://huggingface.co/Systran/faster-whisper-medium.en
   → Download the full repository → place contents in `models/whisper/`

2. **Embedding model:** https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
   → Download the full repository → place contents in `models/embeddings/all-MiniLM-L6-v2/`

3. **LLM GGUF:** https://huggingface.co/NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF
   → Download `Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf` → place in `models/llm/`

### Step 3: Verify models are in place

```powershell
python setup_models.py --verify_only
```

Expected output:
```
  ✓ LLM (GGUF): Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf (3913.0 MB)
  ✓ Whisper (CT2): model.bin (1533.0 MB)
  ✓ Embeddings: config.json (0.0 MB)

✓ All models present. Ready to build Docker image.
```

### Step 4: Add your video files

Place your `.mp4` (or `.mkv`, `.mov`, `.avi`, `.webm`) files in:

```
Data/raw_videos/
├── LMOS Introduction to the process.mp4
├── Scheduled Downs_The Happy Flow.mp4
├── Unscheduled downs_The Unhappy Flow.mp4
└── ... (any number of videos)
```

### Step 5: Build the Docker image

```powershell
# CPU-only build (recommended for most setups)
docker compose build

# GPU build (requires NVIDIA GPU + NVIDIA Container Toolkit)
# Edit docker-compose.yml first: set USE_GPU: "1"
# docker compose build
```

This takes 5–15 minutes depending on your internet speed (it downloads Python packages).

### Step 6: Run the pipeline

```powershell
# Process all videos through the full pipeline
docker compose up
```

This will:
1. Start the LLM server (loads the GGUF model into RAM — takes 30–60s)
2. Extract audio from all videos
3. Transcribe with Whisper
4. Clean transcripts (filler removal, glossary normalization)
5. Structure with LLM (extract steps, safety, tools, metadata)
6. Align timestamps
7. Run semantic segmentation

Output appears in your local `Data/` directories:
```
Data/
├── processed/audio_wav/         ← Extracted WAV files
├── transcripts_raw/             ← Whisper output (raw)
├── transcripts_clean/           ← Cleaned transcripts
├── transcripts_structured/      ← LLM-structured steps & metadata
├── transcripts_aligned/         ← Timestamp-aligned steps
└── transcripts_segmented/       ← Semantically segmented output (final)
```

---

## Common Operations

### Run again with new videos

Just add new `.mp4` files to `Data/raw_videos/` and run:
```powershell
docker compose up
```

The pipeline skips already-processed files by default.

### Force reprocessing

```powershell
docker compose run app pipeline
# The structure_batch step already uses --force
# To fully reprocess, delete the output directories first
```

### Interactive debugging

```powershell
# Open a shell inside the container
docker compose run app bash

# Inside the container, you can run individual scripts:
python3 /app/scripts/extract_audio.py --input /app/Data/raw_videos --help
python3 /app/scripts/transcribe_batch.py --help
```

### Run only the LLM server (for external use)

```powershell
docker compose run -p 1234:1234 app server
# Now you can call http://localhost:1234/v1/chat/completions from your host
```

### Run WER evaluation

```powershell
docker compose run app bash
# Inside container:
python3 /app/scripts/eval_wer.py \
    --ref_txt /app/Data/references/your_reference.ref.txt \
    --hyp_raw_json /app/Data/transcripts_raw/your_video.raw.json
```

---

## GPU Support (Optional)

If you have an NVIDIA GPU and want faster Whisper transcription:

1. Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

2. Edit `docker-compose.yml`:
```yaml
services:
  app:
    build:
      args:
        USE_GPU: "1"
    environment:
      - WHISPER_DEVICE=cuda
      - WHISPER_COMPUTE_TYPE=float16
      - USE_GPU=1
      - GPU_LAYERS=99
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

3. Rebuild: `docker compose build`

---

## Troubleshooting

### "LLM model not found"
Make sure your GGUF file is at `models/llm/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf`. If your file has a different name, update the `LLM_MODEL_PATH` in `docker-compose.yml`.

### "Whisper model directory is empty"
You need the CTranslate2 format, not the `.pt` file. Run `python setup_models.py --skip_llm --skip_embedding` to download it.

### LLM server takes too long to start
On CPU with a 7B Q4 model, loading takes 30–90 seconds. The entrypoint waits up to 240 seconds. If your machine is slow, this is normal.

### Out of memory
The pipeline needs roughly:
- ~4 GB RAM for the LLM (7B Q4_0)
- ~2 GB RAM for Whisper (medium.en)
- ~1 GB for everything else

Total: **~8 GB RAM minimum**, 16 GB recommended. Make sure Docker Desktop is configured with enough memory (Settings → Resources → Memory).

### Structure step produces empty skeletons
This means the LLM returned invalid JSON. Common fixes:
- Increase timeout: set `LLM_CONTEXT_SIZE=8192` in docker-compose.yml
- Reduce transcript length: the pipeline already truncates at 12K chars
- Try a different GGUF model (phi3-medium or mistral-7b-instruct work well)

### "No video files found"
Check that your videos are in `Data/raw_videos/` and have one of these extensions: `.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`.

---

## Architecture

```
┌─────────────────────────────────── Docker Container ───────────────────────────────┐
│                                                                                     │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐  │
│   │ extract_audio │────▶│  transcribe  │────▶│    clean     │────▶│  structure   │  │
│   │   (ffmpeg)    │     │  (Whisper)   │     │ (glossary +  │     │  (LLM JSON)  │  │
│   │              │     │              │     │  fillers)    │     │              │  │
│   └──────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘  │
│         ▲                                                                │          │
│   ┌─────┴─────┐                                                  ┌──────▼───────┐  │
│   │  Videos   │                                                  │   align      │  │
│   │ (mounted) │                                                  │ (timestamps) │  │
│   └───────────┘                                                  └──────┬───────┘  │
│                                                                         │          │
│   ┌───────────────┐                                              ┌──────▼───────┐  │
│   │  llm_server   │◀── /v1/chat/completions ──── structure_batch │   segment    │  │
│   │ (llama.cpp)   │                                              │ (embeddings) │  │
│   └───────────────┘                                              └──────────────┘  │
│         ▲                                                                           │
│   ┌─────┴─────┐                                                                    │
│   │ GGUF model│                                                                    │
│   │ (mounted) │                                                                    │
│   └───────────┘                                                                    │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```
