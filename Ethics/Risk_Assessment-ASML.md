# Risk Assessment & GDPR Considerations  
## AI-Powered Micro‑Learning System for Machine Maintenance (Prototype)

**Date:** 2026-02-23  
**Document version:** v0.3 (markdown)  

---

## 1) Document control

- **Project:** AI-Powered Micro‑Learning System for Machine Maintenance
- **Student:** Neil Ross Daniel (221270)
- **Company:** ASML
- **Company contacts:** Aditi Raool (Data Scientist), Christos Lazaridis (AI Scientist)
- **Duration:** 18 weeks — 12 Feb to 19 Jun 2026
- **Prepared by:** Neil Ross Daniel
- **Intended reviewers:** ASML Data Governance / DPO / Security / Project supervisors

---

## 2) Executive summary

This document identifies, assesses, and mitigates key risks for the prototype that:
1) transcribes maintenance training videos (ASR),
2) structures transcripts into step-level instructional segments (LLM),
3) aligns segments to timestamps,
4) indexes segments for retrieval (vector search / RAG), and
5) optionally assembles micro‑clips for demonstration.

Because the dataset is expected to be **machine-only content** with **AI voice**, personal‑data exposure is expected to be low; however, confidentiality/IP and safety risks remain material. The highest priority risks are:
- **Confidentiality & leakage** (local copies, logs, indexes, demo exposure)
- **Safety-critical incorrect guidance** (hallucinations / retrieval errors)
- **Data residency/region uncertainty** (cloud processing configuration)
- **Delivery risks** (SME time, evaluation dataset size)

---

## 3) Project overview (context)

### 3.1 Goal
Technicians currently spend time scrubbing long videos to find specific troubleshooting steps. The goal is to surface relevant **micro‑learning segments** (typically 1–2 minutes) from existing training footage for a given maintenance query.

### 3.2 In-scope pipeline (prototype)
- **ASR transcription** (Azure Speech-to-Text primary; Whisper benchmark).
- **LLM transcript structuring** into a schema (segment title, step-by-step actions, tool/part references, safety flags).
- **Timestamp alignment** back to source video timecodes.
- **Vector retrieval** using a segment index (Azure AI Search; local FAISS fallback for dev).
- **Evaluation framework** using metrics such as WER, Precision@5, Recall@10, NDCG@5, boundary F1.
- **Stretch (optional):** micro‑clip assembly (ffmpeg) + captions + templated safety overlay; simple UI (e.g., Gradio).

### 3.3 Out of scope
- Generating new synthetic training videos.
- Production-grade deployment and operational integration.
- Automated legal/compliance checking (beyond templated safety notices).

---

## 4) Data sources, handling & sharing model

### 4.1 Source of truth
- **Videos reside in SharePoint** (authoritative repository).

### 4.2 Development handling
- For development, a **local copy of a subset** will be created on an **ASML managed laptop**.
- Initial proof-of-concept scope: **~50 videos** to demonstrate feasibility.
- After deployment, the solution may process more videos; the system should be designed to scale without copying entire libraries locally.

### 4.3 Demonstrations / sharing
- Outputs are shared **only with the internal team and demo audience**.
- The **BUas supervisor will only view during a live demonstration**; no video/transcript data will be transferred to BUas.
- Demo sessions should use a **sanitized dataset subset** and controls to avoid recording/photography.

---

## 5) Risk assessment methodology

- **Likelihood (L):** 1 (Rare) … 5 (Almost certain)
- **Impact (I):** 1 (Minor) … 5 (Severe)
- **Risk score:** L × I
- **Priority bands:**
  - Low: 1–6
  - Medium: 7–12
  - High: 13–19
  - Critical: 20–25

Residual risk is recorded after planned mitigations.

---

## 6) Risk register

> **Legend:** Owner names are placeholders; align with ASML roles (Security, Data Governance, DPO, SMEs).

