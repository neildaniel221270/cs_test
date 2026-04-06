# Sprint 3 — Baseline Pipeline Part 1: ASR Transcription

**Phase:** 3 — Data Exploration and Baseline Pipeline Development  
**Weeks:** 5–6 · **Dates:** 12 Mar – 25 Mar 2026  
**Incremental Goal:** Working toward Goal 1

---

## Sprint Objective

> Get the ASR pipeline working end-to-end: extract audio from training videos, run Whisper transcription, evaluate transcript quality, and build a cleaning pipeline.

---

## Tasks

| # | Task | Status | Due | Notes |
|---|---|---|---|---|
| 3.1 | Write audio extraction script (mp4 → wav) | ✅ Done | 13 Mar | Handle different video formats, batch processing |
| 3.2 | Run Whisper large-v3 on 5–10 sample videos | ✅ Done | 17 Mar | Save raw transcripts with word-level timestamps |
| 3.3 | Evaluate ASR quality (calculate WER) | ✅ Done | 19 Mar | Manually check 2–3 transcripts, use jiwer library |
| 3.4 | Handle domain-specific vocabulary | ✅ Done | 21 Mar | Test prompt engineering, post-processing for ASML terms |
| 3.5 | Build transcript cleaning pipeline | ✅ Done | 24 Mar | Remove fillers, fix ASR errors, normalize → clean JSON |
| 3.6 | Weekly check-in with supervisor | ✅ Done | 25 Mar | Share ASR results and WER findings |

**Status key:** ⬜ Not Started · 🔄 In Progress · ✅ Done · ⛔ Blocked

**Tools needed:** FFmpeg, OpenAI Whisper (large-v3), Python, GPU, jiwer, spaCy, regex, Jupyter Notebook  
**People involved:** NR, KR, SME (for vocabulary)

---

## Research Notes

_Capture any new findings about ASR optimization, Whisper configuration, or domain adaptation._

### Source 1: [Title]
- **Authors / Year:**
- **Key Findings:**
- **How it applies to your project:**
- **Limitations:**

---

## Meeting Notes

### Meeting: Weekly Supervisor Check-in
- **Date:**
- **Attendees:** NR, KR
- **Agenda:**
  1. ASR results overview
  2. WER scores and problem areas
  3. Domain vocabulary challenges
  4. Plan for LLM structuring (next sprint)
- **Key Decisions:**
  -
- **Action Items:**
  - [ ] [Person] — [Action] — by [Date]
- **Notes:**

---

## Development Log

### [Date] — Audio Extraction Script
- **Goal:** Extract audio from all training videos in batch
- **What you did:**
- **Result:**
- **Issues / Blockers:**
- **Next step:**

### [Date] — Whisper Transcription
- **Goal:** Transcribe sample videos with word-level timestamps
- **What you did:**
- **Whisper config:** (model size, language, beam size, etc.)
- **Result:**
- **Issues / Blockers:**
- **Next step:**

### [Date] — WER Evaluation
- **Goal:** Measure transcription accuracy
- **What you did:**
- **Result:**
- **Issues / Blockers:**
- **Next step:**

### [Date] — Domain Vocabulary Handling
- **Goal:** Improve ASR accuracy for ASML-specific terms
- **What you did:**
- **Terms that Whisper gets wrong:** (list them)
- **Correction approach:**
- **Result:**
- **Next step:**

### [Date] — Cleaning Pipeline
- **Goal:** Build automated transcript cleaning
- **What you did:**
- **Result:**
- **Issues / Blockers:**
- **Next step:**

---

## Experiment Tracking

| Experiment | Config / Parameters | Metric | Result | Notes |
|---|---|---|---|---|
| Whisper base run | large-v3, beam=5, lang=en | WER | | |
| Whisper with prompt | large-v3 + initial prompt with ASML terms | WER | | |
| Post-processing corrections | regex + custom dict | WER improvement | | |
| | | | | |

---

## Evaluation Results

| Metric | Target | Achieved | Pass? | Notes |
|---|---|---|---|---|
| WER (overall) | < 5% | | | |
| WER (technical terms) | — | | | Track separately |
| Transcripts generated | All sample videos | | | |

---

## ASML Vocabulary List

_Track domain-specific terms that Whisper struggles with._

| Correct Term | What Whisper Outputs | Fix Applied |
|---|---|---|
| | | |
| | | |
| | | |

---

## Feedback Received

| Date | From | Feedback | Action Taken |
|---|---|---|---|
| | KR | | |
| | SME | | |

---

## Risk Updates

| Risk | Status | Mitigation Applied |
|---|---|---|
| Poor audio quality in videos | 🟡 Monitoring | |
| ASML terms not recognized | 🟡 Monitoring | |
| GPU not fast enough | 🟡 Monitoring | |

---

## Sprint Retrospective

### What went well?
-

### What could be improved?
-

### What will I do differently next sprint?
-

### Key learning this sprint
-

---

## Deliverables Checklist

- [ ] Audio extraction script (working, tested)
- [ ] Raw transcripts for all sample videos
- [ ] WER evaluation report
- [ ] Domain vocabulary list + corrections
- [ ] Transcript cleaning pipeline
- [ ] Worklog updated
- [ ] Learning Log updated

---

## Hours Log

| Date | Hours | Activity |
|---|---|---|
| | | |
| | | |
| | | |
| | | |
| | | |
| **Total** | **0** | |
