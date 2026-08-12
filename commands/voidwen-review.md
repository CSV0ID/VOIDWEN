---
description: Review the current diff for over-engineering (code) and verbose prose.
---

Review the current uncommitted diff (`git diff HEAD`; if empty, `git diff`). Apply
both VOIDWEN layers as a checklist. Report one line per finding, most severe first,
no praise, no scope creep:

`path:line: <severity>: <problem>. <fix>.`

Code-layer checks (Layer 2): speculative abstraction, interface/factory with one
implementation, config for a constant, new dependency for a few-line job,
reimplementation of something already in the repo or stdlib, symptom-only bug fix
that leaves sibling callers broken, missing `voidwen:` tag on a real cut corner,
non-trivial logic with no runnable check.

Prose-layer checks (Layer 1): only for prose the diff adds (docs, comments, PR
text) — filler, hedging, pleasantries, redundant restatement.

Never flag: validation at trust boundaries, error handling, security,
accessibility, or anything explicitly requested. Skip pure formatting nits unless
they change meaning. If nothing survives, say so in one line.
