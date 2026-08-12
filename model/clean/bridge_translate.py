"""Chain-bridge wenyan->modern-zh pairs into wenyan->en pairs.

modern-zh -> en via Helsinki-NLP/opus-mt-zh-en (batched, GPU if available).
Run after fetch_datasets.py. Input: model/data/raw/*.jsonl with modern zh in `tgt`.
Output: model/data/bridged/*.jsonl with {src: wenyan, tgt: en, pair: wenyan-en, source}
"""
from __future__ import annotations
import glob
import json
import os

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "bridged")
os.makedirs(OUT_DIR, exist_ok=True)

MODEL_ID = "Helsinki-NLP/opus-mt-zh-en"
BATCH = 64


def translate_batch(texts, tok, model, device):
    enc = tok(texts, return_tensors="pt", padding=True, truncation=True, max_length=256).to(device)
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=256)
    return tok.batch_decode(out, skip_special_tokens=True)


def bridge_file(path: str, tok, model, device) -> str:
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    rows = [r for r in rows if r.get("tgt")]  # need modern-zh tgt to bridge
    out_path = os.path.join(OUT_DIR, os.path.basename(path))
    n = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for i in range(0, len(rows), BATCH):
            chunk = rows[i:i + BATCH]
            en = translate_batch([r["tgt"] for r in chunk], tok, model, device)
            for r, e in zip(chunk, en):
                f.write(json.dumps({
                    "src": r["src"], "tgt": e, "pair": "wenyan-en",
                    "source": r["source"] + "+opus-mt-zh-en",
                }, ensure_ascii=False) + "\n")
                n += 1
    print(f"[bridge] {path} -> {out_path} ({n} pairs)")
    return out_path


def main() -> None:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID).to(device).eval()
    for path in glob.glob(os.path.join(RAW_DIR, "*.jsonl")):
        if "gutenberg" in path:
            continue  # already english, direct gold tier, no bridge needed
        bridge_file(path, tok, model, device)


if __name__ == "__main__":
    main()
