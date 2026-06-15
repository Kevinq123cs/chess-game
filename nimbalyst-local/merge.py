#!/usr/bin/env python3
"""Append-only merge of new Notion blocks into an existing vault note.

Given the rendered Notion blocks (in document order), the set of block keys we've
already synced, and the current file text, insert ONLY the blocks whose key is
new. Each new block is placed adjacent to its Notion neighbour so newest-first
ordering is preserved, and existing lines are never moved or deleted.

Near-duplicate tripwire: keys are content-based, which is correct for an
append-only log. As insurance against that assumption, when a block is inserted
that is highly similar (but not identical) to existing content, we emit a WARNING
(file, new text, the resembling line, similarity score) without changing merge
behaviour. Identical blocks are already skipped as 'known'; this catches the
near-match gap that signals an in-place Notion edit starting to duplicate.
"""
from __future__ import annotations
import re
import difflib

SIMILAR_THRESHOLD = 0.85
_MIN_CMP_LEN = 12


def _norm_line(s: str) -> str:
    s = re.sub(r"[*`_>#]", "", s)
    s = s.replace("\\", "")
    return re.sub(r"\s+", " ", s).strip().lower()


def _full_norm(unit) -> str:
    txt = re.sub(r"\x00IMG\d+\x00", "", unit.text)
    txt = re.sub(r"[*`_>#]", "", txt).replace("\\", "")
    return re.sub(r"\s+", " ", txt).strip().lower()


def _snippet(unit) -> str:
    return _full_norm(unit)[:40]


def _locate(unit, lines, norm_lines) -> int | None:
    """Line index where an already-known unit's text lives, or None."""
    if unit.child_page_id:                       # child_page/child_database link
        needle = f"[[{(unit.title or '').lower()}"
        for i, ln in enumerate(lines):
            if needle in ln.lower():
                return i
        return None
    if unit.is_image:
        return None                              # images are unreliable anchors
    snip = _snippet(unit)
    if len(snip) < 6:
        return None
    for i, nl in enumerate(norm_lines):
        if snip in nl:
            return i
    return None


def _header_end(lines) -> int:
    """First insertion point after frontmatter + Up: + '# Title' + blank."""
    i = 0
    if lines and lines[0] == "---":
        i = 1
        while i < len(lines) and lines[i] != "---":
            i += 1
        i += 1
    while i < len(lines) and not lines[i].startswith("# "):
        i += 1
    i += 1                                        # past the H1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    return min(i, len(lines))


def _near_duplicate(text_norm: str, candidates: list):
    """Best (score, candidate_text) among existing lines; only near, not exact."""
    best_score, best_text = 0.0, ""
    sm = difflib.SequenceMatcher()
    sm.set_seq2(text_norm)
    for cand in candidates:
        # cheap length gate before the O(n) ratio
        if not cand or abs(len(cand) - len(text_norm)) > max(len(text_norm), 1) * 0.5:
            continue
        sm.set_seq1(cand)
        if sm.real_quick_ratio() < SIMILAR_THRESHOLD:
            continue
        r = sm.ratio()
        if r > best_score:
            best_score, best_text = r, cand
    if SIMILAR_THRESHOLD <= best_score < 1.0:
        return best_score, best_text
    return None


def merge(file_text: str, units: list, known: set, localize, note_dir: str):
    """Return (new_text, n_added_units, added_keys, imgs_done, warnings).

    `localize(desc, note_dir) -> str` swaps an image placeholder for a local link.
    `warnings` is a list of {"new","near","score"} near-duplicate signals.
    """
    lines = file_text.split("\n")
    norm_lines = [_norm_line(l) for l in lines]
    new_flags = [u.key not in known for u in units]
    if not any(new_flags):
        return file_text, 0, [], 0, []

    # candidate pool for the tripwire: existing substantive lines (pre-insert)
    cmp_pool = [nl for nl in norm_lines if len(nl) >= _MIN_CMP_LEN]

    header_idx = _header_end(lines)
    ops = []
    added_keys = []
    warnings = []
    imgs_done = 0

    i, n = 0, len(units)
    while i < n:
        if not new_flags[i]:
            i += 1
            continue
        j = i
        run = []
        while j < n and new_flags[j]:
            run.append(units[j])
            added_keys.append(units[j].key)
            j += 1

        rendered = []
        for u in run:
            # near-duplicate tripwire (text blocks only; never alters behaviour)
            if not u.is_image and not u.child_page_id:
                a = _full_norm(u)
                if len(a) >= _MIN_CMP_LEN:
                    hit = _near_duplicate(a, cmp_pool)
                    if hit:
                        warnings.append({"new": u.text[:120],
                                         "near": hit[1][:120],
                                         "score": round(hit[0], 3)})
            text = u.text
            for desc in u.images:
                link = localize(desc, note_dir)
                text = text.replace(desc["ph"], link)
                imgs_done += 1
            rendered.append(text)

        run_lines = []
        for t in rendered:
            run_lines.extend(t.split("\n"))
            run_lines.append("")

        anchor_line = None
        for u in units[j:]:
            if u.key in known:
                loc = _locate(u, lines, norm_lines)
                if loc is not None:
                    anchor_line = loc
                    break
        if anchor_line is None:
            for u in reversed(units[:i]):
                if u.key in known:
                    loc = _locate(u, lines, norm_lines)
                    if loc is not None:
                        anchor_line = loc + 1
                        break
        if anchor_line is None:
            anchor_line = header_idx

        ops.append((anchor_line, run_lines))
        i = j

    for line_index, run_lines in sorted(ops, key=lambda o: o[0], reverse=True):
        lines[line_index:line_index] = run_lines

    new_text = "\n".join(lines)
    new_text = re.sub(r"\n{4,}", "\n\n\n", new_text)
    return new_text, len(added_keys), added_keys, imgs_done, warnings
