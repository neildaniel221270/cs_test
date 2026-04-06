# Prompt Iteration Workflow

## Overview

This document describes the feedback loop for improving the LLM structuring prompts. The cycle is: **structure → evaluate → diagnose → fix prompts → re-run**.

---

## Step 1 — Initial batch run

```bash
python scripts/structure_batch.py \
    --in_dir Data/transcripts_clean \
    --out_dir Data/transcripts_structured \
    --model "mistralai/mistral-7b-instruct-v0.3"
```

This produces `*.structured.json` files and a `run_manifest.json` summarising successes and failures.

---

## Step 2 — Select 3–5 transcripts for SME review

Pick a representative sample covering different video types:

- 1–2 **procedural** videos (step-by-step maintenance or replacement)
- 1 **overview / safety briefing** video
- 1 **troubleshooting** video (if available)
- 1 that the manifest flagged as `error_skeleton` or that has very few steps

For each, hand the SME:
1. The **original video** (or a link to it)
2. The **`*.structured.json`** file
3. A blank copy of `docs/sme_evaluation_form.md`

---

## Step 3 — Diagnose common failure patterns

After collecting SME forms, categorise the issues into these buckets:

| Failure type | Symptom | Likely prompt fix |
|--------------|---------|-------------------|
| **Hallucinated steps** | AI invented a step not in the video | Add stronger "FIDELITY" rule; add a negative few-shot example |
| **Missing steps** | AI skipped an action the narrator described | Add guidance to treat narrated actions as steps even if implicit |
| **Wrong severity** | Safety warning labelled "caution" instead of "critical" | Refine the severity mapping in the system prompt; add examples |
| **Missing safety warnings** | A hazard was mentioned but not extracted | Add a rule: "scan the full transcript for hazard keywords before writing steps" |
| **Bad timestamps** | Step timestamps point to the wrong part of the video | Reinforce that timestamps come from the `[start - end]` markers |
| **Merged steps** | Two distinct actions collapsed into one step | Add: "Each step = one physical action. If the narrator says 'then', that's likely a new step." |
| **Vocabulary drift** | AI paraphrased an ASML term (e.g. "light source" instead of "LMOS") | Strengthen the terminology preservation rule |
| **JSON parse failure** | LLM returned invalid JSON | Switch to a more instruction-following model (try phi3:medium); lower temperature |
| **Overly verbose** | Summary or step details are too long | Add word-count constraints ("summary ≤ 50 words", "action ≤ 15 words") |

---

## Step 4 — Edit prompts

All prompt logic lives in **`scripts/prompts.py`**. Here's what to change for each fix type:

### Adding or editing extraction rules

Open `prompts.py` and modify the `SYSTEM_PROMPT` string. The rules are numbered — add new ones at the end or refine existing ones.

```python
# Example: adding a new rule to catch merged steps
SYSTEM_PROMPT = f"""\
...
9. GRANULARITY — Each step must represent a single physical action.  If the
   narrator uses words like "then", "next", "after that", treat the following
   clause as a separate step.
"""
```

### Adding a negative few-shot example

If the LLM keeps making a specific mistake (e.g. inventing a step), add a third few-shot pair to `FEW_SHOT_EXAMPLES` that demonstrates what NOT to do:

```python
# In prompts.py, append to FEW_SHOT_EXAMPLES:
{
    "role": "user",
    "content": (
        "=== CLEANED TRANSCRIPT ===\n\n"
        "[0.0 - 15.0] This module covers the basics of EUV wafer handling.\n"
        "[15.0 - 30.0] The wafer is loaded by the robot arm into the chuck.\n"
    ),
},
{
    "role": "assistant",
    "content": json.dumps({
        # Notice: only 1 step, because only 1 action is described.
        # The AI should NOT add "Remove wafer from cassette" — that's not in the transcript.
        "steps": [
            {
                "step_number": 1,
                "action": "Load the wafer into the chuck using the robot arm.",
                ...
            }
        ],
        ...
    }, indent=2),
},
```

### Switching the model

If Mistral 7B struggles with JSON compliance, try `phi3:medium` which tends to be more schema-adherent:

```bash
python scripts/structure_batch.py \
    --in_dir Data/transcripts_clean \
    --out_dir Data/transcripts_structured_v2 \
    --model "microsoft/phi-3-medium-128k-instruct" \
    --force
```

---

## Step 5 — Re-run on problem cases only

Rather than re-processing everything, target the files that had issues:

```bash
# Re-run on a single file
python scripts/clean_transcript.py \
    --in_raw_json Data/transcripts_raw/problem_video.raw.json \
    --out_clean_json Data/transcripts_clean/problem_video.clean.json \
    --structure \
    --lmstudio_model "microsoft/phi-3-medium-128k-instruct"

# Or use structure_batch.py with --force on the specific output
python scripts/structure_batch.py \
    --in_dir Data/transcripts_clean \
    --out_dir Data/transcripts_structured \
    --model "microsoft/phi-3-medium-128k-instruct" \
    --force
```

---

## Step 6 — Track prompt versions

Keep a simple changelog at the top of `prompts.py`:

