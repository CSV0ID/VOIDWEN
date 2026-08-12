# VOIDWEN model

Fine-tuned wenyan (classical Chinese) → English translation model for the browser.

- **Base:** `Helsinki-NLP/opus-mt-zh-en` (MarianMT)
- **Model (published):** `CSV0ID/voidwen-opus-mt` on HuggingFace Hub — ONNX int8, ~80MB
- **Dataset (published):** `CSV0ID/voidwen-wenyan-en` on HuggingFace Datasets

Runs client-side via transformers.js. No server, no API, zero tokens at inference.

## No Chinese in source

Every Chinese character in the pipeline exists only in the data flowing through at
runtime. No CJK literal appears in any `.py`, notebook, config, or test. Detection
and scoring use Unicode codepoint ranges (`classical_scorer.py`). Corpus data is
CJK-bearing, so it lives on HuggingFace only and is gitignored from this repo.

## Reproduce

Everything below runs on Colab free tier (T4). Nothing here was executed in the repo
— run it yourself; no results are pre-filled.

```bash
pip install -r model/requirements.txt

# 1. Build the corpus (scrape + clean) — see notebooks/01_data_pipeline.ipynb.
#    Scraper selectors are best-effort; verify against live DOM first.
python model/clean/pipeline.py            # self-check on a tiny in-memory sample

# 2. Fine-tune (checkpoint to Drive; resume across 12h sessions)
python model/train.py --output_dir /content/drive/MyDrive/voidwen/ckpt --resume

# 3. Export + quantize
python model/export_onnx.py --model ./checkpoints/voidwen --out ./onnx
python model/quantize.py --onnx ./onnx --out ./onnx-int8

# 4. Evaluate on held-out test set (target BLEU > 33)
python model/evaluate.py --model ./onnx-int8 --test model/data/test.tsv --onnx

# 5. Publish (needs your HF token)
huggingface-cli upload CSV0ID/voidwen-opus-mt ./onnx-int8
```

## Layout

```
model/
  requirements.txt
  train.py  export_onnx.py  quantize.py  evaluate.py
  scrape/   fetch.py  ctext_scraper.py  wikisource_scraper.py  sutra_scraper.py
  clean/    pipeline.py  classical_scorer.py  aligner.py
  notebooks/ 01_data_pipeline.ipynb  02_training.ipynb  03_export.ipynb
  data/     (gitignored — pulled from HuggingFace)
```
