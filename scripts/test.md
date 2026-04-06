## Script: `scripts/extract_audio.py`

```python
#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}

def run(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def ffprobe_streams(path: Path) -> Dict[str, Any]:
    # ffprobe can output JSON, useful for detecting streams programmatically. 
    cmd = [
        "ffprobe", "-v", "error",
        "-show_streams", "-show_format",
        "-of", "json",
        str(path)
    ]
    p = run(cmd)
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}:\n{p.stderr}")
    return json.loads(p.stdout)

def has_stream(meta: Dict[str, Any], codec_type: str) -> bool:
    return any(s.get("codec_type") == codec_type for s in meta.get("streams", []))

def extract_wav(video_path: Path, wav_path: Path) -> None:
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    # A common robust extraction pattern is using ffmpeg and re-encoding to WAV. 
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        str(wav_path)
    ]
    p = run(cmd)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg audio extract failed for {video_path}:\n{p.stderr}")

def extract_subtitles(video_path: Path, out_path: Path) -> Optional[Path]:
    """
    Try extracting the first subtitle stream, if any.
    Writes .srt if possible.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Map the first subtitle stream (0:s:0) if present.
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-map", "0:s:0",
        str(out_path)
    ]
    p = run(cmd)
    if p.returncode == 0 and out_path.exists() and out_path.stat().st_size > 0:
        return out_path
    return None

def find_sidecar_sub(video_path: Path) -> Optional[Path]:
    for ext in [".srt", ".vtt"]:
        candidate = video_path.with_suffix(ext)
        if candidate.exists():
            return candidate
    return None

def iter_videos(in_dir: Path, recursive: bool = True) -> List[Path]:
    if in_dir.is_file() and in_dir.suffix.lower() in VIDEO_EXTS:
        return [in_dir]
    pattern = "**/*" if recursive else "*"
    return [p for p in in_dir.glob(pattern) if p.suffix.lower() in VIDEO_EXTS]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Video file or directory")
    ap.add_argument("--out_audio_dir", default="Data/processed/audio_wav")
    ap.add_argument("--out_sub_dir", default="Data/processed/subtitles")
    ap.add_argument("--manifest", default="Data/processed/manifest.jsonl")
    ap.add_argument("--no_recursive", action="store_true")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_audio = Path(args.out_audio_dir)
    out_sub = Path(args.out_sub_dir)
    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    videos = iter_videos(in_path, recursive=not args.no_recursive)

    with manifest_path.open("w", encoding="utf-8") as mf:
        for vp in videos:
            rec = {
                "video": str(vp),
                "status": "pending",
                "audio_wav": None,
                "subtitle": None,
                "notes": []
            }
            try:
                meta = ffprobe_streams(vp)
                has_audio = has_stream(meta, "audio")
                has_subs = has_stream(meta, "subtitle")

                if has_audio:
                    wav_path = out_audio / (vp.stem + ".wav")
                    extract_wav(vp, wav_path)
                    rec["audio_wav"] = str(wav_path)
                    rec["notes"].append("audio_extracted_wav_16k_mono")

                else:
                    rec["notes"].append("no_audio_stream_detected")

                    # Prefer sidecar subtitles first if present
                    sidecar = find_sidecar_sub(vp)
                    if sidecar:
                        rec["subtitle"] = str(sidecar)
                        rec["notes"].append("using_sidecar_subtitles")
                    elif has_subs:
                        sub_path = out_sub / (vp.stem + ".srt")
                        extracted = extract_subtitles(vp, sub_path)
                        if extracted:
                            rec["subtitle"] = str(extracted)
                            rec["notes"].append("embedded_subtitles_extracted")
                        else:
                            rec["notes"].append("subtitle_extract_failed")
                    else:
                        rec["notes"].append("no_subtitle_stream_detected")

                rec["status"] = "ok"

            except Exception as e:
                rec["status"] = "error"
                rec["notes"].append(str(e))

            mf.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Done. Manifest written to: {manifest_path}")

if __name__ == "__main__":
    main()
```

### Usage

```bash
# Extract audio (and subtitles where needed) from a folder:
python scripts/extract_audio.py --input Data/raw_videos --manifest Data/processed/manifest.jsonl
```

## Script: `scripts/transcribe_batch.py`

