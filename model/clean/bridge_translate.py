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
from tqdm.auto import tqdm
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

# Write straight to Drive so progress survives a Colab disconnect/reset.
# Falls back to local data/bridged if Drive isn't mounted (e.g. local runs).
DRIVE_DIR = "/content/drive/MyDrive/VOIDWEN_data/bridged"
LOCAL_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "bridged")
OUT_DIR = DRIVE_DIR if os.path.isdir("/content/drive/MyDrive") else LOCAL_DIR
os.makedirs(OUT_DIR, exist_ok=True)
print(f"[bridge] writing output + checkpoints to: {OUT_DIR}"
      + ("" if OUT_DIR == DRIVE_DIR else "  (Drive not mounted — run `drive.mount('/content/drive')` first to persist across sessions)"))

MODEL_ID = "Helsinki-NLP/opus-mt-zh-en"
BATCH = 128


def translate_batch(texts, tok, model, device):
    enc = tok(texts, return_tensors="pt", padding=True, truncation=True, max_length=128).to(device)
    with torch.no_grad():
        out = model.generate(
            **enc,
            max_new_tokens=128,   # sentences are short; 256 was massive overkill
            num_beams=1,          # greedy instead of beam search — ~4-6x faster, minor quality cost
            do_sample=False,
        )
    return tok.batch_decode(out, skip_special_tokens=True)


def _ckpt_path(out_path: str) -> str:
    return out_path + ".ckpt"


def bridge_file(path: str, tok, model, device) -> str:
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    rows = [r for r in rows if r.get("tgt")]  # need modern-zh tgt to bridge
    out_path = os.path.join(OUT_DIR, os.path.basename(path))
    ckpt_path = _ckpt_path(out_path)

    if os.path.isfile(out_path) and not os.path.isfile(ckpt_path):
        done_lines = sum(1 for _ in open(out_path, encoding="utf-8"))
        if done_lines >= len(rows):
            print(f"[bridge] {os.path.basename(path)} already complete ({done_lines} pairs) — skipping")
            return out_path

    # resume: checkpoint stores the number of rows already written for this file
    start_row = 0
    if os.path.isfile(ckpt_path) and os.path.isfile(out_path):
        try:
            start_row = int(open(ckpt_path).read().strip())
        except ValueError:
            start_row = 0
        # guard against a corrupt/truncated output file from a mid-write crash
        actual_lines = sum(1 for _ in open(out_path, encoding="utf-8"))
        if actual_lines < start_row:
            start_row = actual_lines
        print(f"[bridge] resuming {os.path.basename(path)} from row {start_row}/{len(rows)}")

    n = start_row
    n_batches_total = (len(rows) + BATCH - 1) // BATCH
    batches_done = start_row // BATCH

    mode = "a" if start_row > 0 else "w"
    with open(out_path, mode, encoding="utf-8") as f:
        pbar = tqdm(
            range(start_row, len(rows), BATCH),
            total=n_batches_total,
            initial=batches_done,
            desc=f"bridging {os.path.basename(path)}",
            unit="batch",
        )
        for i in pbar:
            chunk = rows[i:i + BATCH]
            en = translate_batch([r["tgt"] for r in chunk], tok, model, device)
            for r, e in zip(chunk, en):
                f.write(json.dumps({
                    "src": r["src"], "tgt": e, "pair": "wenyan-en",
                    "source": r["source"] + "+opus-mt-zh-en",
                }, ensure_ascii=False) + "\n")
                n += 1
            f.flush()
            os.fsync(f.fileno())  # force to disk/Drive so a crash doesn't lose the last batch
            with open(ckpt_path, "w") as cf:
                cf.write(str(n))
            pbar.set_postfix(pairs=n, total=len(rows))
    os.remove(ckpt_path)  # done — clean up checkpoint so a future run knows it's complete
    print(f"[bridge] {path} -> {out_path} ({n} pairs)")
    return out_path


def main() -> None:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[bridge] device = {device}" + (f" ({torch.cuda.get_device_name(0)})" if device == "cuda" else " -- WARNING: no GPU detected, this will be slow"))
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID).to(device=device, dtype=dtype).eval()
    for path in glob.glob(os.path.join(RAW_DIR, "*.jsonl")):
        if "gutenberg" in path:
            continue  # already english, direct gold tier, no bridge needed
        bridge_file(path, tok, model, device)


if __name__ == "__main__":
    main()
