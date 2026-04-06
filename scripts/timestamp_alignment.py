#!/usr/bin/env python3
"""
timestamp_alignment.py
======================
Post-hoc alignment between structured steps and Whisper word-level timestamps.
Now supports:
- single-file mode (--in_structured_json / --out_aligned_json)
- folder mode      (--in_dir / --out_dir)
"""
import argparse
import copy
import difflib
import json
import math
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "if",
    "in", "into", "is", "it", "of", "on", "or", "that", "the", "this", "to", "up",
    "use", "using", "with", "your", "you", "then", "than", "check", "make", "sure"
}


def normalize_text(text: str) -> str:
    text = str(text or "")
    text = text.replace("\u2019", "'")
    text = text.lower()
    text = re.sub(r"[^\w\s\-/]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    toks = []
    for tok in normalize_text(text).split():
        if tok in STOPWORDS:
            continue
        toks.append(tok)
    return toks


@dataclass
class WordItem:
    index: int
    segment_index: int
    start: float
    end: float
    word: str
    word_clean: str


def flatten_words(payload: Dict[str, Any]) -> List[WordItem]:
    words: List[WordItem] = []
    idx = 0
    for s_idx, seg in enumerate(payload.get("segments") or []):
        seg_words = seg.get("words") or []
        if seg_words:
            for w in seg_words:
                raw_word = w.get("word_clean") or w.get("word") or ""
                clean = normalize_text(raw_word)
                if not clean:
                    continue
                start = float(w.get("start", seg.get("start", 0.0)))
                end = float(w.get("end", seg.get("end", start)))
                words.append(WordItem(idx, s_idx, start, end, str(w.get("word") or raw_word), clean))
                idx += 1
        else:
            seg_text = seg.get("text_clean") or seg.get("text") or ""
            toks = tokenize(seg_text)
            if not toks:
                continue
            s = float(seg.get("start", 0.0))
            e = float(seg.get("end", s))
            dur = max(0.001, e - s)
            step = dur / max(1, len(toks))
            for i, tok in enumerate(toks):
                ws = s + i * step
                we = min(e, s + (i + 1) * step)
                words.append(WordItem(idx, s_idx, ws, we, tok, tok))
                idx += 1
    return words


def step_evidence_text(step: Dict[str, Any]) -> str:
    bits = [step.get("step_title"), step.get("action"), step.get("details"), step.get("caution")]
    joined = " ".join(str(x) for x in bits if x)
    return normalize_text(joined)


def score_window(step_tokens: List[str], window_tokens: List[str]) -> Tuple[float, Dict[str, float]]:
    if not step_tokens or not window_tokens:
        return 0.0, {"jaccard": 0.0, "containment": 0.0, "ratio": 0.0}
    sset = set(step_tokens)
    wset = set(window_tokens)
    inter = len(sset & wset)
    union = len(sset | wset) or 1
    jaccard = inter / union
    containment = inter / max(1, len(sset))
    ratio = difflib.SequenceMatcher(None, " ".join(step_tokens), " ".join(window_tokens)).ratio()
    score = 0.45 * containment + 0.35 * ratio + 0.20 * jaccard
    return score, {"jaccard": jaccard, "containment": containment, "ratio": ratio}


def build_candidate_spans(words: List[WordItem], anchor_start: Optional[float], anchor_end: Optional[float], search_margin: float, min_window_words: int, max_window_words: int) -> List[Tuple[int, int]]:
    if not words:
        return []
    candidate_indices = list(range(len(words)))
    if anchor_start is not None or anchor_end is not None:
        lo = -math.inf if anchor_start is None else anchor_start - search_margin
        hi = math.inf if anchor_end is None else anchor_end + search_margin
        candidate_indices = [i for i, w in enumerate(words) if (w.start <= hi and w.end >= lo)]
        if not candidate_indices:
            candidate_indices = list(range(len(words)))
    first = candidate_indices[0]
    last = candidate_indices[-1]
    spans: List[Tuple[int, int]] = []
    for i in range(first, last + 1):
        for j in range(i, min(last + 1, i + max_window_words)):
            n = j - i + 1
            if n < min_window_words:
                continue
            spans.append((i, j))
    return spans


def align_step(step: Dict[str, Any], words: List[WordItem], search_margin: float = 12.0, max_window_words: int = 80) -> Dict[str, Any]:
    evidence = step_evidence_text(step)
    step_tokens = tokenize(evidence)
    if not step_tokens:
        return {
            "timestamp_start_aligned": step.get("timestamp_start"),
            "timestamp_end_aligned": step.get("timestamp_end"),
            "alignment_confidence": 0.0,
            "alignment_method": "empty_step_text",
            "alignment_evidence": [],
        }
    anchor_start = step.get("timestamp_start")
    anchor_end = step.get("timestamp_end")
    if anchor_start is not None:
        anchor_start = float(anchor_start)
    if anchor_end is not None:
        anchor_end = float(anchor_end)
    min_window_words = max(4, min(20, len(step_tokens) // 2 + 2))
    spans = build_candidate_spans(words, anchor_start, anchor_end, search_margin, min_window_words, max_window_words)
    best = None
    best_score = -1.0
    best_parts = None
    for i, j in spans:
        window_tokens = [w.word_clean for w in words[i:j+1] if w.word_clean]
        score, parts = score_window(step_tokens, window_tokens)
        if anchor_start is not None and anchor_end is not None:
            center = 0.5 * (words[i].start + words[j].end)
            anchor_center = 0.5 * (anchor_start + anchor_end)
            dist = abs(center - anchor_center)
            score *= max(0.75, 1.0 - 0.01 * dist)
        if score > best_score:
            best_score = score
            best = (i, j)
            best_parts = parts
    if best is None:
        return {
            "timestamp_start_aligned": step.get("timestamp_start"),
            "timestamp_end_aligned": step.get("timestamp_end"),
            "alignment_confidence": 0.0,
            "alignment_method": "no_candidate",
            "alignment_evidence": [],
        }
    i, j = best
    matched_words = words[i:j+1]
    evidence_words = [w.word for w in matched_words[:20]]
    return {
        "timestamp_start_aligned": matched_words[0].start,
        "timestamp_end_aligned": matched_words[-1].end,
        "alignment_confidence": round(float(best_score), 4),
        "alignment_method": "lexical_window_match",
        "alignment_debug": best_parts,
        "alignment_word_span": {"start_index": matched_words[0].index, "end_index": matched_words[-1].index},
        "alignment_segment_span": {"start_segment": matched_words[0].segment_index, "end_segment": matched_words[-1].segment_index},
        "alignment_evidence": evidence_words,
    }


def monotonic_postprocess(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    prev_end = None
    for step in steps:
        s = step.get("timestamp_start_aligned")
        e = step.get("timestamp_end_aligned")
        if s is None or e is None:
            continue
        if prev_end is not None and s < prev_end:
            s = prev_end
            step["timestamp_start_aligned"] = s
        if e < s:
            step["timestamp_end_aligned"] = s
        prev_end = step.get("timestamp_end_aligned")
    return steps


def align_payload(payload: Dict[str, Any], search_margin: float = 12.0, max_window_words: int = 80) -> Dict[str, Any]:
    out = copy.deepcopy(payload)
    micro = out.setdefault("micro_learning", {})
    steps = micro.get("steps") or []
    words = flatten_words(out)
    aligned_steps: List[Dict[str, Any]] = []
    for step in steps:
        aligned = copy.deepcopy(step)
        aligned.update(align_step(step, words, search_margin=search_margin, max_window_words=max_window_words))
        aligned_steps.append(aligned)
    micro["steps"] = monotonic_postprocess(aligned_steps)
    out["alignment"] = {
        "engine": "posthoc_step_word_alignment",
        "search_margin_seconds": search_margin,
        "max_window_words": max_window_words,
        "word_count": len(words),
    }
    return out


def derive_output_name(in_path: Path) -> str:
    name = in_path.name
    if name.endswith(".aligned.json"):
        return name
    if name.endswith(".json"):
        name = name[:-5]
    return f"{name}.aligned.json"

def iter_input_files(in_dir: Path, pattern: str, recursive: bool) -> List[Path]:
    files = sorted(in_dir.rglob(pattern) if recursive else in_dir.glob(pattern))
    return [p for p in files if p.is_file() and not p.name.endswith(".aligned.json")]

def process_one(in_path: Path, out_path: Path, args) -> None:
    payload = json.loads(in_path.read_text(encoding="utf-8"))
    aligned = align_payload(payload, search_margin=args.search_margin, max_window_words=args.max_window_words)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(aligned, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Wrote aligned JSON: {out_path}")

def main() -> None:
    ap = argparse.ArgumentParser(description="Align structured step payload(s) to Whisper word timestamps")
    ap.add_argument("--in_structured_json", help="Single structured JSON input")
    ap.add_argument("--out_aligned_json", help="Single aligned JSON output")
    ap.add_argument("--in_dir", help="Input folder")
    ap.add_argument("--out_dir", help="Output folder")
    ap.add_argument("--pattern", default="*.json", help="Glob pattern for folder mode")
    ap.add_argument("--recursive", action="store_true", help="Recurse into subfolders")
    ap.add_argument("--force", action="store_true", help="Overwrite existing outputs in folder mode")
    ap.add_argument("--dry_run", action="store_true")
    ap.add_argument("--delay", type=float, default=0.0)
    ap.add_argument("--search_margin", type=float, default=12.0)
    ap.add_argument("--max_window_words", type=int, default=80)
    args = ap.parse_args()

    single_mode = bool(args.in_structured_json or args.out_aligned_json)
    folder_mode = bool(args.in_dir or args.out_dir)
    if single_mode and folder_mode:
        raise SystemExit("Use either single-file mode or folder mode, not both.")
    if not single_mode and not folder_mode:
        raise SystemExit("Provide either --in_structured_json and --out_aligned_json, or --in_dir and --out_dir.")

    if single_mode:
        if not args.in_structured_json or not args.out_aligned_json:
            raise SystemExit("Single-file mode requires both --in_structured_json and --out_aligned_json")
        process_one(Path(args.in_structured_json), Path(args.out_aligned_json), args)
        return

    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    if not in_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {in_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    files = iter_input_files(in_dir, args.pattern, args.recursive)
    if not files:
        print(f"No matching input files found in {in_dir} with pattern {args.pattern}")
        return

    ok = skipped = errors = 0
    print(f"Found {len(files)} input file(s) in {in_dir}")
    for idx, in_path in enumerate(files, start=1):
        rel = in_path.relative_to(in_dir) if args.recursive else Path(in_path.name)
        out_path = out_dir / rel.parent / derive_output_name(in_path)
        if out_path.exists() and not args.force:
            print(f"[{idx}/{len(files)}] SKIP (exists): {in_path.name}")
            skipped += 1
            continue
        if args.dry_run:
            print(f"[{idx}/{len(files)}] DRY RUN: {in_path} -> {out_path}")
            continue
        print(f"[{idx}/{len(files)}] Processing: {in_path.name}")
        try:
            process_one(in_path, out_path, args)
            ok += 1
        except Exception as exc:
            print(f"  [ERROR] {in_path.name}: {exc}")
            errors += 1
        if args.delay > 0 and idx < len(files):
            time.sleep(args.delay)

    print("\n" + "=" * 60)
    print("TIMESTAMP ALIGNMENT COMPLETE")
    print(f"OK: {ok}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")
    print(f"Output directory: {out_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()