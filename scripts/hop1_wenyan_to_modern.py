#!/usr/bin/env python3
"""Hop1 only: wenyan -> modern Chinese. Called as a subprocess from
scripts/translate_wenyan.js because transformers.js (JS) cannot load this
model's architecture -- it's a BERT2BERT EncoderDecoderModel, and
transformers.js's model registry doesn't recognize the generic
"encoder-decoder" model_type (confirmed by hand: AutoModelForSeq2SeqLM in
Node throws "Unsupported model type: encoder-decoder"). Hop2 (modern-zh ->
English, MarianMT) runs fine natively in Node since Xenova/opus-mt-zh-en is
a supported architecture -- only hop1 needs this Python detour.

Protocol: reads one wenyan sentence per line from stdin, writes one modern-zh
translation per line to stdout, in the same order. No extra output on stdout
(progress/errors go to stderr) so the Node side can parse it as plain lines.
"""
from __future__ import annotations
import sys

MODEL_ID = "raynardj/wenyanwen-ancient-translate-to-modern"


def main() -> None:
    import torch
    from transformers import EncoderDecoderModel, AutoTokenizer

    print(f"[hop1] loading {MODEL_ID} ...", file=sys.stderr)
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = EncoderDecoderModel.from_pretrained(MODEL_ID).eval()

    lines = [l.rstrip("\n") for l in sys.stdin if l.strip()]
    if not lines:
        return

    enc = tok(lines, truncation=True, max_length=128, padding="max_length", return_tensors="pt")
    with torch.no_grad():
        out = model.generate(
            input_ids=enc.input_ids,
            attention_mask=enc.attention_mask,
            num_beams=3,
            max_length=256,
            bos_token_id=101,
            eos_token_id=tok.sep_token_id,
            pad_token_id=tok.pad_token_id,
        )
    results = tok.batch_decode(out, skip_special_tokens=True)
    for r in results:
        print(r, flush=True)


if __name__ == "__main__":
    main()
