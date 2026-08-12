---
description: Audit the whole repo for over-engineering.
---

Audit the repository for over-engineering, not one diff. Sweep the source tree
(skip vendored/`node_modules`/generated dirs). Rank findings by how much complexity
their removal buys back.

Look for: abstractions with one caller, dead code, config that never varies,
duplicated helpers that should be one, dependencies used for a few lines, deep
inheritance where composition or a function would do, scaffolding built "for later"
that later never used.

Output a ranked list, one line per finding:

`path:line: <problem>. <lazier alternative>.`

End with a one-line total: how many files could shrink or disappear. Do not propose
new abstractions. Do not touch validation, error handling, security, or
accessibility. This command reports only — it does not edit.
