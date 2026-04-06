#!/usr/bin/env python3
"""
boundary_detection.py
=====================
Utility helpers for LLM-based step-boundary detection prompts.
This file does not call the LLM directly; it builds payloads compatible with your
LM Studio /chat/completions client from structure_batch.py.
"""
import json
from typing import Any, Dict, List

BOUNDARY_SCHEMA: Dict[str, Any] = {
    "title": "Optional short title for the transcript",
    "boundaries": [
        {
            "boundary_id": 1,
            "previous_step_summary": "What just finished",
            "next_step_summary": "What begins next",
            "timestamp": 12.5,
            "segment_index": 3,
            "confidence": 0.0,
            "reason": "Why a step transition happens here"
        }
    ]
}

BOUNDARY_SYSTEM_PROMPT = f"""
You are an ASML maintenance-training analyst.
Your task is to find step boundaries in a timestamped transcript.
A boundary exists where one technician action/check ends and the next begins.
Return only valid JSON in this schema:
{json.dumps(BOUNDARY_SCHEMA, indent=2)}
Rules:
- Use only evidence from the transcript.
- Prefer boundaries at timestamps already present in the transcript.
- Ignore filler narration and explanatory repetition.
- Use numeric seconds for timestamp.
- Confidence must be between 0 and 1.
""".strip()


def segments_to_block(segments: List[Dict[str, Any]], max_chars: int = 12000) -> str:
    lines = []
    for idx, seg in enumerate(segments):
        start = seg.get("start", "?")
        end = seg.get("end", "?")
        text = seg.get("text_clean") or seg.get("text") or ""
        text = str(text).strip()
        if text:
            lines.append(f"[{start} - {end}] (segment {idx}) {text}")
    block = "\n".join(lines)
    if len(block) > max_chars:
        block = block[:max_chars].rstrip() + "\n[... transcript truncated ...]"
    return block



def build_boundary_messages(segments: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    block = segments_to_block(segments)
    return [
        {
            "role": "user",
            "content": (
                f"{BOUNDARY_SYSTEM_PROMPT}\n\n"
                "Find all instructional step boundaries in this transcript.\n\n"
                f"=== TIMESTAMPED TRANSCRIPT ===\n\n{block}"
            ),
        }
    ]
