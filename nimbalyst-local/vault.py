#!/usr/bin/env python3
"""Vault conventions for the Notion->Obsidian sync.

Single source of truth for how the local mirror is laid out and formatted.
Mirrors the conventions established by migrate_vault.py / consolidate_pictures.py
so the sync produces files indistinguishable from the existing ones.
"""
import os
import re

# Root of the local mirror. Override with VAULT env var.
VAULT = os.environ.get("VAULT", "/Users/kq/Documents/Jeff's database (claude sorted)")

# sector folder -> graph color slug (same as migrate_vault.py SECTORS)
SECTORS = {
    "AI hardware": "aihw",
    "Semi": "semi",
    "Big Tech": "bigtech",
    "Aerospace & Defense": "aerodef",
    "Software": "software",
    "Industrial & Materials": "industrials",
    "AI Application": "aiapp",
}

# sector folder -> Notion hub page title (the page whose children form the sector).
# The on-disk hub note and "<hub>_database" folder both use this title.
SECTOR_HUBS = {
    "AI hardware": "AI Hardware industry",
    "Semi": "Semi",
    "Big Tech": "Big Tech & CSPs",
    "Aerospace & Defense": "Aerospace & Defense",
    "Software": "Software",
    "Industrial & Materials": "Industrials Materials",
    "AI Application": "AI Application",
}

IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")
_HASH = re.compile(r" [0-9a-f]{32}$")
# characters Notion allows in titles but the filesystem / Obsidian dislike
_FS_BAD = re.compile(r'[\\/:*?"<>|]')


def clean(stem: str) -> str:
    """Strip a trailing 32-hex Notion id from a filename stem (legacy export)."""
    return _HASH.sub("", stem)


def safe_filename(title: str) -> str:
    """Notion page title -> a vault-safe basename (no extension).

    The existing vault replaced '/' with ' ' (e.g. '算力/LLM' -> '算力 LLM').
    """
    name = _FS_BAD.sub(" ", title)
    name = re.sub(r"\s+", " ", name).strip()
    return name or "Untitled"


def norm_title(title: str) -> str:
    """Normalized key for matching a Notion title to a local file/folder.

    Folds punctuation to spaces so e.g. 'C3.AI C3 Transform' matches the local
    'C3 AI C3 Transform' (only a '.' vs space apart). Keeps alphanumerics and CJK.
    """
    s = clean(safe_filename(title)).lower()
    s = re.sub(r"[^0-9a-z一-鿿]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def db_dir(sector: str) -> str:
    """Absolute path of the '<hub>_database' folder for a sector."""
    return os.path.join(VAULT, sector, SECTOR_HUBS[sector] + "_database")


def sector_db_root_titles() -> dict:
    """sector folder -> hub title, for the roots the walker starts from."""
    return dict(SECTOR_HUBS)


def pictures_dir(sector: str, owner_title: str) -> str:
    """Where images for a given page ('owner') are stored."""
    return os.path.join(db_dir(sector), "Pictures", safe_filename(owner_title))


def image_link(note_dir: str, sector: str, owner_title: str, filename: str) -> str:
    """Markdown image target relative to a note, matching vault style (%20 spaces)."""
    abs_img = os.path.join(pictures_dir(sector, owner_title), filename)
    return os.path.relpath(abs_img, note_dir).replace(" ", "%20")


def sector_of(abspath: str) -> str:
    """Which sector folder an absolute vault path belongs to."""
    rel = os.path.relpath(abspath, VAULT)
    top = rel.split(os.sep, 1)[0]
    return top if top in SECTORS else ""


def is_hub(note_abspath: str) -> bool:
    """A note is a 'hub' if it owns a sibling child folder of the same stem."""
    stem = os.path.basename(note_abspath)[:-3]
    return os.path.isdir(os.path.join(os.path.dirname(note_abspath), stem))


def child_folder_for(note_abspath: str) -> str:
    """The folder that holds a note's child pages (created on demand)."""
    stem = os.path.basename(note_abspath)[:-3]
    return os.path.join(os.path.dirname(note_abspath), stem)


def frontmatter(sector: str, parent_title: str, hub: bool) -> str:
    """The exact header block migrate_vault.py writes."""
    slug = SECTORS[sector]
    tag2 = "hub" if hub else "leaf"
    return f"---\ntags: [{slug}, {tag2}]\n---\nUp: [[{parent_title}]]\n\n"


def scaffold_note(sector: str, parent_title: str, title: str, body_md: str,
                  hub: bool = False) -> str:
    """Full file content for a brand-new note in vault format."""
    head = frontmatter(sector, parent_title, hub)
    return f"{head}# {title}\n\n{body_md.rstrip()}\n"


def index_local_files() -> dict:
    """norm_title -> [absolute .md paths] across the whole vault."""
    idx = {}
    for dp, _, fs in os.walk(VAULT):
        if ".obsidian" in dp.split(os.sep):
            continue
        for f in fs:
            if f.endswith(".md"):
                idx.setdefault(norm_title(f[:-3]), []).append(os.path.join(dp, f))
    return idx
