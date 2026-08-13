---
description: VOIDWEN quick reference.
---

Print this reference verbatim, then stop.

**VOIDWEN** — one switch, two layers. Prose (what the agent says) + code (what it
builds). `/voidwen <level>` sets both.

Levels:
- `lite` — drop filler/pleasantries, full sentences; ladder with lazier option named.
- `full` — drop articles too, fragments OK; ladder enforced, shortest diff. (Default.)
- `ultra` — telegraphic prose; delete-before-add, reject speculative code.
- `off` — normal prose, normal code.

Prose layer never touches: code blocks, file paths, API names, CLI commands,
commit keywords, error strings, negations, numbers. Full English prose returns for
security warnings, destructive actions, and order-sensitive steps.

Code layer — YAGNI ladder, stop at first rung that holds: (1) needed at all?
(2) already in repo? (3) stdlib? (4) native platform feature? (5) installed dep?
(6) one line? (7) minimum that works. Cut corners marked with `voidwen:` comments.
Never simplify away validation, error handling, security, accessibility.

Commands: `/voidwen [lite|full|ultra|off]`, `/voidwen-help`, `/voidwen-translate [wenyan text]`.

`/voidwen-translate` runs a real local ML model (not a guess) to translate
wenyan -> English: wenyan -> modern Chinese -> English, two chained ONNX
models via `scripts/translate_wenyan.js`. First run downloads ~450MB,
cached after. Different from the `wenyan` prose level above, which makes
Claude *write* in classical Chinese rather than translate it.

Full rules: `skills/voidwen/SKILL.md`. Attribution: `THIRD_PARTY_NOTICES.md`.
