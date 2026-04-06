#!/usr/bin/env python3
"""
prompts.py — LLM structuring prompts for the transcript → steps pipeline
========================================================================
Centralises all prompt logic for converting cleaned transcripts into
structured JSON that can be used for micro-learning, retrieval, or UI display.

Designed to work with the current pipeline described in test.md:
- extract_audio.py -> transcribe_batch.py -> clean_transcript.py
- Reads cleaned transcript segments formatted as [start - end] text
- Outputs structured JSON with chronological steps and metadata
"""

import json
from typing import List, Dict, Any

# ──────────────────────────────────────────────────────────────────────
# 1. OUTPUT SCHEMA (single source of truth)
# ──────────────────────────────────────────────────────────────────────
MICRO_LEARNING_SCHEMA: Dict[str, Any] = {
    "title": "Short descriptive title of the task or topic",
    "summary": "2-3 sentence overview of what the transcript covers",
    "procedure_type": "maintenance | troubleshooting | calibration | inspection | replacement | overview | safety_briefing",
    "skill_level": "beginner | intermediate | advanced",
    "estimated_duration_minutes": "number or null",
    "system_context": "Machine / subsystem, e.g. NXE:3400B — Wafer Stage",
    "safety_warnings": [
        {
            "severity": "critical | warning | caution | info",
            "description": "Risk or best-practice note explicitly mentioned in the transcript",
            "ppe_required": ["PPE item if explicitly mentioned"],
        }
    ],
    "tools_required": [
        {
            "name": "Tool name",
            "specification": "Optional tool specification such as torque or size",
        }
    ],
    "components_referenced": ["List of parts, machine units, or subsystems mentioned"],
    "prerequisites": ["What must be done before starting"],
    "steps": [
        {
            "step_number": 1,
            "step_title": "Short UI-friendly title, e.g. Remove the panel cover",
            "action": "Single imperative action sentence",
            "details": "Extra detail or context from the transcript",
            "caution": "Per-step caution or null",
            "timestamp_start": 0.0,
            "timestamp_end": 12.5,
        }
    ],
    "key_terms": [
        {
            "term": "Domain-specific term",
            "definition": "Plain-language definition grounded in the transcript context",
        }
    ],
}

# ──────────────────────────────────────────────────────────────────────
# 2. SYSTEM PROMPT
# ──────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""\
You are an ASML maintenance-training content analyst.
Your job: convert a cleaned, timestamped transcript into a single JSON object
that captures the procedure as structured steps plus supporting metadata.

Return ONLY valid JSON matching this schema (no markdown fences, no preamble,
no explanation):
{json.dumps(MICRO_LEARNING_SCHEMA, indent=2)}

EXTRACTION RULES
1. FIDELITY
   - Use only what is explicitly stated or directly supported by the transcript.
   - Do not invent missing tools, safety warnings, torque values, prerequisites,
     or step details.
   - If evidence is missing, use null for scalar values or [] for arrays.

2. PRIMARY GOAL: TRANSCRIPT → CHRONOLOGICAL STEPS
   - Convert the transcript into ordered, practical steps.
   - Each step must represent a discrete technician action or check.
   - Keep the step order chronological.
   - Use concise imperative wording, e.g. "Remove the panel cover."
   - The "step_title" should be short and UI-friendly, e.g. "Remove panel cover".
   - The "action" may be slightly fuller than the title, but still concise.
   - If the transcript is descriptive only (overview/explainer), steps may be []
     instead of invented procedural steps.

3. STEP GRANULARITY
   - Split into a new step when the technician begins a new physical action,
     verification action, or system interaction.
   - Do not create a separate step for filler narration or repeated explanation.
   - Do not merge clearly separate actions into one step if they happen at
     different times in the transcript.

4. TIMESTAMPS
   - For every step, set timestamp_start and timestamp_end using the transcript's
     [start - end] markers.
   - Use approximate boundaries covering the lines where the step is discussed.
   - Timestamps must be numeric seconds.

5. SAFETY
   - Add safety_warnings only when the transcript explicitly mentions a hazard,
     careful handling, PPE, de-energising, LOTO, fragile parts, or similar.
   - Severity mapping:
       critical = electrical / laser / chemical / high-pressure hazards
       warning  = risk of equipment damage or process damage
       caution  = minor injury risk / pinch points / fragile handling
       info     = general best-practice note
   - Use per-step "caution" only when the warning applies to that specific step.

