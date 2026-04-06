#!/usr/bin/env python3
"""
structure_batch.py — Run LLM structuring on all cleaned transcripts
===================================================================
Reads every *.clean.json produced by the current pipeline and converts the
cleaned transcript into structured JSON using LM Studio (OpenAI-compatible).

Current setup compatibility (from test.md):
- Input comes from clean_transcript.py output in Data/transcripts_clean
- Expects cleaned transcript segments under payload["segments"]
- Uses text_clean when available, falling back to text
- Preserves id, source_video, asr metadata, and cleaned transcript segments
- Writes one *.structured.json per cleaned transcript plus a run_manifest.json

Usage examples
--------------
python scripts/structure_batch.py --in_dir Data/transcripts_clean --out_dir Data/transcripts_structured
python scripts/structure_batch.py --in_dir Data/transcripts_clean --out_dir Data/transcripts_structured --dry_run
python scripts/structure_batch.py --in_dir Data/transcripts_clean --out_dir Data/transcripts_structured --force
"""

import argparse
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Allow importing prompts.py when the script is run as: python scripts/structure_batch.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompts import build_structuring_messages, build_retry_messages  # noqa: E402


# ─────────────────────────────────────────────────────────────────────
# LM STUDIO CLIENT
# ─────────────────────────────────────────────────────────────────────
def call_lmstudio(
    messages,
    model,
    base_url,
    api_key=None,
    ssl_verify=True,
    timeout=240,
    temperature=0.1,
):

    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = json.dumps(
        {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
    ).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(url, data=payload, headers=headers)

    ctx = None
    if not ssl_verify:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            error_body = "<no response body>"

        # Extra debug info to show how big the request is
        total_chars = sum(len(str(m.get("content", ""))) for m in messages)
        roles = [m.get("role") for m in messages]

        raise RuntimeError(
            f"LM Studio returned HTTP {e.code} for {url}\\n"
            f"Message count: {len(messages)}\\n"
            f"Roles: {roles}\\n"
            f"Total prompt chars: {total_chars}\\n"
            f"Response body:\\n{error_body}"
        ) from e

    choices = body.get("choices") or []
    if choices:
        return choices[0].get("message", {}).get("content", "")
    return body.get("content", "")


# ─────────────────────────────────────────────────────────────────────
# JSON PARSING / NORMALISATION
# ─────────────────────────────────────────────────────────────────────
def parse_llm_json(raw: str) -> Optional[Dict[str, Any]]:
    """Robustly extract JSON from LLM output (handles fences and stray text)."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    candidate = cleaned[start : end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def empty_micro_learning(error_message: str, raw_output: str = "") -> Dict[str, Any]:
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
        "_structuring_error": error_message,
        "_raw_output": raw_output[:2000] if raw_output else "",
    }


def coerce_float(value: Any) -> Optional[float]:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def normalise_micro_learning(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalise likely model variations so downstream code gets a stable shape."""
    out = {
        "title": data.get("title"),
        "summary": data.get("summary"),
        "procedure_type": data.get("procedure_type"),
        "skill_level": data.get("skill_level"),
        "estimated_duration_minutes": coerce_float(data.get("estimated_duration_minutes")),
        "system_context": data.get("system_context"),
        "safety_warnings": data.get("safety_warnings") or [],
        "tools_required": data.get("tools_required") or [],
        "components_referenced": data.get("components_referenced") or [],
        "prerequisites": data.get("prerequisites") or [],
        "steps": [],
        "key_terms": data.get("key_terms") or [],
    }

    for idx, step in enumerate(data.get("steps") or [], start=1):
        if not isinstance(step, dict):
            continue
        step_number = step.get("step_number")
        if not isinstance(step_number, int):
            step_number = idx

        step_title = step.get("step_title")
        action = step.get("action")
        if not step_title and isinstance(action, str):
            step_title = action.rstrip(".")
        if not action and isinstance(step_title, str):
            action = step_title

        out["steps"].append(
            {
                "step_number": step_number,
                "step_title": step_title,
                "action": action,
                "details": step.get("details"),
                "caution": step.get("caution"),
                "timestamp_start": coerce_float(step.get("timestamp_start")),
                "timestamp_end": coerce_float(step.get("timestamp_end")),
            }
        )

    if "_structuring_error" in data:
        out["_structuring_error"] = data["_structuring_error"]
    if "_raw_output" in data:
        out["_raw_output"] = data.get("_raw_output", "")

    return out


# ─────────────────────────────────────────────────────────────────────
# TRANSCRIPT → PROMPT BLOCK
# ─────────────────────────────────────────────────────────────────────
def segments_to_transcript_block(segments: List[Dict[str, Any]], max_chars: int = 12000) -> str:
    """Convert cleaned segments into the timestamped text block expected by the prompt."""
    lines: List[str] = []
    for seg in segments:
        start = seg.get("start", "?")
        end = seg.get("end", "?")
        text = seg.get("text_clean") or seg.get("text") or ""
        text = str(text).strip()
        if not text:
            continue
        lines.append(f"[{start} - {end}] {text}")

    block = "\n".join(lines)
    if len(block) > max_chars:
        block = block[:max_chars].rstrip() + "\n[... transcript truncated ...]"
    return block


# ─────────────────────────────────────────────────────────────────────
# STRUCTURING (with retry)
# ─────────────────────────────────────────────────────────────────────
def structure_one(
    segments: List[Dict[str, Any]],
    model: str,
    base_url: str,
    api_key: Optional[str],
    ssl_verify: bool,
    timeout: int = 240,
    max_retries: int = 2,
    include_few_shot: bool = True,
    max_chars: int = 12000,
) -> Dict[str, Any]:
    """Structure a single transcript. Returns a parsed JSON dict or an error skeleton."""
    block = segments_to_transcript_block(segments, max_chars=max_chars)
    if not block.strip():
        return empty_micro_learning("No usable transcript text found in segments")

    messages = build_structuring_messages(block, include_few_shot=include_few_shot)
    last_raw = ""
    last_error = "LLM did not return valid JSON after retries"

    for attempt in range(max_retries + 1):
        try:
            raw = call_lmstudio(
                messages=messages,
                model=model,
                base_url=base_url,
                api_key=api_key,
                ssl_verify=ssl_verify,
                timeout=timeout,
            )
            last_raw = raw
        except Exception as exc:
            last_error = f"LLM request failed: {exc}"
            if attempt >= max_retries:
                return empty_micro_learning(last_error)
            print(f"  [!] Request failed (attempt {attempt + 1}/{max_retries + 1}): {exc}")
            time.sleep(1.0)
            continue

        parsed = parse_llm_json(raw)
        if parsed is not None:
            return normalise_micro_learning(parsed)

        last_error = "LLM did not return valid JSON after retries"
        if attempt >= max_retries:
            break

        print(f"  [!] JSON parse failed (attempt {attempt + 1}/{max_retries + 1}), retrying...")
        messages = build_retry_messages(
            block,
            raw,
            include_few_shot=include_few_shot,
        )

    return empty_micro_learning(last_error, last_raw)


# ─────────────────────────────────────────────────────────────────────
# BATCH PROCESSING
# ─────────────────────────────────────────────────────────────────────
def find_clean_jsons(in_dir: Path) -> List[Path]:
    """Find all *.clean.json files, sorted alphabetically."""
    return sorted(in_dir.glob("*.clean.json"))


def load_clean_payload(clean_path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    data = json.loads(clean_path.read_text(encoding="utf-8"))
    segments = data.get("segments") or []
    if not isinstance(segments, list):
        raise ValueError("payload['segments'] is not a list")
    return data, segments


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Batch-structure all cleaned transcripts via LM Studio."
    )

    # I/O
    ap.add_argument("--in_dir", required=True, help="Directory containing *.clean.json files")
    ap.add_argument(
        "--out_dir",
        default="Data/transcripts_structured",
        help="Directory where *.structured.json files will be written",
    )

    # LM Studio
    ap.add_argument("--model", default="mistralai/mistral-7b-instruct-v0.3")
    ap.add_argument("--base_url", default="http://localhost:1234/v1")
    ap.add_argument("--api_key", default=None)
    ap.add_argument("--no_ssl_verify", action="store_true")
    ap.add_argument(
        "--no_few_shot",
        action="store_true",
        help="Disable few-shot examples to reduce context size",
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=240,
        help="Timeout in seconds per LM Studio request",
    )
    ap.add_argument(
        "--max_chars",
        type=int,
        default=12000,
        help="Maximum number of transcript characters sent to the model",
    )

    # Behaviour
    ap.add_argument("--force", action="store_true", help="Re-process files even if output exists")
    ap.add_argument("--dry_run", action="store_true", help="List candidate files without calling the LLM")
    ap.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds to wait between requests",
    )
    ap.add_argument(
        "--max_retries",
        type=int,
        default=2,
        help="Retries after the first attempt for invalid JSON or request failures",
    )

    args = ap.parse_args()

    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {in_dir}")

    ssl_verify = not args.no_ssl_verify
    include_few_shot = not args.no_few_shot
    clean_files = find_clean_jsons(in_dir)

    if not clean_files:
        print(f"No *.clean.json files found in {in_dir}")
        return

    print(f"Found {len(clean_files)} cleaned transcript(s) in {in_dir}")
    print(f"Model: {args.model} @ {args.base_url}")
    print(f"Few-shot: {'ON' if include_few_shot else 'OFF'}")
    print(f"Output directory: {out_dir}\n")

    run_log: Dict[str, Any] = {
        "run_started": datetime.now().isoformat(),
        "model": args.model,
        "base_url": args.base_url,
        "few_shot": include_few_shot,
        "timeout": args.timeout,
        "max_chars": args.max_chars,
        "results": [],
    }
    stats = {"ok": 0, "skipped": 0, "error": 0}

    for i, clean_path in enumerate(clean_files, start=1):
        stem = clean_path.name.replace(".clean.json", "")
        out_path = out_dir / f"{stem}.structured.json"

        if out_path.exists() and not args.force:
            print(f"[{i}/{len(clean_files)}] SKIP (exists): {stem}")
            stats["skipped"] += 1
            run_log["results"].append({"id": stem, "status": "skipped", "reason": "exists"})
            continue

        if args.dry_run:
            print(f"[{i}/{len(clean_files)}] DRY RUN: {clean_path.name} -> {out_path.name}")
            continue

        print(f"[{i}/{len(clean_files)}] Processing: {stem}")
        t0 = time.time()

        try:
            data, segments = load_clean_payload(clean_path)
            if not segments:
                elapsed = time.time() - t0
                print("  [!] No segments found — skipping.")
                stats["skipped"] += 1
                run_log["results"].append(
                    {
                        "id": stem,
                        "status": "skipped",
                        "reason": "no_segments",
                        "elapsed_s": round(elapsed, 1),
                    }
                )
                continue

            micro = structure_one(
                segments=segments,
                model=args.model,
                base_url=args.base_url,
                api_key=args.api_key,
                ssl_verify=ssl_verify,
                timeout=args.timeout,
                max_retries=args.max_retries,
                include_few_shot=include_few_shot,
                max_chars=args.max_chars,
            )

            payload = {
                "id": data.get("id", stem),
                "source_video": data.get("source_video"),
                "source_clean_json": str(clean_path),
                "created_at": data.get("created_at"),
                "cleaned_at": data.get("cleaned_at"),
                "structured_at": datetime.now().isoformat(),
                "normalization": data.get("normalization"),
                "structuring": {
                    "engine": "lmstudio",
                    "model": args.model,
                    "base_url": args.base_url,
                    "few_shot": include_few_shot,
                    "timeout_seconds": args.timeout,
                    "max_chars": args.max_chars,
                },
                "asr": data.get("asr"),
                "segments": segments,
                "micro_learning": micro,
            }

            out_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            elapsed = time.time() - t0
            has_error = "_structuring_error" in micro
            status = "error_skeleton" if has_error else "ok"
            if has_error:
                stats["error"] += 1
            else:
                stats["ok"] += 1

            step_count = len(micro.get("steps") or [])
            print(f"  -> {status} | {step_count} steps | {elapsed:.1f}s | {out_path.name}")
            run_log["results"].append(
                {
                    "id": stem,
                    "status": status,
                    "steps": step_count,
                    "elapsed_s": round(elapsed, 1),
                    "output": str(out_path),
                }
            )

        except Exception as exc:
            elapsed = time.time() - t0
            stats["error"] += 1
            print(f"  [ERROR] {exc}")
            run_log["results"].append(
                {
                    "id": stem,
                    "status": "exception",
                    "error": str(exc),
                    "elapsed_s": round(elapsed, 1),
                }
            )

        if args.delay > 0 and i < len(clean_files):
            time.sleep(args.delay)

    run_log["run_finished"] = datetime.now().isoformat()
    run_log["stats"] = stats
    manifest_path = out_dir / "run_manifest.json"
    manifest_path.write_text(
        json.dumps(run_log, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 60)
    print("BATCH COMPLETE")
    print(f"OK: {stats['ok']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Errors: {stats['error']}")
    print(f"Manifest: {manifest_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
