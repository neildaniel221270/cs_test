
# Local LLM Setup Guide (LM Studio) — for `clean_transcript.py --structure`

This guide shows how to run a **local** LLM using **LM Studio** and hook it up to
`clean_transcript.py` to generate the micro‑learning summaries/steps **without**
cloud APIs, admin rights, or corporate TLS certificates (the server runs on
`http://localhost`).

---
## 1) Install LM Studio (desktop app)

1. Download LM Studio for your OS from the official site: https://lmstudio.ai/home  
   (Windows, macOS, Linux)  
2. Launch LM Studio. No SSL/TLS or certificates are required for local use; you
   will be talking to `http://localhost:1234/v1` once the local server is on.

> LM Studio ships an **OpenAI‑compatible** local API on port **1234**
> (base URL `http://localhost:1234/v1`). You can reuse any OpenAI-style
> client by changing only the base URL.  
> **Docs:** OpenAI‑compatible endpoints and base URL examples.  
> – https://lmstudio.ai/docs/developer/openai-compat

If you don’t have admin rights on your laptop, LM Studio still works because it
runs entirely in user space and exposes a localhost HTTP server. (If your IT
policy blocks installer execution, install on a personal machine and copy the
installed folder to your user profile, or use LM Studio’s headless components
later when available.)

---
## 2) Get a local model in LM Studio

1. In LM Studio, open **Discover / Search** and download a compact **instruct**
   model (e.g., *Mistral 7B Instruct* or *Llama 3.x Instruct*).  
2. Wait until the download finishes; it will appear under **My Models**.

You’ll supply the **model identifier** exactly as shown by LM Studio when making
API calls (e.g., `mistralai/Mistral-7B-Instruct-v0.3`). The OpenAI‑compatible
API expects the LM Studio model id in the `model` field.  
**Docs:** “Use the model identifier from LM Studio here.”  
– https://lmstudio.ai/docs/developer/openai-compat

**Offline option:** On a machine with internet, you can also download via the
CLI and copy the model files across later:
```bash
# Example (download on a different computer)
lms get openai/gpt-oss-20b
```
Then move the downloaded files to your work laptop and **Load** them from LM
Studio.  
(See OpenAI’s cookbook article showing `lms get` and how LM Studio serves a
`/v1/chat/completions` endpoint locally.)

---
## 3) Start the LM Studio Local API server

- In LM Studio, go to **Developer / Local Server** ("Start server" toggle) and
  **start** the server.
- The default base URL is **`http://localhost:1234/v1`**.
- You can verify it’s running:

```bash
# List models exposed by the server
curl http://localhost:1234/v1/models
```

**Docs:**
- Local server & how to start it from the app: https://lmstudio.ai/docs/developer/core/server  
- OpenAI‑compatible endpoints and base URL: https://lmstudio.ai/docs/developer/openai-compat

> Tip: If you need to run on another port or machine, you can change the server
> settings in the LM Studio UI. Most corporate laptops will work fine with the
> default `localhost:1234` and no authentication.

---
## 4) Run the pipeline with LM Studio

### Clean only (no LLM)
```bash
python clean_transcript.py   --in_raw_json Data/transcripts_raw/vid1.raw.json   --out_clean_json Data/transcripts_clean/vid1.clean.json
```

### Clean **+ structure** using LM Studio’s local server
```bash
python clean_transcript.py   --in_raw_json Data/transcripts_raw/vid1.raw.json   --out_clean_json Data/transcripts_clean/vid1.clean.json   --structure   --lmstudio_model "mistralai/Mistral-7B-Instruct-v0.3"
```

If you changed the server address/port:
```bash
python clean_transcript.py ...   --structure   --lmstudio_url "http://localhost:1235/v1"
```

(Optional) If you enabled an API key in LM Studio:
```bash
python clean_transcript.py ...   --structure   --lmstudio_api_key "<your_local_key>"
```

---
## 5) Output verification

With `--structure`, the output JSON includes a `micro_learning` object with a
summary, steps, tools, safety warnings, etc., plus a
`"structuring": {"engine": "lmstudio"}` block and timestamps.

---
## Troubleshooting

**“Could not reach LM Studio”**  
Make sure the local server is running (Developer tab → Start server) and the URL
is correct (`http://localhost:1234/v1`). You can test with:
```bash
curl http://localhost:1234/v1/models
```

**Model too slow or out of memory**  
Use a smaller, quantized model (7B class); close memory‑heavy apps. GPU
acceleration helps but is optional.

**LLM returns invalid JSON**  
The script already retries once and falls back to a skeleton. You can try a
different instruction‑tuned model that’s strong at JSON extraction.

---
## Why this meets ASML laptop constraints

- **No corporate certificates** needed: the app speaks **HTTP on localhost** by
  default (`http://localhost:1234/v1`).  
- **No admin access** required at runtime: everything runs in **user space**.

**References**  
- OpenAI‑compatible endpoints and base URL (`http://localhost:1234/v1`, models,
  chat completions): https://lmstudio.ai/docs/developer/openai-compat  
- Starting the local server from the app: https://lmstudio.ai/docs/developer/core/server  
- Example of using `lms get` and local `/v1/chat/completions` in LM Studio:
  https://developers.openai.com/cookbook/articles/gpt-oss/run-locally-lmstudio