```python
# PROMPT CHANGELOG
# v1.0  2026-03-14  Initial prompt with 2 few-shot examples
# v1.1  2026-03-21  Added GRANULARITY rule (step merging fix)
# v1.2  2026-03-21  Added negative few-shot for hallucinated steps
# v1.3  2026-03-28  Tightened severity mapping after SME round 2
```

And record which prompt version produced each batch:

```bash
# Version tag in the output directory name
--out_dir Data/transcripts_structured_v1.1
```

---

## Step 7 — Compute improvement metrics

After each iteration, compare the new SME scores against the previous round:

| Metric | Round 1 | Round 2 | Target |
|--------|---------|---------|--------|
| Completeness (avg /5) | | | ≥ 4.0 |
| Accuracy (avg /5) | | | ≥ 4.0 |
| Safety (avg /5) | | | ≥ 4.5 |
| Usefulness (avg /5) | | | ≥ 4.0 |
| JSON parse success rate | | | ≥ 95% |
| "Ready to use" (%) | | | ≥ 60% |

When all targets are met (or you've exhausted your iteration budget), freeze the prompt and move on to Goal 2 (timestamp alignment and retrieval).

---

## Quick reference — iteration cycle

```
┌──────────────────────┐
│  Edit prompts.py     │
│  (rules / examples)  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  structure_batch.py  │
│  --force on failures │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  SME reviews 3-5     │
│  (evaluation form)   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Diagnose patterns   │
│  (table above)       │
└──────────┬───────────┘
           │
           ▼
     Targets met?
      ╱         ╲
    Yes          No ──→ loop back to top
     │
     ▼
  Freeze prompt
  Move to Goal 2
```


---

# Iteration Workflow — Prompt Tuning for LLM Structuring

> This document describes the feedback loop for improving `prompts.py`
> based on SME evaluation results.  Follow it after every round of
> SME review.

---

## 1. Collect Feedback

After the SME returns their completed `sme_evaluation_form.md`:

1. Read **Section B1 (Common Failure Patterns)** — these tell you *what*
   is going wrong.
2. Read **Section B2 (Top 3 Priorities)** — these tell you *what to fix
   first*.
3. Skim each **Section A** for specific examples you can use as regression
   tests.

---

## 2. Diagnose → Fix (lookup table)

Use the table below to map each failure pattern to a concrete edit in
`prompts.py`.  Most fixes live in either the **EXTRACTION RULES** section
of `SYSTEM_PROMPT` or in the **few-shot examples**.

| Symptom | Root cause | Fix location | Suggested edit |
|---------|-----------|--------------|----------------|
| **Steps merged** (two actions in one step) | Rule 6 (granularity) not strong enough | `SYSTEM_PROMPT`, Rule 6 | Add a negative example: *"Do NOT combine 'remove screw' and 'lift cover' into one step even if they appear in the same sentence."* |
| **Steps split** (one action across 2+ steps) | Model over-splitting on sub-clauses | `SYSTEM_PROMPT`, Rule 6 | Add: *"Sub-actions that are part of a single physical motion (e.g. 'press latch and pull cable') count as one step."* |
| **Hallucinated steps** | Model inventing from domain knowledge | `SYSTEM_PROMPT`, Rule 1 | Strengthen: *"If a step is not described or visually demonstrated in the transcript, do NOT include it — even if you know it is standard practice."* |
| **Missing steps** | Model skipping brief or implicit actions | `SYSTEM_PROMPT`, Rule 2 | Add: *"Every distinct physical action mentioned — even briefly — must become a step. Include implicit actions like 'put on gloves' if the narrator says them."* |
| **Wrong severity** | Severity definitions too vague | `SYSTEM_PROMPT`, Rule 7 | Add concrete ASML examples per severity level, e.g. *"critical: EUV light source interlock, laser curtain; warning: dropping a reticle; caution: pinch points on stage cover."* |
| **Timestamp drift (>5 s)** | Model guessing instead of reading markers | `SYSTEM_PROMPT`, Rule 5 | Add: *"Use the EXACT [start – end] markers from the transcript. Do not estimate or interpolate timestamps."* |
| **ASML terminology errors** | Model expanding or normalising acronyms | `SYSTEM_PROMPT`, Rule 9 | Add the specific mis-expansion as a negative example in the rule. |
| **Overview misclassified as procedure** | Rule 8 not salient enough | Few-shot examples | Add a third few-shot example that is a borderline case (e.g. a video that mentions a tool but doesn't demonstrate a procedure). |
| **Procedure misclassified as overview** | Model not recognising imperative instructions | `SYSTEM_PROMPT`, Rule 8 | Add: *"If the narrator uses imperative instructions ('remove', 'connect', 'torque'), treat the transcript as a procedure even if it also contains conceptual explanation."* |
| **JSON parse failures** | Model wrapping JSON in markdown or adding prose | `SYSTEM_PROMPT`, output format section | Add: *"Do NOT wrap the JSON in markdown code fences. Do NOT add any text before the opening { or after the closing }."* |
| **Empty fields that should have data** | Model using `""` instead of extracting | `SYSTEM_PROMPT`, Rule 10 | Clarify: *"Use null only when data is truly absent. If the transcript mentions a tool by name, you MUST include it in tools_required even if no specification is given."* |

---

## 3. Edit `prompts.py`

### Workflow

```
1.  Open  scripts/prompts.py
2.  Bump  __version__  (e.g. "1.0" → "1.1")
3.  Edit  SYSTEM_PROMPT  rules — keep each rule numbered and concise
4.  If needed, edit or add a FEW_SHOT_EXAMPLES entry
5.  Save
```

### Rules for editing prompts

- **One change at a time.** If you change three rules at once and quality
  improves, you won't know which rule helped.  Make one targeted edit,
  re-run on the problem cases, evaluate, then move to the next fix.
- **Add negative examples** when the model keeps making the same mistake.
  E.g. if it keeps merging "remove screw" + "lift cover", add that exact
  pair as a "DO NOT" in the rule.
- **Add few-shot examples** when a whole category of transcript is failing
  (e.g. safety briefings, calibration procedures).  One well-chosen
  example is more effective than three extra rules.
- **Keep the system prompt under ~2000 tokens** to leave room for the
  transcript and few-shot examples in smaller-context models.

---

## 4. Re-Run on Problem Cases

After editing the prompt, re-run *only* the transcripts that failed in the
SME review.  This is faster than re-running the full batch and lets you
compare directly.

```bash
# Re-run a single file
python scripts/structure_batch.py \
    --in_dir  Data/transcripts_clean \
    --out_dir Data/transcripts_structured \
    --pattern "LMOS Introduction to the process.clean.json" \
    --force

# Re-run a handful of problem files (use a temp folder to isolate)
mkdir -p Data/transcripts_clean_retest
cp Data/transcripts_clean/problem_file_1.clean.json Data/transcripts_clean_retest/
cp Data/transcripts_clean/problem_file_2.clean.json Data/transcripts_clean_retest/

python scripts/structure_batch.py \
    --in_dir  Data/transcripts_clean_retest \
    --out_dir Data/transcripts_structured \
    --force
```

Then manually compare the new `.structured.json` against the old version
and the original video.

---

## 5. Track Prompt Versions

Keep a lightweight changelog at the top of `prompts.py` (the docstring
already has a version-history section).  Suggested format:

```
Version history:
  v1.0  2026-03-17  Initial: 10 rules, 2 few-shot examples
  v1.1  2026-03-21  Strengthened Rule 6 (granularity) after SME found merged steps
  v1.2  2026-03-24  Added safety-briefing few-shot example
  v2.0  2026-04-01  Switched to phi3:medium, rewrote all few-shot examples
```

Also note the version in `run_manifest.json` (structure_batch.py already
writes `prompt_version` into every batch run and every structured file),
so you can always trace which output came from which prompt.

---

## 6. Measure Improvement

### Quantitative checks (from `run_manifest.json`)

After each batch run, check:

| Metric | Target | How to check |
|--------|--------|--------------|
| **Success rate** | ≥ 90% of files produce valid JSON | `run_manifest.json → ok / total_files` |
| **Steps per procedural video** | ≥ 3 steps on average | Filter records where procedure_type ≠ "overview", average steps_count |
| **Zero-step procedural videos** | 0 | Filter records where procedure_type ≠ "overview" and steps_count == 0 |

### Qualitative checks (from SME re-review)

After fixing the top-priority issues, ask the SME to re-review the same
3–5 transcripts using a fresh copy of `sme_evaluation_form.md`.  Compare
scores:

| Criterion | Round 1 avg | Round 2 avg | Δ |
|-----------|:-----------:|:-----------:|:-:|
| Completeness | /5 | /5 | |
| Accuracy | /5 | /5 | |
| Safety | /5 | /5 | |
| Usefulness | /5 | /5 | |

**Gate:** Average ≥ 3.5 across all four criteria before moving to Goal 2.

---

## 7. When to Stop Iterating

Move on from prompt tuning when **any** of these are true:

1. All four SME scores average ≥ 3.5 and no "critical" failures remain.
2. You've completed 3 iteration rounds with diminishing returns (< 0.3
   average score improvement per round).
3. The remaining errors are caused by ASR quality (bad transcript), not
   by the LLM prompt — in that case, fix upstream (improve Whisper
   initial_prompt, glossary, or try a different ASR model).

---

## Quick-Reference: Full Iteration Cycle

```
SME fills in sme_evaluation_form.md
        │
        ▼
Read Section B → identify top failure pattern
        │
        ▼
Look up fix in the diagnosis table (Section 2 above)
        │
        ▼
Edit prompts.py (one change) → bump __version__
        │
        ▼
Re-run structure_batch.py --force on problem cases
        │
        ▼
Compare old vs new .structured.json
        │
        ▼
If improved → commit, pick next failure pattern
If not      → revert edit, try alternative fix
        │
        ▼
After 2–3 fixes → ask SME to re-review
        │
        ▼
Scores ≥ 3.5?  → move to Goal 2
Scores < 3.5?  → next iteration round
```
