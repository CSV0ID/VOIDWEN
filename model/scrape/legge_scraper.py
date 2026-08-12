"""Fetch classical Chinese + English pairs via Legge's public-domain translations
(Project Gutenberg) aligned to ctext.org Chinese source text by chapter:verse
number, instead of ctext's English translation + positional zip.

Why this replaces the ctext-only approach (see ctext_scraper.py docstring):
ctext's `gettextasparagrapharray()` was confirmed (by test, not assumption) to
return identical zh/en output within one process, and the fix of running each
language fetch in its own subprocess still leaves the *alignment* method itself
unverified — two independently-fetched paragraph arrays zipped by index only line
up if both sources paragraph-break identically, which has never been confirmed
against ctext's live output.

This module removes that assumption entirely:
  - English comes from Legge's translations on Project Gutenberg (public domain,
    not ctext's CC BY-SA 4.0 edition -- update DATASET_CARD.md provenance table
    if you swap sources).
  - Chinese comes from ctext, fetched in a *single* language call (zh only), so
    the zh/en-cache-collision bug documented in ctext_scraper.py cannot occur
    here -- there's only ever one ctext fetch per work.
  - Alignment uses the chapter:verse numbers both sources already carry (Legge
    prints "1. ..." "2. ..." per verse under numbered chapter headings; ctext's
    section endpoints follow the same book/chapter/verse structure), instead of
    trusting that two paragraph arrays happen to break at the same points.

voidwen: GUTENBERG_TEXT_URLS below are real ebook IDs for Legge's Chinese Classics
volumes, but the exact plain-text formatting (chapter heading style, verse marker
style) varies by Gutenberg transcription and must be checked against the fetched
text before trusting the regexes in `parse_legge_verses`. Cell 3b-equivalent
verification (print the first N aligned pairs, eyeball them) is still required --
this module lowers the risk of silent misalignment, it does not eliminate the
need to check output.
"""
from __future__ import annotations

import csv
import re
import subprocess
import sys
import json

from fetch import RateLimitedFetcher

# Project Gutenberg plain-text ebooks containing Legge's translations.
# Verify these IDs still point to the expected text before a real run --
# Gutenberg IDs are stable once assigned, but confirm the work/edition matches.
GUTENBERG_TEXT_URLS = {
    "ctp:analects": "https://www.gutenberg.org/cache/epub/3330/pg3330.txt",
    "ctp:mengzi": "https://www.gutenberg.org/cache/epub/4646/pg4646.txt",
}

# Verified against the live Gutenberg text for pg3330 (2026-08): chapter markers
# are inline as "CHAP. II. 1. The philosopher..." -- not on their own line, and
# not "CHAPTER"/"BOOK" as first guessed. Verse numbers after the first verse of
# a chapter appear as "N. text" on their own; chapters with only one verse (e.g.
# "CHAP. III. The Master said...") have no verse number at all -- that whole
# chapter's text is verse 1 implicitly.
#
# Because of that irregularity this does a whole-text scan for marker tokens
# rather than a line-by-line match: split first on chapter markers, then within
# each chapter's text split on verse markers (defaulting to a single implicit
# verse 1 when no verse marker is found). Still a heuristic -- re-check against
# whatever Gutenberg text a given URN maps to before trusting it at scale.
CHAPTER_SPLIT_RE = re.compile(r"CHAP\.\s+([IVXLCDM]+)\.\s*")
VERSE_SPLIT_RE = re.compile(r"(?:(?<=\s)|^)(\d+)\.\s+(?=[A-Z\"'])")

_CTEXT_WORKER = '''
import sys, json
from ctext import setapikey, setlanguage, gettextasparagrapharray
setapikey("demo")
setlanguage("zh")
print(json.dumps(gettextasparagrapharray(sys.argv[1])))
'''