```python
#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WHISPER_MODEL = os.getenv(
    "WHISPER_MODEL",
    str(REPO_ROOT / "models" / "whisper" / "medium.en.pt")
)


def load_manifest(manifest_path: Path):
    with manifest_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def load_whisper_model(model_path: str, device: str = "cpu"):
    import whisper
    return whisper.load_model(model_path, device=device)


def transcribe_audio(
    model,
    audio_path: Path,
    language: str,
    initial_prompt: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    result = model.transcribe(
        str(audio_path),
        language=language,
        initial_prompt=initial_prompt,
        temperature=0.0,
        verbose=False,
        word_timestamps=True,
    )

    out_segments: List[Dict[str, Any]] = []
    for s in result.get("segments", []):
        seg = {
            "start": float(s.get("start", 0.0)),
            "end": float(s.get("end", 0.0)),
            "text": str(s.get("text", "")).strip(),
        }
        words = s.get("words") or []
        if words:
            seg["words"] = [
                {
                    "start": float(w.get("start", seg["start"])),
                    "end": float(w.get("end", seg["end"])),
                    "word": str(w.get("word", "")).strip(),
                }
                for w in words
                if str(w.get("word", "")).strip()
            ]
        out_segments.append(seg)
    meta = {
        "language": result.get("language", language),
        "language_probability": None,
        "duration": None,
    }
    return out_segments, meta

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out_dir", default="Data/transcripts_raw")
    ap.add_argument(
        "--model",
        default=DEFAULT_WHISPER_MODEL,
        help="Path to local Whisper .pt model or a Whisper model name",
    )
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--language", default="en")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument(
        "--initial_prompt",
        default="ASML maintenance training. Use correct terms like wafer, reticle, pellicle, EUV, DUV, NXE, HMI, LMOS.",
    )
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Using local Whisper model: {args.model}")
    model = load_whisper_model(args.model, device=args.device)

    n = 0
    for rec in load_manifest(Path(args.manifest)):
        if n >= args.limit:
            break
        audio_wav = rec.get("audio_wav")
        if not audio_wav:
            continue

        audio_path = Path(audio_wav)
        if not audio_path.exists():
            continue

        video_stem = Path(rec["video"]).stem
        segments, meta = transcribe_audio(
            model,
            audio_path,
            args.language,
            args.initial_prompt,
        )

        payload = {
            "id": video_stem,
            "source_video": rec["video"],
            "source_audio": str(audio_path),
            "created_at": datetime.now().isoformat(),
            "asr": {
                "engine": "openai-whisper-local",
                "model": args.model,
                "language": args.language,
                "meta": meta,
            },
            "segments": segments,
        }

        out_path = out_dir / f"{video_stem}.raw.json"
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Wrote: {out_path}")
        n += 1

if __name__ == "__main__":
    main()
```

### Run on 5–10 videos

```bash
python scripts\transcribe_batch.py --manifest "Data\processed\manifest.jsonl" --out_dir "Data\transcripts_raw" --model "models\whisper\medium.en.pt" --device cpu --language en --limit 10
```

***

## Script: `scripts/eval_wer.py`

```python
#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import jiwer

def transcript_to_text(raw_json_path: Path) -> str:
    data = json.loads(raw_json_path.read_text(encoding="utf-8"))
    # Concatenate segments; for WER you want consistent normalization
    return " ".join(seg["text"].strip() for seg in data["segments"]).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref_txt", required=True, help="Reference (ground truth) .txt")
    ap.add_argument("--hyp_raw_json", required=True, help="ASR output raw.json")
    args = ap.parse_args()

    ref = Path(args.ref_txt).read_text(encoding="utf-8").strip()
    hyp = transcript_to_text(Path(args.hyp_raw_json))

    # jiwer.process_words gives metrics + error counts + alignments. 
    out = jiwer.process_words(ref, hyp)

    print("==== WER Report ====")
    print(f"WER: {out.wer:.4f}")
    print(f"Substitutions: {out.substitutions}")
    print(f"Deletions:     {out.deletions}")
    print(f"Insertions:    {out.insertions}")
    print(f"Hits:          {out.hits}")
    print("\nAlignment visualization:\n")
    print(jiwer.visualize_alignment(out))

if __name__ == "__main__":
    main()
```

### Usage

```bash
# Create a reference text file by manually correcting:
# Data/references/LMOS_Intro.ref.txt

python scripts/eval_wer.py --ref_txt "Data/references/LMOS Introduction to the process.ref.txt" --hyp_raw_json "Data/transcripts_raw/LMOS Introduction to the process.raw.json"
```

