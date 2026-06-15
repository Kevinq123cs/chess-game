#!/usr/bin/env python3
"""Download Notion image bytes into the vault and produce local links.

Notion file URLs are signed S3 links that expire (~1h), so we fetch the bytes at
sync time and store them under <db>/Pictures/<Owner>/. Dedupe by sha256 via the
per-page manifest in sync-state.json so unchanged images are not re-downloaded.
"""
import os
import hashlib
import urllib.request
import urllib.error
from urllib.parse import urlparse, unquote

import vault

IMG_EXT = vault.IMG_EXT
_CT_EXT = {
    "image/png": ".png", "image/jpeg": ".jpg", "image/jpg": ".jpg",
    "image/gif": ".gif", "image/webp": ".webp", "image/svg+xml": ".svg",
}


def _ext_from(url: str, content_type: str) -> str:
    base = os.path.basename(urlparse(url).path)
    _, ext = os.path.splitext(unquote(base))
    if ext.lower() in IMG_EXT:
        return ext.lower()
    return _CT_EXT.get((content_type or "").split(";")[0].strip().lower(), ".png")


def _fetch(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "vault-sync/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read(), r.headers.get("Content-Type", "")


class ImageStore:
    """Localizes images for a single owner page; updates the page's manifest."""

    def __init__(self, sector: str, owner_title: str, manifest: dict, apply: bool):
        self.sector = sector
        self.owner = owner_title
        self.manifest = manifest          # sha256 -> filename (mutated in place)
        self.apply = apply
        self.dir = vault.pictures_dir(sector, owner_title)
        self._existing = set()
        if os.path.isdir(self.dir):
            self._existing = {f for f in os.listdir(self.dir)
                              if f.lower().endswith(IMG_EXT)}
        self.downloaded = 0
        self.reused = 0

    def _next_name(self, ext: str) -> str:
        """'image.png', then 'image 1.png', ... matching consolidate_pictures.py."""
        cand, n = f"image{ext}", 0
        taken = self._existing | set(self.manifest.values())
        while cand in taken:
            n += 1
            cand = f"image {n}{ext}"
        return cand

    def localize(self, desc: dict, note_dir: str) -> str:
        """Download (if new) and return a vault-relative markdown link target.

        On dry-run or fetch failure, returns the placeholder-free best effort:
        a deterministic local path is reserved but no bytes are written.
        """
        url = desc.get("url", "")
        try:
            data, ct = _fetch(url)
        except (urllib.error.URLError, ValueError) as e:
            # leave a clearly-broken-but-local marker rather than an expiring URL
            return vault.image_link(note_dir, self.sector, self.owner,
                                    "_MISSING_.png")
        sha = hashlib.sha256(data).hexdigest()
        if sha in self.manifest:
            self.reused += 1
            return vault.image_link(note_dir, self.sector, self.owner,
                                    self.manifest[sha])
        ext = _ext_from(url, ct)
        name = self._next_name(ext)
        self.manifest[sha] = name
        self.downloaded += 1
        if self.apply:
            os.makedirs(self.dir, exist_ok=True)
            with open(os.path.join(self.dir, name), "wb") as fh:
                fh.write(data)
        return vault.image_link(note_dir, self.sector, self.owner, name)
