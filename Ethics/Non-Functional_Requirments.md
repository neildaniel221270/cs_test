
# Non-Functional Requirements (NFRs)
**AI-Powered Micro‑Learning System for Machine Maintenance**  
**Date:** 2026-02-26

> This document defines *non-functional requirements* (NFRs) for the prototype system that extracts, segments, retrieves, and assembles micro‑clips from ASML maintenance training videos. Targets are aligned with the project’s Success Metrics and constraints.

---

## 1) Scope & Context
The NFRs cover the prototype pipeline end‑to‑end: **ASR transcription → transcript structuring → semantic segmentation → timestamp alignment → vector retrieval (RAG) → optional clip assembly → prototype UI**. Production hardening is out of scope, but NFRs below make the prototype **measurable, safe, and defensible** for stakeholder review.

**Assumptions**
- Primary stack: Azure Speech, Azure OpenAI (GPT‑4o), Azure AI Search; Whisper/FAISS as fallbacks.
- Data are confidential ASML training videos; access is restricted; no external sharing.
- Ground‑truth labels created with subject‑matter experts (SMEs).

---

## 2) Quality & Accuracy
### 2.1 ASR Quality
- **Word Error Rate (WER):** ≤ **10%** on a representative domain test set (stretch: ≤ **5%** with post‑processing).  
  **Measurement:** Manual annotation of ≥20 representative segments; compare ASR output to human transcripts.

**Rationale:** Reliable text is prerequisite for segmentation and retrieval. Lower WER improves downstream boundary detection and matching.

### 2.2 Retrieval Effectiveness
- **Precision@5:** ≥ **0.70** (stretch: ≥ **0.80**).  
- **Recall@10:** ≥ **0.60**.  
- **NDCG@5:** ≥ **0.70** using graded relevance (0–2).  
**Measurement:** Expert‑labeled test set of ≥30 realistic maintenance queries (binary/graded relevance).

**Rationale:** Technicians must see mostly relevant segments in the first results; P@5 and NDCG@5 track both relevance and ranking quality. Recall@10 ensures coverage of needed steps.

### 2.3 Segmentation Fidelity
- **Segment Boundary F1:** ≥ **0.60** against manual boundaries with a ±30s tolerance window.

**Rationale:** Accurate, stable boundaries are essential for extracting playable micro‑clips and for precise citations in RAG answers.

---

## 3) Performance & Responsiveness
### 3.1 Query Latency
- **End‑to‑end query → top‑5 results (no clip render):** **p95 ≤ 10 s**, **p50 ≤ 5 s** on reference hardware (standard ASML workstation + Azure services).  
- **Time‑to‑first‑result (TFR):** **≤ 5 s** at p95.

**Rationale:** Field users expect snappy search; long waits reduce trust and adoption.

### 3.2 Clip Operations
- **Clip extraction from known timestamps:** **p95 ≤ 30 s** per 5‑minute source video; throughput ≥ **2× real‑time** when batched.

**Rationale:** Enables quick creation of explainable snippets during demos without blocking the session.

### 3.3 Index Build / Refresh
- **Initial index build:** ≥ **200 segments/min** on the chosen SKU (document exact SKU in runbook).  
- **Incremental refresh latency:** new/edited segments visible in search **≤ 15 min**.

**Rationale:** Practical limits ensure iterative development and SME feedback cycles.

---

## 4) Reliability, Availability & Resilience
- **Prototype availability (demo/assessment windows):** ≥ **99.0%** during scheduled sessions.  
- **Graceful degradation:** if Azure AI Search is unavailable for >60 s, **automatically fail over** to local FAISS with a banner indicating degraded mode; results remain audit‑logged.  
- **Error handling:** no hard crashes in UI; user‑actionable error messages with retry guidance.

**Rationale:** Even as a prototype, stakeholders should experience stable behavior and transparent fallbacks.

---

