"""Evaluate a model on the held-out wenyan -> English test set.

Reports BLEU and chrF via sacrebleu. Works on a HF checkpoint or an ONNX export
dir. The test set is CJK-bearing data, so it lives on HuggingFace / local disk, never
committed to the repo. Target from the master plan: BLEU > 33.

    python model/evaluate.py --model ./onnx-int8 --test model/data/test.tsv --onnx
"""
from __future__ import annotations

import argparse
import csv

import sacrebleu


def load_pairs(tsv_path: str):
    with open(tsv_path, encoding="utf-8") as fh:
        for row in csv.reader(fh, delimiter="\t"):
            if len(row) == 2 and row[0] and row[1]:
                yield row[0], row[1]


def load_translator(model_path: str, onnx: bool):
    from transformers import AutoTokenizer, pipeline
    if onnx:
        from optimum.onnxruntime import ORTModelForSeq2SeqLM
        model = ORTModelForSeq2SeqLM.from_pretrained(model_path)
    else:
        from transformers import AutoModelForSeq2SeqLM
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    tok = AutoTokenizer.from_pretrained(model_path)
    return pipeline("translation", model=model, tokenizer=tok)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--test", required=True)
    ap.add_argument("--onnx", action="store_true")
    ap.add_argument("--batch_size", type=int, default=32)
    args = ap.parse_args()

    sources, refs = zip(*load_pairs(args.test))
    translate = load_translator(args.model, args.onnx)
    outputs = translate(list(sources), batch_size=args.batch_size, max_length=256)
    hyps = [o["translation_text"] for o in outputs]

    bleu = sacrebleu.corpus_bleu(hyps, [list(refs)])
    chrf = sacrebleu.corpus_chrf(hyps, [list(refs)])
    print(f"BLEU: {bleu.score:.2f}")
    print(f"chrF: {chrf.score:.2f}")
    if bleu.score <= 33:
        print("WARNING: BLEU at or below the 33 target — do not publish this checkpoint.")


if __name__ == "__main__":
    main()
