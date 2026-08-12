"""Scrape Buddhist sutra parallel pairs: Taisho Tripitaka (classical Chinese) aligned
with Numata Center English translations.

High-quality, consistent alignment (master plan section 7.3). Same shape as the
ctext scraper. Taisho source is public domain; verify Numata translation terms per
text before publishing (see THIRD_PARTY_NOTICES / dataset card).

voidwen: source-specific selectors must be verified against whichever Taisho/Numata
host is used before a real run.
"""
from __future__ import annotations

import csv
import sys

from bs4 import BeautifulSoup

from fetch import RateLimitedFetcher

ROW_SELECTOR = "div.parallel .row"
SRC_SELECTOR = ".source"
TGT_SELECTOR = ".translation"


def parse_pairs(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for row in soup.select(ROW_SELECTOR):
        src = row.select_one(SRC_SELECTOR)
        tgt = row.select_one(TGT_SELECTOR)
        if src and tgt:
            s, t = src.get_text(" ", strip=True), tgt.get_text(" ", strip=True)
            if s and t:
                yield s, t


def scrape(urls, out_tsv: str):
    fetcher = RateLimitedFetcher(min_interval_s=2.0)
    n = 0
    with open(out_tsv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, delimiter="\t")
        for url in urls:
            try:
                for src, tgt in parse_pairs(fetcher.get(url)):
                    writer.writerow([src, tgt])
                    n += 1
            except Exception as exc:
                print(f"skip {url}: {exc}", file=sys.stderr)
    print(f"wrote {n} pairs to {out_tsv}")


if __name__ == "__main__":
    scrape(sys.argv[2:], sys.argv[1])
