"""Export a fine-tuned MarianMT checkpoint to ONNX for transformers.js.

Uses optimum, which emits the encoder / decoder / decoder-with-past ONNX graphs that
transformers.js expects for seq2seq.

    python model/export_onnx.py --model ./checkpoints/voidwen --out ./onnx
"""
from __future__ import annotations

import argparse

from optimum.onnxruntime import ORTModelForSeq2SeqLM
from transformers import AutoTokenizer


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", default="./onnx")
    args = ap.parse_args()

    model = ORTModelForSeq2SeqLM.from_pretrained(args.model, export=True)
    model.save_pretrained(args.out)
    AutoTokenizer.from_pretrained(args.model).save_pretrained(args.out)
    print(f"exported ONNX to {args.out}")


if __name__ == "__main__":
    main()