| ID | Risk | Category | L | I | Score | Key mitigations | Owner | Residual |
|---:|------|----------|---:|---:|------:|----------------|-------|---------:|
| R1 | Unexpected personal data appears in video (names on screen, reflections, metadata) and is processed without adequate basis/notice | GDPR & privacy | 2 | 4 | 8 | Sampling check; exclude/redact if found; document lawful basis for internal training processing; consult DPO if scope changes | Project lead + DPO | 4 |
| R2 | Biometric / special-category risk if identity recognition is introduced (speaker/face ID) | GDPR & privacy | 1 | 5 | 5 | Keep identity out of scope; no speaker/face ID; avoid storing biometric templates/embeddings for identification | Project lead + Security | 2 |
| R3 | Confidential content leakage via prompts, logs, telemetry, vector index, or misconfigured access | Security & confidentiality | 3 | 5 | 15 | RBAC least privilege; encryption; reduce/disable content logging; redact prompts; index only necessary segments; monitoring + incident response | Security + Project lead | 8 |
| R4 | Data residency / cross-border processing risk (Azure region not confirmed) | GDPR & vendor | 3 | 4 | 12 | Confirm approved tenant + region (prefer EU if required); verify processor terms/DPA; document transfer assessment if applicable | IT/Legal + DPO | 6 |
| R5 | Unsafe/incorrect guidance surfaced due to hallucination, segmentation errors, or retrieval false positives | Safety & quality | 3 | 5 | 15 | Human-in-the-loop review for demos; show provenance + timestamps; templated safety banner; conservative thresholds; allow “no result” | SMEs/Safety + Project lead | 9 |
| R6 | ASR accuracy insufficient leading to poor retrieval | Technical/ML | 3 | 4 | 12 | Benchmark; domain vocab adaptation; post-processing; measure WER on annotated sample; tune pipeline | Project lead | 8 |
| R7 | Timestamp alignment drift produces wrong clips | Technical/ML | 3 | 4 | 12 | Alignment validation; tolerance windows; preview clips; fallback to longer context; manual correction for eval set | Project lead | 7 |
| R8 | Prompt injection / malicious query causes leakage of unrelated content | Security/AI | 2 | 5 | 10 | ACL filtering; content tags; do not pass raw retrieved text blindly to LLM; system prompt hardening; audit logs | Security + Project lead | 6 |
| R9 | Insufficient SME time for labeling/review impacts evaluation quality and schedule | Project delivery | 4 | 3 | 12 | Agree minimum labeled set early; schedule review blocks; prioritize samples; stage deliverables (Goal 1–3) | Stakeholders + Project lead | 8 |
| R10 | Retention/deletion for transcripts/embeddings/indexes not defined (data kept too long) | Governance | 3 | 4 | 12 | Define retention; keep raw videos only in SharePoint; purge intermediates; document deletion steps | Data owner + Project lead | 6 |
| R11 | Local dev copy on laptop increases exposure (loss/theft, sync/backups, accidental sharing) | Security & confidentiality | 2 | 5 | 10 | Managed ASML laptop; full-disk encryption; approved encrypted folder; minimal subset; no removable media; delete after use; track copies | Security/IT + Project lead | 5 |
| R12 | Demo exposure (screen recording/photography, accidental display of SharePoint paths/filenames) | Operational confidentiality | 3 | 4 | 12 | Disable recording; “no recording” reminder; watermark; sanitized demo data; avoid showing URLs/paths; controlled environment | Project lead | 6 |

---

## 7) GDPR & privacy considerations (video data)

### 7.1 Data categories & likelihood of personal data
- Expected content: **machine maintenance visuals + AI voice**, so direct personal data is unlikely.
- Still, **verify via sampling** (check overlays, metadata, reflections, screen captures).
- If personal data is present, treat it as personal data under GDPR and apply minimisation/redaction.

### 7.2 Roles and lawful basis (to be confirmed with ASML)
- Typical model: ASML acts as **Controller** for internal training materials; cloud services act as **Processors** under contract.
- Select and document a lawful basis (commonly **legitimate interests** or **contract necessity** for internal training/knowledge management, depending on ASML’s internal governance).
- Record the processing activity (purpose, categories of data, systems, recipients).

### 7.3 DPIA screening
A **DPIA screening** is recommended because the project uses new technologies (ASR/LLMs) and automated analysis at non-trivial scale. If screening indicates “likely high risk” (e.g., unexpected special-category data, large scale, or significant effects), perform a full DPIA with the DPO.

### 7.4 Privacy-by-design controls
- **Minimise**: process only the subset needed for evaluation (50 videos initially).
- **Avoid identity processing**: no speaker/face recognition; do not store biometric templates.
- **Retention**: define how long transcripts, embeddings and indexes are kept; periodically purge intermediates.
- **Access control**: enforce least privilege on SharePoint, storage, and search index.

### 7.5 Security (risk-based)
- Local: managed ASML device, full-disk encryption, approved encrypted storage location, and removal of local copies after use.
- Cloud: encryption at rest/in transit, private networking where available, RBAC/MFA, and audit logging.
- LLM/RAG: limit logging of prompts/outputs; redact confidential text in debugging artifacts.

### 7.6 Demo governance
- Use a sanitized demo subset.
- Disable recording; ask participants not to photograph the screen.
- Avoid showing SharePoint URLs, full filenames, or internal paths.

---

## 8) Required checks and sign-off gates

### Gate A — Data sanity check (before scaling beyond initial set)
- Sampling check completed and documented (confirm no personal data; or list mitigation if found).

### Gate B — Cloud configuration confirmation
- Confirm Azure region / data residency for Speech-to-Text, Azure OpenAI, and AI Search.

### Gate C — Safety validation for any clip outputs
- Any assembled micro‑clips shown in demos should be reviewed by SMEs/safety where feasible.

---

## 9) Approvals

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Student |  |  |  |
| ASML Contact |  |  |  |
| Data Governance / DPO |  |  |  |
| BUas Supervisor (view-only demo) |  |  |  |
