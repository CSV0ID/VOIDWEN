"""Merge bridged + gold jsonl -> filtered, deduped train/val jsonl.

Steps: load all pairs -> keep src passing scorer.is_classical() -> MinHash
near-dup filter (datasketch) -> shuffle -> split -> write.
"""
from __future__ import annotations
import glob
import json
import os
import random

from datasketch import MinHash, MinHashLSH

from scorer import is_classical

BRIDGED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "bridged")
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "final")
os.makedirs(OUT_DIR, exist_ok=True)

VAL_FRACTION = 0.02
SEED = 42


def _minhash(text: str) -> MinHash:
    m = MinHash(num_perm=64)
    for ch in text:
        m.update(ch.encode("utf-8"))
    return m


def load_all():
    rows = []
    for path in glob.glob(os.path.join(BRIDGED_DIR, "*.jsonl")):
        rows.extend(json.loads(l) for l in open(path, encoding="utf-8"))
    # gutenberg gold tier: english already, src is raw wenyan paragraph, tgt empty -> skip (needs manual align)
    # kept only if a companion aligned file exists; otherwise excluded from training set.
    return rows


def dedup(rows):
    lsh = MinHashLSH(threshold=0.85, num_perm=64)
    kept = []
    for i, r in enumerate(rows):
        mh = _minhash(r["src"])
        key = f"r{i}"
        if lsh.query(mh):
            continue
        lsh.insert(key, mh)
        kept.append(r)
    return kept


def main() -> None:
    rows = load_all()
    print(f"loaded {len(rows)} raw pairs")

    rows = [r for r in rows if is_classical(r["src"]) and r.get("tgt", "").strip()]
    print(f"{len(rows)} pass classical-src filter")

    rows = dedup(rows)
    print(f"{len(rows)} after near-dup removal")

    random.Random(SEED).shuffle(rows)
    n_val = max(1, int(len(rows) * VAL_FRACTION))
    val, train = rows[:n_val], rows[n_val:]

    for name, split in (("train", train), ("val", val)):
        path = os.path.join(OUT_DIR, f"{name}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for r in split:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"{name}: {len(split)} -> {path}")


if __name__ == "__main__":
    main()
