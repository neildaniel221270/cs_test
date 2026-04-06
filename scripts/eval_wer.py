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