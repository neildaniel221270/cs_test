# Sprint 8 — Retrieval System Part 2: Optimization ✅ GOAL 3

**Phase:** 5 — Retrieval and Relevance Modeling (continued)  
**Weeks:** 13 · **Dates:** 7 May – 13 May 2026  
**Incremental Goal:** 🎯 Goal 3 — Automatically identify relevant videos and segments

---

## Sprint Objective

> Optimize the retrieval pipeline with hybrid search, metadata enrichment, and stakeholder validation. Achieve Goal 3.

---

## Tasks

| # | Task | Status | Due | Notes |
|---|---|---|---|---|
| 8.1 | Iterate on retrieval quality | ⬜ Not Started | 9 May | Try hybrid search (BM25 + semantic), add metadata filters |
| 8.2 | Add metadata enrichment to segments | ⬜ Not Started | 10 May | Tag with: machine type, error codes, safety warnings, tools needed |
| 8.3 | Re-evaluate with improved pipeline | ⬜ Not Started | 11 May | Re-run test queries, measure Precision@5 / Recall@5 improvement |
| 8.4 | Stakeholder validation (AR/CL run queries) | ⬜ Not Started | 12 May | AR/CL run 5 queries, give qualitative feedback |
| 8.5 | Document Goal 3 results | ⬜ Not Started | 13 May | Write up retrieval approach, metrics, iterations |

**Status key:** ⬜ Not Started · 🔄 In Progress · ✅ Done · ⛔ Blocked

**Tools needed:** FAISS/ChromaDB, BM25 (rank_bm25), LLM API, Python, Jupyter Notebook  
**People involved:** NR, AR, CL, KR

---

## Research Notes

### Source 1: [Title]
- **Authors / Year:**
- **Key Findings:**
- **How it applies to your project:**
- **Limitations:**

---

## Meeting Notes

### Meeting: Stakeholder Validation — Retrieval Demo
- **Date:**
- **Attendees:** NR, AR, CL
- **Queries they tested:**
  1.
  2.
  3.
  4.
  5.
- **Qualitative feedback:**
  -
- **Key Decisions:**
  -
- **Action Items:**
  - [ ] [Person] — [Action] — by [Date]
- **Notes:**

---

## Development Log

### [Date] — Hybrid Search Implementation
- **Goal:** Combine keyword (BM25) + semantic search
- **What you did:**
- **Result:**
- **Improvement over pure semantic:**
- **Next step:**

### [Date] — Metadata Enrichment
- **Goal:** Auto-tag segments with machine type, error codes, safety info
- **LLM prompt used:**
- **Result:**
- **Issues / Blockers:**
- **Next step:**

### [Date] — Re-Evaluation
- **Goal:** Measure improvement after iterations
- **What you did:**
- **Result:**
- **Next step:**

---

## Experiment Tracking

| Experiment | Config / Parameters | Metric | Result | Notes |
|---|---|---|---|---|
| Semantic only (baseline) | | Precision@5 | | From Sprint 7 |
| Hybrid: BM25 + semantic | weight=0.5/0.5 | Precision@5 | | |
| With metadata filters | machine_type filter | Precision@5 | | |
| | | | | |

---

## Metadata Schema

| Field | Type | Example | Source |
|---|---|---|---|
| machine_type | string | "EUV scanner" | LLM extraction |
| error_codes | list[string] | ["E401", "E502"] | LLM extraction |
| safety_warnings | list[string] | ["ESD protection required"] | LLM extraction |
| tools_required | list[string] | ["torque wrench", "ESD strap"] | LLM extraction |
| difficulty_level | string | "intermediate" | LLM classification |

---

## Evaluation Results

| Metric | Target | Before Optimization | After Optimization | Pass? |
|---|---|---|---|---|
| Precision@5 | > 0.8 | | | |
| Recall@5 | TBD | | | |
| NDCG | TBD | | | |
| Response time | < 10s | | | |

---

## Feedback Received

| Date | From | Feedback | Action Taken |
|---|---|---|---|
| | AR | | |
| | CL | | |
| | KR | | |

---

## Risk Updates

| Risk | Status | Mitigation Applied |
|---|---|---|
| | 🟢 Resolved / 🟡 Monitoring / 🔴 Active | |

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

## 🎯 Goal 3 Assessment

- [ ] Retrieval pipeline returns relevant segments for test queries
- [ ] Precision@5 meets target (> 0.8)
- [ ] Metadata enrichment adds useful filtering
- [ ] Stakeholders validate retrieval quality
- [ ] **GOAL 3 ACHIEVED: System identifies relevant videos and segments for maintenance queries**

---

## Deliverables Checklist

- [ ] Optimized retrieval pipeline (hybrid search + metadata)
- [ ] Before/after evaluation metrics
- [ ] Stakeholder validation notes
- [ ] Goal 3 write-up
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
