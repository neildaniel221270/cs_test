# AI Content Development — Project Roadmap

**Student:** Neil Ross Daniel · **Company:** ASML  
**Supervisor:** Karna Rewatkar (BUas)  
**Company Contacts:** Aditi Raool, Christos Lazaridis  
**Duration:** 12 Feb 2026 → 19 Jun 2026 (18 weeks)

---

This project follows an **Azure‑first** approach in line with the project scope:

- **Primary:** Azure Speech‑to‑Text (ASR), Azure OpenAI (transcript structuring), Azure AI Search (vector retrieval).
- **Benchmark/Fallback:** Open‑source tools (e.g., Whisper large‑v3, FAISS/Chroma) are used only for benchmarking or local fallback where needed.

---

## Deployment / UI Target (SurvTube)

The prototype user experience will be delivered as a **chatbot feature on a SurvTube SharePoint page**, implemented as a **Copilot Studio agent deployed to SharePoint** and connected to the retrieval backend (Azure AI Search).

---

## Key People

| Abbreviation | Name | Role |
|---|---|---|
| **NR** | Neil Ross Daniel | Student / Project Lead |
| **KR** | Karna Rewatkar | BUas Supervisor |
| **AR** | Aditi Raool | ASML Principal Knowledge Management Architect |
| **CL** | Christos Lazaridis | ASML Knowledge Management Architect |
| **SME** | Subject Matter Expert(s) | Maintenance domain experts at ASML |
| **SR** | Safety Reviewer | ASML Safety / Governance |
| **VE** | Video Editor | ASML Content / Video team |

---

## Sprint Overview

| Sprint | Weeks | Dates | Phase | Goal |
|---|---:|---|---|---|
| 1 | 1–2 | 12 Feb – 25 Feb | Project Initiation | Scope locked; **Azure + SurvTube access confirmed** |
| 2 | 3–4 | 26 Feb – 11 Mar | Literature Review | Lit review + requirements + **baseline/stretch targets defined** |
| 3 | 5–6 | 12 Mar – 25 Mar | Baseline Pipeline (Part 1) | **Azure STT** ASR running; Whisper benchmark; first transcripts |
| 4 | 7 | 26 Mar – 1 Apr | Baseline Pipeline (Part 2) | **Goal 1 ✓** Structured transcripts (Azure OpenAI) |
| 5 | 8–9 | 2 Apr – 15 Apr | Timestamp Alignment (Part 1) | Timestamp alignment approach working |
| 6 | 10 | 16 Apr – 22 Apr | Timestamp Alignment (Part 2) | **Goal 2 ✓** Timestamped segments |
| 7 | 11–12 | 23 Apr – 6 May | Retrieval System (Part 1) | **Azure AI Search** retrieving relevant segments |
| 8 | 13 | 7 May – 13 May | Retrieval System (Part 2) | **Goal 3 ✓** Relevant segment identification |
| 9 | 14–15 | 14 May – 27 May | Micro‑Clip + SurvTube Chatbot | **Goal 4 ✓ (PoC)** Clips + **templated safety** + SharePoint chatbot |
| 10 | 16–17 | 28 May – 10 Jun | Evaluation & Documentation | Final eval using **baseline + stretch targets**; report writing |
| 11 | 18 | 11 Jun – 19 Jun | Delivery | Report submitted, presentation delivered |

---

## Sprint 1 — Project Initiation (Weeks 1–2: 12 Feb – 25 Feb)

**Phase 1 · Objective:** Lock scope, confirm data access, confirm Azure and SurvTube deployment prerequisites.

