#!/usr/bin/env python3
"""
clean_transcript.py - Phase 1 & 2 of the micro-learning pipeline (GPT4All local GGUF)
=======================================================================================
Supports both:
1) single-file mode (--in_raw_json / --out_clean_json)
2) folder mode      (--in_dir / --out_dir)

Folder mode processes all matching JSON files and writes one *.clean.json per input.
"""
import argparse
import csv
import json
import os
import re
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GLOSSARY_CSV = str(REPO_ROOT / "Data" / "ASML Glossary.csv")
DEFAULT_GGUF_MODEL = os.getenv(
    "LOCAL_GGUF_MODEL",
    str(REPO_ROOT / "models" / "llm" / "Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"))
# ---------------------------------------------------------------------------
# 1. TEXT-CLEANING UTILITIES
# ---------------------------------------------------------------------------
FILLERS = {
    "um", "uh", "erm", "ah", "like", "you know",
    "i mean", "sort of", "kind of",
}
BASE_GLOSSARY_ENTRIES: List[Tuple[str, str, str]] = [
    ("ASML", "ASML", "abbr"),
    ("NXE", "NXE", "abbr"),
    ("EUV", "EUV", "abbr"),
    ("DUV", "DUV", "abbr"),
    ("HMI", "HMI", "abbr"),
    ("LMOS", "LMOS", "abbr"),
    ("TWINSCAN", "TWINSCAN", "abbr"),
    ("YieldStar", "YieldStar", "abbr"),
]


def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", str(s)).strip()


def remove_fillers(text: str) -> str:
    t = text
    for f in sorted(FILLERS, key=len, reverse=True):
        t = re.sub(rf"(?<!\w){re.escape(f)}(?!\w)", "", t, flags=re.IGNORECASE)
    return normalize_whitespace(t)


def is_safe_single_word_expansion(term: str) -> bool:
    term = normalize_whitespace(term)
    if not term:
        return False
    if term.isupper():
        return True
    if re.search(r"[0-9/-]", term):
        return True
    return False


def make_term_pattern(
    term: str,
    allow_spaced_letters: bool = False,
    ignore_case: bool = True,
) -> Optional[re.Pattern]:
    term = normalize_whitespace(term)
    if not term:
        return None
    flags = re.IGNORECASE if ignore_case else 0

    if allow_spaced_letters and re.fullmatch(r"[A-Za-z0-9]+", term):
        spaced = r"\s*".join(re.escape(ch) for ch in term)
        pattern = rf"(?<!\w)(?:{spaced}|{re.escape(term)})(?!\w)"
        return re.compile(pattern, flags)

    parts = [re.escape(p) for p in re.split(r"\s+", term) if p]
    if not parts:
        return None
    if len(parts) == 1:
        pattern = rf"(?<!\w){parts[0]}(?![\w'’\-])"
    else:
        pattern = rf"(?<!\w)" + r"\s+".join(parts) + rf"(?![\w'’\-])"
    return re.compile(pattern, flags)


def build_glossary_regex(entries: List[Tuple[str, str, str]]) -> List[Tuple[re.Pattern, str]]:
    compiled_entries = []
    seen = set()
    for source_term, replacement_term, kind in entries:
        source_term = normalize_whitespace(source_term)
        replacement_term = normalize_whitespace(replacement_term)
        if not source_term or not replacement_term:
            continue
        allow_spaced = (kind == "abbr")
        pat = make_term_pattern(
            source_term,
            allow_spaced_letters=allow_spaced,
            ignore_case=True,
        )
        if pat is None:
            continue
        key = (pat.pattern.lower(), replacement_term)
        if key in seen:
            continue
        compiled_entries.append((source_term, pat, replacement_term))
        seen.add(key)
    compiled_entries.sort(key=lambda x: len(x[0]), reverse=True)
    return [(pat, repl) for _, pat, repl in compiled_entries]


