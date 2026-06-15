#!/usr/bin/env python3
"""Minimal Notion REST client (read-only paths used by the sync).

Uses the 2025-09-03 API generation, where a database exposes one or more
`data_sources` and rows are queried via /v1/data_sources/{id}/query.
"""
from __future__ import annotations
import os
import sys
import time
import json
import threading
import urllib.request
import urllib.error

DEBUG = bool(os.environ.get("NOTION_DEBUG"))

API = "https://api.notion.com/v1"
VERSION = os.environ.get("NOTION_VERSION", "2025-09-03")
MIN_INTERVAL = 1.0 / 3.0          # ~3 req/s, Notion's documented ceiling


class NotionError(RuntimeError):
    pass


class Notion:
    def __init__(self, token: str | None = None):
        self.token = token or os.environ.get("NOTION_TOKEN", "")
        if not self.token:
            raise NotionError("NOTION_TOKEN not set (put it in nimbalyst-local/.env)")
        self._headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": VERSION,
            "Content-Type": "application/json",
        }
        self._next_slot = 0.0
        self._lock = threading.Lock()

    def _throttle(self):
        """Reserve the next send slot (thread-safe), then sleep to it OUTSIDE the
        lock so concurrent requests start ~MIN_INTERVAL apart and their network
        latencies overlap."""
        with self._lock:
            now = time.monotonic()
            slot = max(now, self._next_slot)
            self._next_slot = slot + MIN_INTERVAL
        delay = slot - time.monotonic()
        if delay > 0:
            time.sleep(delay)

    # ---- low level -----------------------------------------------------------
    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        url = f"{API}/{path.lstrip('/')}"
        data = json.dumps(body).encode() if body is not None else None
        if DEBUG:
            print(f"API {method} {path}", file=sys.stderr, flush=True)
        for attempt in range(6):
            self._throttle()
            req = urllib.request.Request(url, data=data, method=method,
                                         headers=self._headers)
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                # 429 rate limit / 5xx -> honour Retry-After, else short backoff
                if e.code in (429, 502, 503, 504):
                    wait = float(e.headers.get("Retry-After", 1.0 + attempt))
                    time.sleep(wait)
                    continue
                raise NotionError(f"{e.code} {method} {path}: {e.read().decode()[:300]}")
            except urllib.error.URLError as e:
                time.sleep(1.5 * (attempt + 1))
                if attempt == 5:
                    raise NotionError(f"network error {method} {path}: {e}")
        raise NotionError(f"gave up after retries: {method} {path}")

    def _paginated(self, method: str, path: str, body: dict | None = None):
        """Yield every result across pages for list endpoints."""
        body = dict(body or {})
        cursor = None
        while True:
            if method == "GET":
                p = path + (f"?page_size=100&start_cursor={cursor}" if cursor
                            else "?page_size=100")
                page = self._request("GET", p)
            else:
                if cursor:
                    body["start_cursor"] = cursor
                body["page_size"] = 100
                page = self._request(method, path, body)
            yield from page.get("results", [])
            if not page.get("has_more"):
                return
            cursor = page.get("next_cursor")

    # ---- read helpers --------------------------------------------------------
    def retrieve_page(self, page_id: str) -> dict:
        return self._request("GET", f"pages/{page_id}")

    def retrieve_database(self, database_id: str) -> dict:
        """Returns db incl. .data_sources (2025-09-03)."""
        return self._request("GET", f"databases/{database_id}")

    def block_children(self, block_id: str) -> list:
        return list(self._paginated("GET", f"blocks/{block_id}/children"))

    def query_data_source(self, data_source_id: str) -> list:
        """All rows (pages) of a data source."""
        return list(self._paginated("POST", f"data_sources/{data_source_id}/query"))

    def search(self, query: str, filter_type: str | None = None) -> list:
        body = {"query": query}
        if filter_type:
            body["filter"] = {"property": "object", "value": filter_type}
        return list(self._paginated("POST", "search", body))

    @staticmethod
    def title_of(page: dict) -> str:
        """Extract a page/database title from its object."""
        props = page.get("properties", {})
        for p in props.values():
            if p.get("type") == "title":
                return "".join(t.get("plain_text", "") for t in p["title"]).strip()
        # databases / fallbacks
        if "title" in page and isinstance(page["title"], list):
            return "".join(t.get("plain_text", "") for t in page["title"]).strip()
        return ""
