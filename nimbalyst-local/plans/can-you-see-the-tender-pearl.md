# Plan: Build Notion updates into "Jeff's database (claude sorted)" from the backup

## Context
The user wants the cleaned J_Tian_Notion vault delivered into the empty Obsidian vault at `/Users/kq/Documents/Jeff's database (claude sorted)/`, with two fixes applied first: (1) **remove the Image Library**, (2) **move PDFs into the `Pictures/` folders** (same as images were). The chosen source `Downloads/J_Tian_Notion copy` **no longer exists on disk**, so I fall back to the user's original instruction: re-process **`Downloads/J_Tian_Notion copy_backup`** — which yields the identical, previously-verified end-state.

**Source state** (`J_Tian_Notion copy_backup`): graph-cleaned (renamed notes, wikilinks, `Home.md`, sector color groups) BUT still has the 9-note `Image Library/` and all 2,246 images + 91 PDFs scattered (none in `Pictures/`). 316 research notes + 9 library notes = 325 `.md`.
**Destination**: empty vault, has its own `.obsidian/` (app/appearance/workspace + a default graph.json) — preserve those, but bring the **tuned graph.json** (sector colors, orphans/unresolved hidden) per user.

This is exactly the transformation sequence already proven on the old copy: **consolidate images → move PDFs → normalize links**, which removes the Image Library and produced 0 broken links / 91-of-91 PDFs in Pictures.

## Approach (reuse the committed, verified scripts)
The three scripts in `nimbalyst-local/` already implement and validated every step. Make them path-agnostic and run them against the destination.

1. **Parameterize** `consolidate_pictures.py`, `move_pdfs_clean_dead.py`, `normalize_links.py`: change the hardcoded `VAULT = "…/J_Tian_Notion copy"` to `VAULT = os.environ.get("VAULT", <old default>)`. (One-line edit each; preserves behavior.)
2. **Copy source content** into the destination (preserve destination `.obsidian`):
   `rsync -a --exclude=.obsidian --exclude=.DS_Store "…/J_Tian_Notion copy_backup/" "…/Jeff's database (claude sorted)/"`
