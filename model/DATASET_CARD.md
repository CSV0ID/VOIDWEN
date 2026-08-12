---
license: cc-by-sa-4.0
language:
  - zh
  - en
task_categories:
  - translation
tags:
  - wenyan
  - classical-chinese
  - parallel-corpus
---

# voidwen-wenyan-en

Parallel wenyan (classical Chinese) → English corpus for fine-tuning translation
models.

> **Status: not yet published.** This card is the template. Row counts below are
> the pipeline's *targets* from the VOIDWEN plan, not a built artifact. Rebuild with
> `model/` scripts, then fill in the actual counts.

## Format

TSV, two columns: `source` (wenyan), `target` (English). Splits: train / eval / test
(eval and test held out, no overlap).

## Sources & provenance

| Source | License | Target counts (planned) |
|---|---|---|
| Legge translations (Project Gutenberg), zh source from ctext.org | Public domain (Legge text); ctext zh text CC BY-SA 4.0 | ~180k |
| WikiSource | CC BY-SA 4.0 | ~150k |
| CCTC | research use | ~100k |
| Taisho Tripitaka sutras | public domain | ~50k |
| Numata translations | verify per text | (with sutras) |
| Hand-curated Tier 1 | verified | ~8k |

**Note on the first row:** English comes from Legge's public-domain translations
(Gutenberg), not from ctext's own English edition -- ctext's English output was
never confirmed to be distinct from its Chinese output (see
`model/scrape/legge_scraper.py` and `ctext_scraper.py` docstrings for the
unresolved bug this sidesteps). The zh/en alignment is by chapter:verse number,
not by zipping two independently-fetched paragraph arrays. Because two different
sources feed one row here, the *pair* is only as permissively licensed as its
more restrictive input -- treat this row as CC BY-SA 4.0 for redistribution
purposes even though the English half alone is public domain.

Cleaning: exact + near dedup, language check, length filter, classical scoring
(codepoint arithmetic), hunalign confidence ≥ 0.4, holdout removal. See
`model/clean/`.

## Licensing note

Redistribution follows the most restrictive input license (CC BY-SA 4.0). Verify
Numata translation terms per text before including. Credit all sources here on
publish.