def load_glossary_entries_from_csv(csv_path: str) -> List[Tuple[str, str, str]]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Glossary CSV not found: {csv_path}")

    entries: List[Tuple[str, str, str]] = []
    with path.open("r", encoding="cp1252", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            abbr = normalize_whitespace(row.get("Abbreviation") or "")
            expanded = normalize_whitespace(row.get("Expanded Term") or "")
            if not abbr:
                continue
            entries.append((abbr, abbr, "abbr"))
            if expanded:
                num_words = len(re.split(r"\s+", expanded))
                if num_words >= 2 or is_safe_single_word_expansion(expanded):
                    entries.append((expanded, abbr, "expanded"))
    return entries


GLOSSARY_REGEX: List[Tuple[re.Pattern, str]] = build_glossary_regex(BASE_GLOSSARY_ENTRIES)
GLOSSARY_SOURCE = "built-in"


def apply_glossary(text: str) -> str:
    t = text
    for pat, repl in GLOSSARY_REGEX:
        t = pat.sub(repl, t)
    return t


def clean_text(text: str) -> str:
    t = normalize_whitespace(text)
    t = apply_glossary(t)
    t = remove_fillers(t)
    t = re.sub(r"\s+([,.!?;:])", r"\1", t)
    return t.strip()


def clean_word_token(token: str) -> str:
    return normalize_whitespace(token)


MICRO_LEARNING_SCHEMA = {
    "title": "Short descriptive title of the procedure or topic",
    "summary": "2-3 sentence overview of what this video segment covers",
    "procedure_type": "One of: maintenance | troubleshooting | calibration | inspection | replacement | overview | safety_briefing",
    "skill_level": "One of: beginner | intermediate | advanced",
    "estimated_duration_minutes": "Number - approximate duration of the procedure",
    "system_context": "Machine/subsystem this applies to, e.g. NXE:3400B - Wafer Stage",
    "safety_warnings": [{"severity": "One of: critical | warning | caution | info", "description": "What the technician must watch out for", "ppe_required": ["List of PPE items if mentioned"]}],
    "tools_required": [{"name": "Tool name", "specification": "Optional spec, e.g. 15 Nm torque"}],
    "components_referenced": ["List of ASML parts/subsystems mentioned"],
    "prerequisites": ["What must be done before starting"],
    "steps": [{"step_number": 1, "action": "Short imperative sentence", "details": "Extra detail or context from the transcript", "caution": "Optional per-step safety note"}],
    "key_terms": [{"term": "Domain-specific term used in the video", "definition": "Brief plain-language definition"}],
}
SYSTEM_PROMPT = f"""
You are an ASML maintenance-training content analyst.
Given a cleaned transcript from a maintenance training video, extract structured
micro-learning metadata as JSON.
Return ONLY valid JSON matching this schema:
{json.dumps(MICRO_LEARNING_SCHEMA, indent=2)}
Rules:
- If information is not present in the transcript, use null or an empty list [].
- Do NOT invent steps or safety warnings that are not mentioned or clearly implied.
- Keep the summary concise (2-3 sentences max).
- Steps should follow the chronological order of the transcript.
- Use ASML terminology exactly as it appears (EUV, NXE, DUV, HMI, LMOS, etc.).
- safety_warnings.severity:
  critical = electrical/laser/chemical hazards
  warning = risk of equipment damage
  caution = minor risks
  info = general notes
- procedure_type: pick the single best fit.
""".strip()


def load_local_llm(model_file: str, model_dir: str, n_ctx: int = 2048):
    from gpt4all import GPT4All
    return GPT4All(
        model_name=model_file,
        model_path=model_dir,
        allow_download=False,
        n_ctx=n_ctx,
        device="cpu",
        verbose=False,
    )


def parse_llm_json(raw: str) -> Optional[Dict[str, Any]]:
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        return None
    candidate = cleaned[start : end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def structure_transcript(
    segments: list,
    model_file: str,
    model_dir: str,
    max_chars: int,
    max_tokens: int,
    n_ctx: int,
) -> Dict[str, Any]:
    lines = []
    for seg in segments:
        start = seg.get("start", "?")
        end = seg.get("end", "?")
        text = seg.get("text_clean", seg.get("text", ""))
        lines.append(f"[{start} - {end}] {text}")
    transcript_block = "\n".join(lines)
    if len(transcript_block) > max_chars:
        transcript_block = transcript_block[:max_chars]

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        "=== CLEANED TRANSCRIPT ===\n\n"
        f"{transcript_block}\n\n"
        "Extract the micro-learning metadata as JSON."
    )

    llm = load_local_llm(model_file=model_file, model_dir=model_dir, n_ctx=n_ctx)
    max_retries = 2
    last_error = None
    for attempt in range(max_retries):
        try:
            raw = llm.generate(prompt, max_tokens=max_tokens, temp=0.1)
        except Exception as e:
            last_error = str(e)
            print(f"[!] Local GPT4All request failed (attempt {attempt + 1}/{max_retries}): {e}")
            continue

        parsed = parse_llm_json(raw)
        if parsed is not None:
            return parsed

        prompt = (
            "Your previous response was not valid JSON. "
            "Please respond ONLY with a single JSON object, no extra text.\n\n"
            + prompt
        )
        print(f"[!] Local GPT4All JSON parse failed (attempt {attempt + 1}/{max_retries}), retrying...")

    print("[!] Local GPT4All structuring failed after retries - using empty skeleton.")
    return {
        "title": None,
        "summary": None,
        "procedure_type": None,
        "skill_level": None,
        "estimated_duration_minutes": None,
        "system_context": None,
        "safety_warnings": [],
        "tools_required": [],
        "components_referenced": [],
        "prerequisites": [],
        "steps": [],
        "key_terms": [],
        "_structuring_error": last_error or "Local GPT4All did not return valid JSON",
    }


def configure_glossary(glossary_csv: Optional[str]) -> None:
    global GLOSSARY_REGEX, GLOSSARY_SOURCE
    if glossary_csv:
        csv_entries = load_glossary_entries_from_csv(glossary_csv)
        all_entries = list(BASE_GLOSSARY_ENTRIES) + csv_entries
        GLOSSARY_REGEX = build_glossary_regex(all_entries)
        GLOSSARY_SOURCE = glossary_csv
        print(f"Loaded glossary rules from: {glossary_csv} ({len(GLOSSARY_REGEX)} rules)")
    else:
        GLOSSARY_REGEX = build_glossary_regex(BASE_GLOSSARY_ENTRIES)
        GLOSSARY_SOURCE = "built-in"
        print(f"Using built-in glossary rules ({len(GLOSSARY_REGEX)} rules)")


def clean_payload(data: Dict[str, Any], args) -> Dict[str, Any]:
    for seg in data.get("segments", []):
        seg["text_raw"] = seg.get("text", "")
        seg["text_clean"] = clean_text(seg.get("text", ""))
        if "words" in seg:
            for w in seg["words"]:
                w["word_raw"] = w.get("word", "")
                w["word_clean"] = clean_word_token(w.get("word", ""))

    clean_payload: Dict[str, Any] = {
        "id": data.get("id"),
        "source_video": data.get("source_video"),
        "created_at": data.get("created_at"),
        "cleaned_at": datetime.now().isoformat(),
        "asr": data.get("asr"),
        "normalization": {
            "fillers_removed": True,
            "glossary_applied": True,
            "glossary_rules": len(GLOSSARY_REGEX),
            "glossary_source": GLOSSARY_SOURCE,
            "word_level_glossary_applied": False,
        },
        "segments": data.get("segments", []),
    }

    if args.structure:
        model_path = Path(args.gguf_model)
        model_file = model_path.name
        model_dir = str(model_path.parent)
        print(f"  Structuring with local GPT4All GGUF model: {args.gguf_model}")
        micro = structure_transcript(
            segments=data.get("segments", []),
            model_file=model_file,
            model_dir=model_dir,
            max_chars=args.structure_max_chars,
            max_tokens=args.llm_max_tokens,
            n_ctx=args.llm_ctx,
        )
        clean_payload["structured_at"] = datetime.now().isoformat()
        clean_payload["structuring"] = {
            "engine": "gpt4all",
            "model_path": args.gguf_model,
            "max_tokens": args.llm_max_tokens,
            "context_window": args.llm_ctx,
            "max_chars": args.structure_max_chars,
        }
        clean_payload["micro_learning"] = micro
    else:
        clean_payload["micro_learning"] = None
    return clean_payload


def derive_output_name(in_path: Path) -> str:
    name = in_path.name
    if name.endswith(".clean.json"):
        return name
    if name.endswith(".json"):
        name = name[:-5]
    return f"{name}.clean.json"


def iter_input_files(in_dir: Path, pattern: str, recursive: bool) -> List[Path]:
    files = sorted(in_dir.rglob(pattern) if recursive else in_dir.glob(pattern))
    return [p for p in files if p.is_file() and not p.name.endswith(".clean.json")]


def process_one(in_path: Path, out_path: Path, args) -> None:
    data = json.loads(in_path.read_text(encoding="utf-8"))
    out_payload = clean_payload(data, args)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Wrote clean JSON: {out_path}")


def main():
    ap = argparse.ArgumentParser(
        description="Clean ASR transcript(s) and optionally structure them with a local GPT4All GGUF model."
    )

    io = ap.add_argument_group("I/O")
    io.add_argument("--in_raw_json", help="Path to one raw ASR JSON from transcribe_batch.py")
    io.add_argument("--out_clean_json", help="Output path for single-file mode")
    io.add_argument("--in_dir", help="Folder of raw ASR JSON files")
    io.add_argument("--out_dir", help="Output folder for folder mode")
    io.add_argument("--pattern", default="*.json", help="Glob pattern for folder mode (default: *.json)")
    io.add_argument("--recursive", action="store_true", help="Recurse into subfolders in folder mode")
    io.add_argument("--force", action="store_true", help="Overwrite existing outputs in folder mode")
    io.add_argument("--dry_run", action="store_true", help="List files without processing them")
    io.add_argument("--delay", type=float, default=0.0, help="Optional delay between files in folder mode")
    io.add_argument("--glossary_csv", default=DEFAULT_GLOSSARY_CSV, help="Optional path to ASML Glossary CSV")

    ap.add_argument("--structure", action="store_true", help="Enable local GGUF-based structuring via GPT4All")
    ap.add_argument("--gguf_model", default=DEFAULT_GGUF_MODEL, help="Path to local GGUF model file")
    ap.add_argument("--llm_max_tokens", type=int, default=1024, help="Max generation tokens")
    ap.add_argument("--llm_ctx", type=int, default=4096, help="Context window")
    ap.add_argument("--structure_max_chars", type=int, default=8000, help="Maximum cleaned transcript characters sent to the local LLM")
    args = ap.parse_args()

    single_mode = bool(args.in_raw_json or args.out_clean_json)
    folder_mode = bool(args.in_dir or args.out_dir)
    if single_mode and folder_mode:
        raise SystemExit("Use either single-file mode (--in_raw_json/--out_clean_json) or folder mode (--in_dir/--out_dir), not both.")
    if not single_mode and not folder_mode:
        raise SystemExit("Provide either --in_raw_json and --out_clean_json, or --in_dir and --out_dir.")

    configure_glossary(args.glossary_csv)

    if single_mode:
        if not args.in_raw_json or not args.out_clean_json:
            raise SystemExit("Single-file mode requires both --in_raw_json and --out_clean_json")
        process_one(Path(args.in_raw_json), Path(args.out_clean_json), args)
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

    print(f"Found {len(files)} input file(s) in {in_dir}")
    ok = skipped = errors = 0
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
    print("CLEANING COMPLETE")
    print(f"OK: {ok}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")
    print(f"Output directory: {out_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()