## 5) Security, Privacy & Compliance
- **Access control:** Azure AD with role‑based access (Admin, Engineer/Annotator, Viewer).  
- **Data protection:** Encryption in transit (TLS 1.2+) and at rest (Azure Storage SSE).  
- **Data minimization:** Logs store **query hashes** and result IDs/scores, not raw confidential content.  
- **PII handling:** Transcripts must not retain personal identifiers; if detected, automatically **redact** before indexing.  
- **Data residency:** Store and process data in EU regions in line with ASML policy.  
- **Retention:** Raw logs retained ≤ **90 days**; datasets and model artifacts per ASML governance.

**Rationale:** Training videos may contain sensitive information; controls must meet corporate and regulatory expectations without impeding iteration.

---

## 6) Safety, Grounding & Risk Controls
- **Source‑grounding:** RAG responses **must cite** video segment IDs and timestamps; if **top score < threshold** (e.g., cosine < **0.35**), show **No Answer** with guidance to refine the query.  
- **Safety flags:** Segment schema carries **safety notices**; UI renders them prominently before playback.  
- **Hallucination guardrails:** No free‑form prescriptive steps may be shown **without** linked source clips or transcripts.

**Rationale:** Maintenance guidance must remain tied to vetted content; conservative behavior is safer than confident but ungrounded answers.

---

## 7) Observability & Quality Monitoring
- **Telemetry:** capture latency percentiles, retrieval scores, click‑through, and abandonment.  
- **Evaluation cadence:** re‑run the test suite **weekly** (or per major change); if **P@5 < 0.65** or **WER > 12%**, automatically **open an improvement task**.  
- **Model drift watch:** track embedding model and ASR performance deltas versus baseline; alert on significant change.

**Rationale:** Continuous visibility prevents silent regressions and supports data‑driven iteration.

---

## 8) Usability & Accessibility
- **Result explainability:** show **why** a result matched (matched terms/steps, confidence).  
- **Previewability:** quick transcript snippet and jump‑to‑timestamp; keyboard shortcuts for play/pause and seek.  
- **Accessibility:** color‑contrast AA, captions available for all clips.

**Rationale:** Technicians benefit from transparent results and fast skimming under time pressure.

---

## 9) Maintainability & Operability
- **Reproducible runs:** pipeline orchestrations are **scripted**; one‑command re‑build for index and evaluation suite.  
- **Versioning:** store **model versions, prompts, and dataset hashes** with each run; every retrieval log includes the active versions.  
- **Documentation:** a lightweight **runbook** covering setup, secrets, and failure modes.

**Rationale:** Clear ops hygiene is essential for a short, 18‑week project and smooth handover.

---

## 10) Portability & Extensibility
- **Cloud ↔ local parity:** All core steps have a documented local fallback (Whisper, FAISS) for offline development.  
- **Pluggable components:** embedding model and ranker are **interchangeable** behind an interface; adding a new model does not require reworking the UI.

**Rationale:** Enables benchmarking and future upgrades without lock‑in.

---

## 11) Cost & Efficiency
- **Budget guardrail:** track **cost/100 video minutes** (ASR + embedding + storage + search) and monthly total; alert if forecast exceeds **TBD € budget**.  
- **Compute efficiency:** prefer batch operations for ASR and embeddings; target GPU utilization **>60%** when available.

**Rationale:** Keeps the prototype economically defensible and highlights trade‑offs early.

---

## 12) Acceptance & Evidence
For each NFR above, the acceptance evidence is captured in the **Evaluation Notebook + metrics report** (precision/recall/NDCG curves, latency histograms) and **run logs** with model/prompt versions. A final **readout** summarizes whether targets were met and any deltas.

---

## Appendix A — Mapping to Project Success Metrics
These NFR targets for **WER, P@5, Recall@10, NDCG@5, Segment boundary F1** intentionally mirror the Success Metrics already agreed in scope, to keep a single source of truth for what “good” looks like.

## Appendix B — To‑Be‑Determined (TBD)
- Exact hardware/SKU for reference latency.  
- Final similarity threshold for “No Answer” after pilot labeling.  
- Monthly budget cap (€, owner).  
- Log retention exceptions for audit events, if required by policy.
