#  **Evaluation Framework: Metrics per Goal Stage**

Below is the final consolidated evaluation schema.

***

# **Goal 1 — Transcript Extraction & Structuring**

**Scope:** Video ingestion → ASR transcription → normalization → LLM transcript structuring → semantic segmentation (text-only)

### **1. Video Ingestion & Cataloging**

| What to evaluate                    | Metric                   | How to measure                                                         |
| ----------------------------------- | ------------------------ | ---------------------------------------------------------------------- |
| **Completeness of video ingestion** | Ingestion success rate   | % of videos correctly processed + stored with stable video\_id         |
| **Metadata correctness**            | Metadata integrity score | Automated validation: duration match, fps match, file hash consistency |

### **2. ASR Transcription (Azure Speech primary)**

| Metric                        | Target                   | Measurement                                                    | Source                                                                                                                                                                                               |
| ----------------------------- | ------------------------ | -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **WER (Word Error Rate)**     | ≤ **10%** (stretch ≤ 5%) | Compare ASR output to SME-created transcripts for ≥20 segments |   |
| **SER (Sentence Error Rate)** | Informational            | Sentence-level alignment accuracy                              | —                                                                                                                                                                                                    |
| **ASR Runtime**               | n/a (recorded)           | Seconds of compute per minute of video                         | —                                                                                                                                                                                                    |

### **3. ASR Benchmark Mode (Whisper Large-v3)**

| Metric                     | Description                                                                  |
| -------------------------- | ---------------------------------------------------------------------------- |
| **Relative WER Delta**     | Whisper WER – Azure WER (to determine fallback value)                        |
| **Stability Across Noise** | Compare WER across "clean", "moderate noise", "machine-in-operation" samples |

### **4. Transcript Normalization (Punctuation / ITN)**

| Metric                   | Definition                                              | Method                        |
| ------------------------ | ------------------------------------------------------- | ----------------------------- |
| **Punctuation Accuracy** | % punctuation tokens matching human-annotated reference | Random sample of 50 sentences |
| **ITN Error Rate**       | Error in numbers/units normalization                    | Compare to ground truth       |

### **5. LLM Structuring to Segment Schema**

(Title, steps, tools/parts, safety flags)

| Metric                         | Definition                                             | Method            |
| ------------------------------ | ------------------------------------------------------ | ----------------- |
| **Schema Validity Rate**       | % segments that pass JSON schema validation            | Automated         |
| **Instructional Completeness** | SME-rated (0–2)                                        | 10% sample review |
| **Safety-Flag Recall**         | # actual safety notices captured / total in SME labels | SME labeling      |

### **6. Semantic Segmentation (Topic Boundaries)**

| Metric                      | Target                                  | Method                                             |                                                                                                                                                                                                      |
| --------------------------- | --------------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Boundary F1**             | ≥ **0.6**                               | Boundary match within ±30s tolerance vs SME labels |   |
| **Over-segmentation rate**  | # predicted boundaries > SME boundaries | Compute diff                                       |                                                                                                                                                                                                      |
| **Under-segmentation rate** | # predicted < SME                       | Compute diff                                       |                                                                                                                                                                                                      |

***

# **Goal 2 — Timestamp Alignment**

**Scope:** Align structured segments → timecodes from ASR (Whisper timestamps)

### **Timestamp Alignment Metrics**

| Metric                       | Target                                 | Method                                      |
| ---------------------------- | -------------------------------------- | ------------------------------------------- |
| **Timestamp Error (sec)**    | ≤ 5–10s median, ≤15s max tolerance     | Compare predicted vs SME-defined boundaries |
| **Alignment Coverage**       | ≥ 90% of segments have valid start/end | Automatic                                   |
| **Boundary F1 (time-aware)** | ≥0.6 F1                                | SME ground truth                            |

### **Video-to-text temporal consistency**

| Metric                         | Definition                                                |
| ------------------------------ | --------------------------------------------------------- |
| **Drift Rate**                 | Segment timestamp drift from transcript over longer clips |
| **Clip Playability Pass Rate** | SME checks that clipped video reflects whole segment      |

***

# **Goal 3 — Retrieval System**

**Scope:** Vector index, semantic reranking, query → segment ranking, evaluation suite

### **Retrieval Effectiveness**

(From NFRs + Success Metrics)

