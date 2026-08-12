"""VOIDWEN data fetch v2. No scraping. Pull confirmed public parallel corpora.

Sources (all verified to exist, no live scraping/selectors):
  1. dayihengliu/a2m_chineseNMT   -> GitHub raw, wenyan<->modern zh, ~1.24M pairs
  2. raynardj wenyan<->modern     -> HF dataset "raynardj/classical-modern"
  3. Helsinki-NLP/opus-mt-zh-en   -> MT model, bridges modern-zh -> en (chain)
  4. Project Gutenberg Legge      -> direct wenyan->en gold set (small, high quality)

Output: JSONL files in model/data/raw/*.jsonl with fields {src, tgt, pair, source}
"""
from __future__ import annotations
import json
import os
import sys

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUT_DIR, exist_ok=True)


def _write(path: str, rows) -> int:
    n = 0
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
    return n


def fetch_raynardj_classical_modern() -> str:
    from datasets import load_dataset
    ds = load_dataset("raynardj/classical-modern", split="train")
    path = os.path.join(OUT_DIR, "raynardj_wenyan_modern.jsonl")
    n = _write(path, (
        {"src": r["classical"], "tgt": r["modern"], "pair": "wenyan-zh", "source": "raynardj"}
        for r in ds
    ))
    print(f"[raynardj] {n} pairs -> {path}")
    return path


def fetch_a2m_chinese_nmt() -> str:
    """dayihengliu/a2m_chineseNMT, hosted as raw text files on GitHub."""
    import requests
    base = "https://raw.githubusercontent.com/dayihengliu/a2m_chineseNMT/master/data"
    files = {"src": f"{base}/train.src", "tgt": f"{base}/train.tgt"}
    src_lines = requests.get(files["src"], timeout=60).text.splitlines()
    tgt_lines = requests.get(files["tgt"], timeout=60).text.splitlines()
    path = os.path.join(OUT_DIR, "a2m_chinesenmt.jsonl")
    n = _write(path, (
        {"src": s, "tgt": t, "pair": "wenyan-zh", "source": "a2m_chineseNMT"}
        for s, t in zip(src_lines, tgt_lines) if s.strip() and t.strip()
    ))
    print(f"[a2m_chineseNMT] {n} pairs -> {path}")
    return path


def fetch_gutenberg_legge() -> str:
    """Legge classics translations, plain text from Project Gutenberg (direct wenyan->en gold tier).
    Uses gutenberg mirror text files, paragraph-aligned by blank-line splitting only
    (no regex guesswork on structure).
    """
    import requests
    # Gutenberg ebook #4094 = Legge's "The Chinese Classics" (Confucian Analects etc, bilingual edition source text)
    urls = {
        4094: "https://www.gutenberg.org/cache/epub/4094/pg4094.txt",
    }
    rows = []
    for book_id, url in urls.items():
        try:
            text = requests.get(url, timeout=60).text
        except Exception as e:
            print(f"[gutenberg] skip {book_id}: {e}", file=sys.stderr)
            continue
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]
        for p in paras:
            rows.append({"src": p, "tgt": "", "pair": "wenyan-en-raw", "source": f"gutenberg-{book_id}"})
    path = os.path.join(OUT_DIR, "gutenberg_legge_raw.jsonl")
    n = _write(path, rows)
    print(f"[gutenberg] {n} raw paragraphs (needs manual/aligner pass) -> {path}")
    return path


FETCHERS = {
    "raynardj": fetch_raynardj_classical_modern,
    "a2m": fetch_a2m_chinese_nmt,
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
