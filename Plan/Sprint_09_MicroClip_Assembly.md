# Sprint 9 — Micro-Clip Assembly & Safety ✅ GOAL 4

**Phase:** 6 — Micro-Clip Assembly and Safety Validation  
**Weeks:** 14–15 · **Dates:** 14 May – 27 May 2026  
**Incremental Goal:** 🎯 Goal 4 — Assemble safety-compliant micro-clips

---

## Sprint Objective

> Build the final piece: extract video clips from timestamps, assemble multi-segment clips, add captions and safety notes, build the Gradio demo interface, and validate with safety reviewer. Achieve Goal 4.

---

## Tasks

| # | Task | Status | Due | Notes |
|---|---|---|---|---|
| 9.1 | Build video clip extraction script | ⬜ Not Started | 16 May | Video + timestamps → standalone clip (FFmpeg) |
| 9.2 | Assemble multi-segment clips | ⬜ Not Started | 18 May | Stitch segments from multiple videos with transitions |
| 9.3 | Add captions/subtitles to clips | ⬜ Not Started | 19 May | Overlay structured transcript text as captions |
| 9.4 | Generate and add safety notes | ⬜ Not Started | 20 May | LLM generates safety warnings, overlay on clips |
| 9.5 | Safety review with safety reviewer | ⬜ Not Started | 22 May | SR watches 3–5 clips, validates safety notices |
| 9.6 | Build Gradio demo interface | ⬜ Not Started | 24 May | Search bar → ranked results → plays micro-clip |
| 9.7 | Create wireframe/mockup of production UI | ⬜ Not Started | 25 May | Low-fidelity mockup for technician interface |
| 9.8 | End-to-end integration test | ⬜ Not Started | 26 May | Run 5 queries through full pipeline, fix broken connections |
| 9.9 | Stakeholder demo of full prototype | ⬜ Not Started | 27 May | Present to AR/CL, collect feedback |

**Status key:** ⬜ Not Started · 🔄 In Progress · ✅ Done · ⛔ Blocked

**Tools needed:** FFmpeg, MoviePy, Python, LLM API, Gradio, Figma/draw.io, SRT files  
**People involved:** NR, SR (Safety Reviewer), VE (Video Editor), AR, CL, KR

---

## Research Notes

### Source 1: [Title]
- **Authors / Year:**
- **Key Findings:**
- **How it applies to your project:**
- **Limitations:**

---

## Meeting Notes

### Meeting: Safety Review Session
- **Date:**
- **Attendees:** NR, SR
- **Clips reviewed:**
  1.
  2.
  3.
  4.
  5.
- **Agenda:**
  1. Watch each assembled micro-clip
  2. Are safety notices correct and complete?
  3. Any missing warnings?
  4. Are captions clear and readable?
- **Key Decisions:**
  -
- **Action Items:**
  - [ ] [Person] — [Action] — by [Date]
- **Notes:**

### Meeting: Full Prototype Demo — Goal 4
- **Date:**
- **Attendees:** NR, AR, CL
- **Demo queries tested:**
  1.
  2.
  3.
- **Feedback:**
  -
- **Key Decisions:**
  -
- **Action Items:**
  - [ ] [Person] — [Action] — by [Date]
- **Notes:**

---

## Development Log

### [Date] — Video Clip Extraction
- **Goal:** Extract standalone clips from video using timestamps
- **FFmpeg command used:**
- **Result:**
- **Issues / Blockers:**
- **Next step:**

### [Date] — Multi-Segment Assembly
- **Goal:** Stitch segments from multiple source videos
- **What you did:**
- **Transition style:**
- **Result:**
- **Issues / Blockers:**
- **Next step:**

### [Date] — Captions & Subtitles
- **Goal:** Add text overlay to clips
- **Method:** (SRT burn-in / overlay)
- **Result:**
- **Issues / Blockers:**
- **Next step:**

### [Date] — Safety Note Generation
- **Goal:** Auto-generate and overlay safety warnings
- **LLM prompt used:**
- **Result:**
- **Issues / Blockers:**
- **Next step:**

### [Date] — Gradio Interface
- **Goal:** Build demo UI
- **Features implemented:**
- **Result:**
- **Screenshot:** (paste or reference)
- **Issues / Blockers:**
- **Next step:**

### [Date] — End-to-End Integration Test
- **Goal:** Full pipeline test: query → retrieval → clip assembly → playback
- **Queries tested:**
- **Results:**
- **Bugs found:**
- **Fixes applied:**

---

## Safety Review Log

| Clip ID | Safety Notes Present | SR Approved? | Missing Warnings | Action Taken |
|---|---|---|---|---|
| | | ✅ / ❌ | | |
| | | ✅ / ❌ | | |
| | | ✅ / ❌ | | |

---

## Experiment Tracking

| Experiment | Config / Parameters | Metric | Result | Notes |
|---|---|---|---|---|
| Clip extraction quality | FFmpeg, codec=H.264 | Visual quality | | |
| Caption readability | Font=Arial, size=24 | User feedback | | |
| Safety note accuracy | LLM-generated | SR approval rate | | |

---

## Evaluation Results

| Metric | Target | Achieved | Pass? | Notes |
|---|---|---|---|---|
| Clip extraction success | 100% | | | All timestamps produce valid clips |
| Caption accuracy | > 95% | | | Captions match spoken content |
| Safety notice completeness | 100% (SR approved) | | | |
| End-to-end pipeline success | All test queries work | | | |
| Gradio demo functional | Working for all queries | | | |

---

## Feedback Received

| Date | From | Feedback | Action Taken |
|---|---|---|---|
| | SR | | |
| | VE | | |
| | AR / CL | | |
| | KR | | |

---

## Risk Updates

| Risk | Status | Mitigation Applied |
|---|---|---|
| Safety review delays | 🟡 Monitoring | Schedule SR early in sprint |
| Video codec compatibility issues | 🟡 Monitoring | |
| Clip transitions look jarring | 🟡 Monitoring | |

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

## 🎯 Goal 4 Assessment

- [ ] Video clips extracted from timestamps
- [ ] Multi-segment clips assembled with smooth transitions
- [ ] Captions/subtitles added and accurate
- [ ] Safety notes generated and validated by SR
- [ ] Gradio demo interface working
- [ ] Wireframe/mockup of production UI created
- [ ] End-to-end pipeline tested successfully
- [ ] **GOAL 4 ACHIEVED: Safety-compliant micro-clips assembled and demo-ready**

---

## Deliverables Checklist

- [ ] Clip extraction script
- [ ] Multi-segment assembly pipeline
- [ ] Caption/subtitle module
- [ ] Safety note generation module
- [ ] Safety review documentation
- [ ] Gradio demo interface
- [ ] UI wireframe/mockup
- [ ] End-to-end test results
- [ ] Goal 4 write-up
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
