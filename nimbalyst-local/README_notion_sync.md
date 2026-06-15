# Notion → Obsidian vault sync

One-way, incremental, append-only mirror. Notion is the source of truth; the local
vault (`Jeff's database (claude sorted)`) is the mirror. Never writes to Notion.

## Setup (one time, ~5 min)

1. Go to https://www.notion.so/my-integrations → **New integration** (internal).
   Give it read access. Copy the **Internal Integration Secret** (starts `ntn_`).
2. `cp .env.example .env` and paste the token into `NOTION_TOKEN`.
3. In Notion, open each sector's top page (AI Hardware industry, Semi, Big Tech & CSPs,
   Aerospace & Defense, Software, Industrials Materials, AI Application) → `•••` →
   **Connections → Connect to → <your integration>**. Children inherit access, so you
   only share the 7 roots (or a common parent if they share one).

No Python packages needed — standard library only (Python 3.9+).

## Usage (run from this folder)

```bash
python3 notion_sync.py --init                 # first run: reconcile, snapshot, NO writes
python3 notion_sync.py --sector Semi          # dry-run one sector (shows planned changes)
python3 notion_sync.py --sector Semi --apply  # write changes for one sector
python3 notion_sync.py --apply                # full vault sync
```

`--init` must be run once first: it matches Notion pages to existing local files and
records the current content as "already synced" so nothing gets duplicated.

## How it works

- **Change detection**: each page's `last_edited_time` (cheap metadata). Block content is
  fetched only for changed/new pages; unchanged subtrees are skipped.
- **Merge**: only blocks whose content-key is new are inserted, placed next to their Notion
  neighbour (newest-first preserved). Existing lines are never moved or deleted.
- **New child pages**: created in the parent's child folder in vault format (frontmatter +
  `Up:` link), and a `[[link]]` is added to the parent.
- **Images**: bytes downloaded into `<sector>_database/Pictures/<Page>/`, deduped by
  sha256, links rewritten to the vault's `%20` style. Expiring S3 URLs are never stored.
- **Near-duplicate tripwire**: if an inserted block is ≥0.85 similar (not identical) to
  existing content — the signal of an in-place Notion edit duplicating — it still inserts
  but logs a warning to the run summary and `sync-warnings.log`. Review, don't trust blindly.

## State

`sync-state.json` (git-ignored) holds per-page `last_edited_time`, local path, parentage,
synced block keys, and the image manifest. Delete it to force a full re-reconcile (`--init`).
