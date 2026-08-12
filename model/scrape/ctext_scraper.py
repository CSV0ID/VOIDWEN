"""Fetch classical Chinese + English translation pairs from ctext.org via the
`ctext` PyPI package (MIT, Donald Sturgeon).

Bug found and confirmed by testing: gettextasparagrapharray() caches by URN only
and ignores setlanguage() on a second call in the same process — calling zh then
en back-to-back returned identical text both times (confirmed: zh[0] == en[0]).

Fix attempted: fetch each language in its own subprocess, on the theory that
separate processes can't share whatever cache causes this. That fix is UNVERIFIED
against live ctext -- it has never actually been run against the real API, only
reasoned about. Separately, `if=en` may control ctext's UI language rather than
which translation edition's text is returned, in which case no combination of
setlanguage()/subprocess isolation exposes English text at all through this path.

Given both of those open questions, model/scrape/legge_scraper.py is the
recommended path for zh->en pairs: it drops ctext's English translation entirely
and uses Legge's public-domain translations from Project Gutenberg instead,
aligned to ctext's zh-only output (a single-language fetch, so the caching bug
above can't trigger) by chapter:verse number. This file is kept for anyone who
wants to test the subprocess theory against a live ctext instance, and because
its zh-only fetch path is reused by legge_scraper.py's own worker.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys

_WORKER = '''
import sys, json
from ctext import setapikey, setlanguage, gettextasparagrapharray
setapikey("demo")
setlanguage(sys.argv[2])
passages = gettextasparagrapharray(sys.argv[1])
print(json.dumps(passages))
'''

DEFAULT_URNS = [
    "ctp:analects",
    "ctp:mengzi",
    "ctp:zhuangzi",
    "ctp:dao-de-jing",
]


def _fetch_one_language(urn: str, lang: str) -> list[str]:
    result = subprocess.run(
        [sys.executable, "-c", _WORKER, urn, lang],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{urn} ({lang}) subprocess failed: {result.stderr.strip()[-500:]}")
    return json.loads(result.stdout.strip().splitlines()[-1])


def fetch_pairs(urn: str):
    zh = _fetch_one_language(urn, "zh")
    print(f"  {urn}: {len(zh)} Chinese passages", file=sys.stderr)

    en = _fetch_one_language(urn, "en")
    print(f"  {urn}: {len(en)} English passages", file=sys.stderr)

    if zh and en and zh[0] == en[0]:
        raise RuntimeError(
            f"{urn}: zh[0] == en[0] even across subprocesses — the caching bug "
            f"is not process-local, do not trust this output, needs a different fix"
        )

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
                print(f"FAILED on {urn}: {exc}", file=sys.stderr)
    print(f"wrote {n} pairs total to {out_tsv}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "ctext.tsv"
    urns = sys.argv[2:] or DEFAULT_URNS
    scrape(urns, out)
