#!/usr/bin/env python3
"""Incremental one-way sync: Notion (source of truth) -> Obsidian vault (mirror).

Append-only: brings over new dated entries, new images, and new child pages; never
rewrites or reorders existing local content, and never writes back to Notion.

Usage (run from nimbalyst-local/):
    python notion_sync.py --init                 # first-run reconcile (no writes)
    python notion_sync.py --sector Semi          # dry-run one sector
    python notion_sync.py --sector Semi --apply  # write changes for one sector
    python notion_sync.py --apply                # full vault sync

Change detection re-checks each page's live last_edited_time (a child page can change
without bumping its parent, so every page is checked every run). The tree is walked
as a rate-limited concurrent BFS so per-call network latency overlaps. Block content
is fetched only for changed/new pages. Token from nimbalyst-local/.env (NOTION_TOKEN).
Standard library only.
"""
import os
import re
import sys
import json
import difflib
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

import vault
import state as state_mod
import blocks_to_md
import merge as merge_mod
from notion_api import Notion, NotionError
from images import ImageStore

HERE = os.path.dirname(os.path.abspath(__file__))
WARN_LOG = os.path.join(HERE, "sync-warnings.log")
WORKERS = 6


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
        self.lock = threading.Lock()
        self.checked = self.changed = self.created = 0
        self.blocks = self.imgs_dl = self.imgs_reuse = 0
        self.warnings = []
        self.unmatched = []
        self.needs_confirm = []     # (notion_title, suggested_local, notion_id)

    def tick(self):
        with self.lock:
            self.checked += 1
            n = self.checked
        if n % 20 == 0:
            print(f"   ... {n} pages checked", flush=True)

    def report(self, apply):
        print("\n" + "=" * 60)
        print(f"pages checked:   {self.checked}")
        print(f"pages changed:   {self.changed}")
        print(f"pages created:   {self.created}")
        print(f"blocks added:    {self.blocks}")
        print(f"images: downloaded {self.imgs_dl}, reused {self.imgs_reuse}")
        if self.needs_confirm:
            print(f"\nNEEDS CONFIRMATION — look like renamed existing notes, NOT created: {len(self.needs_confirm)}")
            for t, sug, nid in self.needs_confirm:
                print(f"   ? '{t}'  ~looks like~  {sug}")
                print(f"        (alias: \"{nid}\": \"{sug}\")")
        if self.unmatched:
            print(f"\nunmatched Notion pages (genuinely new, would be created): {len(self.unmatched)}")
            for t, p in self.unmatched[:25]:
                print(f"   + {t}   (parent: {p})")
        if self.warnings:
            print(f"\n! near-duplicate warnings: {len(self.warnings)} (see sync-warnings.log)")
            for rel, w in self.warnings[:10]:
                print(f"   [{w['score']}] {rel}\n      new : {w['new']}\n      near: {w['near']}")
            if apply:
                with open(WARN_LOG, "w", encoding="utf-8") as fh:
                    for rel, w in self.warnings:
                        fh.write(f"[{w['score']}] {rel}\n  new : {w['new']}\n  near: {w['near']}\n\n")
        print("=" * 60)
        print(f"DONE  apply={apply}")


# ------------------------------------------------------------------------- helpers
def resolve_roots(notion, state, sectors):
    roots = state.setdefault("roots", {})
    for sec in sectors:
        if roots.get(sec):
            continue
        hub = vault.SECTOR_HUBS[sec]
        hits = notion.search(hub, filter_type="page")
        want = vault.norm_title(hub)
        match = next((h for h in hits if vault.norm_title(Notion.title_of(h)) == want), None)
        if not match:
            print(f"!! no Notion root for sector '{sec}' (title '{hub}'). Shared with integration?")
            continue
        roots[sec] = match["id"]
        print(f"   root '{hub}' -> {match['id']}", flush=True)
    return roots


def discover_children(notion, blocks):
    """Yield (child_id, title) for child_page and child_database rows."""
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
    cands = local_index.get(vault.norm_title(title), [])
    if not cands:
        return None
    under = [c for c in cands if c.startswith(children_dir + os.sep)]
    return under[0] if under else cands[0]


