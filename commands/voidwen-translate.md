---
description: Translate wenyan (Classical Chinese) text to English using a real local model, in the terminal.
argument-hint: "[wenyan text]"
---

Translate the wenyan (Classical Chinese) text in `$ARGUMENTS` to English by actually
running the local translation pipeline -- this is a real two-hop ML model chain
(wenyan -> modern Chinese -> English), not a language-model guess.

Requires Python 3 with `transformers` + `torch` installed (for hop1 -- see
`scripts/hop1_wenyan_to_modern.py` for why hop1 can't run in pure Node/JS) and
Node with `npm install` already run (for hop2, native).

Run:

```bash
node scripts/translate_wenyan.js "$ARGUMENTS"
```

If `node_modules` is missing or the command fails with a module-not-found error,
run `npm install` first, then retry once.

First run downloads two ONNX models (~450MB total) and caches them; later runs
are fast and fully offline. Print the script's output as the answer. If the
script errors, show the error rather than attempting to translate the text
yourself from memory -- accuracy matters more than speed here, and this
command exists specifically to avoid guessing.
