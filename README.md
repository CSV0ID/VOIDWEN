# VOIDWEN

> **By CS VOID LABS · CSV0ID**
> *Classical silence. Minimal code. Zero waste.*

# VOIDWEN

> **By CS VOID LABS · CSV0ID**
> *Classical silence. Minimal code. Zero waste.*

One switch for two problems: compress what an AI coding agent **says** (prose) and
what it **builds** (code). Optionally, output prose in **wenyan** (classical Chinese),
and translate real wenyan text back to English right in the terminal via
`/voidwen-translate` — a real two-hop ML model chain, not a language-model guess.

VOIDWEN merges the approaches of two upstream skills into one conflict-free skill:

- [**caveman**](https://github.com/JuliusBrussee/caveman) — prose compression
- [**ponytail**](https://github.com/DietrichGebert/ponytail) — YAGNI code minimalism

Their rules were **rewritten from scratch**, not copied. See
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Status

| Part | State |
|---|---|
| Prose + code skill (`skills/voidwen/SKILL.md`) | Done |
| Commands (8) | Done |
| Wenyan -> English translation (`/voidwen-translate`) | Done, tested end-to-end |
| Tests (`tests/`, run below) | Passing |

## How translation works

`/voidwen-translate` chains two existing pretrained models rather than a
custom-trained one:

1. **wenyan -> modern Chinese** — `raynardj/wenyanwen-ancient-translate-to-modern`
   (BERT2BERT), run via a Python subprocess (`scripts/hop1_wenyan_to_modern.py`).
   Python is required here because this model's architecture (a generic
   encoder-decoder wrapper around two BERT models) isn't supported by
   transformers.js's model registry -- confirmed by hand, not assumed.
2. **modern Chinese -> English** — `Xenova/opus-mt-zh-en` (MarianMT), runs
   natively in Node via `@huggingface/transformers` -- no Python needed for
   this hop.

## Install the skill (Claude Code)

```
/plugin marketplace add CSV0ID/voidwen
/plugin install voidwen@voidwen
```

Or copy [`AGENTS.md`](AGENTS.md) into any project for a portable, all-agent version.

## Setup for translation

```
npm install                       # installs @huggingface/transformers (hop2)
pip install transformers torch    # for hop1 (see scripts/hop1_wenyan_to_modern.py)
```

First translation run downloads both models (~1GB+ combined, mostly hop1's
PyTorch weights); subsequent runs use the local cache.

## Usage

```
/voidwen full        # default: compressed prose + YAGNI code
/voidwen ultra       # telegraphic prose, delete-before-add
/voidwen wenyan      # classical Chinese output
/voidwen off

/voidwen-translate <wenyan text>   # translate real wenyan -> English
```

Or directly from a terminal:

```
node scripts/translate_wenyan.js "<wenyan text>"
echo "<wenyan text>" | node scripts/translate_wenyan.js
node scripts/translate_wenyan.js --verbose "<wenyan text>"   # show the modern-zh bridge step too
```

## Before / after (prose)

```
before: Sure! I'd be happy to help. The issue is most likely caused by the auth
        middleware, which checks the token expiry.
after:  Bug in auth middleware. Token expiry check wrong.
```

`python benchmarks/run_benchmarks.py` estimates the cut (heuristic, ~69% on that
pair) -- **note: `benchmarks/` was removed in this cut-down build**; restore it
from an earlier commit if you want this specific measurement. Code savings are
qualitative and not separately benchmarked.

## Run the tests

```
python tests/test_skill.py       # structure + enforces "no CJK in source" (Principle 3.1)
```

## Design rule: no Chinese in source

Chinese characters appear in exactly one place: the agent's runtime output in wenyan
mode, or user-supplied text passed as a CLI argument. Never in source, configs,
comments, identifiers, tests, or docs. Detection/enforcement is Unicode codepoint
arithmetic, checked by `tests/test_skill.py`.

## License

MIT — see [`LICENSE`](LICENSE). Upstream credits in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). Note: caveman is MIT for its
prose/skill half and BSL-1.1 for its engine dirs; VOIDWEN adapts only the MIT half.
Translation models (raynardj's wenyanwen-ancient-translate-to-modern,
Helsinki-NLP's opus-mt-zh-en) are used as-is under their own licenses -- see their
respective Hugging Face model cards.
