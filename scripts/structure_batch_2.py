#!/usr/bin/env python3
"""
structure_batch_2.py — Batch local LLM processing for:
1) transcript -> structured micro-learning JSON
2) transcript -> step boundary JSON

llama-cpp-python version:
- Uses a local GGUF model file directly via llama-cpp-python (no server, no API)
- Optimised quantised CPU inference
- Loads the model once and reuses it across the batch
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from llama_cpp import Llama

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LLM_MODEL_PATH = os.getenv(
    "LOCAL_LLM_MODEL_PATH",
    str(REPO_ROOT / "models" / "llm" / "Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"),
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompts_2 import (  # noqa: E402
    build_structuring_messages,
    build_retry_messages,
    build_boundary_messages,
    build_boundary_retry_messages,
    segments_to_transcript_block,
    segments_to_boundary_block,
)

_LOCAL_MODEL = None
_LOCAL_MODEL_KEY = None


def get_local_gguf_model(
    model_path: Path,
    n_ctx: int = 4096,
    n_threads: Optional[int] = None,
) -> Llama:
    """Load and cache a local GGUF model via llama-cpp-python."""
    global _LOCAL_MODEL, _LOCAL_MODEL_KEY

    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"GGUF model file not found: {model_path}")
    if not model_path.is_file():
        raise ValueError(f"--model_path must point to a .gguf file, not a directory: {model_path}")

    if n_threads is None or n_threads <= 0:
        n_threads = max(1, (os.cpu_count() or 4) - 1)

    model_key = (str(model_path.resolve()), int(n_ctx), int(n_threads))

    if _LOCAL_MODEL is None or _LOCAL_MODEL_KEY != model_key:
        _LOCAL_MODEL = Llama(
            model_path=str(model_path),
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_gpu_layers=0,
            verbose=False,
        )
        _LOCAL_MODEL_KEY = model_key

    return _LOCAL_MODEL


def call_local_gguf(
    messages: List[Dict[str, Any]],
    model_path: Path,
    n_threads: Optional[int] = None,
    max_input_tokens: int = 4096,
    max_new_tokens: int = 1024,
    do_sample: bool = False,
    temperature: float = 0.2,
    top_p: float = 0.95,
) -> str:
    """Run inference against a local GGUF model via llama-cpp-python."""
    llm = get_local_gguf_model(
        model_path=model_path,
        n_ctx=max_input_tokens + max_new_tokens,
        n_threads=n_threads,
    )

    gen_kwargs: Dict[str, Any] = {
        "messages": messages,
        "max_tokens": max_new_tokens,
    }

    if do_sample:
        gen_kwargs["temperature"] = max(float(temperature), 1e-5)
        gen_kwargs["top_p"] = float(top_p)
    else:
        gen_kwargs["temperature"] = 0.0

    result = llm.create_chat_completion(**gen_kwargs)
    text = result["choices"][0]["message"]["content"]
    return (text or "").strip()


def parse_llm_json(raw: str) -> Optional[Dict[str, Any]]:
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    candidate = cleaned[start:end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def coerce_float(value: Any) -> Optional[float]:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def coerce_int(value: Any) -> Optional[int]:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except (TypeError, ValueError):
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


def normalise_micro_learning(data: Dict[str, Any]) -> Dict[str, Any]:
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

        step_number = step.get("step_number") if isinstance(step.get("step_number"), int) else idx
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


def empty_boundaries(error_message: str, raw_output: str = "") -> Dict[str, Any]:
    return {
        "title": None,
        "boundaries": [],
        "_boundary_error": error_message,
        "_raw_output": raw_output[:2000] if raw_output else "",
    }


def normalise_boundaries(data: Dict[str, Any]) -> Dict[str, Any]:
    out = {"title": data.get("title"), "boundaries": []}

    for idx, boundary in enumerate(data.get("boundaries") or [], start=1):
        if not isinstance(boundary, dict):
            continue

        boundary_id = boundary.get("boundary_id") if isinstance(boundary.get("boundary_id"), int) else idx
        confidence = coerce_float(boundary.get("confidence"))
        if confidence is not None:
            confidence = max(0.0, min(1.0, confidence))

        out["boundaries"].append(
            {
                "boundary_id": boundary_id,
                "previous_step_summary": boundary.get("previous_step_summary"),
                "next_step_summary": boundary.get("next_step_summary"),
                "timestamp": coerce_float(boundary.get("timestamp")),
                "segment_index": coerce_int(boundary.get("segment_index")),
                "confidence": confidence,
                "reason": boundary.get("reason"),
            }
        )

    if "_boundary_error" in data:
        out["_boundary_error"] = data["_boundary_error"]
    if "_raw_output" in data:
        out["_raw_output"] = data.get("_raw_output", "")
    return out


def structure_one(
    segments: List[Dict[str, Any]],
    model_path: str,
    timeout: int = 240,
    max_retries: int = 2,
    include_few_shot: bool = True,
    max_chars: int = 12000,
    max_input_tokens: int = 4096,
    max_new_tokens: int = 1024,
    cpu_threads: Optional[int] = None,
    trust_remote_code: bool = False,
    do_sample: bool = False,
    temperature: float = 0.2,
    top_p: float = 0.95,
) -> Dict[str, Any]:
    del timeout, trust_remote_code  # metadata parity only
    block = segments_to_transcript_block(segments, max_chars=max_chars)
    if not block.strip():
        return empty_micro_learning("No usable transcript text found in segments")

    messages = build_structuring_messages(block, include_few_shot=include_few_shot)
    last_raw = ""
    last_error = "Local GGUF model did not return valid JSON after retries"

    for attempt in range(max_retries + 1):
        try:
            raw = call_local_gguf(
                messages=messages,
                model_path=Path(model_path),
                n_threads=cpu_threads,
                max_input_tokens=max_input_tokens,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                temperature=temperature,
                top_p=top_p,
            )
            last_raw = raw
        except Exception as exc:
            last_error = f"Local model inference failed: {exc}"
            if attempt >= max_retries:
                return empty_micro_learning(last_error)
            print(f"  [!] Request failed (attempt {attempt + 1}/{max_retries + 1}): {exc}")
            time.sleep(1.0)
            continue

        parsed = parse_llm_json(raw)
        if parsed is not None:
            return normalise_micro_learning(parsed)

        if attempt >= max_retries:
            break

        print(f"  [!] JSON parse failed (attempt {attempt + 1}/{max_retries + 1}), retrying...")
        messages = build_retry_messages(block, raw, include_few_shot=include_few_shot)

    return empty_micro_learning(last_error, last_raw)


def detect_boundaries_one(
    segments: List[Dict[str, Any]],
    model_path: str,
    timeout: int = 240,
    max_retries: int = 2,
    include_few_shot: bool = True,
    max_chars: int = 12000,
    max_input_tokens: int = 4096,
    max_new_tokens: int = 1024,
    cpu_threads: Optional[int] = None,
    trust_remote_code: bool = False,
    do_sample: bool = False,
    temperature: float = 0.2,
    top_p: float = 0.95,
) -> Dict[str, Any]:
    del timeout, trust_remote_code  # metadata parity only
    block = segments_to_boundary_block(segments, max_chars=max_chars)
    if not block.strip():
        return empty_boundaries("No usable transcript text found in segments")

    messages = build_boundary_messages(block, include_few_shot=include_few_shot)
    last_raw = ""
    last_error = "Local GGUF model did not return valid JSON after retries"

    for attempt in range(max_retries + 1):
        try:
            raw = call_local_gguf(
                messages=messages,
                model_path=Path(model_path),
                n_threads=cpu_threads,
                max_input_tokens=max_input_tokens,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                temperature=temperature,
                top_p=top_p,
            )
            last_raw = raw
        except Exception as exc:
            last_error = f"Local model inference failed: {exc}"
            if attempt >= max_retries:
                return empty_boundaries(last_error)
            print(f"  [!] Request failed (attempt {attempt + 1}/{max_retries + 1}): {exc}")
            time.sleep(1.0)
            continue

        parsed = parse_llm_json(raw)
        if parsed is not None:
            return normalise_boundaries(parsed)

        if attempt >= max_retries:
            break

        print(f"  [!] JSON parse failed (attempt {attempt + 1}/{max_retries + 1}), retrying...")
        messages = build_boundary_retry_messages(block, raw, include_few_shot=include_few_shot)

    return empty_boundaries(last_error, last_raw)


def find_clean_jsons(in_dir: Path, pattern: str = "*.clean.json", recursive: bool = False) -> List[Path]:
    return sorted(in_dir.rglob(pattern) if recursive else in_dir.glob(pattern))


def load_clean_payload(clean_path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    data = json.loads(clean_path.read_text(encoding="utf-8"))
    segments = data.get("segments") or []
    if not isinstance(segments, list):
        raise ValueError("payload['segments'] is not a list")
    return data, segments


def build_output_payload_structure(
    data: Dict[str, Any],
    clean_path: Path,
    model_path: str,
    include_few_shot: bool,
    timeout: int,
    max_chars: int,
    max_input_tokens: int,
    max_new_tokens: int,
    cpu_threads: Optional[int],
    trust_remote_code: bool,
    do_sample: bool,
    temperature: float,
    top_p: float,
    micro: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "id": data.get("id"),
        "source_video": data.get("source_video"),
        "source_clean_json": str(clean_path),
        "created_at": data.get("created_at"),
        "cleaned_at": data.get("cleaned_at"),
        "structured_at": datetime.now().isoformat(),
        "normalization": data.get("normalization"),
        "structuring": {
            "engine": "llama_cpp_local",
            "mode": "structure",
            "model_path": str(model_path),
            "few_shot": include_few_shot,
            "timeout_seconds": timeout,
            "max_chars": max_chars,
            "max_input_tokens": max_input_tokens,
            "max_new_tokens": max_new_tokens,
            "cpu_threads": cpu_threads,
            "trust_remote_code": trust_remote_code,
            "do_sample": do_sample,
            "temperature": temperature,
            "top_p": top_p,
        },
        "asr": data.get("asr"),
        "segments": data.get("segments"),
        "micro_learning": micro,
    }


def build_output_payload_boundary(
    data: Dict[str, Any],
    clean_path: Path,
    model_path: str,
    include_few_shot: bool,
    timeout: int,
    max_chars: int,
    max_input_tokens: int,
    max_new_tokens: int,
    cpu_threads: Optional[int],
    trust_remote_code: bool,
    do_sample: bool,
    temperature: float,
    top_p: float,
    boundaries: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "id": data.get("id"),
        "source_video": data.get("source_video"),
        "source_clean_json": str(clean_path),
        "created_at": data.get("created_at"),
        "cleaned_at": data.get("cleaned_at"),
        "boundaries_at": datetime.now().isoformat(),
        "normalization": data.get("normalization"),
        "boundary_detection": {
            "engine": "llama_cpp_local",
            "mode": "boundary",
            "model_path": str(model_path),
            "few_shot": include_few_shot,
            "timeout_seconds": timeout,
            "max_chars": max_chars,
            "max_input_tokens": max_input_tokens,
            "max_new_tokens": max_new_tokens,
            "cpu_threads": cpu_threads,
            "trust_remote_code": trust_remote_code,
            "do_sample": do_sample,
            "temperature": temperature,
            "top_p": top_p,
        },
        "asr": data.get("asr"),
        "segments": data.get("segments"),
        "step_boundaries": boundaries,
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Batch-process cleaned transcripts via a local GGUF model using llama-cpp-python (no API server required)."
    )
    ap.add_argument("--in_dir", required=True, help="Directory containing *.clean.json files")
    ap.add_argument("--out_dir", default=None, help="Directory where output files will be written. Defaults depend on --mode.")
    ap.add_argument("--pattern", default="*.clean.json", help="Input glob pattern (default: *.clean.json)")
    ap.add_argument("--recursive", action="store_true", help="Recurse into subfolders when scanning the input folder")
    ap.add_argument("--mode", choices=["structure", "boundary"], default="structure", help="Run structured micro-learning extraction or boundary detection.")
    ap.add_argument("--model_path", default=DEFAULT_LLM_MODEL_PATH, help="Path to local .gguf model file")
    ap.add_argument("--cpu_threads", type=int, default=None, help="CPU threads for llama-cpp (default: cpu_count - 1)")
    ap.add_argument("--trust_remote_code", action="store_true", help="(Unused, kept for CLI parity)")
    ap.add_argument("--no_few_shot", action="store_true", help="Disable few-shot examples to reduce context size")
    ap.add_argument("--timeout", type=int, default=240, help="Metadata-only timeout value for parity with previous script")
    ap.add_argument("--max_chars", type=int, default=12000, help="Maximum number of transcript characters inserted into the prompt block")
    ap.add_argument("--max_input_tokens", type=int, default=4096, help="Maximum input tokens passed to the local model after tokenization/truncation")
    ap.add_argument("--max_new_tokens", type=int, default=1024, help="Maximum newly generated tokens from the local model")
    ap.add_argument("--do_sample", action="store_true", help="Enable sampling instead of greedy decoding (not recommended for strict JSON output)")
    ap.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature (used only when --do_sample is set)")
    ap.add_argument("--top_p", type=float, default=0.95, help="Top-p nucleus sampling value (used only when --do_sample is set)")
    ap.add_argument("--force", action="store_true", help="Re-process files even if output exists")
    ap.add_argument("--dry_run", action="store_true", help="List candidate files without calling the model")
    ap.add_argument("--delay", type=float, default=1.0, help="Seconds to wait between files")
    ap.add_argument("--max_retries", type=int, default=2, help="Retries after the first attempt for invalid JSON or local inference failures")
    args = ap.parse_args()

    in_dir = Path(args.in_dir)
    if not in_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {in_dir}")

    model_path = Path(args.model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"GGUF model file does not exist: {model_path}")
    if not model_path.is_file():
        raise ValueError(f"--model_path must point to a .gguf file, not a directory: {model_path}")

    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        out_dir = Path("Data/transcripts_structured") if args.mode == "structure" else Path("Data/transcripts_boundaries")
    out_dir.mkdir(parents=True, exist_ok=True)

    include_few_shot = not args.no_few_shot
    clean_files = find_clean_jsons(in_dir, pattern=args.pattern, recursive=args.recursive)

    if not clean_files:
        print(f"No matching files found in {in_dir} with pattern {args.pattern}")
        return

    print(f"Found {len(clean_files)} cleaned transcript(s) in {in_dir}")
    print(f"Mode: {args.mode}")
    print(f"GGUF model: {model_path}")
    print(f"Few-shot: {'ON' if include_few_shot else 'OFF'}")
    print(f"CPU threads: {args.cpu_threads if args.cpu_threads is not None else 'auto'}")
    print(f"Max input tokens: {args.max_input_tokens}")
    print(f"Max new tokens: {args.max_new_tokens}")
    print(f"Sampling: {'ON' if args.do_sample else 'OFF'}")
    print(f"Output directory: {out_dir}\n")

    if not args.dry_run:
        print("Loading GGUF model via llama-cpp-python...")
        _ = get_local_gguf_model(
            model_path=model_path,
            n_ctx=args.max_input_tokens + args.max_new_tokens,
            n_threads=args.cpu_threads,
        )
        print("Model loaded.\n")

    run_log: Dict[str, Any] = {
        "run_started": datetime.now().isoformat(),
        "mode": args.mode,
        "engine": "llama_cpp_local",
        "model_path": str(model_path),
        "few_shot": include_few_shot,
        "timeout": args.timeout,
        "max_chars": args.max_chars,
        "max_input_tokens": args.max_input_tokens,
        "max_new_tokens": args.max_new_tokens,
        "cpu_threads": args.cpu_threads,
        "trust_remote_code": args.trust_remote_code,
        "do_sample": args.do_sample,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "results": [],
    }

    stats = {"ok": 0, "skipped": 0, "error": 0}

    for i, clean_path in enumerate(clean_files, start=1):
        rel = clean_path.relative_to(in_dir) if args.recursive else Path(clean_path.name)
        stem = rel.name.replace(".clean.json", "")
        suffix = ".structured.json" if args.mode == "structure" else ".boundaries.json"
        out_path = out_dir / rel.parent / f"{stem}{suffix}"

        if out_path.exists() and not args.force:
            print(f"[{i}/{len(clean_files)}] SKIP (exists): {rel}")
            stats["skipped"] += 1
            run_log["results"].append({"id": stem, "status": "skipped", "reason": "exists"})
            continue

        if args.dry_run:
            print(f"[{i}/{len(clean_files)}] DRY RUN: {clean_path.name} -> {out_path}")
            continue

        print(f"[{i}/{len(clean_files)}] Processing: {rel}")
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

            if args.mode == "structure":
                micro = structure_one(
                    segments=segments,
                    model_path=str(model_path),
                    timeout=args.timeout,
                    max_retries=args.max_retries,
                    include_few_shot=include_few_shot,
                    max_chars=args.max_chars,
                    max_input_tokens=args.max_input_tokens,
                    max_new_tokens=args.max_new_tokens,
                    cpu_threads=args.cpu_threads,
                    trust_remote_code=args.trust_remote_code,
                    do_sample=args.do_sample,
                    temperature=args.temperature,
                    top_p=args.top_p,
                )
                payload = build_output_payload_structure(
                    data=data,
                    clean_path=clean_path,
                    model_path=str(model_path),
                    include_few_shot=include_few_shot,
                    timeout=args.timeout,
                    max_chars=args.max_chars,
                    max_input_tokens=args.max_input_tokens,
                    max_new_tokens=args.max_new_tokens,
                    cpu_threads=args.cpu_threads,
                    trust_remote_code=args.trust_remote_code,
                    do_sample=args.do_sample,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    micro=micro,
                )
                has_error = "_structuring_error" in micro
                item_count = len(micro.get("steps") or [])
                label = "steps"
            else:
                boundaries = detect_boundaries_one(
                    segments=segments,
                    model_path=str(model_path),
                    timeout=args.timeout,
                    max_retries=args.max_retries,
                    include_few_shot=include_few_shot,
                    max_chars=args.max_chars,
                    max_input_tokens=args.max_input_tokens,
                    max_new_tokens=args.max_new_tokens,
                    cpu_threads=args.cpu_threads,
                    trust_remote_code=args.trust_remote_code,
                    do_sample=args.do_sample,
                    temperature=args.temperature,
                    top_p=args.top_p,
                )
                payload = build_output_payload_boundary(
                    data=data,
                    clean_path=clean_path,
                    model_path=str(model_path),
                    include_few_shot=include_few_shot,
                    timeout=args.timeout,
                    max_chars=args.max_chars,
                    max_input_tokens=args.max_input_tokens,
                    max_new_tokens=args.max_new_tokens,
                    cpu_threads=args.cpu_threads,
                    trust_remote_code=args.trust_remote_code,
                    do_sample=args.do_sample,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    boundaries=boundaries,
                )
                has_error = "_boundary_error" in boundaries
                item_count = len(boundaries.get("boundaries") or [])
                label = "boundaries"

            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

            elapsed = time.time() - t0
            status = "error_skeleton" if has_error else "ok"
            stats["error" if has_error else "ok"] += 1

            print(f"  -> {status} | {item_count} {label} | {elapsed:.1f}s | {out_path.name}")
            run_log["results"].append(
                {
                    "id": stem,
                    "status": status,
                    label: item_count,
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

    manifest_name = "run_manifest.structure.json" if args.mode == "structure" else "run_manifest.boundary.json"
    manifest_path = out_dir / manifest_name
    manifest_path.write_text(json.dumps(run_log, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print("BATCH COMPLETE")
    print(f"Mode: {args.mode}")
    print(f"OK: {stats['ok']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Errors: {stats['error']}")
    print(f"Manifest: {manifest_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()

# Structure mode
# python scripts\structure_batch_2.py --in_dir "Data\transcripts_clean" --out_dir "Data\transcripts_structured" --pattern "*.clean.json" --mode structure --model_path "models\llm\Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf" --cpu_threads 8 --max_input_tokens 4096 --max_new_tokens 1024 --force

# Boundary mode
# python scripts\structure_batch_2.py --in_dir "Data\transcripts_clean" --out_dir "Data\transcripts_boundaries" --pattern "*.clean.json" --mode boundary --model_path "models\llm\Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf" --cpu_threads 8 --max_input_tokens 4096 --max_new_tokens 1024 --force