6. ASML TERMINOLOGY
   - Preserve ASML and semiconductor terminology exactly when present:
     EUV, DUV, HMI, LMOS, NXE, TWINSCAN, pellicle, reticle, wafer stage, etc.

7. CLASSIFICATION
   - procedure_type must be the single best-fit label.
   - skill_level should reflect the assumed prior knowledge required.

8. SUMMARISATION
   - Keep the summary to 2-3 concise sentences.
   - estimated_duration_minutes should be a rough estimate only if the transcript
     provides enough evidence; otherwise null.

9. JSON VALIDITY
   - Return exactly one JSON object.
   - Do not include comments, trailing commas, or markdown code fences.
"""

# ──────────────────────────────────────────────────────────────────────
# 3. FEW-SHOT EXAMPLES
# ──────────────────────────────────────────────────────────────────────
FEW_SHOT_EXAMPLES: List[Dict[str, str]] = [
    {
        "role": "user",
        "content": (
            "=== CLEANED TRANSCRIPT ===\n\n"
            "[0.0 - 4.0] In this video we will replace the filter cover on the service panel.\n"
            "[4.0 - 10.0] Before you begin, power down the unit and wear your ESD wristband.\n"
            "[10.0 - 18.0] Use a T20 driver to loosen the two screws on the front cover.\n"
            "[18.0 - 27.5] Remove the panel cover and place it on a clean surface.\n"
            "[27.5 - 36.0] Disconnect the small sensor cable carefully because the connector is fragile.\n"
            "[36.0 - 47.0] Lift out the old filter and insert the new filter in the same orientation.\n"
            "[47.0 - 56.0] Reconnect the cable, reinstall the cover, and tighten the screws.\n"
            "[56.0 - 64.0] Finish by checking the status in the HMI."
        ),
    },
    {
        "role": "assistant",
        "content": json.dumps(
            {
                "title": "Replace the Filter Cover on the Service Panel",
                "summary": "This transcript explains how to remove the service panel cover, replace the filter, and restore the unit to operation. It also mentions the shutdown prerequisite, required tool, and a fragile cable connection.",
                "procedure_type": "replacement",
                "skill_level": "intermediate",
                "estimated_duration_minutes": 5,
                "system_context": "Service panel filter assembly",
                "safety_warnings": [
                    {
                        "severity": "warning",
                        "description": "Power down the unit before starting the replacement.",
                        "ppe_required": ["ESD wristband"],
                    },
                    {
                        "severity": "caution",
                        "description": "The sensor cable connector is fragile and should be handled carefully.",
                        "ppe_required": [],
                    },
                ],
                "tools_required": [
                    {"name": "T20 driver", "specification": None},
                    {"name": "ESD wristband", "specification": None},
                ],
                "components_referenced": [
                    "service panel",
                    "panel cover",
                    "sensor cable",
                    "filter",
                    "HMI",
                ],
                "prerequisites": [
                    "Power down the unit",
                    "Wear an ESD wristband",
                ],
                "steps": [
                    {
                        "step_number": 1,
                        "step_title": "Loosen the cover screws",
                        "action": "Loosen the two screws on the front cover using a T20 driver.",
                        "details": None,
                        "caution": None,
                        "timestamp_start": 10.0,
                        "timestamp_end": 18.0,
                    },
                    {
                        "step_number": 2,
                        "step_title": "Remove the panel cover",
                        "action": "Remove the panel cover and place it on a clean surface.",
                        "details": None,
                        "caution": None,
                        "timestamp_start": 18.0,
                        "timestamp_end": 27.5,
                    },
                    {
                        "step_number": 3,
                        "step_title": "Disconnect the sensor cable",
                        "action": "Disconnect the small sensor cable.",
                        "details": None,
                        "caution": "The connector is fragile.",
                        "timestamp_start": 27.5,
                        "timestamp_end": 36.0,
                    },
                    {
                        "step_number": 4,
                        "step_title": "Replace the filter",
                        "action": "Lift out the old filter and insert the new filter in the same orientation.",
                        "details": None,
                        "caution": None,
                        "timestamp_start": 36.0,
                        "timestamp_end": 47.0,
                    },
                    {
                        "step_number": 5,
                        "step_title": "Reinstall the cover",
                        "action": "Reconnect the cable, reinstall the cover, and tighten the screws.",
                        "details": None,
                        "caution": None,
                        "timestamp_start": 47.0,
                        "timestamp_end": 56.0,
                    },
                    {
                        "step_number": 6,
                        "step_title": "Verify in the HMI",
                        "action": "Check the status in the HMI.",
                        "details": None,
                        "caution": None,
                        "timestamp_start": 56.0,
                        "timestamp_end": 64.0,
                    },
                ],
                "key_terms": [
                    {"term": "HMI", "definition": "Human-Machine Interface used to check system state and perform operator actions."},
                    {"term": "ESD wristband", "definition": "Protective grounding strap used to reduce electrostatic discharge risk while handling sensitive components."},
                ],
            },
            indent=2,
        ),
    },
    {
        "role": "user",
        "content": (
            "=== CLEANED TRANSCRIPT ===\n\n"
            "[0.0 - 7.0] In this module we give an overview of the LMOS light source in an EUV system.\n"
            "[7.0 - 20.0] A CO2 laser hits tin droplets to generate plasma that emits EUV light at 13.5 nanometres.\n"
            "[20.0 - 32.0] The collector mirror directs the light into the illumination system.\n"
            "[32.0 - 45.0] Tin deposition can reduce performance, so cleaning intervals are planned as part of maintenance."
        ),
    },
    {
        "role": "assistant",
        "content": json.dumps(
            {
                "title": "Overview of the LMOS Light Source",
                "summary": "This transcript provides a high-level explanation of how the LMOS light source generates EUV light and directs it into the illumination system. It also notes that tin deposition affects performance and drives planned maintenance.",
                "procedure_type": "overview",
                "skill_level": "beginner",
                "estimated_duration_minutes": 2,
                "system_context": "EUV — LMOS light source subsystem",
                "safety_warnings": [],
                "tools_required": [],
                "components_referenced": [
                    "LMOS",
                    "CO2 laser",
                    "tin droplets",
                    "plasma",
                    "collector mirror",
                    "illumination system",
                ],
                "prerequisites": [],
                "steps": [],
                "key_terms": [
                    {"term": "LMOS", "definition": "Laser-produced Plasma Light Source used to generate EUV light."},
                    {"term": "EUV", "definition": "Extreme ultraviolet light used in advanced lithography at 13.5 nanometres."},
                    {"term": "collector mirror", "definition": "Mirror that captures and directs generated EUV light into the illumination system."},
                ],
            },
            indent=2,
        ),
    },
]


# ──────────────────────────────────────────────────────────────────────
# 4. MESSAGE BUILDERS
# ──────────────────────────────────────────────────────────────────────
def build_structuring_messages(
    transcript_block: str,
    include_few_shot: bool = True,
) -> List[Dict[str, str]]:
    """
    Build the full chat message list for structuring a transcript.

    Important:
    Some LM Studio model prompt templates only support 'user' and 'assistant'
    roles. To stay compatible, we fold the old system instructions into the
    first user message instead of sending a separate system role.
    """
    intro_user_message = {
        "role": "user",
        "content": (
            f"{SYSTEM_PROMPT}\n\n"
            "Acknowledge these instructions internally and use them for all following examples "
            "and the final transcript. Return only valid JSON when you answer the real task."
        ),
    }

    messages: List[Dict[str, str]] = [intro_user_message]                                                                   

    if include_few_shot:
        messages.extend(FEW_SHOT_EXAMPLES)

    messages.append(
        {
            "role": "user",
            "content": (
                "=== CLEANED TRANSCRIPT ===\n\n"
                f"{transcript_block}\n\n"
                "Convert this transcript into structured JSON with chronological steps. "
                "If the transcript is not procedural, return an empty steps array instead of inventing steps."
            ),
        }
    )
    return messages


def build_retry_messages(
    transcript_block: str,
    failed_raw: str,
    include_few_shot: bool = True,
) -> List[Dict[str, str]]:
    """
    Build a retry prompt when the first attempt returned invalid JSON.
    Compatible with models that only support 'user' and 'assistant' roles.
    """
    messages = build_structuring_messages(
        transcript_block,
        include_few_shot=include_few_shot,
    )

    messages.append(
        {
            "role": "assistant",
            "content": failed_raw,
        }
    )

    messages.append(
        {
            "role": "user",
            "content": (
                "Your previous response was not valid JSON. "
                "Respond again with ONLY one valid JSON object that matches the schema exactly. "
                "Do not include markdown, commentary, or trailing text."
            ),
        }
    )
    return messages
