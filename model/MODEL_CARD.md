---
license: mit
language:
  - zh
  - en
base_model: Helsinki-NLP/opus-mt-zh-en
pipeline_tag: translation
tags:
  - wenyan
  - classical-chinese
  - onnx
  - transformers.js
---

# voidwen-opus-mt

Fine-tuned wenyan (classical Chinese) → English translation, exported to ONNX int8
for in-browser use via transformers.js.

> **Status: not yet trained or published.** This card ships with the VOIDWEN repo as
> the template for the eventual release. Metric cells below are targets, not results.
> Do not cite them as measured until this model is trained and evaluated.

## Model

- Base: `Helsinki-NLP/opus-mt-zh-en` (MarianMT)
- Fine-tune: 3 epochs on `CSV0ID/voidwen-wenyan-en`
- Export: ONNX, dynamic int8 (~80MB)
- Runtime: transformers.js in the browser — no server, no API

## Results

| Metric | Baseline (no fine-tune) | Target after fine-tune |
|---|---|---|
| BLEU (wenyan→en) | TBD | > 33 |
| chrF | TBD | TBD |

Fill these from `model/evaluate.py` on the held-out test set before publishing.

## Intended use

Reading VOIDWEN wenyan-mode agent output back in English, client-side. Not a general
classical-Chinese scholarly translator — it targets the compressed-output use case.

## License & attribution

MIT. Base model © Helsinki-NLP (opus-mt). Training data provenance: see the
`CSV0ID/voidwen-wenyan-en` dataset card.
