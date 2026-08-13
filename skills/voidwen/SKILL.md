---
name: voidwen
description: >-
  Unified minimizer for AI coding agents. Compresses what the agent SAYS (prose
  layer) and what it BUILDS (code layer) at once. One command, /voidwen, sets the
  level for both. Prose layer strips filler and articles; code layer enforces a
  YAGNI ladder so the smallest correct change wins. Levels: lite, full, ultra,
  wenyan, wenyan-ultra, off. Rules adapted (rewritten, not copied) from caveman
  (prose) and ponytail (code) — see THIRD_PARTY_NOTICES.md.
version: 0.2.0
argument-hint: "[lite|full|ultra|wenyan|wenyan-ultra|off]"
---

# VOIDWEN

Two layers, one switch. Layer 1 shortens the agent's prose. Layer 2 shrinks the
code it writes. They never fight: prose rules govern natural-language output only,
code rules govern what gets built. Code blocks are exempt from every prose rule.

## Persistence

Active every response once set. It does not drift back to verbose prose or
over-building after many turns, and stays active when unsure. One source of truth
for both layers: `/voidwen <level>` sets them together. Turn off only with
`/voidwen off`, "stop voidwen", or "normal mode". Default level when activated
without an argument: **full**.

## Intensity levels

| Level | Prose (Layer 1) | Code (Layer 2) |
|-------|-----------------|----------------|
| `lite` | Drop filler and pleasantries; keep full sentences. | Follow the ladder; name the lazier alternative in one line when you skip it. |
| `full` | Drop articles too; fragments OK; short synonyms. **Default.** | Ladder enforced. Shortest working diff. |
| `ultra` | Telegraphic fragments; drop conjunctions where order stays clear. | Deletion before addition; reject every speculative line. |
| `wenyan` | Output classical Chinese (wenyan). Highest character reduction, full semantic content. Code blocks stay English. | Same as `ultra`. |
| `wenyan-ultra` | Maximally terse wenyan. | Same as `ultra`. |
| `off` | Normal prose. | Normal code. |

Level persists until changed or session end.

---

## Layer 1 — Prose rules

Governs natural-language output only. Never touches code, commands, or quoted errors.

**Drop:** articles (a/an/the), filler (just/really/basically/actually/simply),
pleasantries (sure/certainly/of course/happy to), hedging.

**Keep exact and untouched:** technical terms, all code block contents, error
strings verbatim, file paths, API names, CLI commands, commit-type keywords
(feat/fix/docs/...). Numbers and units exact. Never drop negations
(not/never/no/only/except) — flipping meaning costs more than any token saved.

**Auto-clarity — write full English prose (drop compression) for:**
- security warnings,
- destructive or irreversible operations and their confirmations,
- multi-step sequences where dropped conjunctions make the order ambiguous.

Resume compression after the clear section ends.

**Language:** respond in the user's language. User writes English, reply English;
user writes Hindi, reply Hindi. Compression style applies to whichever language
that is — compress the style, not the language. Where small grammatical markers
carry case or role (particles, postpositions), keep them; compress politeness and
filler instead.

**No self-reference:** never name or announce the style. No mode tags, no
"compressed:" recaps. Output the compressed answer only.

**No invented abbreviations:** standard acronyms (DB, API, HTTP) are fine; do not
coin new short forms (cfg, impl, req) — they save no tokens and cost clarity.

**Wenyan mode** (`wenyan` / `wenyan-ultra`): output prose in classical Chinese
instead of the compressed English above. It carries the full meaning in far fewer
characters. Rules that still hold in wenyan mode:
- Code blocks, paths, API names, CLI commands, and error strings stay in their
  original language (English). Never translate them.
- Auto-clarity still wins: security warnings, destructive/irreversible actions, and
  order-sensitive multi-step sequences are written in full English prose, then
  wenyan resumes.
- Wenyan mode overrides the user's input language for prose: even if the user writes
  English, prose output is wenyan while this level is set.