| # | Task | What to Do | Tools | People |
|---|---|---|---|---|
| 1.1 | Kickoff meeting with ASML | Meet AR + CL. Discuss expectations, data availability, access to training videos, compute resources. Take meeting notes. | Teams/Zoom, meeting notes template | NR, AR, CL |
| 1.2 | Meet BUas supervisor | Align on academic requirements, grading criteria (ILOs), check‑in schedule. | Teams/Zoom | NR, KR |
| 1.3 | Finalize project scope | Confirm what's in/out and the 4 goals; get sign‑off. | Word | NR, AR, KR |
| 1.4 | Confirm data access | Access to ASML training video library; file formats, durations, audio quality notes. | ASML systems, VPN | NR, AR, CL |
| 1.5 | Set up dev environment | Python repo + environment; notebook baseline to prototype pipeline. | Git, Python, VS Code, pip | NR |
| 1.6 | Risk & ethics assessment | Risk register v1 + GDPR/data governance notes. | Spreadsheet / Notion | NR |
| 1.7 | Create project management board | Kanban board; Worklog + Learning Log templates. | Jira/Trello/Notion | NR |
| 1.8 | Refine research question & sub‑questions | Finalize RQ + sub‑questions and how each maps to Goals 1–4. | Word | NR, KR |
| 1.9 | Confirm Azure service access | Confirm access/quotas for Azure Speech‑to‑Text, Azure OpenAI, Azure AI Search; document endpoints/auth + governance constraints. | Azure portal / internal process | NR, AR, CL |
| 1.10 | Confirm SurvTube deployment permissions | Confirm NR has write access to SurvTube site (required to deploy an agent to SharePoint); identify site owner/admin. | SharePoint | NR (+ site owner) |
| 1.11 | Confirm Copilot Studio environment | Confirm Copilot Studio availability and authentication approach (“Authenticate with Microsoft”) for SharePoint channel deployment. | Copilot Studio | NR, AR, CL |

**Sprint 1 Deliverables:** Approved scope doc; risk register v1; dev environment ready; data + Azure + SurvTube access confirmed.

---

## Sprint 2 — Literature Review & Requirements (Weeks 3–4: 26 Feb – 11 Mar)

**Phase 2 · Objective:** Build theoretical foundation and define functional + non‑functional requirements and evaluation metrics.

| # | Task | What to Do | Tools | People |
|---|---|---|---|---|
| 2.1 | Collect & read core papers | 15–20 papers: microlearning, ASR, LLM structuring, retrieval/RAG, maintenance knowledge organization. | Google Scholar, Zotero | NR |
| 2.2 | Create annotated literature matrix | Citation + method + relevance + limitations. | Excel / Sheets | NR |
| 2.3 | Write literature review draft | 3–5 pages: microlearning, ASR, LLM structuring, retrieval approaches. | Word / Overleaf | NR |
| 2.4 | Define functional requirements | Inputs (free text/error code), outputs (ranked segments + timestamps), safety presentation rules. | Requirements doc | NR, AR, CL |
| 2.5 | Define non‑functional requirements (baseline + stretch) | Baseline + stretch targets (validated after early exploration): WER <10% (stretch <5%); Precision@5 >0.7 (stretch >0.8); Recall@10 >0.6; NDCG@5 >0.7; Segment boundary F1 >0.6 (±30s). | Requirements doc | NR, AR |
| 2.6 | Define evaluation framework | Metrics per goal + labeling plan with SMEs. | Spreadsheet | NR, KR |
| 2.7 | Stakeholder check‑in | Present requirements + evaluation plan. | Teams/Zoom | NR, AR, CL |
| 2.8 | Explore sample data | Inspect 3–5 videos; note audio issues and vocabulary. | VLC, Audacity, Python | NR |

**Sprint 2 Deliverables:** Lit matrix; lit review draft; requirements doc (incl. baseline/stretch targets); evaluation framework.

---

## Sprint 3 — Baseline Pipeline Part 1 (Weeks 5–6: 12 Mar – 25 Mar)

**Phase 3 · Objective:** Get ASR working and produce first transcripts (Azure primary).

