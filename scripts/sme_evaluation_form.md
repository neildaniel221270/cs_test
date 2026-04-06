# SME Evaluation Form — Hybrid Review for AI-Structured Maintenance Transcripts

> **Reviewer:** __________________________  
> **Date:** __________________________  
> **Prompt version:** __________________________  
> **Model used:** __________________________  
> **Number of transcripts reviewed:** ____ / ____  

---

## Instructions

1. Review **3–5 structured transcripts**.
2. Aim for a representative mix:
   - at least one **procedural** video
   - at least one **overview/conceptual** video
   - at least one transcript with **few steps, weak extraction, or an error flag**
3. For each transcript:
   - open the **structured JSON**
   - compare it side by side with the **original video**
   - fill in **one copy of Section A**
4. After reviewing all selected transcripts, complete **Section B** to capture recurring issues and improvement priorities.

---

# Section A — Per-Transcript Review
*Copy this section once for each transcript reviewed.*

## A0. Transcript Metadata

| Field | Value |
|---|---|
| **File name** |  |
| **Transcript ID** |  |
| **Video title** |  |
| **Source video** |  |
| **procedure_type** (AI output) |  |
| **Number of steps extracted** |  |
| **Evaluator confidence in this review** | High / Medium / Low |

---

## A1. Title, Summary & Metadata Check

| Field / Criterion | AI Output | Rating | Suggested Fix / Notes |
|---|---|---|---|
| **Title** accurately describes the procedure |  | ☐ Correct ☐ Partial ☐ Wrong |  |
| **Summary** captures the key points in 2–3 sentences |  | ☐ Correct ☐ Partial ☐ Wrong |  |
| **procedure_type** is appropriate |  | ☐ Correct ☐ Wrong |  |
| **skill_level** is appropriate |  | ☐ Correct ☐ Wrong |  |
| **system_context** is correct |  | ☐ Correct ☐ Wrong |  |

---

## A2. Steps Accuracy

### A2.1 Extracted Steps Review

| Step # | Action / step_title (from AI) | Matches video? | Issues / Corrections |
|---|---|---|---|
| 1 |  | ☐ Yes ☐ Partial ☐ Wrong |  |
| 2 |  | ☐ Yes ☐ Partial ☐ Wrong |  |
| 3 |  | ☐ Yes ☐ Partial ☐ Wrong |  |
| 4 |  | ☐ Yes ☐ Partial ☐ Wrong |  |
| 5 |  | ☐ Yes ☐ Partial ☐ Wrong |  |
| 6 |  | ☐ Yes ☐ Partial ☐ Wrong |  |
| 7 |  | ☐ Yes ☐ Partial ☐ Wrong |  |
| 8 |  | ☐ Yes ☐ Partial ☐ Wrong |  |

*Add rows as needed.*

### A2.2 Missing Steps

| What the missing step should say | Approximate timestamp / position in video | Why it matters |
|---|---|---|
|  |  |  |
|  |  |  |

### A2.3 Hallucinated / Invented Steps

| Step # | What the AI invented | Why it is wrong |
|---|---|---|
|  |  |  |
|  |  |  |

### A2.4 Step Order Quality

**Is the step ordering correct?**  
☐ Yes  
☐ No → Describe issue: __________________________________________

**Are any steps merged or split incorrectly?**  
☐ No  
☐ Yes → Explain: ________________________________________________

---

## A3. Safety Warnings Review

| Warning # | AI-extracted warning | Correct? | Severity correct? | PPE correct? | Notes / Corrections |
|---|---|---|---|---|---|
| 1 |  | ☐ Yes ☐ No | ☐ Yes ☐ No | ☐ Yes ☐ No |  |
| 2 |  | ☐ Yes ☐ No | ☐ Yes ☐ No | ☐ Yes ☐ No |  |
| 3 |  | ☐ Yes ☐ No | ☐ Yes ☐ No | ☐ Yes ☐ No |  |

### Missing Safety Content

| What was missed | Severity | PPE | Why important |
|---|---|---|---|
|  |  |  |  |
|  |  |  |  |

---

## A4. Tools, Components & Materials

### A4.1 Tools

| AI-extracted tool | Correct? | Spec correct? | Notes / Corrections |
|---|---|---|---|
|  | ☐ Yes ☐ No | ☐ Yes ☐ No |  |
|  | ☐ Yes ☐ No | ☐ Yes ☐ No |  |
|  | ☐ Yes ☐ No | ☐ Yes ☐ No |  |

**Missing tools:** ________________________________________________

### A4.2 Components

| AI-extracted component | Correct? | Notes / Corrections |
|---|---|---|
|  | ☐ Yes ☐ No |  |
|  | ☐ Yes ☐ No |  |
|  | ☐ Yes ☐ No |  |

**Missing components:** ___________________________________________

---

## A5. Prerequisites

