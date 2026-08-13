"""Wenyan (Classical Chinese) -> English, via two chained pretrained models.
No training required.

  Hop 1: raynardj/wenyanwen-ancient-translate-to-modern   (wenyan -> modern zh)
  Hop 2: Helsinki-NLP/opus-mt-zh-en                        (modern zh -> en)

Usage:
    python wenyan_to_english.py "学而时习之，不亦说乎？"
    python wenyan_to_english.py --file sentences.txt        # one wenyan line per line
"""
from __future__ import annotations
import argparse
import sys

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    EncoderDecoderModel,
)

HOP1_MODEL = "raynardj/wenyanwen-ancient-translate-to-modern"
HOP2_MODEL = "Helsinki-NLP/opus-mt-zh-en"


def load_models(device: str):
    print(f"[load] hop1 ({HOP1_MODEL}) ...", file=sys.stderr)
    tok1 = AutoTokenizer.from_pretrained(HOP1_MODEL)
    model1 = EncoderDecoderModel.from_pretrained(HOP1_MODEL).to(device).eval()

    print(f"[load] hop2 ({HOP2_MODEL}) ...", file=sys.stderr)
    tok2 = AutoTokenizer.from_pretrained(HOP2_MODEL)
    model2 = AutoModelForSeq2SeqLM.from_pretrained(HOP2_MODEL).to(device).eval()

    return (tok1, model1), (tok2, model2)


def wenyan_to_modern(texts, tok, model, device):
    """Hop 1. Uses raynardj's documented inference recipe (custom bos/eos ids —
    required or output gets truncated/garbled, per the model's own README)."""
    enc = tok(
        texts, truncation=True, max_length=128, padding="max_length",
        return_tensors="pt",
    ).to(device)
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
    return tok.batch_decode(out, skip_special_tokens=True)


def modern_to_english(texts, tok, model, device):
    """Hop 2. Standard MarianMT generate."""
    enc = tok(
        texts, return_tensors="pt", padding=True, truncation=True, max_length=128,
    ).to(device)
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=128, num_beams=3)
    return tok.batch_decode(out, skip_special_tokens=True)


def translate(texts, hop1, hop2, device):
    tok1, model1 = hop1
    tok2, model2 = hop2
    modern = wenyan_to_modern(texts, tok1, model1, device)
    english = modern_to_english(modern, tok2, model2, device)
    return list(zip(texts, modern, english))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?", help="A single wenyan sentence to translate")
    ap.add_argument("--file", help="Path to a file with one wenyan sentence per line")
    args = ap.parse_args()

    if not args.text and not args.file:
        ap.error("provide either a text argument or --file")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[device] {device}", file=sys.stderr)
    hop1, hop2 = load_models(device)

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
    else:
        lines = [args.text]

    results = translate(lines, hop1, hop2, device)
    for wenyan, modern, english in results:
        print(f"wenyan:  {wenyan}")
        print(f"modern:  {modern}")
        print(f"english: {english}")
        print()


if __name__ == "__main__":
    main()