***

## Script: `scripts/clean_transcript.py`

```python
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
```

### Usage

```bash
python scripts\clean_transcript.py --in_dir "Data\transcripts_raw" --out_dir "Data\transcripts_clean" --pattern "*.raw.json" --glossary_csv "Data\ASML Glossary.csv" --structure_max_chars 6000
```

## Script: `scripts/structure_batch_2.py` (Structure Mode)

```python
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
```

### Usage

```bash
python scripts\structure_batch_2.py --in_dir "Data\transcripts_clean" --out_dir "Data\transcripts_structured" --pattern "*.clean.json" --mode structure --model_path "models\llm\Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf" --cpu_threads 8 --max_input_tokens 4096 --max_new_tokens 1024 --force
```

***

## Script: `scripts/timestamp_alignment.py`

```python
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

```

### Usage

```bash
python scripts\timestamp_alignment.py --in_dir "Data\transcripts_structured" --out_dir "Data\transcripts_aligned" --pattern "*.structured.json" --force
```

***

## Script: `scripts/semantic_segmentation.py`

```python
#!/usr/bin/env python3
"""
semantic_segmentation.py
========================
Semantic segmentation of transcript chunks into coherent instructional segments.

Offline-first version:
- supports single-file mode (--in_json / --out_json)
- supports folder mode (--in_dir / --out_dir)
- uses a local Hugging Face model folder for embeddings by default
- avoids network calls entirely
"""

import argparse
import json
import os
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]

# Preferred local embedding model locations
LOCAL_EMBED_MODEL_MODELS = REPO_ROOT / "models" / "embeddings" / "all-MiniLM-L6-v2"
LOCAL_EMBED_MODEL_DATA = REPO_ROOT / "Data" / "embeddings" / "all-MiniLM-L6-v2"

# Local HF LLM folder you already have
LOCAL_HF_LLM_MODEL = REPO_ROOT / "models" / "llm" / "Nous-Hermes-2-Mistral-7B-DPO"

def detect_default_model() -> str:
    """
    Choose the default model path in this order:
    1) EMBEDDING_MODEL env var
    2) local sentence-transformer folder in models/
    3) local sentence-transformer folder in Data/
    4) local HF LLM folder
    5) fallback remote-ish name (not recommended; only kept as a last resort)
    """
    if os.getenv("EMBEDDING_MODEL"):
        return os.getenv("EMBEDDING_MODEL")
    if LOCAL_EMBED_MODEL_MODELS.exists():
        return str(LOCAL_EMBED_MODEL_MODELS)
    if LOCAL_EMBED_MODEL_DATA.exists():
        return str(LOCAL_EMBED_MODEL_DATA)
    if LOCAL_HF_LLM_MODEL.exists():
        return str(LOCAL_HF_LLM_MODEL)
    # Last resort only
    return "all-MiniLM-L6-v2"
DEFAULT_EMBED_MODEL = detect_default_model()


def load_segments(path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    segments = payload.get("segments") or []
    return payload, segments


def chunk_segments(
    segments: List[Dict[str, Any]],
    chunk_size: int = 2,
    stride: int = 1
) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    if not segments:
        return chunks
    i = 0
    idx = 0
    while i < len(segments):
        window = segments[i : i + chunk_size]
        text = " ".join(
            (s.get("text_clean") or s.get("text") or "").strip()
            for s in window
        ).strip()

        if text:
            chunks.append({
                "chunk_index": idx,
                "start_segment_index": i,
                "end_segment_index": i + len(window) - 1,
                "start": float(window[0].get("start", 0.0)),
                "end": float(window[-1].get("end", window[0].get("start", 0.0))),
                "text": text,
            })
            idx += 1
        i += stride
    return chunks


def mean_pool(last_hidden_state, attention_mask):
    """
    Mean-pool token embeddings using the attention mask.
    """
    import torch

    mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
    masked_embeddings = last_hidden_state * mask
    summed = masked_embeddings.sum(dim=1)
    counts = mask.sum(dim=1).clamp(min=1e-9)
    return summed / counts


@lru_cache(maxsize=1)
def get_sentence_transformer(model_name: str):
    from sentence_transformers import SentenceTransformer
    # local_files_only=True prevents network calls
    return SentenceTransformer(model_name, local_files_only=True)


@lru_cache(maxsize=1)
def get_hf_embedding_model(model_name: str):
    """
    Load a local Hugging Face model and tokenizer for embedding extraction.
    """
    import torch
    from transformers import AutoModel, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        local_files_only=True,
        use_fast=True,
    )

    # Some decoder-only models do not define a pad token; reuse eos token if needed
    if tokenizer.pad_token is None and tokenizer.eos_token is not None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModel.from_pretrained(
        model_name,
        local_files_only=True,
        torch_dtype=torch.float32,   # safer on CPU
        low_cpu_mem_usage=True,
    )
    model.eval()

    return tokenizer, model


def is_hf_model_dir(model_name: str) -> bool:
    p = Path(model_name)
    if not p.exists() or not p.is_dir():
        return False

    required_any = [
        p / "config.json",
        p / "tokenizer.json",
        p / "tokenizer.model",
        p / "model.safetensors",
        p / "model.safetensors.index.json",
    ]

    # Must at least have config and some tokenizer file
    has_config = (p / "config.json").exists()
    has_tokenizer = (p / "tokenizer.json").exists() or (p / "tokenizer.model").exists()
    has_weights = (p / "model.safetensors").exists() or (p / "model.safetensors.index.json").exists()

    return has_config and has_tokenizer and has_weights


def embed_with_hf_hidden_states(
    texts: List[str],
    model_name: str,
    batch_size: int = 4,
    max_length: int = 512,
) -> np.ndarray:
    import torch
    import torch.nn.functional as F

    tokenizer, model = get_hf_embedding_model(model_name)

    all_embeddings = []

    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]

            encoded = tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors="pt",
            )

            outputs = model(**encoded)
            pooled = mean_pool(outputs.last_hidden_state, encoded["attention_mask"])
            pooled = F.normalize(pooled, p=2, dim=1)
            all_embeddings.append(pooled.cpu().numpy())

    return np.vstack(all_embeddings).astype(float)


def embed_with_tfidf(texts: List[str]) -> np.ndarray:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import normalize

    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    x = vec.fit_transform(texts)
    x = normalize(x)
    return x.toarray().astype(float)


def embed_texts(
    texts: List[str],
    model_name: str = DEFAULT_EMBED_MODEL,
    prefer_backend: str = "auto",
    batch_size: int = 4,
    max_length: int = 512,
) -> Tuple[np.ndarray, str, List[str]]:
    """
    Returns:
        embeddings, backend_name, notes
    """

    notes: List[str] = []

    if not texts:
        return np.zeros((0, 0), dtype=float), "none", ["No input texts provided"]

    # 1) Explicit sentence-transformer request
    if prefer_backend == "sentence_transformer":
        try:
            model = get_sentence_transformer(model_name)
            embs = model.encode(texts, normalize_embeddings=True)
            return np.asarray(embs, dtype=float), "sentence_transformer", notes
        except Exception as exc:
            notes.append(f"SentenceTransformer load failed: {exc}")
            raise

    # 2) Explicit HF hidden-state embedding request
    if prefer_backend == "hf_auto":
        embs = embed_with_hf_hidden_states(
            texts,
            model_name=model_name,
            batch_size=batch_size,
            max_length=max_length,
        )
        return embs, "hf_auto_hidden_state_mean_pool", notes

    # 3) Explicit TF-IDF
    if prefer_backend == "tfidf":
        embs = embed_with_tfidf(texts)
        notes.append("Used TF-IDF embeddings by explicit request")
        return embs, "tfidf", notes

    # 4) Auto mode
    #    Try sentence-transformer if the folder looks like one;
    #    otherwise try local HF model; otherwise fallback to TF-IDF.
    try:
        p = Path(model_name)
        if p.exists() and (p / "modules.json").exists():
            model = get_sentence_transformer(model_name)
            embs = model.encode(texts, normalize_embeddings=True)
            return np.asarray(embs, dtype=float), "sentence_transformer", notes
    except Exception as exc:
        notes.append(f"SentenceTransformer auto-detect/load failed: {exc}")

    try:
        if is_hf_model_dir(model_name):
            embs = embed_with_hf_hidden_states(
                texts,
                model_name=model_name,
                batch_size=batch_size,
                max_length=max_length,
            )
            notes.append("Used local Hugging Face model hidden states for embeddings")
            return embs, "hf_auto_hidden_state_mean_pool", notes
    except Exception as exc:
        notes.append(f"HF local model load failed: {exc}")

    embs = embed_with_tfidf(texts)
    notes.append("Fell back to TF-IDF embeddings")
    return embs, "tfidf", notes


def cosine_adjacent(embs: np.ndarray) -> List[float]:
    sims: List[float] = []
    for i in range(len(embs) - 1):
        a = embs[i]
        b = embs[i + 1]
        denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1.0
        sims.append(float(np.dot(a, b) / denom))
    return sims


def choose_boundaries(
    chunks: List[Dict[str, Any]],
    sims: List[float],
    z_threshold: float = -0.75
) -> List[int]:
    if not sims:
        return []
    arr = np.asarray(sims, dtype=float)
    mean = float(arr.mean())
    std = float(arr.std()) or 1.0
    z = (arr - mean) / std

    boundaries: List[int] = []
    for i, z_i in enumerate(z):
        if float(z_i) <= z_threshold:
            boundaries.append(i)
    return boundaries


def merge_chunks_into_segments(
    chunks: List[Dict[str, Any]],
    boundaries: List[int]
) -> List[Dict[str, Any]]:
    if not chunks:
        return []
    boundaries = sorted(set(boundaries))
    groups: List[Dict[str, Any]] = []
    start = 0
    seg_id = 1

    for b in boundaries:
        end = b
        group = chunks[start : end + 1]
        groups.append({
            "segment_id": seg_id,
            "start": group[0]["start"],
            "end": group[-1]["end"],
            "start_segment_index": group[0]["start_segment_index"],
            "end_segment_index": group[-1]["end_segment_index"],
            "text": " ".join(c["text"] for c in group),
        })
        seg_id += 1
        start = b + 1
    group = chunks[start:]
    if group:
        groups.append({
            "segment_id": seg_id,
            "start": group[0]["start"],
            "end": group[-1]["end"],
            "start_segment_index": group[0]["start_segment_index"],
            "end_segment_index": group[-1]["end_segment_index"],
            "text": " ".join(c["text"] for c in group),
        })
    return groups


def segment_payload(
    payload: Dict[str, Any],
    chunk_size: int = 2,
    stride: int = 1,
    model_name: str = DEFAULT_EMBED_MODEL,
    z_threshold: float = -0.75,
    embedding_backend: str = "auto",
    batch_size: int = 4,
    max_length: int = 512,
) -> Dict[str, Any]:
    segments = payload.get("segments") or []
    chunks = chunk_segments(segments, chunk_size=chunk_size, stride=stride)
    texts = [c["text"] for c in chunks]
    out = dict(payload)
    if len(texts) < 2:
        out["semantic_segmentation"] = {
            "engine": "embedding_similarity",
            "embedding_model": model_name,
            "embedding_backend": "none",
            "chunks": chunks,
            "adjacent_similarity": [],
            "instructional_segments": [],
            "notes": ["Not enough chunks to segment"],
        }
        return out

    embs, backend_used, notes = embed_texts(
        texts,
        model_name=model_name,
        prefer_backend=embedding_backend,
        batch_size=batch_size,
        max_length=max_length,
    )

    sims = cosine_adjacent(embs)
    boundaries = choose_boundaries(chunks, sims, z_threshold=z_threshold)
    instructional = merge_chunks_into_segments(chunks, boundaries)
    out["semantic_segmentation"] = {
        "engine": "embedding_similarity",
        "embedding_model": model_name,
        "embedding_backend": backend_used,
        "chunk_size": chunk_size,
        "stride": stride,
        "z_threshold": z_threshold,
        "chunks": chunks,
        "adjacent_similarity": sims,
        "boundary_after_chunk_indices": boundaries,
        "instructional_segments": instructional,
        "notes": notes,
    }
    return out


def derive_output_name(in_path: Path) -> str:
    name = in_path.name
    if name.endswith(".segmented.json"):
        return name
    if name.endswith(".json"):
        name = name[:-5]
    return f"{name}.segmented.json"


def iter_input_files(in_dir: Path, pattern: str, recursive: bool) -> List[Path]:
    files = sorted(in_dir.rglob(pattern) if recursive else in_dir.glob(pattern))
    return [p for p in files if p.is_file() and not p.name.endswith(".segmented.json")]


def process_one(in_path: Path, out_path: Path, args) -> None:
    payload = json.loads(in_path.read_text(encoding="utf-8"))
    out = segment_payload(
        payload,
        chunk_size=args.chunk_size,
        stride=args.stride,
        model_name=args.embedding_model,
        z_threshold=args.z_threshold,
        embedding_backend=args.embedding_backend,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Wrote segmentation JSON: {out_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Semantic segmentation for transcript payload(s)")
    ap.add_argument("--in_json", help="Single input JSON")
    ap.add_argument("--out_json", help="Single output JSON")
    ap.add_argument("--in_dir", help="Input folder")
    ap.add_argument("--out_dir", help="Output folder")
    ap.add_argument("--pattern", default="*.json", help="Glob pattern for folder mode")
    ap.add_argument("--recursive", action="store_true", help="Recurse into subfolders")
    ap.add_argument("--force", action="store_true", help="Overwrite existing outputs in folder mode")
    ap.add_argument("--dry_run", action="store_true")
    ap.add_argument("--delay", type=float, default=0.0)

    ap.add_argument("--chunk_size", type=int, default=2)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--z_threshold", type=float, default=-0.75)

    ap.add_argument(
        "--embedding_model",
        default=DEFAULT_EMBED_MODEL,
        help="Path or name of embedding model (default: offline auto-detect)"
    )
    ap.add_argument(
        "--embedding_backend",
        default="auto",
        choices=["auto", "sentence_transformer", "hf_auto", "tfidf"],
        help="Embedding backend to use"
    )
    ap.add_argument("--batch_size", type=int, default=4)
    ap.add_argument("--max_length", type=int, default=512)

    args = ap.parse_args()

    single_mode = bool(args.in_json or args.out_json)
    folder_mode = bool(args.in_dir or args.out_dir)

    if single_mode and folder_mode:
        raise SystemExit("Use either single-file mode or folder mode, not both.")

    if not single_mode and not folder_mode:
        raise SystemExit("Provide either --in_json and --out_json, or --in_dir and --out_dir.")

    if single_mode:
        if not args.in_json or not args.out_json:
            raise SystemExit("Single-file mode requires both --in_json and --out_json")
        process_one(Path(args.in_json), Path(args.out_json), args)
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
    print(f"Embedding model: {args.embedding_model}")
    print(f"Embedding backend: {args.embedding_backend}")

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
    print("SEMANTIC SEGMENTATION COMPLETE")
    print(f"OK: {ok}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")
    print(f"Output directory: {out_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()

# "adjacent_similarity"
# This script segments a transcript into instructional units. It assumes that:

# When topics stay the same → adjacent chunks are similar → high cosine score
# When a new topic begins → similarity drops

# By computing similarity between neighbors, the script can detect boundaries where the topic shifts.
# Those drops are detected later by:
# Pythonboundaries = choose_boundaries(chunks, sims, z_threshold)Show more lines
# This takes unusually low similarities (low z-scores) as boundaries.

# Cosine similarity ranges from -1 to 1:

# 1.0 → chunks are nearly identical
# 0.5–0.8 → related topic
# 0.0 → unrelated
# negative → opposite/contradictory (rare for embeddings of natural text)

# A typical output might look like:
# adjacent_similarity: [0.82, 0.77, 0.12, 0.05, 0.88]

# Here, the sudden dip from ~0.8 to ~0.1 would be interpreted as a new instructional section.
```

### Usage

```bash
python python scripts\semantic_segmentation.py --in_dir "Data\transcripts_clean" --out_dir "Data\transcripts_segmented" --embedding_model "models\llm\Nous-Hermes-2-Mistral-7B-DPO --embedding_backend hf_aut0 --force
```

***

## Script: `scripts/structure_batch_2.py` (Boundary Mode)

```python
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
```

### Usage

```bash
python scripts\structure_batch_2.py --in_dir "Data\transcripts_clean" --out_dir "Data\transcripts_boundaries" --pattern "*.clean.json" --mode boundary --model_path "models\llm\Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf" --cpu_threads 8 --max_input_tokens 4096 --max_new_tokens 1024 --force
```

## Script: `scripts/compare_reports.py`

```python
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
```

### Usage

```bash
python scripts\compare_reports.py --boundaries_json "Data\transcripts_boundaries\LMOS Introduction to the process.boundaries.json" --segmented_json "Data\transcripts_segmented\LMOS Introduction to the process.segmented.json" --aligned_json "Data\transcripts_aligned\LMOS Introduction to the process.aligned.json" --out_report "Data\reports\LMOS Introduction to the process.comparison.txt"
```
---