| # | Task | What to Do | Tools | People |
|---|---|---|---|---|
| 3.1 | Extract audio from videos | Script to extract audio tracks (mp4 → wav). | FFmpeg, Python | NR |
| 3.2 | Run ASR on sample videos (Azure primary; Whisper benchmark) | Transcribe 5–10 videos using Azure Speech‑to‑Text (primary); run Whisper large‑v3 as benchmark/fallback on the same set; store consistent JSON outputs. | Azure Speech‑to‑Text; Whisper (benchmark); Python | NR |
| 3.3 | Evaluate ASR quality | Manual checks; compute WER using labeled segments where available. | Python (jiwer), manual review | NR |
| 3.4 | Handle domain‑specific vocabulary | Identify ASML terms; evaluate Azure STT customization options (if permitted) and/or post‑processing corrections; compare vs Whisper. | Azure Speech options; vocab list; Python | NR, SME |
| 3.5 | Build transcript cleaning pipeline | Remove filler, normalize formatting, output clean JSON. | Python, regex, spaCy | NR |
| 3.6 | Weekly check‑in | Share ASR findings and issues. | Teams/Zoom | NR, KR |
| 3.7 | Punctuation restoration / normalization | Apply punctuation restoration/ITN to improve downstream structuring and segmentation quality. | Azure Speech punctuation/ITN (primary) or post‑processing fallback | NR |

**Sprint 3 Deliverables:** Audio extraction script; transcripts (Azure STT primary + Whisper benchmark); WER report; cleaning + punctuation/ITN pipeline.

---

## Sprint 4 — Baseline Pipeline Part 2 (Week 7: 26 Mar – 1 Apr)

**Phase 3 continued · Objective:** Structure transcripts → **Goal 1** (Azure OpenAI primary).

| # | Task | What to Do | Tools | People |
|---|---|---|---|---|
| 4.1 | Design structuring prompts | Prompts to output schema: title, step actions, tool/part refs, safety flags. | Azure OpenAI (GPT‑4o or equivalent), Jupyter | NR |
| 4.2 | Run structuring on transcripts | Process cleaned transcripts through Azure OpenAI; save structured JSON. | Azure OpenAI, Python | NR |
| 4.3 | Evaluate structuring quality | SME review of 3–5 outputs. | Manual review | NR, SME |
| 4.4 | Iterate on prompts | Improve prompts based on SME feedback. | Azure OpenAI, Jupyter | NR |
| 4.5 | Document Goal 1 results | Write up method + evaluation. | Word / Markdown | NR |
| 4.6 | Stakeholder demo | Demo structured transcripts to AR/CL. | Teams/Zoom | NR, AR, CL |

**🎯 Goal 1 Achieved:** Spoken instructions extracted and structured into instructional segments (no temporal alignment yet).

---

## Sprint 5 — Timestamp Alignment Part 1 (Weeks 8–9: 2 Apr – 15 Apr)

**Phase 4 · Objective:** Align structured segments to timestamps.

| # | Task | What to Do | Tools | People |
|---|---|---|---|---|
| 5.1 | Use available timestamp outputs | Use timestamp granularity from ASR output; for fine‑grained word‑level alignment, use Whisper word timestamps as benchmark/fallback alignment aid. | Azure STT outputs; Whisper (benchmark); Python | NR |
| 5.2 | Implement semantic segmentation | Use embeddings to detect topic boundaries and refine segment splits. | sentence-transformers, Python | NR |
| 5.3 | Explore LLM boundary detection | Use Azure OpenAI to propose boundaries and validate against text. | Azure OpenAI, Jupyter | NR |
| 5.4 | Compare text-only vs multimodal (exploratory) | Keep as feasibility note only; text-first is primary. | Optional CLIP/LLaVA | NR |
| 5.5 | Build timestamp alignment module | Module producing start/end times per segment. | Python, JSON | NR |
| 5.6 | Weekly check‑in | Discuss early results. | Teams/Zoom | NR, KR |

**Sprint 5 Deliverables:** Alignment module; segmentation comparison; preliminary timestamped segments.

---

## Sprint 6 — Timestamp Alignment Part 2 (Week 10: 16 Apr – 22 Apr)

**Phase 4 continued · Objective:** Finalize timestamps → **Goal 2**.

