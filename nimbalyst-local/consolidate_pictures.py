#!/usr/bin/env python3
"""Consolidate every sector's images into <Sector>_database/Pictures/<Owner>/,
rewrite research-note embeds to the new paths, delete the Image Library, and
remove emptied folders. Run with --apply."""
import os, re, sys, json, shutil
from urllib.parse import unquote, quote

VAULT = os.environ.get("VAULT", "/Users/kq/Downloads/J_Tian_Notion copy")
APPLY = "--apply" in sys.argv
IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")
SECTORS = ["AI hardware","Semi","Big Tech","Aerospace & Defense","Software",
           "Industrial & Materials","AI Application","Internet"]

def db_dir(sector):
    s = os.path.join(VAULT, sector)
    return os.path.join(s, [d for d in os.listdir(s) if d.endswith("_database")][0])

# ---- 1. build move map  old_abspath -> new_abspath --------------------------
move = {}
used_targets = set()
for sector in SECTORS:
    db = db_dir(sector)
    pics = os.path.join(db, "Pictures")
    for dp, _, fs in os.walk(db):
        if os.path.basename(dp) == "Pictures" or (os.sep+"Pictures"+os.sep) in dp+os.sep:
            continue  # already-consolidated (idempotency)
        for f in sorted(fs):
            if not f.lower().endswith(IMG_EXT):
                continue
            owner = os.path.basename(dp)
            if owner == os.path.basename(db):
                owner = "_loose"
            tgt_dir = os.path.join(pics, owner)
            tgt = os.path.join(tgt_dir, f)
            stem, ext = os.path.splitext(f)
            n = 1
            while tgt in used_targets:   # cross-branch same-owner collision
                n += 1; tgt = os.path.join(tgt_dir, f"{stem} {n}{ext}")
            used_targets.add(tgt)
            move[os.path.join(dp, f)] = tgt

print(f"[1] images to move: {len(move)}")

# index for embed rewrite: old_abspath -> new_abspath (already is `move`)
# ---- 2. apply moves ----------------------------------------------------------
if APPLY:
    for old, new in move.items():
        os.makedirs(os.path.dirname(new), exist_ok=True)
        shutil.move(old, new)
print(f"[2] moved (apply={APPLY})")

# ---- 3. rewrite embeds in research notes ------------------------------------
IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
rewrites = 0; unresolved = 0
note_paths = []
for dp, _, fs in os.walk(VAULT):
    if ".obsidian" in dp or (os.sep+"Image Library") in dp: continue
    for f in fs:
        if f.endswith(".md"): note_paths.append(os.path.join(dp, f))

for note in note_paths:
    nd = os.path.dirname(note)
    s = open(note, encoding="utf-8").read(); orig = s
    def fix(m):
        global rewrites, unresolved
        alt, url = m.group(1), m.group(2)
        if url.startswith(("http://","https://")): return m.group(0)
        u = unquote(url)
        # try both note-relative and vault-absolute interpretations
        new_abs = (move.get(os.path.normpath(os.path.join(nd, u)))
                   or move.get(os.path.normpath(os.path.join(VAULT, u))))
        if new_abs is None:
            # maybe url already points at new location (idempotent re-run)
            if os.path.isfile(os.path.join(nd, u)): return m.group(0)
            unresolved += 1; return m.group(0)
        rel = os.path.relpath(new_abs, nd).replace(" ", "%20")
        rewrites += 1
        return f"![{alt}]({rel})"
    s = IMG.sub(fix, s)
    if s != orig and APPLY:
        open(note, "w", encoding="utf-8").write(s)
print(f"[3] embed rewrites: {rewrites} | embeds with no map entry: {unresolved}")

# ---- 4. delete Image Library + Home link + graph color group ----------------
lib = os.path.join(VAULT, "Image Library")
if APPLY and os.path.isdir(lib):
    shutil.rmtree(lib)
home = os.path.join(VAULT, "Home.md")
hs = open(home, encoding="utf-8").read()
hs2 = re.sub(r"\n## Reference\n- \[\[Image Library\]\]\n?", "\n", hs)
if APPLY and hs2 != hs:
    open(home, "w", encoding="utf-8").write(hs2)
gpath = os.path.join(VAULT, ".obsidian", "graph.json")
g = json.load(open(gpath))
g["colorGroups"] = [c for c in g.get("colorGroups", []) if c.get("query") != "tag:#images"]
if APPLY:
    json.dump(g, open(gpath, "w"), indent=2)
print(f"[4] Image Library removed, Home link removed, images color group dropped (apply={APPLY})")

# ---- 5. remove emptied folders (bottom-up) ----------------------------------
removed = 0
if APPLY:
    for dp, dirs, fs in os.walk(VAULT, topdown=False):
        if ".obsidian" in dp or dp == VAULT: continue
        try:
            if not os.listdir(dp):
                os.rmdir(dp); removed += 1
        except OSError:
            pass
print(f"[5] empty folders removed: {removed}")
print("DONE apply=" + str(APPLY))
