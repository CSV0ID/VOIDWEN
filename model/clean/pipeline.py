"""Cleaning pipeline for the wenyan -> English parallel corpus.

Input/output are lists of (source, target) tuples. Chinese text lives only in the
data flowing through at runtime, never as a literal in this file. Heavy deps
(datasketch, langdetect) are imported inside the steps that need them so the pure
steps run without them.

Order: exact dedup -> near dedup -> language check -> length filter -> classical
score -> holdout removal. See VOIDWEN master plan section 7.2.
"""
from __future__ import annotations

import hashlib

from classical_scorer import cjk_ratio, is_classical

SRC_MIN_CHARS, SRC_MAX_CHARS = 4, 120
TGT_MIN_WORDS, TGT_MAX_WORDS = 5, 200
NEAR_DUP_JACCARD = 0.8


def _norm(text: str) -> str:
    return " ".join(text.split()).strip()


def _pair_hash(src: str, tgt: str) -> str:
    return hashlib.sha256(f"{_norm(src)}\t{_norm(tgt)}".encode()).hexdigest()


def exact_dedup(pairs):
    seen = set()
    for src, tgt in pairs:
        h = _pair_hash(src, tgt)
        if h not in seen:
            seen.add(h)
            yield src, tgt


def near_dedup(pairs, threshold: float = NEAR_DUP_JACCARD):
    from datasketch import MinHash, MinHashLSH  # requirements: datasketch

    pairs = list(pairs)
    lsh = MinHashLSH(threshold=threshold, num_perm=64)
    kept = []
    for i, (src, tgt) in enumerate(pairs):
        m = MinHash(num_perm=64)
        for token in set(_norm(tgt).lower().split()):
            m.update(token.encode())
        if not lsh.query(m):
            lsh.insert(str(i), m)
            kept.append((src, tgt))
    return kept


def lang_ok(src: str, tgt: str) -> bool:
    from langdetect import detect  # requirements: langdetect

    if cjk_ratio(src) <= 0.0:
        return False
    try:
        return detect(tgt) == "en"
    except Exception:
        return False


def length_ok(src: str, tgt: str) -> bool:
    return SRC_MIN_CHARS <= len(src) <= SRC_MAX_CHARS and TGT_MIN_WORDS <= len(tgt.split()) <= TGT_MAX_WORDS


def clean(pairs, holdout_hashes=frozenset(), skip_near_dedup=False, skip_lang=False):
    """Run the full pipeline. skip_* flags let callers run without heavy deps."""
    out = list(exact_dedup(pairs))
    if not skip_near_dedup:
        out = near_dedup(out)
    result = []
    for src, tgt in out:
        if _pair_hash(src, tgt) in holdout_hashes:
            continue
        if not length_ok(src, tgt):
            continue
        if not skip_lang and not lang_ok(src, tgt):
            continue
        if not is_classical(src):
            continue
        result.append((src, tgt))
    return result


def _selfcheck() -> None:
    # Codepoint-built classical source; ASCII English target. No CJK literals here.
    cls = "".join(chr(c) for c in (0x5B50, 0x66F0, 0x5B78, 0x800C, 0x6642, 0x4E60, 0x4E4B))
    pairs = [
        (cls, "The Master said: to learn and practice in time."),
        (cls, "The Master said: to learn and practice in time."),  # exact dup
        ("ab", "too short target"),                                 # src too short
    ]
    out = clean(pairs, skip_near_dedup=True, skip_lang=True)
    assert len(out) == 1, out
    assert out[0][0] == cls
    print("pipeline self-check OK")


if __name__ == "__main__":
    _selfcheck()