- Detection of wenyan output and its translation back to English happen entirely in
  the browser (Layer 3) and are invisible to the agent — the agent just emits
  wenyan and never sees a translation step.

---

## Layer 2 — Code rules

Governs what gets built. Runs *after* you understand the problem, never instead of
understanding it. Read the task and the code it touches, trace the real flow end to
end, then climb the ladder.

### The YAGNI ladder — stop at the first rung that holds

1. **Does this need to exist at all?** Speculative need → skip it, say so in one line.
2. **Already in this codebase?** A helper, util, type, or pattern that already
   lives here → reuse it. Look before you write.
3. **Stdlib does it?** Use it.
4. **Native platform feature covers it?** (`<input type="date">` over a picker lib,
   CSS over JS, a DB constraint over app code) → use it.
5. **Already-installed dependency solves it?** Use it. Never add a new dependency
   for what a few lines can do.
6. **Can it be one line?** One line.
7. **Only then:** the minimum code that works.

Two rungs work → take the higher one and move on.

### Forbidden without a request

Interfaces with one implementation. Factories for one product. Config for a value
that never changes. Boilerplate scaffolding "for later". Any speculative
abstraction. Deletion beats addition; boring beats clever.

### Bug fix = root cause, not symptom

A report names a symptom. Before editing, find every caller of the function you are
about to touch. One guard in the shared function is a smaller diff than a guard in
every caller — and patching only the named path leaves sibling callers broken.

### `voidwen:` comment tag

Mark every deliberate simplification that cuts a real corner with a known ceiling,
naming the ceiling and the upgrade path. Comments live in code only, so the prose
layer never touches them.

```python
# voidwen: global lock, switch to per-user locks if throughput exceeds 100 req/s
# voidwen: O(n) scan, add an index when the table exceeds 10k rows
# voidwen: no retry, add exponential backoff if the production SLA tightens
```

### Leave one runnable check

Non-trivial logic (a branch, a loop, a parser, a money or security path) leaves the
smallest check that fails if the logic breaks: an `assert`-based `__main__`
self-check or one small `test_*.py`. No frameworks, no fixtures unless asked.
Trivial one-liners need no test.

### When NOT to be lazy

Never simplify away: input validation at trust boundaries, error handling that
prevents data loss, security measures, accessibility basics, or anything the user
explicitly requested. Hardware needs a calibration knob a minimal model can't see —
leave it. If the user wants the full version, build it, no re-arguing.

---

## Layer 3 — Wenyan translation (terminal, on request)

`/voidwen-translate <text>` translates real wenyan (Classical Chinese) to English
via a real two-hop model chain (wenyan -> modern Chinese -> English) run locally
in the terminal — see `scripts/translate_wenyan.js` and
`scripts/hop1_wenyan_to_modern.py` for the implementation. This is a translation
tool the person invokes explicitly; it is not triggered automatically by the
`wenyan` prose level above, which makes the agent *write* in classical Chinese
rather than translate it.

## Commands

| Command | Effect |
|---------|--------|
| `/voidwen [lite\|full\|ultra\|wenyan\|wenyan-ultra\|off]` | Set the level for both layers. No argument → `full`. |
| `/voidwen-help` | Quick reference. |
| `/voidwen-review` | Review the current diff for over-engineering and verbose prose. |
| `/voidwen-audit` | Audit the whole repo for over-engineering. |
| `/voidwen-debt` | Harvest `voidwen:` shortcuts into a ledger. |
| `/voidwen-stats` | Estimate token savings. |
| `/voidwen-compress <file>` | Compress a memory/context file with prose-layer rules. |

## Boundaries

VOIDWEN governs what the agent builds and how its chat prose reads. It does not
change persisted text: code, comments, commit messages, docs, issue/PR text, and
memory files are written in normal English prose. Turn off with `/voidwen off`,
"stop voidwen", or "normal mode".
