"""Classical Chinese (wenyan) scoring via Unicode codepoint arithmetic.

VOIDWEN Core Principle 3.1: no CJK character literals anywhere in source.
All Chinese character logic uses integer codepoints only.
"""
from __future__ import annotations

# CJK Unified Ideographs
CJK_START     = 0x4E00
CJK_END       = 0x9FFF
# CJK Extension A
CJK_EXT_A_START = 0x3400
CJK_EXT_A_END   = 0x4DBF

# Codepoints of classical function words (named in romanization).
# These appear far more frequently in wenyan than in modern Chinese.
# zhi, hu, zhe, ye, yi, yan, qi, er, nai, fu, suo, yu
CLASSICAL_PARTICLE_CODEPOINTS = frozenset({
    0x4E4B,  # zhi  - genitive / object particle
    0x4E4E,  # hu   - question / exclamation particle
    0x8005,  # zhe  - nominalizer
    0x4E5F,  # ye   - final particle (classical copula)
    0x77E3,  # yi   - perfective final particle
    0x7109,  # yan  - final particle / pronoun
    0x5176,  # qi   - possessive pronoun
    0x800C,  # er   - conjunction
    0x4E43,  # nai  - then / thereupon
    0x5F17,  # fu   - initial discourse particle
    0x6240,  # suo  - relativizer
    0x4E88,  # yu   - first-person pronoun (classical form)
    0x6B64,  # ci   - this / demonstrative (classical usage)
    0x4E4D,  # hu   - alternate form, locative particle
    0x65BC,  # yu   - at / in / than (preposition)
})

# Codepoints of common modern-only function words.
# High ratio of these = likely modern Chinese, not wenyan.
# de, le, zhe, ne, ma, ba, men, guo (aspect markers, modern particles)
MODERN_MARKER_CODEPOINTS = frozenset({
    0x7684,  # de  - modern possessive / attributive particle
    0x4E86,  # le  - modern aspect marker (completion)
    0x7740,  # zhe - modern progressive aspect marker
    0x5462,  # ne  - modern question particle
    0x5417,  # ma  - modern yes/no question particle
    0x5427,  # ba  - modern suggestion particle
    0x4EEC,  # men - modern plural suffix
    0x8FC7,  # guo - modern experiential aspect marker
})


def is_cjk(codepoint: int) -> bool:
    return (CJK_START <= codepoint <= CJK_END) or \
           (CJK_EXT_A_START <= codepoint <= CJK_EXT_A_END)


def cjk_ratio(text: str) -> float:
    if not text:
        return 0.0
    count = sum(1 for ch in text if is_cjk(ord(ch)))
    return count / len(text)


def particle_density(text: str) -> float:
    """Fraction of CJK chars that are classical function words."""
    cjk_chars = [ch for ch in text if is_cjk(ord(ch))]
    if not cjk_chars:
        return 0.0
    hits = sum(1 for ch in cjk_chars if ord(ch) in CLASSICAL_PARTICLE_CODEPOINTS)
    return hits / len(cjk_chars)


def modern_marker_ratio(text: str) -> float:
    """Fraction of CJK chars that are modern-only particles."""
    cjk_chars = [ch for ch in text if is_cjk(ord(ch))]
    if not cjk_chars:
        return 0.0
    hits = sum(1 for ch in cjk_chars if ord(ch) in MODERN_MARKER_CODEPOINTS)
    return hits / len(cjk_chars)


def is_classical(
    text: str,
    min_cjk_ratio: float = 0.50,
    min_particle_density: float = 0.05,
    max_modern_marker_ratio: float = 0.08,
) -> bool:
    """True if text scores as classical Chinese suitable for the wenyan corpus."""
    if cjk_ratio(text) < min_cjk_ratio:
        return False
    if particle_density(text) < min_particle_density:
        return False
    if modern_marker_ratio(text) > max_modern_marker_ratio:
        return False
    return True


def _selfcheck() -> None:
    # Build test strings from codepoints only. No CJK literals in source.
    # "zi yue xue er shi xi zhi" - Analects 1.1 opening (classical)
    classical = "".join(chr(c) for c in (0x5B50, 0x66F0, 0x5B78, 0x800C, 0x6642, 0x4E60, 0x4E4B))
    # "wo men jin tian qu xue xiao" - modern sentence "we go to school today"
    modern    = "".join(chr(c) for c in (0x6211, 0x4EEC, 0x4ECA, 0x5929, 0x53BB, 0x5B66, 0x6821))

    assert cjk_ratio(classical) == 1.0
    assert cjk_ratio(modern) == 1.0
    assert particle_density(classical) > particle_density(modern)
    assert modern_marker_ratio(modern) > modern_marker_ratio(classical)
    assert is_classical(classical), "classical sample failed is_classical"
    assert not is_classical(modern), "modern sample should fail is_classical"
    assert not is_cjk(ord("a"))
    assert is_cjk(0x4E00)
    print("scorer self-check OK")


if __name__ == "__main__":
    _selfcheck()
