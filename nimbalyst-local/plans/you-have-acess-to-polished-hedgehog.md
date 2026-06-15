# Plan: Incremental one-way Notion → Obsidian vault sync (official Notion API)

## Context

The user maintains a curated local Obsidian vault, `~/Documents/Jeff's database (claude sorted)/`
(316 notes, ~4.2 MB), that mirrors a Notion workspace. Notion is the source of truth; the vault is a
read-only mirror. Today the only way to refresh it is a manual, page-by-page sync (we did one such
append last session). The user wants a **repeatable, incremental, one-way sync**: detect what changed
on Notion via `last_edited_time`, bring over only new/changed content, download images locally so the
vault stays self-contained, and **never** push local → Notion.

Decisions already locked with the user:
- **Access = official Notion API** (an integration token), not the interactive MCP. Rationale: change
  detection needs a cheap "list all pages' last_edited_time" call. Via MCP that costs ~316 page
  fetches (~4M tokens, ~$40–60) per run; via the API it's a few KB. The API also makes the script
  self-contained and cron-able — exactly what the spec describes.
- **Update mode = entry-level MERGE (append-only into the file).** Never clobber the user's curation
  (frontmatter, `Up:` link, existing entries, ordering). Only *insert* new blocks. Plus: **structural
  sync** — brand-new Notion child pages become new local files (in the vault's exact format) and the
  parent note gains the `[[child]]` link (this is how nav links like "Applied Materials - AMAT" get
  carried over).
- **Scope = whole vault** (all 7 sectors) — affordable now that detection is an API query.

**Hard constraints (from the user):** do not change existing vault structure, filenames, folder
layout, front-matter rules, or image-link style. Match whatever each existing file already does.
Make the minimal changes needed. One-way only.

## Vault conventions to preserve (discovered)

- Built originally by `nimbalyst-local/migrate_vault.py` from a Notion Markdown export, which
  **stripped the trailing 32-hex Notion page-id** from filenames. So local files no longer carry
  their Notion id — the id→file mapping must be rebuilt by title/path (see First Run).
- Layout: `<Sector>/<Sector>_database/<Page>.md`; a page's children live in a sibling folder
  `<Page>/` (e.g. `AI hardware/AI Hardware industry_database/Networking.md` +
  `.../Networking/Arista - ANET.md`).
- Front-matter: `--- tags: [<sector-slug>, hub] ---` then `Up: [[Parent]]`, then `# Title`.
  Sector slugs are defined in `migrate_vault.py` (`SECTORS`).
- Entries are **newest-first**, prefixed `YYMMDD`, grouped under `##`/`###` headers.
- Images: `![alt](Pictures/<Page>/<file>.png)` with URL-encoded spaces, stored in
  `<...>_database/Pictures/<Page>/`. Link normalization lives in `normalize_links.py`; image
  consolidation logic in `consolidate_pictures.py` — **reuse these conventions, don't reinvent.**

## Architecture

A small Python package under `nimbalyst-local/` (stdlib + `requests` + `python-dotenv`; no heavy
deps). Default run is **dry-run** (reports planned changes); `--apply` writes — mirroring the existing
`migrate_vault.py --apply` convention. Modules kept small and single-purpose:

| File | Responsibility |
|---|---|
| `notion_sync.py` | CLI + orchestrator (the existing empty placeholder becomes this). Flags: `--apply`, `--sector NAME`, `--page ID`, `--init`. |
| `notion_api.py` | Thin Notion API client: auth header + version, paginated `databases.query` / `blocks.children.list` / `pages.retrieve`, ret/backoff. |
| `state.py` | Load/save `sync-state.json`; per page record `{id, last_edited_time, local_path, parent_id, title, block_keys[], images{block_id→sha256}}`. |
| `blocks_to_md.py` | Notion block JSON → vault-style Markdown for the block types present (paragraph, headings, bulleted/numbered list, quote, image, child_page, columns, rich-text marks). Applies `normalize_links.py` conventions. |
| `merge.py` | Block-level diff + position-aware insertion into an existing file (the append-only core). |
| `images.py` | Download S3/external image bytes → `Pictures/<Page>/`, content-hash dedupe, rewrite links to vault style. |
| `vault.py` | Path/format helpers: sector slug lookup, parent-folder resolution, new-file scaffolding (frontmatter + `Up:` + title). |

Secrets/state (git-ignored): `nimbalyst-local/.env` (holds `NOTION_TOKEN`),
`nimbalyst-local/sync-state.json`. Add both to `.gitignore`.

## Algorithm

**Setup (one-time, user does ~5 min, I guide):** create a Notion *internal integration*, copy the
token into `nimbalyst-local/.env`, and share the top Notion page(s) covering the 7 sectors with the
integration (children inherit access). Known root ids so far: AI Hardware industry `76bee8d8…`,
Semi `1d5b453e…`; remaining sector roots are discovered on first run.

**First run / `--init` (reconciliation, writes nothing to notes):**
1. Walk the Notion tree from the shared roots (`databases.query` + child-page recursion).
2. Match each Notion page to an existing local file by normalized title + parent path (handles the
   stripped-hash problem; reuse `clean()`/`SECTORS` from `migrate_vault.py`).
3. Record `last_edited_time` and the current set of block keys (so existing content is treated as
   "already synced" — no churn). Report any Notion pages with no local match (candidates to create).

**Each run:**
1. **Detect:** for each tracked page compare Notion `last_edited_time` vs state. Newer → changed.
   Notion id not in state → new page. Equal → skip (no fetch of body needed beyond the listing).
2. **Changed page → merge:** fetch ordered blocks; compute a stable key per top-level block
   (normalized text / child-page id). New blocks = keys not in the page's `block_keys`. Insert each
   new block adjacent to its Notion neighbor — before the nearest *following* already-known block
   (this naturally lands a new newest-first entry at the top of its section); fall back to top-of-body
   under the header. Existing lines are never moved or deleted.
3. **New child page → create:** scaffold a new file in the parent's `<Parent>/` folder via `vault.py`
   (correct frontmatter slug + `Up: [[Parent]]` + rendered body), and insert a `[[Child]]` link into
   the parent note's body (same merge insertion logic).
4. **Images:** for image blocks in inserted content, download bytes *now* (URLs are fresh), save to
   `Pictures/<Page>/`, dedupe/skip-unchanged by sha256 in state, rewrite the markdown link to the
   vault's encoded local style; download external (non-S3) images too.
5. **Persist:** update each synced page's `last_edited_time`, `block_keys`, and image hashes in
   `sync-state.json`. Never write to Notion.

## Files to create / modify

- Create/populate: `nimbalyst-local/notion_sync.py` (was empty) + the modules above.
- Create: `nimbalyst-local/.env.example`, append entries to `.gitignore` for `.env` and
  `sync-state.json`.
- Reuse (do not duplicate): conventions/regex from `migrate_vault.py`, `normalize_links.py`,
  `consolidate_pictures.py`.
- The empty `notion_baseline.json` is superseded by `sync-state.json` and will be removed.
- No changes to any vault file except the additive merges the sync itself performs.

## Verification

1. **Setup check:** `notion_sync.py --init` (dry-run) prints the discovered Notion tree, the
   id→local-file matches, and any unmatched pages — confirm mapping looks right before any write.
2. **Single-sector dry-run:** `notion_sync.py --sector Semi` shows planned merges/new files/images
   with no writes. Eyeball a couple against Notion.
3. **Apply + spot-check:** `--sector Semi --apply`; confirm a known recent edit lands correctly
   (e.g. the 算力/LLM `260612` entry), images downloaded into `Pictures/<Page>/`, links rewritten,
   no `amazonaws` URLs left in any `.md`, frontmatter/`Up:` intact, line counts only increase.
4. **Idempotency:** immediately re-run `--sector Semi --apply` → reports "nothing changed", zero
   diffs (proves `last_edited_time` + `block_keys` short-circuit works).
5. **New-page path:** verify a Notion page lacking a local file is created in the right folder with
   correct frontmatter and that its parent gains the `[[link]]`.
6. **Full run:** `notion_sync.py --apply`; review the change summary; `git diff` the vault is purely
   additive.
