---
description: Rewrite a memory/context file with prose-layer compression to save input tokens.
argument-hint: "<path>"
---

Compress the file at `$ARGUMENTS` by applying VOIDWEN Layer 1 prose rules, then
write the result back to the same path.

This is a deliberate exception to the "persisted files stay normal prose" boundary:
the point is to shrink a context/memory file the agent re-reads every session.

Rules:
- Drop articles, filler, pleasantries, hedging.
- Keep verbatim: code blocks, file paths, API names, CLI commands, error strings,
  numbers, units, negations. Never alter meaning.
- Do not use wenyan here — compress is prose compression in the file's own
  language, not translation. Wenyan output is a separate runtime feature.
- Preserve document structure (headings, lists) so it stays scannable.

Before writing, show a one-line estimate of the character reduction. If the file is
code, source, or config rather than prose/notes, refuse — compressing those risks
breaking them; say so and stop.
