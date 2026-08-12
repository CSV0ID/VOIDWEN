"""Classical Chinese (wenyan) scoring via Unicode codepoint arithmetic.

No CJK character literals appear in this file (VOIDWEN Core Principle 3.1). Every
Chinese character is referenced by its integer codepoint. The self-check builds its
test strings with chr(codepoint), so no literal ever enters the source.

Signal: density of common classical function words (particles). Classical Chinese
uses these far more than modern Chinese, so their density separates the two well
enough for corpus filtering.

voidwen: particle-density heuristic, not a trained classifier. Upgrade to an
integer-codepoint-keyed frequency model (see load_frequency_ranks) if precision on
borderline semi-classical text matters.
"""
from __future__ import annotations

import json

# CJK codepoint ranges (no character literals).
CJK_START, CJK_END = 0x4E00, 0x9FFF
CJK_EXT_A_START, CJK_EXT_A_END = 0x3400, 0x4DBF

# Codepoints of common classical function words, named in romanization only.
CLASSICAL_PARTICLE_CODEPOINTS = frozenset({
    0x4E4B,  # zhi  - genitive / object particle
    0x4E4E,  # hu   - question / exclamation particle
    0x8005,  # zhe  - nominalizer
    0x4E5F,  # ye   - classical copula / final particle
    0x77E3,  # yi   - perfective final particle
    0x7109,  # yan  - final particle / pronoun
    0x5176,  # qi   - possessive pronoun
    0x800C,  # er   - conjunction
    0x4E43,  # nai  - then / thereupon
    0x5F17,  # fu   - initial particle
    0x6240,  # suo  - relativizer
    0x4E88,  # yu   - first-person pronoun (classical)
})

MODERN_VOCAB_RATIO_MAX = 0.30


def is_cjk(codepoint: int) -> bool:
    return (CJK_START <= codepoint <= CJK_END) or (CJK_EXT_A_START <= codepoint <= CJK_EXT_A_END)


def cjk_ratio(text: str) -> float:
    if not text:
        return 0.0
    cjk = sum(1 for ch in text if is_cjk(ord(ch)))
    return cjk / len(text)


def particle_density(text: str) -> float:
    """Fraction of CJK characters that are classical function words."""
    cjk = [ch for ch in text if is_cjk(ord(ch))]
    if not cjk:
        return 0.0
    hits = sum(1 for ch in cjk if ord(ch) in CLASSICAL_PARTICLE_CODEPOINTS)
    return hits / len(cjk)


def load_frequency_ranks(path: str) -> dict[int, int]:
    """Load an optional modern-frequency model: {codepoint_int: rank}.

    Keys are integer codepoints, never characters, so the file stays CJK-free.
    Lower rank = more common in modern Chinese.
    """
    with open(path, encoding="ascii") as fh:
        raw = json.load(fh)
    return {int(k): int(v) for k, v in raw.items()}


def is_classical(text: str, min_particle_density: float = 0.06, min_cjk_ratio: float = 0.5) -> bool:
    """True if text scores as classical Chinese suitable for the wenyan corpus."""
    return cjk_ratio(text) >= min_cjk_ratio and particle_density(text) >= min_particle_density


def _selfcheck() -> None:
    # Build test strings from codepoints only (no CJK literals in source).
    classical = "".join(chr(c) for c in (0x5B50, 0x66F0, 0x5B78, 0x800C, 0x6642, 0x4E60, 0x4E4B))
    modern = "".join(chr(c) for c in (0x6211, 0x4EEC, 0x4ECA, 0x5929, 0x53BB, 0x5B66, 0x6821))
    assert cjk_ratio(classical) == 1.0
    assert particle_density(classical) > particle_density(modern)
    assert is_classical(classical)
    assert not is_classical(modern)
    assert not is_cjk(ord("a")) and is_cjk(0x4E00)
    print("classical_scorer self-check OK")


if __name__ == "__main__":
    _selfcheck()
