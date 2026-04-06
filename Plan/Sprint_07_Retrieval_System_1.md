# Sprint 7 — Retrieval System Part 1: RAG Pipeline

**Phase:** 5 — Retrieval and Relevance Modeling  
**Weeks:** 11–12 · **Dates:** 23 Apr – 6 May 2026  
**Incremental Goal:** Working toward Goal 3

---

## Sprint Objective

> Build the RAG retrieval pipeline: generate embeddings for all segments, set up a vector database, implement query processing and retrieval with ranking, and run initial evaluation.

---

## Tasks

| # | Task | Status | Due | Notes |
|---|---|---|---|---|
| 7.1 | Generate embeddings for all segments | ⬜ Not Started | 25 Apr | Embed each timestamped segment using sentence transformer |
| 7.2 | Set up vector database (FAISS/ChromaDB) | ⬜ Not Started | 28 Apr | Index all embeddings, test basic similarity search |
| 7.3 | Build query processing module | ⬜ Not Started | 30 Apr | Error code + description → embedding for search |
| 7.4 | Implement retrieval + ranking pipeline | ⬜ Not Started | 2 May | Query → top-K segments → re-rank → return ranked list |
| 7.5 | Create 10–15 realistic test queries | ⬜ Not Started | 3 May | Based on common machine issues, get AR/SME input |
| 7.6 | Evaluate retrieval (Precision@K, Recall@K) | ⬜ Not Started | 5 May | Run test queries, manually label relevance, calculate metrics |
| 7.7 | Weekly check-in with supervisor | ⬜ Not Started | 6 May | Discuss retrieval results and edge cases |

**Status key:** ⬜ Not Started · 🔄 In Progress · ✅ Done · ⛔ Blocked

**Tools needed:** sentence-transformers, FAISS/ChromaDB, Python, Jupyter Notebook  
**People involved:** NR, KR, AR, SME

---

## Research Notes

_Capture findings about retrieval strategies, embedding models, and RAG approaches._

### Source 1: [Title]
- **Authors / Year:**
- **Key Findings:**
- **How it applies to your project:**
- **Limitations:**

---

## Meeting Notes

### Meeting: Test Query Design with AR/SME
- **Date:**
- **Attendees:** NR, AR, SME
- **Agenda:**
  1. What are the most common maintenance queries technicians have?
  2. What error codes are most frequent?
  3. Draft 10–15 realistic test queries together
- **Key Decisions:**
  -
- **Action Items:**
  - [ ] [Person] — [Action] — by [Date]
- **Notes:**

### Meeting: Weekly Supervisor Check-in
- **Date:**
- **Attendees:** NR, KR
- **Key Decisions:**
  -
- **Action Items:**
  - [ ] [Person] — [Action] — by [Date]

---

## Development Log

### [Date] — Embedding Generation
- **Goal:** Embed all timestamped segments
- **Model used:**
- **Number of segments embedded:**
- **Embedding dimension:**
- **Result:**
- **Issues / Blockers:**
- **Next step:**

### [Date] — Vector Database Setup
- **Goal:** Index embeddings for fast retrieval
- **DB chosen:** FAISS / ChromaDB (circle one)
- **Why this choice:**
- **Result:**
- **Issues / Blockers:**
- **Next step:**

### [Date] — Query Processing
- **Goal:** Convert maintenance queries to embeddings
- **What you did:**
- **Result:**
- **Next step:**

### [Date] — Retrieval Pipeline
- **Goal:** End-to-end query → ranked results
- **What you did:**
- **Top-K setting:**
- **Result:**
- **Issues / Blockers:**
- **Next step:**

---

## Test Queries

| # | Query | Expected Relevant Videos/Segments | Notes |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |
| 10 | | | |

---

## Experiment Tracking

| Experiment | Config / Parameters | Metric | Result | Notes |
|---|---|---|---|---|
| Embedding model A | all-MiniLM-L6-v2 | Precision@5 | | |
| Embedding model B | all-mpnet-base-v2 | Precision@5 | | |
| Top-K = 5 | | Precision@5 | | |
| Top-K = 10 | | Precision@10 | | |

---

## Evaluation Results

| Metric | Target | Achieved | Pass? | Notes |
|---|---|---|---|---|
| Precision@5 | > 0.8 | | | |
| Recall@5 | TBD | | | |
| NDCG | TBD | | | |
| Query response time | < 10s | | | |

---

## Feedback Received

| Date | From | Feedback | Action Taken |
|---|---|---|---|
| | AR / SME | | |
| | KR | | |

---

## Risk Updates

| Risk | Status | Mitigation Applied |
|---|---|---|
| Embedding model not suited to domain | 🟡 Monitoring | |
| Too few segments for meaningful retrieval | 🟡 Monitoring | |

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

- [ ] All segments embedded and indexed
- [ ] Vector database set up and populated
- [ ] Query processing module working
- [ ] Retrieval + ranking pipeline working
- [ ] Test queries created (10–15)
- [ ] Initial evaluation metrics calculated
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
