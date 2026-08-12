"""Polite rate-limited HTTP GET shared by the scrapers.

Reused by ctext / wikisource / sutra scrapers instead of copy-pasting the fetch
loop three times.
"""
from __future__ import annotations

import time

import requests

USER_AGENT = "voidwen-corpus-builder/0.1 (+https://github.com/CSV0ID/voidwen)"


class RateLimitedFetcher:
    def __init__(self, min_interval_s: float = 2.0):
        self.min_interval_s = min_interval_s
        self._last = 0.0
        self._session = requests.Session()
        self._session.headers["User-Agent"] = USER_AGENT

    def get(self, url: str) -> str:
        wait = self.min_interval_s - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        resp = self._session.get(url, timeout=30)
        resp.raise_for_status()
        self._last = time.monotonic()
        return resp.text