def fuzzy_suggest(title, children_dir):
    """Best existing-file guess for a Notion page with no exact match, searching
    only within the page's own folder. Returns a path (a likely rename) or None
    (genuinely new). Conservative: used to flag for confirmation, never to merge."""
    if not os.path.isdir(children_dir):
        return None
    nt = vault.norm_title(title)
    toks = {w for w in re.findall(r"\w+", nt) if len(w) >= 3}
    best, best_score = None, 0.0
    for f in os.listdir(children_dir):
        if not f.endswith(".md"):
            continue
        stem = vault.norm_title(f[:-3])
        if len(stem) < 3:
            continue
        if stem in nt or nt in stem:
            score = 0.9
        else:
            r = difflib.SequenceMatcher(None, nt, stem).ratio()
            stoks = {w for w in re.findall(r"\w+", stem) if len(w) >= 3}
            share = toks & stoks
            if r >= 0.72:
                score = r
            elif share and len(share) / max(1, len(stoks)) >= 0.5:
                score = 0.75
            else:
                score = 0.0
        if score > best_score:
            best, best_score = os.path.join(children_dir, f), score
    return best


# ----------------------------------------------------------------------- worker
class Walker:
    def __init__(self, notion, state, summ, apply, init):
        self.notion = notion
        self.state = state
        self.summ = summ
        self.apply = apply
        self.init = init
        self.lock = threading.Lock()
        self.visited = set()
        self.index = state["_index"]
        self.alias = {}                      # notion_id -> local relpath (manual)
        ap = os.path.join(HERE, "alias.json")
        if os.path.isfile(ap):
            try:
                self.alias = json.load(open(ap, encoding="utf-8"))
            except Exception:
                self.alias = {}

    def process(self, task):
        """Handle one page; return a list of child tasks to enqueue."""
        page_id, title, local_path, parent_title, parent_id, sector, children_dir = task
        with self.lock:
            if page_id in self.visited:
                return []
            self.visited.add(page_id)
        self.summ.tick()

        last_edited = self.notion.retrieve_page(page_id).get("last_edited_time", "")
        with self.lock:
            rec = self.state["pages"].get(page_id)
        changed = self.init or rec is None or rec.get("last_edited_time") != last_edited

        children = []
        if not changed:
            # body unchanged -> recurse into known children (each re-checked live)
            with self.lock:
                kids = [(pid, r) for pid, r in self.state["pages"].items()
                        if r.get("parent_id") == page_id]
            for cid, cr in kids:
                cpath = os.path.join(vault.VAULT, cr["local_path"])
                children.append((cid, cr["title"], cpath, title, page_id, sector,
                                 vault.child_folder_for(cpath)))
            self._save(page_id, title, local_path, parent_id, sector, last_edited,
                       set(rec["block_keys"]), dict(rec.get("images", {})))
            return children

        # changed/new/init -> fetch top-level body only (no nested calls)
        blocks = self.notion.block_children(page_id)
        units = blocks_to_md.render(blocks, self.notion, shallow=True)
        known = set(rec["block_keys"]) if rec else set()
        manifest = dict((rec or {}).get("images", {}))
        store = ImageStore(sector, title, manifest, self.apply)
        note_dir = os.path.dirname(local_path)

        def render_new(u):
            if u.needs_deep:
                text, imgs = blocks_to_md.deep_render(u, self.notion)
            else:
                text, imgs = u.text, u.images
            for desc in imgs:
                text = text.replace(desc["ph"], store.localize(desc, note_dir))
            return text

        if self.init:
            if os.path.isfile(local_path):
                known = {u.key for u in units}           # snapshot existing as known
        elif os.path.isfile(local_path):
            text = open(local_path, encoding="utf-8").read()
            new_text, n_added, added, warns = merge_mod.merge(
                text, units, known, render_new)
            if n_added:
                with self.summ.lock:
                    self.summ.changed += 1
                    self.summ.blocks += n_added
                print(f"   ~ {os.path.relpath(local_path, vault.VAULT)} (+{n_added})", flush=True)
                if self.apply:
                    open(local_path, "w", encoding="utf-8").write(new_text)
            known |= set(added)
            if warns:
                rel = os.path.relpath(local_path, vault.VAULT)
                with self.summ.lock:
                    self.summ.warnings.extend((rel, w) for w in warns)

        with self.summ.lock:
            self.summ.imgs_dl += store.downloaded
            self.summ.imgs_reuse += store.reused
        self._save(page_id, title, local_path, parent_id, sector, last_edited,
                   known, manifest)

        # discover children, creating new local files as needed
        for cid, ctitle in discover_children(self.notion, blocks):
            if not ctitle:
                continue
            with self.lock:
                if cid in self.visited:
                    continue
                if cid in self.alias:
                    cpath = os.path.join(vault.VAULT, self.alias[cid])
                else:
                    cpath = match_local(self.index, ctitle, children_dir)
            if cpath is None:
                sug = fuzzy_suggest(ctitle, children_dir)
                if sug:                       # likely a renamed existing note
                    with self.summ.lock:
                        self.summ.needs_confirm.append(
                            (ctitle, os.path.relpath(sug, vault.VAULT), cid))
                    continue                  # do NOT create or merge; await confirmation
                cpath = self.create_page(cid, ctitle, title, sector, children_dir, page_id)
                if cpath is None:
                    continue
                with self.lock:
                    self.index.setdefault(vault.norm_title(ctitle), []).append(cpath)
            children.append((cid, ctitle, cpath, title, page_id, sector,
                             vault.child_folder_for(cpath)))
        return children

    def create_page(self, page_id, title, parent_title, sector, children_dir, parent_id):
        if self.init:
            with self.summ.lock:
                self.summ.unmatched.append((title, parent_title))
            with self.lock:
                self.state.setdefault("pending_create", []).append({
                    "id": page_id, "title": title, "parent_title": parent_title,
                    "parent_id": parent_id, "sector": sector,
                    "children_dir": os.path.relpath(children_dir, vault.VAULT)})
            return None
        blocks = self.notion.block_children(page_id)
        units = blocks_to_md.render(blocks, self.notion, shallow=True)
        path = os.path.join(children_dir, vault.safe_filename(title) + ".md")
        note_dir = os.path.dirname(path)
        store = ImageStore(sector, title, {}, self.apply)
        parts = []
        for u in units:                          # whole page is new: materialize all
            if u.needs_deep:
                text, imgs = blocks_to_md.deep_render(u, self.notion)
            else:
                text, imgs = u.text, u.images
            for desc in imgs:
                text = text.replace(desc["ph"], store.localize(desc, note_dir))
            parts.append(text)
        hub = any(u.child_page_id for u in units)
        content = vault.scaffold_note(sector, parent_title, title, "\n\n".join(parts), hub=hub)
        with self.summ.lock:
            self.summ.created += 1
            self.summ.imgs_dl += store.downloaded
        print(f"   + {os.path.relpath(path, vault.VAULT)} (new page)", flush=True)
        if self.apply:
            os.makedirs(note_dir, exist_ok=True)
            open(path, "w", encoding="utf-8").write(content)
        self._save(page_id, title, path, parent_id, sector,
                   self.notion.retrieve_page(page_id).get("last_edited_time", ""),
                   {u.key for u in units}, store.manifest)
        return path

    def _save(self, page_id, title, local_path, parent_id, sector, last_edited,
              known, manifest):
        with self.lock:
            existing = self.state["pages"].get(page_id, {})
            state_mod.upsert_page(
                self.state, page_id, title=title,
                local_path=os.path.relpath(local_path, vault.VAULT),
                parent_id=parent_id if parent_id is not None else existing.get("parent_id"),
                sector=sector, last_edited_time=last_edited,
                block_keys=sorted(known), images=manifest)


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
    walker = Walker(notion, state, summ, args.apply, args.init)

    seeds = []
    for sec in sectors:
        rid = roots.get(sec)
        if not rid:
            continue
        hub = vault.SECTOR_HUBS[sec]
        hub_path = os.path.join(vault.VAULT, sec, hub + ".md")
        print(f"# sector {sec}  (root: {hub})", flush=True)
        seeds.append((rid, hub, hub_path, "Home", None, sec, vault.db_dir(sec)))

    # drain the init-time backlog of pages that exist in Notion but not locally
    if not args.init:
        for item in list(state.get("pending_create", [])):
            if item["sector"] not in sectors:
                continue
            cdir = os.path.join(vault.VAULT, item["children_dir"])
            cpath = match_local(walker.index, item["title"], cdir)
            if cpath is None:
                cpath = walker.create_page(item["id"], item["title"],
                                           item["parent_title"], item["sector"],
                                           cdir, item["parent_id"])
            if cpath:
                seeds.append((item["id"], item["title"], cpath, item["parent_title"],
                              item["parent_id"], item["sector"],
                              vault.child_folder_for(cpath)))

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        pending = {ex.submit(walker.process, t) for t in seeds}
        while pending:
            done, pending = wait(pending, return_when=FIRST_COMPLETED)
            for f in done:
                for child in f.result():
                    pending.add(ex.submit(walker.process, child))

    # prune backlog entries whose local file now exists
    if state.get("pending_create"):
        state["pending_create"] = [
            it for it in state["pending_create"]
            if not os.path.isfile(os.path.join(vault.VAULT, it["children_dir"],
                                               vault.safe_filename(it["title"]) + ".md"))]

    state.pop("_index", None)
    state_mod.save(state, args.apply or args.init)
    summ.report(args.apply)


if __name__ == "__main__":
    main()
