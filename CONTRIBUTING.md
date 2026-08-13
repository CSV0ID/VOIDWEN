# Contributing to VOIDWEN

VOIDWEN follows its own rules. Before opening a PR:

1. **No CJK in source.** Chinese characters belong only in runtime output and the
   HuggingFace-hosted corpus. Everything tracked here is English + codepoint math.
   `python tests/test_skill.py` enforces this and must pass.
2. **YAGNI.** Climb the ladder before adding code (see `AGENTS.md`). No speculative
   abstractions, no scaffolding "for later". Deletion beats addition.
3. **Don't copy upstream.** caveman and ponytail are MIT (caveman's engine is BSL);
   rewrite behavior from the rules, keep their license text only in
   `THIRD_PARTY_NOTICES.md`.
4. **Leave one runnable check** for non-trivial logic.

Run all tests:

```
python tests/test_skill.py
```