| # | Task | What to Do | Tools | People |
|---|---|---|---|---|
| 6.1 | Evaluate timestamp accuracy | Manually check 5+ videos: do the segment boundaries match the actual visual content? Measure overlap accuracy. | VLC, Python, manual review | NR |
| 6.2 | Fine-tune segmentation | Adjust thresholds or prompts based on evaluation. Handle edge cases. | Python, Azure OpenAI | NR |
| 6.3 | SME validation of segments | SME watches videos and validates segment boundaries. | Video player, feedback form | NR, SME |
| 6.4 | Document Goal 2 results | Write up timestamp alignment method, evaluation, findings. | Word / Markdown | NR |
| 6.5 | Stakeholder check-in | Demo timestamped segments to AR/CL. | Teams/Zoom | NR, AR, CL |

**🎯 Goal 2 Achieved:** Timestamped instructional segments available for processed videos.

---

## Sprint 7 — Retrieval System Part 1 (Weeks 11–12: 23 Apr – 6 May)

**Phase 5 · Objective:** Build retrieval pipeline (Azure AI Search primary).

| # | Task | What to Do | Tools | People |
|---|---|---|---|---|
| 7.1 | Generate embeddings for all segments | Generate embeddings (Azure OpenAI embeddings preferred; sentence-transformers acceptable if needed) for each segment. | Azure OpenAI embeddings / sentence-transformers; Python | NR |
| 7.2 | Set up vector index (Azure AI Search primary) | Create Azure AI Search vector index + metadata fields; ingest segment docs (text, timestamps, IDs, metadata, embeddings). Keep FAISS/Chroma as fallback only. | Azure AI Search (primary); FAISS/Chroma (fallback) | NR |
| 7.3 | Build query processing | Convert query to embedding and pass to Azure AI Search; support text/error-code queries. | Azure OpenAI embeddings or sentence-transformers; Python | NR |
| 7.4 | Implement retrieval + ranking (Azure AI Search) | Query → embedding → Azure AI Search vector/hybrid retrieval → ranked segments with video IDs/URLs + timestamps. | Azure AI Search, Python | NR |
| 7.5 | Create test queries | 10–15 realistic queries with AR/SME input. | Spreadsheet | NR, AR, SME |
| 7.6 | Evaluate retrieval | Label relevance; compute Precision@5/Recall@10/NDCG@5. | Python scripts | NR |
| 7.7 | Weekly check-in | Discuss results. | Teams/Zoom | NR, KR |

**Sprint 7 Deliverables:** Azure AI Search index populated; retrieval working; initial metrics.

---

## Sprint 8 — Retrieval System Part 2 (Week 13: 7 May – 13 May)

**Phase 5 continued · Objective:** Optimize retrieval → **Goal 3**.

| # | Task | What to Do | Tools | People |
|---|---|---|---|---|
| 8.1 | Iterate on retrieval quality | Improve embedding choice; use hybrid search (keyword + vector) and metadata filters. | Azure AI Search hybrid + filters; optional BM25 | NR |
| 8.2 | Add metadata enrichment | Tag segments with machine type, error codes, tool requirements, safety flags; LLM can suggest tags. | Azure OpenAI, Python | NR |
| 8.3 | Re-evaluate improved pipeline | Measure improvements vs baselines. | Python | NR |
| 8.4 | Stakeholder validation | AR/CL qualitative feedback on top results. | Demo session | NR, AR, CL |
| 8.5 | Document Goal 3 results | Write retrieval approach + metrics. | Word / Markdown | NR |

**🎯 Goal 3 Achieved:** System identifies relevant segments for a maintenance query using Azure AI Search retrieval.

---

## Sprint 9 — Micro‑Clip Assembly + SurvTube SharePoint Chatbot (Weeks 14–15: 14 May – 27 May)

**Phase 6 · Objective:** Assemble micro‑clips, add captions, apply **templated safety notices**, and deploy a **SurvTube SharePoint chatbot** that returns ranked segments/clips as answers.