| AI-extracted prerequisite | Correct? | Notes / Corrections |
|---|---|---|
|  | ☐ Yes ☐ No |  |
|  | ☐ Yes ☐ No |  |
|  | ☐ Yes ☐ No |  |

**Missing prerequisites:** ________________________________________

---

## A6. Key Terms / Terminology

| AI-extracted term | Definition correct? | ASML terminology correct? | Notes / Corrections |
|---|---|---|---|
|  | ☐ Yes ☐ Partial ☐ Wrong | ☐ Yes ☐ No |  |
|  | ☐ Yes ☐ Partial ☐ Wrong | ☐ Yes ☐ No |  |
|  | ☐ Yes ☐ Partial ☐ Wrong | ☐ Yes ☐ No |  |

**Missing key terms:** ____________________________________________

---

## A7. Timestamp Spot-Check

*Pick 3 steps at random and jump to the AI timestamp in the video.*

| Step # | Expected time range | AI time range / timestamp_start | Acceptable? | Offset (sec) | Notes |
|---|---|---|---|---|---|
|  |  |  | ☐ Yes ☐ Off by <10s ☐ Wrong |  |  |
|  |  |  | ☐ Yes ☐ Off by <10s ☐ Wrong |  |  |
|  |  |  | ☐ Yes ☐ Off by <10s ☐ Wrong |  |  |

---

## A8. Scoring (1 = poor, 5 = excellent)

| Dimension | Score | Comment |
|---|---|---|
| **Completeness** — did the AI capture all important info? | /5 |  |
| **Accuracy** — are step descriptions factually correct? | /5 |  |
| **Safety** — are warnings and PPE requirements correct and complete? | /5 |  |
| **Usefulness** — would a technician find this output helpful? | /5 |  |

### Trust Decision

**Would you trust this output to be shown to a technician as-is?**  
☐ Yes, ready to use  
☐ Mostly, needs minor edits  
☐ No, significant issues  

### Top Issues to Fix for This Transcript
1. __________________________________________  
2. __________________________________________  
3. __________________________________________  

### Additional Comments
______________________________________________________________  
______________________________________________________________  

---

# Section B — Cross-Transcript Synthesis
*Complete once after all transcripts are reviewed.*

## B1. Common Failure Patterns
Check all that apply and give examples.

- [ ] **Steps merged** — two distinct actions collapsed into one  
  - Example: __________________________________________
- [ ] **Steps split** — one action split into multiple unnecessary steps  
  - Example: __________________________________________
- [ ] **Missing steps** — real actions omitted  
  - Example: __________________________________________
- [ ] **Hallucinated content** — invented steps / warnings / tools / prerequisites  
  - Example: __________________________________________
- [ ] **Wrong severity** — safety warnings over- or under-classified  
  - Example: __________________________________________
- [ ] **PPE mismatch** — PPE missing or incorrectly assigned  
  - Example: __________________________________________
- [ ] **Timestamp drift** — timestamps off by more than 5–10 seconds  
  - Example: __________________________________________
- [ ] **Terminology errors** — acronyms, component names, or system terms wrong  
  - Example: __________________________________________
- [ ] **Metadata issues** — title / summary / procedure_type / skill_level incorrect  
  - Example: __________________________________________
- [ ] **Overview misclassified as procedure** (or vice versa)  
  - Example: __________________________________________
- [ ] **Tools/components missing or incorrect**  
  - Example: __________________________________________
- [ ] **Prerequisites missing**  
  - Example: __________________________________________

---

## B2. Top 3 Improvement Priorities
Rank the most impactful fixes for the next prompt/model iteration.

1. __________________________________________  
2. __________________________________________  
3. __________________________________________  

---

## B3. Overall Impression

**Is the output quality good enough for a first prototype, or does it need significant rework before showing to technicians?**

______________________________________________________________  
______________________________________________________________  
______________________________________________________________  

---

## B4. Files Reviewed (Traceability)

| # | File name | Completeness | Accuracy | Safety | Usefulness | Trust level |
|---|---|:---:|:---:|:---:|:---:|---|
| 1 |  | /5 | /5 | /5 | /5 |  |
| 2 |  | /5 | /5 | /5 | /5 |  |
| 3 |  | /5 | /5 | /5 | /5 |  |
| 4 |  | /5 | /5 | /5 | /5 |  |
| 5 |  | /5 | /5 | /5 | /5 |  |
| **Average** |  | /5 | /5 | /5 | /5 |  |

**Suggested quality gate before next project phase:**  
Average ≥ **3.5 / 5** across all four criteria.
 
---

## B5. Final Recommendation

☐ Ready for broader SME review  
☐ Ready for limited technician pilot  
☐ Needs another prompt iteration first  
☐ Needs major restructuring before reuse  

**Why:**  
______________________________________________________________  
______________________________________________________________  

---

## Submission

Return the completed form to **Neil** for synthesis and prompt iteration tracking.
``