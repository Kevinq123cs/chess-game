#!/usr/bin/env python3
"""Incremental one-way sync: Notion (source of truth) -> Obsidian vault (mirror).

Append-only: brings over new dated entries, new images, and new child pages; never
rewrites or reorders existing local content, and never writes back to Notion.

Usage (run from nimbalyst-local/):
    python notion_sync.py --init                 # first-run reconcile (no writes)
    python notion_sync.py --sector Semi          # dry-run one sector
    python notion_sync.py --sector Semi --apply  # write changes for one sector
    python notion_sync.py --apply                # full vault sync

Change detection uses each page's last_edited_time (cheap metadata). Block content
is fetched only for changed/new pages. Token comes from nimbalyst-local/.env
(NOTION_TOKEN=...). No third-party packages required (stdlib only).
"""
import os
import sys
import argparse

import vault
import state as state_mod
import blocks_to_md
import merge as merge_mod
from notion_api import Notion, NotionError
from images import ImageStore

HERE = os.path.dirname(os.path.abspath(__file__))
WARN_LOG = os.path.join(HERE, "sync-warnings.log")


# --------------------------------------------------------------------------- env
def load_env():
    path = os.path.join(HERE, ".env")
    if os.path.isfile(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# ------------------------------------------------------------------------ summary
class Summary:
    def __init__(self):
        self.checked = self.changed = self.created = 0
        self.blocks = self.imgs_dl = self.imgs_reuse = 0
        self.warnings = []      # (rel_path, {new,near,score})
        self.unmatched = []     # notion pages with no local file (dry-run report)

    def report(self, apply):
        print("\n" + "=" * 60)
        print(f"pages checked:   {self.checked}")
        print(f"pages changed:   {self.changed}")
        print(f"pages created:   {self.created}")
        print(f"blocks added:    {self.blocks}")
        print(f"images: downloaded {self.imgs_dl}, reused {self.imgs_reuse}")
        if self.unmatched:
            print(f"\nunmatched Notion pages (would be created): {len(self.unmatched)}")
            for t, p in self.unmatched[:20]:
                print(f"   + {t}   (parent: {p})")
        if self.warnings:
            print(f"\n! near-duplicate warnings: {len(self.warnings)} "
                  f"(see sync-warnings.log)")
            for rel, w in self.warnings[:10]:
                print(f"   [{w['score']}] {rel}\n      new : {w['new']}"
                      f"\n      near: {w['near']}")
            if apply:
                with open(WARN_LOG, "w", encoding="utf-8") as fh:
                    for rel, w in self.warnings:
                        fh.write(f"[{w['score']}] {rel}\n  new : {w['new']}\n"
                                 f"  near: {w['near']}\n\n")
        print("=" * 60)
        print(f"DONE  apply={apply}")


# ------------------------------------------------------------------------- helpers
def resolve_roots(notion, state, sectors):
    """sector folder -> root notion page id (discover by hub title, cache in state)."""
    roots = state.setdefault("roots", {})
    for sec in sectors:
        if roots.get(sec):
            continue
        hub = vault.SECTOR_HUBS[sec]
        hits = notion.search(hub, filter_type="page")
        want = vault.norm_title(hub)
        match = next((h for h in hits if vault.norm_title(Notion.title_of(h)) == want),
                     None)
        if not match:
            print(f"!! could not find Notion root page for sector '{sec}' "
                  f"(title '{hub}'). Is it shared with the integration?")
            continue
        roots[sec] = match["id"]
        print(f"   root '{hub}' -> {match['id']}")
    return roots


def child_units(notion, page_id):
    """Rendered top-level units + raw blocks for a page."""
    blocks = notion.block_children(page_id)
    return blocks_to_md.render(blocks, notion), blocks


def discover_children(notion, blocks):
    """From a page's blocks, yield (child_page_id, title) including db rows."""
    for b in blocks:
        t = b.get("type")
        if t == "child_page":
            yield b["id"], b["child_page"]["title"].strip()
        elif t == "child_database":
            db = notion.retrieve_database(b["id"])
            for ds in db.get("data_sources", []):
                for row in notion.query_data_source(ds["id"]):
                    yield row["id"], Notion.title_of(row)


def match_local(local_index, title, children_dir):
    """Existing .md path for a Notion title, preferring one under children_dir."""
    cands = local_index.get(vault.norm_title(title), [])
    if not cands:
        return None
    under = [c for c in cands if c.startswith(children_dir + os.sep)]
    if len(under) == 1:
        return under[0]
    return under[0] if under else cands[0]


# -------------------------------------------------------------------------- walk
def sync_page(notion, state, summ, *, page_id, last_edited, title, local_path,
              parent_title, sector, children_dir, apply, init):
    """Process one page: merge new blocks (or snapshot at init), then recurse."""
    summ.checked += 1
    rec = state["pages"].get(page_id)
    known = set(rec["block_keys"]) if rec else set()
    unchanged = rec is not None and rec.get("last_edited_time") == last_edited and not init

    note_dir = os.path.dirname(local_path)

    if unchanged:
        # no body fetch; recurse into known children only (unchanged => no new children)
        for cid, cr in [(pid, r) for pid, r in state["pages"].items()
                        if r.get("parent_id") == page_id]:
            cpath = os.path.join(vault.VAULT, cr["local_path"])
            sync_page(notion, state, summ, page_id=cid,
                      last_edited=cr.get("last_edited_time"), title=cr["title"],
                      local_path=cpath, parent_title=title, sector=sector,
                      children_dir=vault.child_folder_for(cpath), apply=apply, init=init)
        return

    units, blocks = child_units(notion, page_id)
    manifest = dict((rec or {}).get("images", {}))
    store = ImageStore(sector, title, manifest, apply)

    if init:
        if os.path.isfile(local_path):
            known = {u.key for u in units}   # snapshot: existing content == known
    elif os.path.isfile(local_path):
        text = open(local_path, encoding="utf-8").read()
        new_text, n_added, added, imgs, warns = merge_mod.merge(
            text, units, known, store.localize, note_dir)
        if n_added:
            summ.changed += 1
            summ.blocks += n_added
            print(f"   ~ {os.path.relpath(local_path, vault.VAULT)}  (+{n_added} blocks)")
            if apply:
                open(local_path, "w", encoding="utf-8").write(new_text)
        for w in warns:
            summ.warnings.append((os.path.relpath(local_path, vault.VAULT), w))
        known |= set(added)

    summ.imgs_dl += store.downloaded
    summ.imgs_reuse += store.reused

    state_mod.upsert_page(state, page_id, title=title,
                          local_path=os.path.relpath(local_path, vault.VAULT),
                          parent_id=state["pages"].get(page_id, {}).get("parent_id"),
                          sector=sector, last_edited_time=last_edited,
                          block_keys=sorted(known), images=manifest)

    # recurse into children, creating any that have no local file yet
    local_index = state["_index"]
    for cid, ctitle in discover_children(notion, blocks):
        if not ctitle:
            continue
        cpath = match_local(local_index, ctitle, children_dir)
        if cpath is None:
            cpath = create_page(notion, state, summ, page_id=cid, title=ctitle,
                                parent_title=title, sector=sector,
                                children_dir=children_dir, apply=apply, init=init)
            if cpath is None:
                continue
            local_index.setdefault(vault.norm_title(ctitle), []).append(cpath)
        c_last = notion.retrieve_page(cid).get("last_edited_time", "")
        state_mod.upsert_page(state, cid,
                              parent_id=page_id)  # record parentage
        sync_page(notion, state, summ, page_id=cid, last_edited=c_last, title=ctitle,
                  local_path=cpath, parent_title=title, sector=sector,
                  children_dir=vault.child_folder_for(cpath), apply=apply, init=init)


def create_page(notion, state, summ, *, page_id, title, parent_title, sector,
                children_dir, apply, init):
    """Create a brand-new local note for a Notion page that has no local file."""
    if init:
        summ.unmatched.append((title, parent_title))
        return None
    units, blocks = child_units(notion, page_id)
    path = os.path.join(children_dir, vault.safe_filename(title) + ".md")
    note_dir = os.path.dirname(path)
    store = ImageStore(sector, title, {}, apply)
    parts = []
    for u in units:
        text = u.text
        for desc in u.images:
            text = text.replace(desc["ph"], store.localize(desc, note_dir))
        parts.append(text)
    hub = any(u.child_page_id for u in units)
    content = vault.scaffold_note(sector, parent_title, title, "\n\n".join(parts), hub=hub)
    summ.created += 1
    summ.imgs_dl += store.downloaded
    print(f"   + {os.path.relpath(path, vault.VAULT)}  (new page)")
    if apply:
        os.makedirs(note_dir, exist_ok=True)
        open(path, "w", encoding="utf-8").write(content)
    state_mod.upsert_page(state, page_id, title=title,
                          local_path=os.path.relpath(path, vault.VAULT),
                          parent_id=None, sector=sector,
                          last_edited_time=notion.retrieve_page(page_id).get(
                              "last_edited_time", ""),
                          block_keys=sorted(u.key for u in units),
                          images=store.manifest)
    return path


# -------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Notion -> Obsidian vault sync")
    ap.add_argument("--apply", action="store_true", help="write changes (default dry-run)")
    ap.add_argument("--init", action="store_true", help="reconcile only; snapshot keys, no note writes")
    ap.add_argument("--sector", action="append", help="limit to sector folder name(s)")
    args = ap.parse_args()

    load_env()
    try:
        notion = Notion()
    except NotionError as e:
        print(f"!! {e}")
        sys.exit(1)

    state = state_mod.load()
    state["_index"] = vault.index_local_files()
    summ = Summary()
    sectors = args.sector or list(vault.SECTORS.keys())
    bad = [s for s in sectors if s not in vault.SECTORS]
    if bad:
        print(f"!! unknown sector(s): {bad}\n   valid: {list(vault.SECTORS)}")
        sys.exit(1)

    roots = resolve_roots(notion, state, sectors)
    for sec in sectors:
        rid = roots.get(sec)
        if not rid:
            continue
        hub = vault.SECTOR_HUBS[sec]
        hub_path = os.path.join(vault.VAULT, sec, hub + ".md")
        root_page = notion.retrieve_page(rid)
        print(f"\n# sector {sec}  (root: {hub})")
        sync_page(notion, state, summ, page_id=rid,
                  last_edited=root_page.get("last_edited_time", ""), title=hub,
                  local_path=hub_path, parent_title="Home", sector=sec,
                  children_dir=vault.db_dir(sec), apply=args.apply, init=args.init)

    state.pop("_index", None)
    state_mod.save(state, args.apply or args.init)
    summ.report(args.apply)


if __name__ == "__main__":
    main()
