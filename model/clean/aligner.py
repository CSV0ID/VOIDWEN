"""Thin wrapper around the hunalign sentence aligner.

Requires the `hunalign` binary on PATH (open source). Used to align noisy
source/target text (WikiSource) into sentence pairs with a confidence score.

voidwen: shells out to hunalign rather than reimplementing alignment. Replace with
a library only if the subprocess boundary becomes a bottleneck.
"""
from __future__ import annotations

import subprocess
import tempfile

MIN_CONFIDENCE = 0.4


def align(src_lines: list[str], tgt_lines: list[str], dictionary: str = "/dev/null"):
    """Return [(src, tgt, confidence)] for pairs above MIN_CONFIDENCE.

    hunalign output format: src <tab> tgt <tab> score, one pair per line.
    """
    with tempfile.NamedTemporaryFile("w", suffix=".src", delete=False) as s, \
         tempfile.NamedTemporaryFile("w", suffix=".tgt", delete=False) as t:
        s.write("\n".join(src_lines))
        t.write("\n".join(tgt_lines))
        src_path, tgt_path = s.name, t.name

    proc = subprocess.run(
        ["hunalign", "-text", dictionary, src_path, tgt_path],
        capture_output=True, text=True, check=True,
    )
    pairs = []
    for line in proc.stdout.splitlines():
        cols = line.split("\t")
        if len(cols) != 3:
            continue
        src, tgt, score = cols
        try:
            conf = float(score)
        except ValueError:
            continue
        if conf >= MIN_CONFIDENCE and src.strip() and tgt.strip():
            pairs.append((src.strip(), tgt.strip(), conf))
    return pairs