3. **Bring tuned graph settings**: copy `…copy_backup/.obsidian/graph.json` → destination `.obsidian/graph.json` (keeps destination's other config). The scripts will later drop the now-unneeded `tag:#images` color group.
4. **Run the proven sequence** with `VAULT="…/Jeff's database (claude sorted)"` (dry-run each, then `--apply`):
  - `consolidate_pictures.py` → deletes `Image Library/`, removes the `[[Image Library]]` link from `Home.md`, drops the `tag:#images` graph group, and moves every image into `<Sector>_database/Pictures/<Company>/`, rewriting embeds.
  - `move_pdfs_clean_dead.py` → moves the 91 PDFs into the same `Pictures/<Company>/`, rewrites their links, removes genuinely-dead links.
  - `normalize_links.py` → fixes any double-encoded/odd attachment link paths.

Sources (`copy_backup`, the two raw originals) remain untouched; this is a copy, not a move.

## Critical files / paths
- Edited (params): `nimbalyst-local/consolidate_pictures.py`, `move_pdfs_clean_dead.py`, `normalize_links.py`
- Written: everything under `/Users/kq/Documents/Jeff's database (claude sorted)/` (8 sectors, `Home.md`, `Pictures/` trees) + that vault's `.obsidian/graph.json`
- Untouched: `J_Tian_Notion copy_backup`, `Desktop/J_Tian_Notion`, `Downloads/J_Tian_Notion`

## Verification (run against the destination)
1. **Structure**: 8 sector folders + `Home.md`; **no `Image Library/`**; `Home.md` has no `[[Image Library]]` link.
2. **Counts**: 316 `.md`; 2,246 images and 91 PDFs, **all inside `Pictures/`**, 0 stray.
3. **Links**: 0 broken image embeds; 0 broken local file links (reuse the scan from the prior step).
4. **graph.json**: valid; sector color groups present, `tag:#images` absent, `showOrphans:false`, `hideUnresolved:true`.
5. **Sources intact**: backup + 2 originals unchanged (still no `Pictures/`).
6. **Manual (user)**: open `Jeff's database (claude sorted)` in Obsidian — notes render, images/PDFs resolve, graph is color-coded, file tree shows one `Pictures/` per database.

---

# (DONE / earlier) Plan: Consolidate images into a `Pictures/` folder per `_database` (de-bloat)

## Context
The scattered images (2,246 of them, interleaved through every company/category folder) make the vault tree noisy. The user wants each sector's images **physically consolidated into one `Pictures/` folder inside that sector's `_database`**, grouped by company, to cut the bloat. This **supersedes the virtual Image Library** (those 9 gallery notes are to be deleted).

Survey facts driving the design: heavy filename collisions (AI hardware: 1106 images / 177 distinct names) → a flat folder is impossible without renaming, so **company subfolders inside Pictures**. **117 image-only folders** empty out after the move (removed); 86 folders mix images with notes (only the images move).

**User-confirmed:** layout `<Sector>_database/Pictures/<Company>/<file>` · **move** the files and **auto-fix every research-note embed** · **delete** the 9 Image Library gallery notes.

## Target
For each of the 8 `_database` folders:
```
<Sector>_database/
  Pictures/
    <Company or Category>/   image.png, image 1.png, ...
    ...
  <clean note tree: only .md + category folders remain>
```
"Owner/Company" = basename of the image's current parent folder; images sitting directly in `<Sector>_database/` go to `Pictures/_loose/`.

## Approach — one move-and-rewrite script (dry-run first)
0. **Fresh backup** of the vault to a sibling `…_backup` (current verified state) before moving 2,246 files.
1. **Build move map** old→new for every image (png/jpg/jpeg/gif/webp/svg) under the 8 sectors (exclude `.obsidian/`, `Image Library/`). Target = `<Sector>_database/Pictures/<owner>/<file>`; if a target collides across two same-named owners, append  `2`,  `3`.
2. **Move files** (create dirs as needed).
3. **Rewrite embeds**: for every research `.md`, resolve each `![](path)` to its old absolute path, look it up in the map, and rewrite to the new note-relative path. (Non-image attachment links untouched.)
4. **Delete** the 9 `Image Library/*.md` notes and the `Image Library/` folder; remove the `## Reference → [[Image Library]]` block from `Home.md`; drop the `tag:#images` color group from `graph.json`.
5. **Remove emptied folders** (bottom-up rmdir of any dir left with no files/subdirs).

## Critical files
- Moves: all 2,246 images → `…/<Sector>_database/Pictures/<Company>/…` (representative: `AI hardware/AI Hardware industry_database/Pictures/Innio - INIO/c32997….jpg`)
- Edited: every research `.md` containing image embeds (~150+ notes); `Home.md`; `.obsidian/graph.json`
- Deleted: `Image Library/` (9 notes)
- Untouched: note `[[wikilinks]]`, hierarchy, non-image attachment links

## Verification
1. **All image embeds resolve** on disk (parse every `.md`, check each non-external `![]()` target exists) → 0 broken.
2. **No stray images**: zero image files remain under any `_database` outside a `Pictures/` folder.
3. **Coverage**: 2,246 images now live under the 8 `Pictures/` folders (count matches).
4. **No empty leftover folders**; `Image Library/` gone; `Home.md` no longer references it; `graph.json` valid.
5. **Manual (user):** open a few notes (e.g. Innio, Networking) in Obsidian — images still render; file tree shows a single tidy `Pictures/` per database.

---

# (SUPERSEDED) Plan: In-vault Image Library (virtual gallery, grouped by sector → company)

## Context
After cleaning up the J_Tian_Notion copy vault graph, the user wants all **2,246 images** collected into a browsable, categorized "library" — **kept inside the same vault** (`/Users/kq/Downloads/J_Tian_Notion copy/`), grouped **by sector → owning company/note**, as an **Obsidian gallery with notes**. Confirmed choice: **virtual gallery, no file copying** (gallery notes embed the existing images in place) — adds ~0 MB, leaves originals and the research-note embeds untouched.

Real distribution (read-only survey): 2,246 images (2,192 png / 53 jpg / 1 jpeg), 204 owner-groups:
| Sector | images | groups |
| --- | --- | --- |
| AI hardware | 1106 | 104 |
| Semi | 614 | 38 |
| Big Tech | 199 | 9 |
| AI Application | 96 | 4 |
| Software | 92 | 13 |
| Aerospace & Defense | 77 | 22 |
| Industrial & Materials | 52 | 10 |
| Internet | 10 | 4 |

"Owner" = the page whose folder the image sits in (image's immediate parent folder basename); images directly in `<Sector>_database/` group under a `(sector root)` bucket.

## Structure (new folder `Image Library/` at vault root — part of the existing vault)
```
Image Library/
  Image Library.md            home: tags [images]; links the 8 sector galleries (with counts)
  AI hardware — Images.md      sector gallery: ## <Owner> (n) headings, thumbnail embeds
  Semi — Images.md
  Big Tech — Images.md
  AI Application — Images.md
  Software — Images.md
  Aerospace & Defense — Images.md
  Industrial & Materials — Images.md
  Internet — Images.md
```
9 notes total (low graph clutter). Each sector note groups images under `## <Owner> — <n> images` sections.

## Build method — one Python script (read-only walk + write 9 notes)
1. Walk the 8 sector folders, collect image files (`.png/.jpg/.jpeg/.gif/.webp/.svg`), excluding `.obsidian/` and `Image Library/` itself. (Backup folder is outside the vault, not walked.)
2. Group by `(sector, owner)`; sort owners alpha, `(sector root)` last.
3. **Embeds**: Obsidian wikilink embeds with full vault-relative path + thumbnail width, e.g.
   `![[AI hardware/AI Hardware industry_database/Power + Utilities/Innio - INIO/c32997….jpg|220]]`
   (full path disambiguates duplicate basenames like `image.png`; `|220` renders a scannable thumbnail grid).
4. Write the 8 sector gallery notes + `Image Library.md` home, each with `tags: [images, <sector-slug>]`.
5. **Connect to existing graph**: append `- [[Image Library]]` to the vault `Home.md` so the library hangs off the master map.
6. **graph.json**: add one color group `tag:#images` (distinct bright color) so the library is a visually separate cluster. (Note: Obsidian may rewrite graph.json on UI interaction.)

## Critical files
- New: `/Users/kq/Downloads/J_Tian_Notion copy/Image Library/*.md` (9 notes)
- Edit: `/Users/kq/Downloads/J_Tian_Notion copy/Home.md` (+1 link), `.obsidian/graph.json` (+1 color group)
- Untouched: every image file, every research note, all existing embeds.

## Verification
1. **Coverage**: sum of embeds across the 9 notes == 2,246, each image embedded exactly once (script asserts; cross-check vs `find` count).
2. **All embeds resolve**: every `![[path]]` target exists on disk (paths come from the walk → guaranteed; re-verify by parsing notes).
3. **Home links**: `Image Library.md` links all 8 sector galleries; vault `Home.md` links `[[Image Library]]`.
4. **graph.json** valid JSON with an `images` color group.
5. **Manual (user)**: open Obsidian → `Image Library` note → click through sector galleries (thumbnail grids grouped by company); graph shows an `Image Library` cluster hanging off `Home`.

---

# Plan: Make the ENTIRE J_Tian_Notion copy vault a clear, readable Obsidian graph

## Context

`/Users/kq/Downloads/J_Tian_Notion copy/` is an Obsidian vault exported from Notion. The **Internet** sector has already been cleaned up by hand (renamed notes, wikilinks, sub-hubs, fixed embeds, color groups) and is the proven template. The user now wants **the same treatment applied to the whole vault** — the other 7 sectors plus a unifying top level.

Same root problems as Internet, now vault-wide:
- **294 of 315 `.md` files carry Notion hash-ID suffixes** ( `<32-hex>.md`) → unreadable graph node labels. (Folders are already clean — 0 hashed dirs.)
- **No `[[wikilinks]]`** outside Internet. Note bodies use Notion-style URL-encoded markdown links with hashes (e.g. `[Networking Basics](Networking%20Basics%20255b…756.md)`), and many child pages aren't linked from their parent at all.
- **Image embeds are broken** the same way — a stale vault-absolute prefix `<Sector>/<Sector>_database/…` (e.g. `![](AI%20hardware/AI%20Hardware%20industry_database/Networking/image.png)`). ~2000 embeds; 18 are external `https://` (leave alone).
- Graph shows a disconnected dust cloud.

**Key difference from Internet:** the grouping is **already encoded in the folder tree**. Notion exported every page as `Page <hash>.md` *plus* a same-named folder holding its children. So the hierarchy `Sector → Category → Sub-category → Company` already exists on disk (e.g. `AI hardware → Networking → 光模块 → Optical component → company`, up to ~6 levels deep). We mirror that existing hierarchy into the link graph instead of inventing groups.

**User-confirmed decisions:** color by **sector (8 colors)** · add a single **Home** map-of-content note linking all 8 sectors · **link the 4 "Untitled" notes in like normal leaves**, delete nothing (`.csv` Notion dumps left untouched).

## Sectors (7 to process; Internet already done)
AI hardware · Semi · Big Tech · Aerospace & Defense · Software · Industrial & Materials · AI Application. Each has a `<Sector>_Notes.md` hub + `<Sector>_database/` tree.

## Approach — one idempotent migration script

Because this is 294 renames + thousands of link/embed rewrites, it must be a single **Python script** (dry-run first, then apply), scoped to the 7 sectors (Internet dir is skipped — already clean). Mirror of the validated Internet logic, generalized to walk the tree.

### Per-note transformation
For every `.md` under a sector's `_database/`:

1. **Rename** — strip the trailing  `<32-hex>` → clean basename matching its sibling folder (e.g. `Networking 4178…cb.md` → `Networking.md`).
2. **Derive parent (Up-link)** from folder position: a note inside folder `Foo/` has parent note `Foo.md` (the sibling of that folder); a note directly in `<Sector>_database/` has the **sector hub** as parent. Prepend `Up: [[Parent]]`.
3. **Frontmatter / tags** — prepend `tags: [<sector-slug>, <hub|leaf>]`. `hub` if the note owns a child folder (it's a category/index page), else `leaf`. Sector slug drives the color.
4. **Rewrite down-links** — convert every body `[Text](…%20<hash>.md)` to `[[CleanName]]` (basename resolution).
5. **Complete the hubs** — for each hub note, append a `## Pages` section with `[[child]]` links for any folder-child not already linked in the body, guaranteeing top-down connectivity.
6. **Fix image embeds** — for each non-external `![alt](path)`, resolve the real file on disk by trying, in order: relative-to-note as-is → vault-absolute as-is → with the note's own dir-prefix stripped → inside the note's same-named folder; rewrite to the note-relative path that exists. External `https://` embeds untouched.

### Sector hubs
Rename each `<Sector>_Notes.md` → clean name (drop `_Notes`): `AI Hardware industry.md`, `Semi.md`, `Big Tech & CSPs.md`, `Aerospace & Defense.md`, `Software.md`, `Industrials Materials.md`, `AI Application.md`. Tag `[<sector-slug>, hub]`, add `Up: [[Home]]`, and convert their body links to `[[wikilinks]]`.

### Home MOC (new)
Create `Home.md` at the vault root: `tags: [home]`, a heading, and a bulleted `[[wikilink]]` list of all 8 sector hubs (incl. `[[Internet]]`). This makes the whole vault one connected, centered web.

### graph.json
Re-apply readable settings: `showOrphans: false`, `hideUnresolved: true`, and **8 sector color groups by tag** (`tag:#aihw`, `#semi`, `#bigtech`, `#aerodef`, `#internet`, `#software`, `#industrials`, `#aiapp`) plus a bright `tag:#home`/`#hub` accent. Note: **Obsidian rewrites `graph.json` when the user interacts with the graph UI**, so the durable readability comes from the link+tag structure; the color groups are a re-applyable convenience.

## Safety
The folder is the working "copy", but 294 renames are irreversible — **step 0 is a one-shot backup** (`zip` the vault, or `cp -R` to a sibling `…_backup`) before applying. Run the script in dry-run (print planned renames/edits, no writes) and eyeball a sample, then apply.

## Critical files / representative paths
- New: `/Users/kq/Downloads/J_Tian_Notion copy/Home.md`
- Renamed hubs: `…/<Sector>/<Sector>_Notes.md` → clean name (7 files)
- Bulk: every `…/<Sector>/<Sector>_database/**/*.md` (294 notes renamed, tagged, back/down-linked, embeds fixed). Representative deep path: `AI hardware/AI Hardware industry_database/Networking/光模块/Optical component/Macom - MTSI.md`
- `/Users/kq/Downloads/J_Tian_Notion copy/.obsidian/graph.json`
- Untouched: Internet/ (done), all `.png/.jpg/.csv`, external `https://` embeds.

## Verification (vault-wide, mirrors the Internet checks)
1. **No stale hash links:** grep all `.md` for `]\(.*%20[0-9a-f]{32}` → expect 0.
2. **No stale embed prefixes:** grep for `](<Sector>/<Sector>_database/` patterns → expect 0.
3. **Every `[[wikilink]]` target resolves** to a real `.md` basename (allow the one legitimate dup, "Reddit", in Internet+Software).
4. **Every non-external image embed resolves** to a file on disk (script reports any misses).
5. **graph.json valid JSON** with 8+ color groups; orphans off, unresolved hidden.
6. **Connectivity spot-check:** from `Home`, every sector hub reachable; pick 3 deep leaves (e.g. `Macom - MTSI`, `万泽 - 000534 CH`, `Corning - GLW`) and confirm an `Up:` chain back to `Home`.
7. **Manual (user):** open Obsidian → Graph view. Expect one `Home` center → 8 color-coded sector clusters → category sub-hubs → companies, no orphan/ghost cloud.
```
```

## Note
Internet was done with hand-authored sub-groups (E-Commerce, Media & Streaming, etc.) since it had no intermediate category folders; it already carries the `internet` tag, so it fits the by-sector coloring with no rework.
