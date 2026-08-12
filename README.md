# VOIDWEN

> **By CS VOID LABS · CSV0ID**
> *Classical silence. Minimal code. Zero waste.*

One switch for two problems: compress what an AI coding agent **says** (prose) and
what it **builds** (code). Optionally, output prose in **wenyan** (classical Chinese)
and translate it back to English entirely in the browser — zero server, zero API,
zero tokens.

VOIDWEN merges the approaches of two upstream skills into one conflict-free skill:

- [**caveman**](https://github.com/JuliusBrussee/caveman) — prose compression
- [**ponytail**](https://github.com/DietrichGebert/ponytail) — YAGNI code minimalism

Their rules were **rewritten from scratch**, not copied. See
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Status

Built and tested here:

| Part | State |
|---|---|
| Prose + code skill (`skills/voidwen/SKILL.md`) | Done |
| Commands (7) | Done |
| Browser detector + doc→markdown + translator UI (`web/`) | Code done; needs the model to translate |
| Data pipeline + model + export scripts (`model/`) | Ready to run on Colab |
| Tests (`tests/`, run below) | Passing |

**Not done** (needs your accounts / GPUs / hours — nothing was faked):

- The wenyan→English model is **not trained or published** yet. `model/` has
  ready-to-run scripts; BLEU > 33 is a **target**, not a measured result.
- The dataset `CSV0ID/voidwen-wenyan-en` is **not published** yet.
- The site is **not deployed**; there is no GitHub repo created yet.

## Install the skill (Claude Code)

```
/plugin marketplace add CSV0ID/voidwen
/plugin install voidwen@voidwen
```

Or copy [`AGENTS.md`](AGENTS.md) into any project for a portable, all-agent version.

Set the level:

```
/voidwen full        # default: compressed prose + YAGNI code
/voidwen ultra       # telegraphic prose, delete-before-add
/voidwen wenyan      # classical Chinese output (translate in the browser app)
/voidwen off
```

## Before / after (prose)

```
before: Sure! I'd be happy to help. The issue is most likely caused by the auth
        middleware, which checks the token expiry.
after:  Bug in auth middleware. Token expiry check wrong.
```

`python benchmarks/run_benchmarks.py` estimates the cut (heuristic, ~69% on that
pair). It measures prose only; code savings are qualitative.

## Run the tests

```
python tests/test_skill.py       # structure + enforces "no CJK in source" (Principle 3.1)
python model/clean/classical_scorer.py
python model/clean/pipeline.py
node tests/test_detection.js
node tests/test_pipeline.js
```

## Browser app (`web/`)

Static site. Serve it locally:

```
python -m http.server -d web 8000   # then open http://localhost:8000
```

Doc → markdown works immediately. Wenyan → English needs the published model.

## Reproduce the model

See [`model/README.md`](model/README.md). Everything runs on Colab free tier; no
step here was executed for you.

## Design rule: no Chinese in source

Chinese characters appear in exactly one place: the agent's runtime output in wenyan
mode. Never in source, configs, comments, identifiers, tests, notebooks, or docs.
Detection is Unicode codepoint arithmetic. `tests/test_skill.py` enforces this.
The bilingual training corpus is the sole exception and lives on HuggingFace only
(gitignored).

## License

MIT — see [`LICENSE`](LICENSE). Upstream credits in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). Note: caveman is MIT for its
prose/skill half and BSL-1.1 for its engine dirs; VOIDWEN adapts only the MIT half.
