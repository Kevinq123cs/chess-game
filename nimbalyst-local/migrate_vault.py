#!/usr/bin/env python3
"""Mirror the Notion folder hierarchy of the J_Tian_Notion vault into a clean
Obsidian link graph. Idempotent-ish; run with --apply to write, else dry-run."""
import os, re, sys, json
from urllib.parse import unquote

VAULT = "/Users/kq/Downloads/J_Tian_Notion copy"
APPLY = "--apply" in sys.argv

SECTORS = {  # top-level folder -> color slug
    "AI hardware": "aihw",
    "Semi": "semi",
    "Big Tech": "bigtech",
    "Aerospace & Defense": "aerodef",
    "Software": "software",
    "Industrial & Materials": "industrials",
    "AI Application": "aiapp",
}
HASH = re.compile(r" [0-9a-f]{32}$")
IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")

def clean(stem):  # strip trailing notion hash from a filename stem
    return HASH.sub("", stem)

log = []
renames = {}          # old abspath -> new abspath  (.md only)
sector_hub = {}       # sector folder -> clean hub basename

# ---- Phase A: compute renames -------------------------------------------------
for sector in SECTORS:
    sroot = os.path.join(VAULT, sector)
    # hub note  <X>_Notes.md  -> drop _Notes
    for f in os.listdir(sroot):
        if f.endswith("_Notes.md"):
            newbase = f[:-len("_Notes.md")]
            sector_hub[sector] = newbase
            renames[os.path.join(sroot, f)] = os.path.join(sroot, newbase + ".md")
    # database tree
    dbroot = os.path.join(sroot, sector_db := [d for d in os.listdir(sroot) if d.endswith("_database")][0])
    for dirpath, dirs, files in os.walk(dbroot):
        used = set()
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            base = clean(f[:-3])
            cand, n = base, 1
            while cand in used:        # de-collide (e.g. 4x "Untitled")
                n += 1; cand = f"{base} {n}"
            used.add(cand)
            old = os.path.join(dirpath, f)
            new = os.path.join(dirpath, cand + ".md")
            if old != new:
                renames[old] = new

# final set of all note paths after rename (for parent/child resolution)
final_files = set()
for dp, _, fs in os.walk(VAULT):
    if ".obsidian" in dp: continue
    for f in fs:
        if f.endswith(".md"):
            final_files.add(renames.get(os.path.join(dp, f), os.path.join(dp, f)))

def page_for_dir(d):
    """Clean basename of the Notion page that owns directory d."""
    if d == VAULT or not d.startswith(VAULT):
        return "Home"                    # safety guard
    base = os.path.basename(d)
    if base.endswith("_database"):
        sector = os.path.basename(os.path.dirname(d))
        return sector_hub[sector]
    cand = os.path.join(os.path.dirname(d), base + ".md")
    if cand in final_files:
        return base                      # folders are already hash-free
    return page_for_dir(os.path.dirname(d))   # container dir w/o a page -> go up

# global index: image basename -> [abspaths]
img_index = {}
for dp, _, fs in os.walk(VAULT):
    if ".obsidian" in dp: continue
    for f in fs:
        if not f.endswith(".md"):
            img_index.setdefault(f, []).append(os.path.join(dp, f))

def resolve_img(note_dir, note_stem, raw):
    p = unquote(raw)
    bn = os.path.basename(p)
    reldir = os.path.relpath(note_dir, VAULT)
    cands = [os.path.join(note_dir, p), os.path.join(VAULT, p),
             os.path.join(note_dir, note_stem, bn),   # note's own page-folder
             os.path.join(note_dir, bn)]
    if p.startswith(reldir + os.sep):
        cands.append(os.path.join(note_dir, p[len(reldir)+1:]))
    for c in cands:
        if os.path.isfile(c):
            return os.path.relpath(c, note_dir).replace(" ", "%20")
    # global fallback: prefer a match inside this note's subtree, else unique match
    matches = img_index.get(bn, [])
    under = [m for m in matches if m.startswith(note_dir + os.sep)]
    pick = under[0] if len(under) == 1 else (matches[0] if len(matches) == 1 else None)
    if pick:
        return os.path.relpath(pick, note_dir).replace(" ", "%20")
    return None

img_miss = []

