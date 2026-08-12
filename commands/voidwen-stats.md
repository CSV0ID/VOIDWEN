---
description: Estimate token savings from VOIDWEN prose + code minimalism.
argument-hint: "[optional: path to a before/after sample]"
---

Estimate the tokens VOIDWEN saved. There is no telemetry backing this — it is an
approximation, label it as such.

If `$ARGUMENTS` names a file with a verbose "before" version, compare it to the
compressed "after". Otherwise estimate over the current session's visible assistant
prose.

Approximate tokens as `characters / 4` (English) and `characters / 2.2` (wenyan, if
present). Report:

```
Prose:   ~<before> -> ~<after> tokens  (<pct>% cut)
Code:    <n> speculative pieces skipped, ~<loc> lines not written
Est. saving this session: ~<total> output tokens
```

Keep it one small block. Do not invent precise dollar figures; if asked for cost,
multiply by the model's published output price and label the result an estimate.
