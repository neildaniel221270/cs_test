#!/usr/bin/env python3
"""
compare_reports.py
==================
Read one .boundaries.json, one .segmented.json, and one .aligned.json file
and print a side-by-side comparison report.

Expected schemas (based on the current pipeline):
- boundaries.json:
    payload["step_boundaries"]["boundaries"]
- segmented.json:
    payload["semantic_segmentation"]["instructional_segments"]
- aligned.json:
    payload["micro_learning"]["steps"]

The script prints:
1. A short metadata summary
2. Counts of boundaries / segments / steps
3. A side-by-side row view aligned by sequence index
4. Coverage summaries
5. Simple timing deltas between methods where possible

Usage example:
python scripts\compare_reports.py \
  --boundaries_json "Data\\transcripts_boundaries\\video.boundaries.json" \
  --segmented_json  "Data\\transcripts_segmented\\video.segmented.json" \
  --aligned_json    "Data\\transcripts_aligned\\video.aligned.json"

Optional:
  --out_report "Data\\reports\\video_comparison.txt"
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_time(value: Optional[float]) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):.2f}s"
    except Exception:
        return str(value)



def safe_float(value: Any) -> Optional[float]:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None



def compact(text: Any, limit: int = 70) -> str:
    s = str(text or "").strip().replace("\n", " ")
    s = " ".join(s.split())
    if len(s) <= limit:
        return s
    return s[: limit - 3] + "..."



def interval_overlap(a_start: Optional[float], a_end: Optional[float], b_start: Optional[float], b_end: Optional[float]) -> Optional[float]:
    if None in (a_start, a_end, b_start, b_end):
        return None
    lo = max(a_start, b_start)
    hi = min(a_end, b_end)
    overlap = max(0.0, hi - lo)
    union = max(a_end, b_end) - min(a_start, b_start)
    if union <= 0:
        return None
    return overlap / union


# -----------------------------------------------------------------------------
# Extractors
# -----------------------------------------------------------------------------
def extract_boundaries(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    sb = payload.get("step_boundaries") or {}
    out = []
    for idx, b in enumerate(sb.get("boundaries") or [], start=1):
        out.append(
            {
                "index": idx,
                "boundary_id": b.get("boundary_id", idx),
                "timestamp": safe_float(b.get("timestamp")),
                "segment_index": b.get("segment_index"),
                "confidence": safe_float(b.get("confidence")),
                "previous": b.get("previous_step_summary"),
                "next": b.get("next_step_summary"),
                "reason": b.get("reason"),
            }
        )
    return out



def extract_segments(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    ss = payload.get("semantic_segmentation") or {}
    out = []
    for idx, s in enumerate(ss.get("instructional_segments") or [], start=1):
        out.append(
            {
                "index": idx,
                "segment_id": s.get("segment_id", idx),
                "start": safe_float(s.get("start")),
                "end": safe_float(s.get("end")),
                "start_segment_index": s.get("start_segment_index"),
                "end_segment_index": s.get("end_segment_index"),
                "text": s.get("text"),
            }
        )
    return out



def extract_steps(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    ml = payload.get("micro_learning") or {}
    out = []
    for idx, s in enumerate(ml.get("steps") or [], start=1):
        out.append(
            {
                "index": idx,
                "step_number": s.get("step_number", idx),
                "title": s.get("step_title"),
                "action": s.get("action"),
                "start": safe_float(s.get("timestamp_start_aligned", s.get("timestamp_start"))),
                "end": safe_float(s.get("timestamp_end_aligned", s.get("timestamp_end"))),
                "confidence": safe_float(s.get("alignment_confidence")),
                "evidence": s.get("alignment_evidence"),
            }
        )
    return out



def payload_meta(boundaries_payload: Dict[str, Any], segmented_payload: Dict[str, Any], aligned_payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": aligned_payload.get("id") or segmented_payload.get("id") or boundaries_payload.get("id"),
        "source_video": aligned_payload.get("source_video") or segmented_payload.get("source_video") or boundaries_payload.get("source_video"),
        "boundaries_model": ((boundaries_payload.get("boundary_detection") or {}).get("model")),
        "segmentation_engine": ((segmented_payload.get("semantic_segmentation") or {}).get("engine")),
        "segmentation_model": ((segmented_payload.get("semantic_segmentation") or {}).get("embedding_model")),
        "alignment_engine": ((aligned_payload.get("alignment") or {}).get("engine")),
    }


# -----------------------------------------------------------------------------
# Reporting
# -----------------------------------------------------------------------------
def make_side_by_side_rows(boundaries: List[Dict[str, Any]], segments: List[Dict[str, Any]], steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    n = max(len(boundaries), len(segments), len(steps))
    rows = []
    for i in range(n):
        b = boundaries[i] if i < len(boundaries) else None
        s = segments[i] if i < len(segments) else None
        st = steps[i] if i < len(steps) else None

        row = {
            "row": i + 1,
            "boundary_time": b.get("timestamp") if b else None,
            "boundary_conf": b.get("confidence") if b else None,
            "boundary_next": compact(b.get("next"), 55) if b else "-",
            "segment_range": f"{fmt_time(s.get('start'))} -> {fmt_time(s.get('end'))}" if s else "-",
            "segment_text": compact(s.get("text"), 55) if s else "-",
            "step_range": f"{fmt_time(st.get('start'))} -> {fmt_time(st.get('end'))}" if st else "-",
            "step_title": compact(st.get("title") or st.get("action"), 55) if st else "-",
            "boundary_vs_step_start_delta": None,
            "segment_vs_step_iou": None,
        }

        if b and st and b.get("timestamp") is not None and st.get("start") is not None:
            row["boundary_vs_step_start_delta"] = abs(b["timestamp"] - st["start"])

        if s and st:
            row["segment_vs_step_iou"] = interval_overlap(s.get("start"), s.get("end"), st.get("start"), st.get("end"))

        rows.append(row)
    return rows



def render_report(meta: Dict[str, Any], boundaries: List[Dict[str, Any]], segments: List[Dict[str, Any]], steps: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("COMPARISON REPORT")
    lines.append("=" * 100)
    lines.append(f"ID                : {meta.get('id')}")
    lines.append(f"Source video      : {meta.get('source_video')}")
    lines.append(f"Boundary model    : {meta.get('boundaries_model')}")
    lines.append(f"Segmentation      : {meta.get('segmentation_engine')} ({meta.get('segmentation_model')})")
    lines.append(f"Alignment engine  : {meta.get('alignment_engine')}")
    lines.append("")

    lines.append("COUNTS")
    lines.append("-" * 100)
    lines.append(f"LLM boundaries           : {len(boundaries)}")
    lines.append(f"Semantic segments        : {len(segments)}")
    lines.append(f"Aligned structured steps : {len(steps)}")
    lines.append("")

    rows = make_side_by_side_rows(boundaries, segments, steps)
    header = (
        f"{'#':<3} | {'LLM boundary':<18} | {'Boundary next step':<55} | "
        f"{'Semantic segment':<24} | {'Aligned step':<24}"
    )
    lines.append("SIDE-BY-SIDE OVERVIEW")
    lines.append("-" * 100)
    lines.append(header)
    lines.append("-" * len(header))
    for r in rows:
        b_time = fmt_time(r["boundary_time"])
        if r["boundary_conf"] is not None:
            b_time = f"{b_time} ({r['boundary_conf']:.2f})"
        lines.append(
            f"{r['row']:<3} | {b_time:<18} | {r['boundary_next']:<55} | "
            f"{r['segment_range']:<24} | {r['step_range']:<24}"
        )
        lines.append(
            f"    | {'':<18} | {'segment: ' + r['segment_text']:<55} | "
            f"{'step: ' + r['step_title']:<24} |"
        )
    lines.append("")

    lines.append("PAIRWISE TIMING COMPARISON")
    lines.append("-" * 100)
    for r in rows:
        delta = r["boundary_vs_step_start_delta"]
        iou = r["segment_vs_step_iou"]
        delta_str = f"{delta:.2f}s" if delta is not None else "-"
        iou_str = f"{iou:.2f}" if iou is not None else "-"
        lines.append(
            f"Row {r['row']}: boundary↔step-start delta = {delta_str}; segment↔step IoU = {iou_str}"
        )
    lines.append("")

    lines.append("DETAILED LLM BOUNDARIES")
    lines.append("-" * 100)
    if not boundaries:
        lines.append("No LLM boundaries found.")
    else:
        for b in boundaries:
            conf = f"{b['confidence']:.2f}" if b.get("confidence") is not None else "-"
            lines.append(
                f"[{b['index']}] t={fmt_time(b.get('timestamp'))}, seg={b.get('segment_index')}, conf={conf}"
            )
            lines.append(f"     prev : {compact(b.get('previous'), 120)}")
            lines.append(f"     next : {compact(b.get('next'), 120)}")
            lines.append(f"     why  : {compact(b.get('reason'), 140)}")
    lines.append("")

    lines.append("DETAILED SEMANTIC SEGMENTS")
    lines.append("-" * 100)
    if not segments:
        lines.append("No semantic segments found.")
    else:
        for s in segments:
            lines.append(
                f"[{s['index']}] {fmt_time(s.get('start'))} -> {fmt_time(s.get('end'))} | seg idx {s.get('start_segment_index')} -> {s.get('end_segment_index')}"
            )
            lines.append(f"     text : {compact(s.get('text'), 140)}")
    lines.append("")

    lines.append("DETAILED ALIGNED STEPS")
    lines.append("-" * 100)
    if not steps:
        lines.append("No aligned structured steps found.")
    else:
        for st in steps:
            conf = f"{st['confidence']:.2f}" if st.get("confidence") is not None else "-"
            lines.append(
                f"[{st['index']}] {fmt_time(st.get('start'))} -> {fmt_time(st.get('end'))} | step #{st.get('step_number')} | align_conf={conf}"
            )
            lines.append(f"     step : {compact(st.get('title') or st.get('action'), 140)}")
            evidence = st.get("evidence") or []
            if evidence:
                ev = ", ".join(str(x) for x in evidence[:12])
                lines.append(f"     ev   : {compact(ev, 140)}")
    lines.append("")

    # Simple summary paragraph
    lines.append("SUMMARY")
    lines.append("-" * 100)
    if len(boundaries) == len(steps) == len(segments):
        lines.append(
            "The three methods produced the same number of units, which makes sequence-level comparison straightforward."
        )
    else:
        lines.append(
            "The three methods produced different numbers of units. This may indicate different granularity between LLM boundaries, semantic segments, and structured steps."
        )

    deltas = [r["boundary_vs_step_start_delta"] for r in rows if r["boundary_vs_step_start_delta"] is not None]
    if deltas:
        avg_delta = sum(deltas) / len(deltas)
        lines.append(f"Average boundary-to-step-start delta: {avg_delta:.2f}s")

    ious = [r["segment_vs_step_iou"] for r in rows if r["segment_vs_step_iou"] is not None]
    if ious:
        avg_iou = sum(ious) / len(ious)
        lines.append(f"Average segment-to-step interval IoU: {avg_iou:.2f}")

    lines.append("=" * 100)
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Compare boundaries, semantic segments, and aligned steps")
    ap.add_argument("--boundaries_json", required=True, help="Path to *.boundaries.json")
    ap.add_argument("--segmented_json", required=True, help="Path to *.segmented.json")
    ap.add_argument("--aligned_json", required=True, help="Path to *.aligned.json")
    ap.add_argument("--out_report", default=None, help="Optional path to save the text report")
    args = ap.parse_args()

    boundaries_payload = load_json(Path(args.boundaries_json))
    segmented_payload = load_json(Path(args.segmented_json))
    aligned_payload = load_json(Path(args.aligned_json))

    boundaries = extract_boundaries(boundaries_payload)
    segments = extract_segments(segmented_payload)
    steps = extract_steps(aligned_payload)
    meta = payload_meta(boundaries_payload, segmented_payload, aligned_payload)

    report = render_report(meta, boundaries, segments, steps)
    print(report)

    if args.out_report:
        out_path = Path(args.out_report)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"\nSaved report to: {out_path}")


if __name__ == "__main__":
    main()

# python scripts\compare_reports.py --boundaries_json "Data\transcripts_boundaries\LMOS Introduction to the process.boundaries.json" --segmented_json "Data\transcripts_segmented\LMOS Introduction to the process.segmented.json" --aligned_json "Data\transcripts_aligned\LMOS Introduction to the process.aligned.json" --out_report "Data\reports\LMOS Introduction to the process.comparison.txt"