| # | Task | What to Do | Tools | People |
|---|---|---|---|---|
| 9.1 | Build video clip extraction | Script: video + timestamps → clip file. | FFmpeg, Python | NR |
| 9.2 | Assemble multi‑segment clips | Stitch segments into a micro‑clip with transitions when needed. | FFmpeg, MoviePy, Python | NR |
| 9.3 | Add captions/subtitles | Generate SRT and burn-in or attach subtitles. | FFmpeg, SRT | NR |
| 9.4 | Safety notes & metadata (templated) | Apply predefined safety templates triggered by safety flags/tags. LLM may suggest tags only; notice text is templated and SR/SME validated. No automated compliance checking. | Templates/rules; optional Azure OpenAI tagging; FFmpeg overlay | NR, SR |
| 9.5 | Safety review with reviewer | SR reviews 3–5 clips for correctness/completeness. | Video player, feedback form | NR, SR |
| 9.6 | Build Copilot Studio agent | Chatbot flow: accept query → call retrieval endpoint → return ranked segment cards (links/timestamps). | Copilot Studio | NR |
| 9.7 | Deploy agent to SurvTube SharePoint | Publish agent and deploy using the SharePoint channel to SurvTube (requires write access). | Copilot Studio SharePoint channel | NR (+ site owner if needed) |
| 9.8 | End‑to‑end integration test | 5 queries: SurvTube chatbot → retrieval → segments/clips returned → validate playback + metadata. | Full pipeline | NR |
| 9.9 | Stakeholder demo | Demo on SurvTube: question → ranked segments/clips as answers. | SurvTube SharePoint page | NR, AR, CL |

**🎯 Goal 4 Achieved (PoC):** Safety‑templated micro‑clips (and/or timestamped segment answers) delivered via the SurvTube SharePoint chatbot interface.

---

## Sprint 10 — Evaluation & Documentation (Weeks 16–17: 28 May – 10 Jun)

**Phase 7 · Objective:** Final evaluation + report.

| # | Task | What to Do | Tools | People |
|---|---|---|---|---|
| 10.1 | Full system evaluation (baseline + stretch) | Evaluate against targets: WER <10% baseline (<5% stretch); Precision@5 >0.7 baseline (>0.8 stretch); Recall@10 >0.6; NDCG@5 >0.7; Segment boundary F1 >0.6 (±30s). | Python, evaluation scripts | NR |
| 10.2 | Collect stakeholder feedback | AR/CL/SMEs try SurvTube chatbot; capture feedback forms. | SurvTube chatbot | NR, AR, CL, SME |
| 10.3 | Final iteration on system | Fix retrieval/UX; improve clip transitions; adjust templates. | Full stack | NR |
| 10.4 | Write graduation report | Full report structure. | Word / LaTeX | NR |
| 10.5 | Write technical documentation | Architecture + setup instructions + limitations. | Markdown / README | NR |
| 10.6 | Finalize Worklog & Learning Log | Complete weekly entries. | BUas template | NR |
| 10.7 | Supervisor review | KR feedback and iterations. | Word/email | NR, KR |
| 10.8 | Ethics & governance section | GDPR + responsible AI + safety validation approach. | Report | NR |

**Sprint 10 Deliverables:** Draft report; technical docs; complete logs; evaluation results vs baseline/stretch.

---

## Sprint 11 — Final Delivery (Week 18: 11 Jun – 19 Jun)

**Phase 8 · Objective:** Submit everything and present.

