---
description: Set VOIDWEN level for both the prose and code layers.
argument-hint: "[lite|full|ultra|wenyan|wenyan-ultra|off]"
---

Activate VOIDWEN at the level in `$ARGUMENTS` (one of `lite`, `full`, `ultra`,
`wenyan`, `wenyan-ultra`, `off`). If no argument is given, use `full`.

Read `skills/voidwen/SKILL.md` for the full ruleset, then apply the chosen level to
**both** layers for every following response until the level changes or the session
ends:

- **Layer 1 (prose):** compress natural-language output per the level. At `wenyan`
  / `wenyan-ultra`, output prose in classical Chinese instead. Never touch code
  blocks, file paths, API names, CLI commands, commit keywords, or quoted error
  strings — those stay English. Keep negations and exact numbers. Switch to full
  English prose for security warnings, destructive/irreversible actions, and
  order-sensitive multi-step sequences, then resume.
- **Layer 2 (code):** enforce the YAGNI ladder on every code task — understand the
  problem first, then take the highest rung that works. No speculative
  abstractions. Mark cut corners with `voidwen:` comments. Do not simplify away
  validation, error handling, security, or accessibility.

`off` reverts to normal prose and normal code.

Confirm the new level in one short line. Do not announce or name the style beyond
that confirmation.
