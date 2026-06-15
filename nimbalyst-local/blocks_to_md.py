#!/usr/bin/env python3
"""Notion blocks -> vault-style Markdown.

Produces a list of RenderedBlock units (one per top-level Notion block). Each
unit carries a stable `key` (for diffing), its markdown `text`, and any image
descriptors. Images are emitted as placeholder tokens; the orchestrator swaps in
the real local link after downloading bytes (URLs expire, so we can't key on
them).
"""
import re

IMG_PH = "\x00IMG{}\x00"  # placeholder token, replaced after download


class RenderedBlock:
    __slots__ = ("key", "text", "images", "is_image", "child_page_id", "title")

    def __init__(self, key, text, images=None, is_image=False,
                 child_page_id=None, title=None):
        self.key = key                  # stable diff key (None for images: set later)
        self.text = text                # markdown, may contain IMG placeholders
        self.images = images or []      # [{"url","external","caption","ph"}]
        self.is_image = is_image
        self.child_page_id = child_page_id
        self.title = title              # for child_page


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip().lower()


def _rich(rich) -> str:
    """rich_text array -> inline markdown with annotations + links."""
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
        href = t.get("href")
        if href:
            txt = f"[{txt}]({href})"
        out.append(txt)
    return "".join(out)


def _plain(rich) -> str:
    return "".join(t.get("plain_text", "") for t in (rich or []))


def _image_unit(block, idx_holder) -> RenderedBlock:
    img = block.get("image", {})
    if img.get("type") == "external":
        url, external = img.get("external", {}).get("url", ""), True
    else:
        url, external = img.get("file", {}).get("url", ""), False
    caption = _plain(img.get("caption"))
    ph = IMG_PH.format(idx_holder[0])
    idx_holder[0] += 1
    desc = {"url": url, "external": external, "caption": caption, "ph": ph}
    alt = caption or "image"
    # keyed by stable Notion block id so existing images aren't re-downloaded
    return RenderedBlock(key=f"img:{block['id']}", text=f"![{alt}]({ph})",
                         images=[desc], is_image=True)


def render(blocks, notion, idx_holder=None) -> list:
    """Top-level blocks -> [RenderedBlock]. `notion` used to fetch nested children."""
    if idx_holder is None:
        idx_holder = [0]
    units = []
    for b in blocks:
        t = b.get("type")
        data = b.get(t, {})

        if t == "paragraph":
            md = _rich(data.get("rich_text"))
            if not md.strip():
                continue  # skip empty paragraphs (vault uses blank lines)
            units.append(RenderedBlock(f"p:{_norm(_plain(data.get('rich_text')))}", md))

        elif t in ("heading_1", "heading_2", "heading_3"):
            hashes = "#" * int(t[-1])
            md = _rich(data.get("rich_text"))
            units.append(RenderedBlock(f"h:{_norm(_plain(data.get('rich_text')))}",
                                       f"{hashes} {md}"))

        elif t in ("bulleted_list_item", "numbered_list_item", "to_do"):
            marker = "1." if t == "numbered_list_item" else "-"
            md = _rich(data.get("rich_text"))
            if t == "to_do":
                box = "[x]" if data.get("checked") else "[ ]"
                md = f"{box} {md}"
            lines = [f"{marker} {md}"]
            if b.get("has_children"):
                for sub in render(notion.block_children(b["id"]), notion, idx_holder):
                    for ln in sub.text.split("\n"):
                        lines.append("\t" + ln)
                    units_imgs = sub.images
                    # bubble nested images up to this unit
                    if units_imgs:
                        # attach to the list unit below
                        pass
            unit = RenderedBlock(f"li:{_norm(_plain(data.get('rich_text')))}",
                                 "\n".join(lines))
            units.append(unit)

        elif t == "quote":
            md = _rich(data.get("rich_text"))
            units.append(RenderedBlock(f"q:{_norm(_plain(data.get('rich_text')))}",
                                       f"> {md}"))

        elif t == "callout":
            md = _rich(data.get("rich_text"))
            units.append(RenderedBlock(f"co:{_norm(_plain(data.get('rich_text')))}",
                                       f"> {md}"))

        elif t == "code":
            lang = data.get("language", "")
            code = _plain(data.get("rich_text"))
            units.append(RenderedBlock(f"code:{_norm(code)[:80]}",
                                       f"```{lang}\n{code}\n```"))

        elif t == "divider":
            units.append(RenderedBlock("hr", "---"))

        elif t == "image":
            units.append(_image_unit(b, idx_holder))

        elif t == "child_page":
            title = data.get("title", "").strip()
            units.append(RenderedBlock(f"cp:{b['id']}", f"[[{title}]]",
                                       child_page_id=b["id"], title=title))

        elif t == "child_database":
            title = data.get("title", "").strip()
            units.append(RenderedBlock(f"cdb:{b['id']}", f"[[{title}]]",
                                       child_page_id=b["id"], title=title))

        elif t in ("column_list",):
            # Obsidian has no columns: flatten grandchildren in order
            for col in notion.block_children(b["id"]):
                if col.get("has_children"):
                    units.extend(render(notion.block_children(col["id"]),
                                        notion, idx_holder))

        elif t == "toggle":
            md = _rich(data.get("rich_text"))
            units.append(RenderedBlock(f"p:{_norm(_plain(data.get('rich_text')))}", md))
            if b.get("has_children"):
                units.extend(render(notion.block_children(b["id"]), notion, idx_holder))

        elif t in ("bookmark", "embed", "link_preview"):
            url = data.get("url", "")
            if url:
                units.append(RenderedBlock(f"link:{_norm(url)}", url))

        elif t == "table":
            if b.get("has_children"):
                rows = []
                for row in notion.block_children(b["id"]):
                    cells = row.get("table_row", {}).get("cells", [])
                    rows.append("| " + " | ".join(_rich(c) for c in cells) + " |")
                if rows:
                    units.append(RenderedBlock(f"table:{_norm(rows[0])[:80]}",
                                               "\n".join(rows)))

        else:
            # unknown: best-effort plain text, skip if empty
            txt = _plain(data.get("rich_text")) if isinstance(data, dict) else ""
            if txt.strip():
                units.append(RenderedBlock(f"x:{_norm(txt)}", _rich(data.get("rich_text"))))

    return units
