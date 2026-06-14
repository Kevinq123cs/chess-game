#!/usr/bin/env python3
"""Corrective pass: fix only currently-broken local file links (encoding/double-
encoding issues), removing any that are genuinely dead. Run with --apply."""
import os, re, sys, glob
from urllib.parse import unquote, quote

VAULT = "/Users/kq/Downloads/J_Tian_Notion copy"
APPLY = "--apply" in sys.argv
os.chdir(VAULT)

def uq(s):
    prev = None
    while s != prev:           # fully decode (handles double-encoding)
        prev = s; s = unquote(s)
    return s

# index all non-md files by basename variants -> real paths
all_files = set(); bindex = {}
for dp, _, fs in os.walk(VAULT):
    if ".obsidian" in dp: continue
    for f in fs:
        if f.endswith(".md"): continue
        ap = os.path.normpath(os.path.join(dp, f))
        all_files.add(ap)
        for key in {f, unquote(f), uq(f)}:
            bindex.setdefault(key, []).append(ap)

def find_links(text):
    out=[]; i=0; n=len(text)
    while True:
        j=text.find("](",i)
        if j==-1: break
        k=text.rfind("[",0,j)
        if k==-1: i=j+2; continue
        d=j+2; depth=1
        while d<n and depth>0:
            if text[d]=="(": depth+=1
            elif text[d]==")":
                depth-=1
                if depth==0: break
            d+=1
        if d>=n: break
        if "\n" in text[j+2:d]:
            le=text.find("\n",j); le=le if le!=-1 else n
            lp=text[j+2:le].rfind(")")
            if lp!=-1: d=j+2+lp
        out.append((k-1 if k>0 and text[k-1]=="!" else k, d+1,
                    k>0 and text[k-1]=="!", text[k+1:j], text[j+2:d]))
        i=d+1
    return out

def resolves_now(nd, dest):
    for v in {dest, unquote(dest), uq(dest)}:
        if os.path.isfile(os.path.join(nd, v)): return True
    return False

def robust(nd, dest):
    for v in {dest, unquote(dest), uq(dest)}:
        for base in (nd, VAULT):
            c = os.path.normpath(os.path.join(base, v))
            if c in all_files: return c
    for bn in {os.path.basename(dest), unquote(os.path.basename(dest)), uq(os.path.basename(dest))}:
        lst = bindex.get(bn, [])
        under = [p for p in lst if p.startswith(nd+os.sep)]
        if len(under)==1: return under[0]
        if len(lst)==1: return lst[0]
    return None

fixed=dead=0; dead_s=[]
for note in glob.glob("**/*.md", recursive=True):
    if note.startswith(".obsidian"): continue
    nd=os.path.dirname(os.path.join(VAULT, note))
    s=open(note,encoding="utf-8").read()
    links=find_links(s)
    if not links: continue
    out=[]; last=0; changed=False
    for st,en,emb,txt,dest in links:
        out.append(s[last:st]); last=en
        if (dest.startswith(("http://","https://","mailto:","#","data:","[["))
                or uq(dest).endswith(".md") or resolves_now(nd,dest)):
            out.append(s[st:en]); continue
        real=robust(nd,dest)
        if real:
            rel=quote(os.path.relpath(real,nd), safe="/")
            out.append(f"{'!' if emb else ''}[{txt}]({rel})"); fixed+=1; changed=True
        else:
            dead+=1; changed=True
            if len(dead_s)<20: dead_s.append((note,dest[:60]))
    out.append(s[last:])
    if changed and APPLY:
        open(note,"w",encoding="utf-8").write("".join(out))
print(f"links re-encoded/fixed: {fixed} | dead removed: {dead} | apply={APPLY}")
for n,d in dead_s: print(f"   DEAD: [{n}] {d}")
