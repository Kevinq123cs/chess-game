#!/usr/bin/env python3
"""Load/save sync-state.json.

State maps each Notion page id to its last_edited_time, the local file it mirrors,
the set of block keys already synced (for append-only diffing), and an image
manifest (sha256 -> filename). Kept in nimbalyst-local/, outside the vault.
"""
import os
import json

STATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "sync-state.json")


def load() -> dict:
    if os.path.isfile(STATE_PATH) and os.path.getsize(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    return {"version": 1, "roots": {}, "pages": {}}


def save(state: dict, apply: bool) -> None:
    if not apply:
        return
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, STATE_PATH)


def page_record(state: dict, page_id: str) -> dict:
    return state["pages"].get(page_id)


def upsert_page(state: dict, page_id: str, **fields) -> dict:
    rec = state["pages"].setdefault(page_id, {
        "title": "", "local_path": "", "parent_id": None, "sector": "",
        "last_edited_time": "", "block_keys": [], "images": {},
    })
    rec.update(fields)
    return rec
