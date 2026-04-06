# Sprint 4 — Baseline Pipeline Part 2: LLM Structuring ✅ GOAL 1

**Phase:** 3 — Data Exploration and Baseline Pipeline Development (continued)  
**Weeks:** 7 · **Dates:** 26 Mar – 1 Apr 2026  
**Incremental Goal:** 🎯 Goal 1 — Extract and structure spoken maintenance instructions

---

## Sprint Objective

> Use LLMs to transform raw transcripts into structured, step-by-step maintenance instructions. Validate quality with SMEs and achieve Goal 1.

---

## Tasks

| # | Task | Status | Due | Notes |
|---|---|---|---|---|
| 4.1 | Design LLM structuring prompts | ✅ Done | 27 Mar | Raw transcript → structured steps (Step 1: Remove panel cover, etc.) |
| 4.2 | Run LLM structuring on all transcripts | ✅ Done | 28 Mar | Process all cleaned transcripts, save as JSON |
| 4.3 | SME evaluation of structured output | 🔄 In Progress | 29 Mar | Have SME review 3–5 transcripts for correctness |
| 4.4 | Iterate on prompts based on feedback | ⛔ Blocked | 30 Mar | Improve prompts, re-run on problem cases |
| 4.5 | Document Goal 1 results | 🔄 In Progress | 31 Mar | Write up ASR pipeline + structuring approach + evaluation |
| 4.6 | Stakeholder demo | ✅ Done | 1 Apr | Show AR/CL the structured transcripts |

**Status key:** ⬜ Not Started · 🔄 In Progress · ✅ Done · ⛔ Blocked

**Tools needed:** GPT-4 / Claude API, Python, Jupyter Notebook, Word/Markdown  
**People involved:** NR, SME, AR, CL, KR

---

## Research Notes

_Capture findings about prompt engineering for transcript structuring._

### Source 1: [Title]
- **Authors / Year:**
- **Key Findings:**
- **How it applies to your project:**
- **Limitations:**

---

## Meeting Notes

### Meeting: SME Review Session
- **Date:**
- **Attendees:** NR, SME
- **Agenda:**
  1. Walk through 3–5 structured transcripts
  2. Are the steps correct and complete?
  3. Anything missing or misinterpreted?
  4. Is the level of detail right for technicians?
- **Key Decisions:**
  -
- **Action Items:**
  - [ ] [Person] — [Action] — by [Date]
- **Notes:**

### Meeting: Stakeholder Demo — Goal 1
- **Date:**
- **Attendees:** NR, AR, CL
- **Agenda:**
  1. Demo the ASR → cleaning → LLM structuring pipeline
  2. Show structured output format
  3. Discuss feedback and next steps (timestamp alignment)
- **Key Decisions:**
  -
- **Action Items:**
  - [ ] [Person] — [Action] — by [Date]
- **Notes:**

---

## Development Log

### [Date] — Prompt Design
- **Goal:** Create prompts that reliably structure transcripts into maintenance steps
- **Prompt version:** v1
- **Prompt text:** (paste your prompt here)
- **Result:**
- **Issues / Blockers:**
- **Next step:**

### [Date] — Prompt Iteration
- **Goal:** Improve based on SME feedback
- **Prompt version:** v2
- **Changes made:**
- **Result:**
- **Next step:**

### [Date] — Batch Processing
- **Goal:** Run structuring on all transcripts
- **What you did:**
- **Result:**
- **Issues / Blockers:**
- **Next step:**

---

## Experiment Tracking

| Experiment | Config / Parameters | Metric | Result | Notes |
|---|---|---|---|---|
| Prompt v1 | GPT-4 / Claude, temp=0.3 | SME accuracy rating | | |
| Prompt v2 (post-feedback) | GPT-4 / Claude, temp=0.3 | SME accuracy rating | | |
| | | | | |

---

## Prompt Version Log

_Keep track of your prompt iterations._

### Prompt v1
```
[Paste your prompt here]
```
**Result:** 
**SME Feedback:**

### Prompt v2
```
[Paste improved prompt here]
```
**Result:**
**SME Feedback:**

---

## Evaluation Results

| Metric | Target | Achieved | Pass? | Notes |
|---|---|---|---|---|
| Steps correctly identified | > 90% | | | Based on SME review |
| Steps in correct order | > 95% | | | |
| No hallucinated steps | 0 | | | |
| All transcripts processed | 100% | | | |

---

## Feedback Received

| Date | From | Feedback | Action Taken |
|---|---|---|---|
| | SME | | |
| | AR / CL | | |
| | KR | | |

---

## Risk Updates

| Risk | Status | Mitigation Applied |
|---|---|---|
| LLM hallucinates steps | 🟡 Monitoring | |
| API rate limits / cost | 🟡 Monitoring | |

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

## 🎯 Goal 1 Assessment

- [ ] ASR transcripts generated for all sample videos
- [ ] Transcripts cleaned and normalized
- [ ] LLM successfully structures transcripts into maintenance steps
- [ ] SME validates step correctness
- [ ] **GOAL 1 ACHIEVED: Spoken instructions extracted and structured (without timestamps)**

---

## Deliverables Checklist

- [ ] LLM structuring prompts (documented)
- [ ] Structured transcripts for all videos (JSON)
- [ ] SME evaluation notes
- [ ] Goal 1 write-up (method + results)
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
