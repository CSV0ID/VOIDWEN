"""Estimate token savings from VOIDWEN prose compression.

Deliberately model-free: it approximates tokens as characters / divisor and compares
a verbose "before" against a compressed "after". This measures prose compression
only; code-minimalism savings (lines not written) are not automatable and are
reported qualitatively in the README. No numbers here are pre-filled — run it on
your own before/after pairs.

    python benchmarks/run_benchmarks.py                 # built-in demo pair
    python benchmarks/run_benchmarks.py before.txt after.txt
"""
from __future__ import annotations

import sys

CHARS_PER_TOKEN_EN = 4.0
CHARS_PER_TOKEN_WENYAN = 2.2


def is_cjk(cp: int) -> bool:
    return 0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF


def est_tokens(text: str) -> float:
    cjk = sum(1 for ch in text if is_cjk(ord(ch)))
    other = len(text) - cjk
    return cjk / CHARS_PER_TOKEN_WENYAN + other / CHARS_PER_TOKEN_EN


def report(before: str, after: str) -> float:
    b, a = est_tokens(before), est_tokens(after)
    pct = 0.0 if b == 0 else (b - a) / b * 100
    print(f"before: ~{b:.0f} tokens")
    print(f"after:  ~{a:.0f} tokens")
    print(f"cut:    {pct:.0f}%  (estimate, chars/token heuristic)")
    return pct


def main() -> None:
    if len(sys.argv) == 3:
        before = open(sys.argv[1], encoding="utf-8").read()
        after = open(sys.argv[2], encoding="utf-8").read()
    else:
        before = ("Sure! I'd be happy to help you with that. The issue you are "
                  "experiencing is most likely caused by the authentication "
                  "middleware, which checks the token expiry.")
        after = "Bug in auth middleware. Token expiry check wrong."
    report(before, after)


if __name__ == "__main__":
    main()
