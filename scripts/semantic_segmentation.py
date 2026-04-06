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