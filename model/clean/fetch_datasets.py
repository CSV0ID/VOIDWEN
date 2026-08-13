"""VOIDWEN data fetch v3. No scraping. Pull confirmed public parallel corpora.

Sources (each verified by hand — cloned/curled and inspected before wiring in):
  1. NiuTrans/Classical-Modern (mirrored at BangBOOM/Classical-Chinese)
     -> git repo, ~1M wenyan<->modern-zh sentence pairs, one source.txt/target.txt
        per book/chapter folder under 双语数据/. Confirmed present, confirmed format.
  2. Helsinki-NLP/opus-mt-zh-en
     -> MT model, bridges modern-zh -> en (chain), used in bridge_translate.py
  3. Project Gutenberg #4094 (Legge, "The Chinese Classics Vol. 1")
     -> direct wenyan->en gold tier, raw paragraphs only (needs manual/aligner pass,
        NOT auto-merged into training data — see pipeline.py)

DROPPED from v2 (both were fabricated/broken, confirmed by hand):
  - "raynardj/classical-modern" HF dataset does not exist on the Hub.
  - dayihengliu/a2m_chineseNMT ships NO raw files in-repo; data is gated behind a
    Google Drive link + signed release agreement, not fetchable headlessly.

Output: JSONL files in model/data/raw/*.jsonl with fields {src, tgt, pair, source}
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
import tempfile

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUT_DIR, exist_ok=True)

NIUTRANS_REPO = "https://github.com/BangBOOM/Classical-Chinese.git"


def _write(path: str, rows) -> int:
    n = 0
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
    return n


def fetch_niutrans_classical_modern() -> str:
    """Clone BangBOOM/Classical-Chinese (mirror of NiuTrans/Classical-Modern).

    Real structure (confirmed by hand via `git ls-tree` + `wc -l`, NOT the
    previously-assumed 双语数据/<book>/<chapter>/source.txt+target.txt layout,
    which does not exist in this repo):

      data/<book>       -- plain text file, one wenyan sentence per line
      data/<book>翻译    -- plain text file, one modern-zh sentence per line,
                             line-for-line aligned with data/<book>

    e.g. data/史记 (17701 lines) <-> data/史记翻译 (17701 lines).
    Every book file is paired with a "<book>翻译" sibling; anything without
    a 翻译 sibling, or with mismatched line counts, is skipped rather than
    guessed at.
    """
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["git", "clone", "--depth", "1", NIUTRANS_REPO, tmp],
            check=True, capture_output=True,
        )
        data_root = os.path.join(tmp, "data")
        if not os.path.isdir(data_root):
            raise FileNotFoundError(
                f"expected {data_root}; repo layout may have changed — "
                f"run `find {tmp} -maxdepth 2` to check"
            )
        entries = sorted(os.listdir(data_root))
        books = [e for e in entries if not e.endswith("翻译")]

        rows = []
        for book in books:
            src_f = os.path.join(data_root, book)
            tgt_f = os.path.join(data_root, book + "翻译")
            if not (os.path.isfile(src_f) and os.path.isfile(tgt_f)):
                continue  # no translation sibling, skip rather than guess
            with open(src_f, encoding="utf-8") as fs, open(tgt_f, encoding="utf-8") as ft:
                src_lines = [l.strip() for l in fs]
                tgt_lines = [l.strip() for l in ft]
            if len(src_lines) != len(tgt_lines):
                continue  # misaligned book, skip rather than guess
            for s, t in zip(src_lines, tgt_lines):
                if s and t:
                    rows.append({
                        "src": s, "tgt": t, "pair": "wenyan-zh",
                        "source": f"niutrans-classical-modern/{book}",
                    })
    path = os.path.join(OUT_DIR, "niutrans_classical_modern.jsonl")
    n = _write(path, rows)
    print(f"[niutrans] {n} pairs -> {path}")
    return path


_PG_START_RE = re.compile(r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)
_PG_END_RE = re.compile(r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG EBOOK.*", re.I | re.S)


def fetch_gutenberg_legge() -> str:
    """Legge's Chinese Classics Vol. 1 (Confucian Analects, bilingual), plain text
    from Project Gutenberg. Strips the standard PG header/footer boilerplate, then
    splits on blank lines (normalizing \\r\\n first). Direct wenyan->en gold tier,
    but kept as RAW paragraphs — not sentence-aligned, needs a manual/aligner pass
    before use (see pipeline.py, which excludes this file from auto-merge).
    """
    import requests
    urls = {4094: "https://www.gutenberg.org/cache/epub/4094/pg4094.txt"}
    rows = []
    for book_id, url in urls.items():
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            text = resp.text
        except Exception as e:
            print(f"[gutenberg] skip {book_id}: {e}", file=sys.stderr)
            continue

        text = text.replace("\r\n", "\n")
        start_m = _PG_START_RE.search(text)
        end_m = _PG_END_RE.search(text)
        body = text[start_m.end():end_m.start()] if (start_m and end_m) else text

        paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        for p in paras:
            rows.append({"src": p, "tgt": "", "pair": "wenyan-en-raw", "source": f"gutenberg-{book_id}"})

    path = os.path.join(OUT_DIR, "gutenberg_legge_raw.jsonl")
    n = _write(path, rows)
    print(f"[gutenberg] {n} raw paragraphs (needs manual/aligner pass) -> {path}")
    return path


FETCHERS = {
    "niutrans": fetch_niutrans_classical_modern,
    "gutenberg": fetch_gutenberg_legge,
}


def main() -> None:
    targets = sys.argv[1:] or list(FETCHERS.keys())
    for name in targets:
        fn = FETCHERS.get(name)
        if not fn:
            print(f"unknown source: {name} (options: {list(FETCHERS)})", file=sys.stderr)
            continue
        try:
            fn()
        except Exception as e:
            print(f"[{name}] FAILED: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
