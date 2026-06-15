#!/usr/bin/env python3
"""Move all PDFs into <Sector>_database/Pictures/<Owner>/, rewrite their links,
and remove genuinely-dead local links/embeds. Run with --apply."""
import os, re, sys, glob, shutil
from urllib.parse import unquote, quote

VAULT = os.environ.get("VAULT", "/Users/kq/Downloads/J_Tian_Notion copy")
APPLY = "--apply" in sys.argv
SECTORS = ["AI hardware","Semi","Big Tech","Aerospace & Defense","Software",
           "Industrial & Materials","AI Application","Internet"]
os.chdir(VAULT)

def db_dir(sector):
    return os.path.join(VAULT, sector, [d for d in os.listdir(os.path.join(VAULT,sector)) if d.endswith("_database")][0])

# ---- build PDF move map ------------------------------------------------------
pdf_move = {}
used = set()
for sector in SECTORS:
    db = db_dir(sector); pics = os.path.join(db, "Pictures")
    for dp, _, fs in os.walk(db):
        if os.path.basename(dp) == "Pictures" or (os.sep+"Pictures"+os.sep) in dp+os.sep:
            continue
        for f in sorted(fs):
            if not f.lower().endswith(".pdf"):
                continue
            owner = os.path.basename(dp)
            if owner == os.path.basename(db): owner = "_loose"
            stem, ext = os.path.splitext(f); n = 1
            tgt = os.path.join(pics, owner, f)
            while tgt in used:
                n += 1; tgt = os.path.join(pics, owner, f"{stem} {n}{ext}")
            used.add(tgt)
            pdf_move[os.path.normpath(os.path.join(dp, f))] = tgt
print(f"PDFs to move: {len(pdf_move)}")

# ---- balanced-paren markdown link finder ------------------------------------
def find_links(text):
    out=[]; i=0; n=len(text)
    while True:
        j = text.find("](", i)
        if j == -1: break
        k = text.rfind("[", 0, j)
        if k == -1: i = j+2; continue
        is_embed = k > 0 and text[k-1] == "!"
        d = j+2; depth = 1
        while d < n and depth > 0:
            if text[d] == "(": depth += 1
            elif text[d] == ")":
                depth -= 1
                if depth == 0: break
            d += 1
        if d >= n: break
        # If balanced parsing ran past a newline, the filename had an unbalanced
        # '(' (Notion exports do this). Fall back to the last ')' on j's line.
        if "\n" in text[j+2:d]:
            line_end = text.find("\n", j)
            if line_end == -1: line_end = n
            seg = text[j+2:line_end]
            lp = seg.rfind(")")
            if lp != -1:
                d = j+2+lp
        out.append((k-1 if is_embed else k, d+1, is_embed, text[k+1:j], text[j+2:d]))
        i = d+1
    return out

# ---- index every non-md file by basename (raw + url-decoded) -----------------
all_files = set(); bindex = {}
for dp, _, fs in os.walk(VAULT):
    if ".obsidian" in dp: continue
    for f in fs:
        if f.endswith(".md"): continue
        ap = os.path.normpath(os.path.join(dp, f))
        all_files.add(ap)
        for key in {f, unquote(f)}:
            bindex.setdefault(key, []).append(ap)

def resolve(nd, dest):
    """Return the real on-disk path a link points to, or None."""
    for base in (nd, VAULT):
        for variant in {unquote(dest), dest}:
            c = os.path.normpath(os.path.join(base, variant))
            if c in all_files:
                return c
    for bn in {unquote(os.path.basename(dest)), os.path.basename(dest)}:
        lst = bindex.get(bn, [])
        under = [p for p in lst if p.startswith(nd + os.sep)]
        if len(under) == 1: return under[0]
        if len(lst) == 1: return lst[0]
    return None

# ---- apply PDF moves ---------------------------------------------------------
if APPLY:
    for old, new in pdf_move.items():
        os.makedirs(os.path.dirname(new), exist_ok=True)
        shutil.move(old, new)

# ---- rewrite notes: fix pdf links, drop dead local links --------------------
pdf_fixed = dead_removed = 0
dead_samples = []
for note in glob.glob("**/*.md", recursive=True):
    if note.startswith(".obsidian"): continue
    nd = os.path.dirname(os.path.join(VAULT, note))
    s = open(note, encoding="utf-8").read()
    links = find_links(s)
    if not links: continue
    pieces = []; last = 0
    for start, end, is_embed, txt, dest in links:
        pieces.append(s[last:start]); last = end
        keep = s[start:end]
        if dest.startswith(("http://","https://","mailto:","#","data:")) or dest.startswith("[["):
            pieces.append(keep); continue
        if unquote(dest).endswith(".md"):
            pieces.append(keep); continue
        real = resolve(nd, dest)
        if real and real in pdf_move:        # a PDF we moved -> rewrite path
            relpath = os.path.relpath(pdf_move[real], nd).replace(" ", "%20")
            pieces.append(f"{'!' if is_embed else ''}[{txt}]({relpath})")
            pdf_fixed += 1
        elif real:
            pieces.append(keep)              # resolves to a real file -> leave
        else:
            dead_removed += 1                # genuinely dead -> drop markup
            if len(dead_samples) < 25: dead_samples.append((note, dest[:70]))
    pieces.append(s[last:])
    new = "".join(pieces)
    if new != s and APPLY:
        open(note, "w", encoding="utf-8").write(new)

print(f"pdf links rewritten: {pdf_fixed} | dead links removed: {dead_removed} | apply={APPLY}")
for n,d in dead_samples: print(f"   DEAD: [{n}] {d}")

# remove emptied folders
if APPLY:
    removed = 0
    for dp,_,_ in os.walk(VAULT, topdown=False):
        if ".obsidian" in dp or dp == VAULT: continue
        try:
            if not os.listdir(dp): os.rmdir(dp); removed += 1
        except OSError: pass
    print(f"empty folders removed: {removed}")
print("DONE apply=" + str(APPLY))