| # | Task | What to Do | Tools | People |
|---|---|---|---|---|
| 11.1 | Finalize graduation report | Apply supervisor feedback. Proofread. Format per BUas guidelines. | Word / LaTeX | NR |
| 11.2 | Prepare presentation slides | 15–20 slides: problem, approach, demo, results, conclusions. Include live demo plan. | PowerPoint | NR |
| 11.3 | Record demo video | 3–5 min screencast of the SurvTube chatbot + pipeline. | Screen recorder | NR |
| 11.4 | Practice presentation | Dry runs and Q&A prep. | Timer, notes | NR, KR |
| 11.5 | Submit deliverables | Submit report, code repo, presentation, Worklog, Learning Log. | BUas portal, Git | NR |
| 11.6 | Final presentation | Present + demo. | Projector, laptop | NR, KR, AR, CL |
| 11.7 | Handover to ASML | Share repo, docs, and recommendations with AR/CL. | Git, email | NR, AR, CL |

**Sprint 11 Deliverables:** Final report submitted, presentation delivered, project handed over.

---

## Risk Quick‑Reference

| Risk | Impact | Mitigation |
|---|---|---|
| Poor audio quality in training videos | ASR accuracy drops | Noise reduction + compare Azure STT vs Whisper benchmark; adjust preprocessing |
| ASML‑specific terminology not recognized | Wrong transcripts | Vocabulary list + post‑processing; evaluate Azure STT customization options if allowed |
| Azure access/quotas delayed | Schedule slip | Confirm Azure access in Sprint 1; keep open‑source fallback for local progress |
| Scope creep (multimodal too complex) | Schedule overrun | Text-first is primary; multimodal only as exploratory note |
| Safety review delays | Goal 4 delayed | Schedule SR sessions early in Sprint 9; rely on templated notices + SR validation |

---

## Tool Access Checklist (Updated)

A consolidated list of every tool referenced across all sprints.

| Tool | Category | First Needed | Access? |
|---|---|---:|---|
| Microsoft Teams | Communication | Sprint 1 | ✅ |
| Microsoft Word | Document Editing | Sprint 1 | ✅ |
| ASML Internal Systems (video library) | Data Access | Sprint 1 | ✅ |
| VPN | Network Access | Sprint 1 | ✅ |
| Git / GitHub | Version Control | Sprint 1 | ✅ |
| Python 3.10+ | Programming | Sprint 1 | ✅ |
| VS Code | IDE | Sprint 1 | ✅ |
| pip | Package Manager | Sprint 1 | ✅ |
| Excel | Spreadsheets | Sprint 2 | ✅ |
| GitHub Projects | Project Management | Sprint 1 | ✅ |
| LaTeX / Overleaf | Academic Writing | Sprint 2 | ✅ |
| VLC | Video Playback | Sprint 2 | ✅ |
| FFmpeg | Audio/Video Processing | Sprint 3 | ✅ |
| GPU (local or cloud) | Compute Resource | Sprint 3 | ✅ |
| jiwer | WER Evaluation | Sprint 3 | ✅ |
| spaCy | NLP / Text Processing | Sprint 3 | ✅ |
| noisereduce | Audio Cleaning | Sprint 3 | ✅ |
| Azure Speech‑to‑Text (Primary) | ASR | Sprint 3 | ☐ |
| Whisper large‑v3 (Benchmark/Fallback) | ASR | Sprint 3 | ✅ |
| Azure OpenAI (Primary) | Transcript Structuring | Sprint 4 | ☐ |
| Jupyter Notebook | Development | Sprint 3–4 | ✅ |
| sentence-transformers | Embeddings | Sprint 5 | ☐ |
| Azure AI Search (Primary) | Vector Index/Retrieval | Sprint 7 | ☐ |
| FAISS / ChromaDB (Fallback) | Local Retrieval | Sprint 7 | ☐ |
| BM25 (rank-bm25) | Keyword Search | Sprint 8 | ✅ |
| MoviePy | Video Editing | Sprint 9 | ✅ |
| Copilot Studio (SharePoint chatbot) | UI / Agent | Sprint 9 | ☐ |
| SurvTube SharePoint site | Deployment Target | Sprint 1/9 | ✅ |
| Figma / draw.io | UI Wireframing | Sprint 9 | ☐ |
| Screen Recorder | Demo Recording | Sprint 11 | ✅ |
| PowerPoint | Presentation | Sprint 11 | ✅ |