| Metric             | Target                     | Description                           | Source                                                                                                                                                                                               |
| ------------------ | -------------------------- | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Precision\@5**   | ≥ **0.70** (stretch ≥0.80) | Relevance of top 5                    |   |
| **Recall\@10**     | ≥ **0.60**                 | % of all relevant segments retrieved  |   |
| **NDCG\@5**        | ≥ **0.70**                 | Ranking quality with graded relevance |   |
| **MRR (Optional)** | n/a                        | Ease of surfacing first relevant hit  | Industry standard                                                                                                                                                                                    |

### **Retrieval Performance**

| Metric                               | Target             | Description                      |                                                                                                                                                                                                      |
| ------------------------------------ | ------------------ | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Query Latency (p95)**              | ≤ 10 seconds       | End-to-end query → top-5 results |                                                                                                                                                                                                      |
| **Time-to-first-result (TFR)**       | ≤ 5 seconds        | Rendering speed in UI            |                                                                                                                                                                                                      |
| **Index Build Rate**                 | ≥ 200 segments/min | Azure AI Search index build      |   |
| **Incremental Index Update Latency** | ≤ 15 min           | After reprocessing segments      |                                                                                                                                                                                                      |

### **Explainability / Debugging**

| Metric                             | Description                                       |
| ---------------------------------- | ------------------------------------------------- |
| **Explanation coverage**           | % results with available "why matched" metadata   |
| **Top-match similarity stability** | Track cosine distance distribution across updates |

***

# **Goal 4 — Micro-Clip Assembly (Stretch)**

**Scope:** Clip extraction → concatenation → captioning → safety overlays

### **Clip Extraction Quality**

| Metric                           | Target                      | Method                          |                                                                                                                                                                                                      |
| -------------------------------- | --------------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Clip Extraction Success Rate** | ≥ 95%                       | ffmpeg successful cut           |   |
| **Temporal Accuracy**            | ≤ ±2 sec from target        | Compare cut times vs timestamps |                                                                                                                                                                                                      |
| **Clip Rendering Time**          | ≤ 30s (p95) for 5min source | Performance metric              |                                                                                                                                                                                                      |

### **Micro-Clip Assembly Coherence**

| Metric                            | Definition                    | Method                              |
| --------------------------------- | ----------------------------- | ----------------------------------- |
| **Instructional Coherence Score** | 0–2 SME rating                | Does the assembled clip make sense? |
| **Safety Overlay Coverage**       | 100% where safety flags exist | Automatic check                     |
| **Caption Accuracy**              | WER ≤10%                      | Compare captions to transcript      |

***

# **Cross-cutting Evaluation**

These apply across all stages.

### **Observability**

| Metric                | Description                            |
| --------------------- | -------------------------------------- |
| Latency p50 / p95     | Query + clip processes                 |
| Retrieval score drift | Detect regressions after model updates |
| ASR drift             | Compare WER week-over-week             |

### **Reliability**

| Metric                | Description                      |
| --------------------- | -------------------------------- |
| Failover Success Rate | Azure AI Search → FAISS fallback |
| Crash-free Runtime    | % sessions without UI crash      |

### **Quality & Safety**

| Metric             | Description                                    |
| ------------------ | ---------------------------------------------- |
| Hallucination rate | LLM outputs with steps not found in transcript |
| No-answer accuracy | Correctly refusing when similarity < threshold |

***

# 🔥 **One-Page Summary Table (Final Deliverable)**

| Pipeline Stage              | Key Metrics                                                  | Targets                |
| --------------------------- | ------------------------------------------------------------ | ---------------------- |
| **Video ingestion**         | Ingestion success, metadata integrity                        | 100% valid             |
| **ASR (Azure)**             | **WER**, SER                                                 | **≤10%**               |
| **ASR Benchmark (Whisper)** | Relative WER delta                                           | Azure better or tied   |
| **Normalization (ITN)**     | Punctuation accuracy, ITN error rate                         | Qualitative            |
| **LLM Structuring**         | Schema validity, SME instructional score, safety-flag recall | ≥95% valid schema      |
| **Semantic Segmentation**   | **Boundary F1**                                              | **≥0.60**              |
| **Timestamp Alignment**     | Time error, coverage                                         | Median ≤10s            |
| **Retrieval**               | **P\@5**, **R\@10**, **NDCG\@5**, MRR                        | **0.70 / 0.60 / 0.70** |
| **Retrieval latency**       | Query latency, TFR                                           | p95 ≤10s               |
| **Clip extraction**         | Success rate, cut accuracy                                   | ≥95%                   |
| **Micro-clip assembly**     | Coherence score, safety coverage                             | SME ≥1.5/2             |
| **Explainability**          | Explanation completeness                                     | ≥90%                   |
| **Monitoring**              | Drift detection                                              | Weekly                 |