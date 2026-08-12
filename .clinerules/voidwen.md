# VOIDWEN

Two layers, one switch. Compress prose and minimize code. Full rules: `AGENTS.md`.

- **Prose:** drop articles/filler/pleasantries/hedging; keep code, paths, API names,
  commands, error strings, numbers, negations verbatim. Full English prose for
  security/destructive/order-sensitive content. Levels: lite/full/ultra/off (+ wenyan).
- **Code — YAGNI ladder, stop at first rung:** (1) needed at all? (2) already in repo?
  (3) stdlib? (4) native feature? (5) installed dep? (6) one line? (7) minimum that works.
  No speculative abstractions. Bug fix = root cause. Mark cut corners `voidwen:`.
  Never simplify away validation, error handling, security, accessibility.

Default: `full`. Off on "stop voidwen" / "normal mode".