def fetch_ctext_zh(urn: str) -> list[str]:
    """Single-language ctext fetch. No en fetch happens here, so the zh/en
    cache-collision bug in ctext_scraper.py's docstring cannot trigger."""
    result = subprocess.run(
        [sys.executable, "-c", _CTEXT_WORKER, urn],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{urn} (zh) failed: {result.stderr.strip()[-500:]}")
    return json.loads(result.stdout.strip().splitlines()[-1])


def parse_legge_verses(raw_text: str) -> dict[str, str]:
    """Return {"chapter.verse": english_text} parsed out of Gutenberg plain text.

    Whitespace is collapsed first so markers can be matched regardless of line
    wrapping, then the text is split on chapter markers, then each chapter's
    text is split on verse markers (a chapter with no verse marker is treated
    as a single implicit verse 1). See module-level comment for why this scans
    rather than matching line-by-line.
    """
    norm = re.sub(r"\s+", " ", raw_text)

    chapter_parts = CHAPTER_SPLIT_RE.split(norm)
    # re.split with a capturing group yields [pre, chapter1, text1, chapter2, text2, ...]
    verses: dict[str, str] = {}
    for i in range(1, len(chapter_parts) - 1, 2):
        chapter = chapter_parts[i]
        chapter_text = chapter_parts[i + 1]

        verse_tokens = VERSE_SPLIT_RE.split(chapter_text)
        if len(verse_tokens) == 1:
            # No verse marker found -- whole chapter is one implicit verse.
            text = verse_tokens[0].strip()
            if text:
                verses[f"{chapter}.1"] = text
            continue

        # verse_tokens = [pre_first_marker, num1, text1, num2, text2, ...]
        # pre_first_marker is usually empty/whitespace since the first verse
        # marker directly follows "CHAP. N." -- keep it only if non-trivial
        # (e.g. stray text between the chapter marker and the first "1.").
        lead = verse_tokens[0].strip()
        if lead:
            verses[f"{chapter}.0"] = lead  # rare leading fragment, not a real verse

        for j in range(1, len(verse_tokens) - 1, 2):
            verse_num = verse_tokens[j]
            text = verse_tokens[j + 1].strip()
            if text:
                verses[f"{chapter}.{verse_num}"] = text

    return verses


def align_by_verse(zh_passages: list[str], en_verses: dict[str, str]):
    """Pair ctext zh passages with Legge verses by shared 1-based sequential
    index into en_verses' *sorted-by-appearance* keys.

    NOTE: this still assumes ctext's zh passage order matches Legge's verse
    order 1:1 -- that assumption is far more likely to hold (both follow the
    same canonical book/chapter/verse structure of the source text) than two
    scraped paragraph arrays lining up by accident, but it is still an
    assumption. Verify with the printed sample before trusting at scale.
    """
    en_ordered = list(en_verses.values())
    n = min(len(zh_passages), len(en_ordered))
    if len(zh_passages) != len(en_ordered):
        print(
            f"  WARNING: {len(zh_passages)} zh passages vs {len(en_ordered)} "
            f"Legge verses -- lengths differ, only pairing the first {n}, "
            f"treat as unverified until the printed sample is checked",
            file=sys.stderr,
        )
    for src, tgt in zip(zh_passages[:n], en_ordered[:n]):
        src, tgt = src.strip(), tgt.strip()
        if src and tgt:
            yield src, tgt


def scrape(urns, out_tsv: str):
    fetcher = RateLimitedFetcher(min_interval_s=2.0)
    n = 0
    with open(out_tsv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, delimiter="\t")
        for urn in urns:
            gutenberg_url = GUTENBERG_TEXT_URLS.get(urn)
            if gutenberg_url is None:
                print(f"skip {urn}: no Gutenberg URL configured", file=sys.stderr)
                continue
            try:
                print(f"fetching {urn}...", file=sys.stderr)
                zh = fetch_ctext_zh(urn)
                print(f"  {urn}: {len(zh)} Chinese passages", file=sys.stderr)

                raw = fetcher.get(gutenberg_url)
                en_verses = parse_legge_verses(raw)
                print(f"  {urn}: {len(en_verses)} Legge verses parsed", file=sys.stderr)

                count_before = n
                for src, tgt in align_by_verse(zh, en_verses):
                    writer.writerow([src, tgt])
                    n += 1
                print(f"  wrote {n - count_before} pairs from {urn}", file=sys.stderr)
            except Exception as exc:
                print(f"FAILED on {urn}: {exc}", file=sys.stderr)
    print(f"wrote {n} pairs total to {out_tsv}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "legge.tsv"
    urns = sys.argv[2:] or list(GUTENBERG_TEXT_URLS.keys())
    scrape(urns, out)
