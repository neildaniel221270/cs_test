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
    ap.add_argument("--limit", type=int, default=None)
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