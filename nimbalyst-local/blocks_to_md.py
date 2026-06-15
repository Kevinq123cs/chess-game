#!/usr/bin/env python3
"""Notion blocks -> vault-style Markdown.

Two modes:
- shallow=True (default for the walk): render only top-level blocks, making ZERO
  extra API calls. Blocks with nested content (lists with sub-items, columns,
  toggles, tables) are emitted as single units flagged `needs_deep`. This is all
  that's needed for change detection and key snapshots, and keeps the walk from
  exploding into nested block_children calls.
- shallow=False (deep): fully expand nested children. Used only to materialize a
  block that is actually new and about to be inserted, so deep fetches stay
  proportional to new content, not the whole vault.

Each RenderedBlock carries a stable `key` (for diffing), markdown `text`, image
descriptors (placeholder tokens swapped for local links by the caller), and the
raw `block` so a shallow unit can be deep-rendered later.
"""
from __future__ import annotations
import re

IMG_PH = "\x00IMG{}\x00"


class RenderedBlock:
    __slots__ = ("key", "text", "images", "is_image", "child_page_id", "title",
                 "block", "needs_deep")

    def __init__(self, key, text, images=None, is_image=False, child_page_id=None,
                 title=None, block=None, needs_deep=False):
        self.key = key
        self.text = text
        self.images = images or []
        self.is_image = is_image
        self.child_page_id = child_page_id
        self.title = title
        self.block = block
        self.needs_deep = needs_deep


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip().lower()


def _rich(rich) -> str:
    out = []
    for t in rich or []:
        txt = t.get("plain_text", "")
        if not txt:
            continue
        a = t.get("annotations", {})
        if a.get("code"):
            txt = f"`{txt}`"
        if a.get("bold"):
            txt = f"**{txt}**"
        if a.get("italic"):
            txt = f"*{txt}*"
        if a.get("strikethrough"):
            txt = f"~~{txt}~~"
        if t.get("href"):
            txt = f"[{txt}]({t['href']})"
        out.append(txt)
    return "".join(out)


def _plain(rich) -> str:
    return "".join(t.get("plain_text", "") for t in (rich or []))


def _image_unit(block, idx_holder) -> RenderedBlock:
    img = block.get("image", {})
    if img.get("type") == "external":
        url = img.get("external", {}).get("url", "")
    else:
        url = img.get("file", {}).get("url", "")
    caption = _plain(img.get("caption"))
    ph = IMG_PH.format(idx_holder[0])
    idx_holder[0] += 1
    desc = {"url": url, "external": img.get("type") == "external",
            "caption": caption, "ph": ph}
    return RenderedBlock(f"img:{block['id']}", f"![{caption or 'image'}]({ph})",
                         images=[desc], is_image=True, block=block)


def render(blocks, notion, shallow=False, idx_holder=None) -> list:
    if idx_holder is None:
        idx_holder = [0]
    units = []
    for b in blocks:
        t = b.get("type")
        data = b.get(t, {}) if isinstance(b.get(t), dict) else {}
        rich = data.get("rich_text")

        if t == "paragraph":
            md = _rich(rich)
            if md.strip():
                units.append(RenderedBlock(f"p:{_norm(_plain(rich))}", md, block=b))

        elif t in ("heading_1", "heading_2", "heading_3"):
            units.append(RenderedBlock(f"h:{_norm(_plain(rich))}",
                                       f"{'#' * int(t[-1])} {_rich(rich)}", block=b))

        elif t in ("bulleted_list_item", "numbered_list_item", "to_do"):
            marker = "1." if t == "numbered_list_item" else "-"
            md = _rich(rich)
            if t == "to_do":
                md = f"[{'x' if data.get('checked') else ' '}] {md}"
            lines, imgs, needs_deep = [f"{marker} {md}"], [], False
            if b.get("has_children"):
                if shallow:
                    needs_deep = True
                else:
                    for sub in render(notion.block_children(b["id"]), notion, False,
                                      idx_holder):
                        for ln in sub.text.split("\n"):
                            lines.append("\t" + ln)
                        imgs.extend(sub.images)
            units.append(RenderedBlock(f"li:{_norm(_plain(rich))}", "\n".join(lines),
                                       images=imgs, block=b, needs_deep=needs_deep))

        elif t in ("quote", "callout"):
            units.append(RenderedBlock(f"q:{_norm(_plain(rich))}", f"> {_rich(rich)}",
                                       block=b))

        elif t == "code":
            code = _plain(rich)
            units.append(RenderedBlock(f"code:{_norm(code)[:80]}",
                                       f"```{data.get('language','')}\n{code}\n```",
                                       block=b))

        elif t == "divider":
            units.append(RenderedBlock(f"hr:{b['id']}", "---", block=b))

        elif t == "image":
            units.append(_image_unit(b, idx_holder))

        elif t in ("child_page", "child_database"):
            title = data.get("title", "").strip()
            units.append(RenderedBlock(f"cp:{b['id']}", f"[[{title}]]",
                                       child_page_id=b["id"], title=title, block=b))

        elif t == "column_list":
            if shallow:
                units.append(RenderedBlock(f"col:{b['id']}", "", block=b, needs_deep=True))
            else:
                for col in notion.block_children(b["id"]):
                    if col.get("has_children"):
                        units.extend(render(notion.block_children(col["id"]), notion,
                                            False, idx_holder))

        elif t == "toggle":
            units.append(RenderedBlock(f"p:{_norm(_plain(rich))}", _rich(rich), block=b,
                                       needs_deep=(shallow and b.get("has_children"))))
            if not shallow and b.get("has_children"):
                units.extend(render(notion.block_children(b["id"]), notion, False,
                                    idx_holder))

        elif t in ("bookmark", "embed", "link_preview"):
            url = data.get("url", "")
            if url:
                units.append(RenderedBlock(f"link:{_norm(url)}", url, block=b))

        elif t == "table":
            if shallow:
                units.append(RenderedBlock(f"tbl:{b['id']}", "", block=b, needs_deep=True))
            elif b.get("has_children"):
                rows = ["| " + " | ".join(_rich(c) for c in
                        row.get("table_row", {}).get("cells", [])) + " |"
                        for row in notion.block_children(b["id"])]
                if rows:
                    units.append(RenderedBlock(f"tbl:{b['id']}", "\n".join(rows), block=b))

        else:
            txt = _plain(rich)
            if txt.strip():
                units.append(RenderedBlock(f"x:{_norm(txt)}", _rich(rich), block=b))

    return units


def deep_render(unit, notion) -> tuple:
    """Fully expand a single shallow unit. Returns (text, images)."""
    deep = render([unit.block], notion, shallow=False)
    text = "\n\n".join(u.text for u in deep if u.text)
    images = [img for u in deep for img in u.images]
    return text, images