def transform_body(text, note_dir, note_stem):
    def fix_img(m):
        alt, url = m.group(1), m.group(2)
        if url.startswith(("http://", "https://")):
            return m.group(0)
        rel = resolve_img(note_dir, note_stem, url)
        if rel is None:
            img_miss.append((note_dir, url)); return m.group(0)
        return f"![{alt}]({rel})"
    def fix_link(m):
        text_, url = m.group(1), m.group(2)
        dec = unquote(url)
        if dec.endswith(".md"):
            target = clean(os.path.basename(dec)[:-3])
            return f"[[{target}]]" if text_ == target else f"[[{target}|{text_}]]"
        return m.group(0)
    text = IMG.sub(fix_img, text)
    text = LINK.sub(fix_link, text)
    return text

def write(path, content):
    if APPLY:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)

# ---- Apply renames ------------------------------------------------------------
if APPLY:
    for old, new in renames.items():
        os.rename(old, new)
print(f"[A] renamed {len(renames)} .md files (apply={APPLY})")

# ---- Phase B/C: transform every note -----------------------------------------
processed = 0
for sector, slug in SECTORS.items():
    sroot = os.path.join(VAULT, sector)
    hub = sector_hub[sector]
    # walk all notes in this sector (hub + database)
    for dp, _, fs in os.walk(sroot):
        for f in fs:
            if not f.endswith(".md"):
                continue
            path = os.path.join(dp, f)
            stem = f[:-3]
            with open(path, encoding="utf-8") as fh:
                body = fh.read()
            if body.startswith("---\n"):
                continue  # already processed
            is_sector_hub = (dp == sroot and (stem == hub or f.endswith("_Notes.md")))
            if is_sector_hub:
                parent = "Home"
                child_folder = os.path.join(sroot, [d for d in os.listdir(sroot) if d.endswith("_database")][0])
                is_hub = True
            else:
                parent = page_for_dir(dp)
                child_folder = os.path.join(dp, stem)
                is_hub = os.path.isdir(child_folder)
            new_body = transform_body(body, dp, clean(stem))
            # complete hubs: append links to immediate child pages not yet linked
            if is_hub and os.path.isdir(child_folder):
                kids = sorted(clean(c[:-3]) for c in os.listdir(child_folder) if c.endswith(".md"))
                have = set(re.findall(r"\[\[([^\]|#]+)", new_body))
                missing = [k for k in kids if k not in have]
                if missing:
                    new_body += "\n\n## Pages\n" + "\n".join(f"- [[{k}]]" for k in missing) + "\n"
            tag2 = "hub" if is_hub else "leaf"
            front = f"---\ntags: [{slug}, {tag2}]\n---\nUp: [[{parent}]]\n\n"
            write(path, front + new_body)
            processed += 1
print(f"[B] transformed {processed} notes; image embeds unresolved: {len(img_miss)}")
for d, u in img_miss[:15]:
    print("   MISS:", os.path.relpath(d, VAULT), "::", u)

# ---- Phase D: Home MOC --------------------------------------------------------
home = os.path.join(VAULT, "Home.md")
hub_links = "\n".join(f"- [[{sector_hub[s]}]]" for s in SECTORS) + "\n- [[Internet]]"
home_content = f"---\ntags: [home]\n---\n# Home\n\nMaster map of all sectors.\n\n## Sectors\n{hub_links}\n"
write(home, home_content)
print(f"[D] Home.md {'written' if APPLY else '(dry-run)'} with {len(SECTORS)+1} sector links")

# ---- Phase E: graph.json ------------------------------------------------------
colors = {
    "aihw": 5227511, "semi": 16740419, "bigtech": 11225020, "aerodef": 10275941,
    "internet": 16766287, "software": 5093036, "industrials": 10586239,
    "aiapp": 15753874, "home": 16777215,
}
gpath = os.path.join(VAULT, ".obsidian", "graph.json")
g = json.load(open(gpath))
g["showOrphans"] = False
g["hideUnresolved"] = True
g["colorGroups"] = [{"query": f"tag:#{t}", "color": {"a": 1, "rgb": rgb}} for t, rgb in colors.items()]
if APPLY:
    json.dump(g, open(gpath, "w"), indent=2)
print(f"[E] graph.json {'written' if APPLY else '(dry-run)'} with {len(colors)} color groups")
print("DONE  apply=" + str(APPLY))
