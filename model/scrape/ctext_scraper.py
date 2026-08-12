"""Fetch classical Chinese + English translation pairs from ctext.org via its
official API (not HTML scraping — ctext.org bot-blocks plain requests.get() on
its text pages).

Uses the `ctext` PyPI package (MIT, Donald Sturgeon). Install: pip install ctext

Fixed from the previous version: setlanguage("") is not a valid call (the API
needs a real language code) — that silently raised inside a broad except and
produced 0 pairs with no visible error. This version calls setlanguage("zh")
explicitly for the Chinese pull and never swallows errors silently.
"""
from __future__ import annotations

import csv
import sys
import time

from ctext import setapikey, setlanguage, gettextasparagrapharray

setapikey("demo")

# CTP URNs for classical-Chinese chapters with English translations available.
# Add more from https://ctext.org (URN shown bottom-right of each text page).
DEFAULT_URNS = [
    "ctp:analects",
    "ctp:mencius",
    "ctp:zhuangzi",
    "ctp:dao-de-jing",
]


def fetch_pairs(urn: str, min_interval_s: float = 1.0):
    """Yield (chinese, english) pairs for one URN.

    gettextasparagrapharray returns Chinese and English paragraph arrays that
    are index-aligned when both languages are available for the text.
    """
    setlanguage("zh")
    zh = gettextasparagrapharray(urn)
    print(f"  {urn}: {len(zh)} Chinese passages", file=sys.stderr)
    time.sleep(min_interval_s)

    setlanguage("en")
    en = gettextasparagrapharray(urn)
    print(f"  {urn}: {len(en)} English passages", file=sys.stderr)
    time.sleep(min_interval_s)

    if len(zh) != len(en):
        print(f"  WARNING {urn}: length mismatch ({len(zh)} vs {len(en)}) "
              f"— pairs past the shorter length are dropped, alignment may drift",
              file=sys.stderr)

    for src, tgt in zip(zh, en):
        src, tgt = src.strip(), tgt.strip()
        if src and tgt:
            yield src, tgt


def scrape(urns, out_tsv: str):
    n = 0
    with open(out_tsv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, delimiter="\t")
        for urn in urns:
            print(f"fetching {urn}...", file=sys.stderr)
            try:
                count_before = n
                for src, tgt in fetch_pairs(urn):
                    writer.writerow([src, tgt])
                    n += 1
                print(f"  wrote {n - count_before} pairs from {urn}", file=sys.stderr)
            except Exception as exc:
                # Print the real error instead of swallowing it — a previous
                # version of this scraper hid a real bug this way.
                import traceback
                print(f"FAILED on {urn}: {exc}", file=sys.stderr)
                traceback.print_exc()
    print(f"wrote {n} pairs total to {out_tsv}")


if __name__ == "__main__":
    # python ctext_scraper.py out.tsv [urn1 urn2 ...]
    # Falls back to DEFAULT_URNS if none given.
    out = sys.argv[1] if len(sys.argv) > 1 else "ctext.tsv"
    urns = sys.argv[2:] or DEFAULT_URNS
    scrape(urns, out)
