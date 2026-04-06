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