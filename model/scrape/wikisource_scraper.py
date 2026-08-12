"""Scrape classical Chinese works + crowd-sourced English from WikiSource.

Noisier than ctext.org: source and translation are often on separate pages with no
sentence-level alignment. Uses the hunalign wrapper (model/clean/aligner.py) to
produce sentence pairs, then filtered downstream by the cleaning pipeline.

voidwen: selectors and the source/target page pairing are best-effort and must be
verified against live WikiSource before a real run.
"""
from __future__ import annotations

import csv
import sys

from bs4 import BeautifulSoup

from fetch import RateLimitedFetcher

CONTENT_SELECTOR = "div.mw-parser-output p"


def extract_lines(html: str):
    soup = BeautifulSoup(html, "html.parser")
    return [p.get_text(" ", strip=True) for p in soup.select(CONTENT_SELECTOR) if p.get_text(strip=True)]


def scrape(page_pairs, out_tsv: str):
    """page_pairs: iterable of (source_url, target_url) for the same work."""
    # aligner lives in model/clean; make it importable when run from model/scrape.
    sys.path.insert(0, "../clean")
    from aligner import align

    fetcher = RateLimitedFetcher(min_interval_s=2.0)
    n = 0
    with open(out_tsv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, delimiter="\t")
        for src_url, tgt_url in page_pairs:
            try:
                src_lines = extract_lines(fetcher.get(src_url))
                tgt_lines = extract_lines(fetcher.get(tgt_url))
                for src, tgt, _conf in align(src_lines, tgt_lines):
                    writer.writerow([src, tgt])
                    n += 1
            except Exception as exc:
                print(f"skip {src_url}: {exc}", file=sys.stderr)
    print(f"wrote {n} pairs to {out_tsv}")


if __name__ == "__main__":
    print("Provide (source_url, target_url) page pairs via scrape(). See module docstring.")
