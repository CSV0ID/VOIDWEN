"""Scrape classical Chinese + English translation pairs from ctext.org.

Largest structured classical corpus online (Analects, Mencius, Zhuangzi, Laozi,
Shiji, Han Feizi, ...) with public-domain English (Legge/Giles). Rate limited to one
request per 2 seconds per the master plan (section 7.3).

voidwen: the CSS selectors below are best-effort and MUST be verified against the
live ctext.org DOM before a real run. ctext markup changes; treat a zero-pair result
as "selectors stale", not "no data".
"""
from __future__ import annotations

import csv
import sys

from bs4 import BeautifulSoup

from fetch import RateLimitedFetcher

# Verify against live DOM before running. ctext renders source and translation in
# aligned table rows; adjust if the structure differs.
ROW_SELECTOR = "table.text tr"
SRC_CELL_SELECTOR = "td.ctext"
TGT_CELL_SELECTOR = "td.etext"


def parse_pairs(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for row in soup.select(ROW_SELECTOR):
        src = row.select_one(SRC_CELL_SELECTOR)
        tgt = row.select_one(TGT_CELL_SELECTOR)
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
            except Exception as exc:  # keep going; one bad page must not kill the run
                print(f"skip {url}: {exc}", file=sys.stderr)
    print(f"wrote {n} pairs to {out_tsv}")


if __name__ == "__main__":
    # Pass text URLs as args: python ctext_scraper.py out.tsv url1 url2 ...
    scrape(sys.argv[2:], sys.argv[1])
