#!/usr/bin/env python3
"""Build a single-file financial-model visualizer from broker Excel models.

Usage:
    python3 build.py companies/weichai.py

Reads the company config (which Excel files, which labelled rows / cells to
pull), extracts the data, and injects it into template.html. The output is a
self-contained HTML file written to the repo root.

Rows are located by LABEL TEXT (normalized), not by row number, so the same
config style keeps working when a bank shifts rows around — and adapting to a
new company is mostly a matter of pointing at its files and fixing the few
labels that differ. SOTP sheets are free-form, so those use explicit cell
references.
"""
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def clean(v, scale=1.0):
    if v is None or isinstance(v, str):
        return None
    try:
        f = float(v) * scale
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return round(f, 4) if abs(f) < 100 else round(f, 1)


class Model:
    """One bank's workbook with label-based row lookup."""

    def __init__(self, path):
        self.wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        self._cols = {}  # (sheet, col) -> [normalized labels]

    def _col(self, sheet, col):
        key = (sheet, col)
        if key not in self._cols:
            ws = self.wb[sheet]
            self._cols[key] = [
                norm(row[0]) if row[0] is not None else ""
                for row in ws.iter_rows(min_col=col, max_col=col, values_only=True)
            ]
        return self._cols[key]

    def find_row(self, sheet, col, label, occ=1, after=0):
        """Row number of the occ-th match of label in a column. Exact
        (whitespace/case-insensitive) match first, then unique startswith."""
        tgt = norm(label)
        vals = self._col(sheet, col)
        exact = [i + 1 for i, v in enumerate(vals) if v == tgt and i + 1 > after]
        if len(exact) >= occ:
            return exact[occ - 1]
        prefix = [i + 1 for i, v in enumerate(vals) if v.startswith(tgt) and v and i + 1 > after]
        if len(prefix) >= occ:
            return prefix[occ - 1]
        raise KeyError(f"label {label!r} (occ {occ}, after row {after}) not found in {sheet}!col{col}")

    def grab(self, sheet, row, col0, n, scale=1.0):
        ws = self.wb[sheet]
        vals = next(ws.iter_rows(min_row=row, max_row=row, min_col=col0,
                                 max_col=col0 + n - 1, values_only=True))
        return [clean(v, scale) for v in vals]

    def cell(self, sheet, ref):
        return self.wb[sheet][ref].value


def fmt_cells(model, sheet, template):
    """Replace {C4:,.0f}-style refs in a string with formatted cell values."""

    def repl(m):
        ref, spec = m.group(1), m.group(2) or ""
        v = model.cell(sheet, ref)
        if v is None:
            return "–"
        return format(v, spec) if spec else str(v)

    return re.sub(r"\{([A-Z]{1,3}\d+)(?::([^}]*))?\}", repl, template)


def extract(cfg):
    models = {k: Model(s["file"]) for k, s in cfg["sources"].items()}

    sources = {}
    for key, s in cfg["sources"].items():
        y0, y1 = s["years"]
        sources[key] = {
            "name": s["name"],
            "asOf": s["asOf"],
            "years": list(range(y0, y1 + 1)),
            "estFrom": s["estFrom"],
        }

    # ---- metrics (label-based row lookup) ----
    metrics = []
    for m in cfg["metrics"]:
        entry = {"id": m["id"], "label": m["label"], "unit": m["unit"],
                 "category": m["category"], "series": {}}
        for key, spec in m["rows"].items():
            if spec is None:
                continue
            label, occ = (spec, 1) if isinstance(spec, str) else spec
            s = cfg["sources"][key]
            row = models[key].find_row(s["metricSheet"], s["labelCol"], label, occ)
            n = len(sources[key]["years"])
            entry["series"][key] = models[key].grab(s["metricSheet"], row, s["valueCol"], n)
        metrics.append(entry)

    # ---- segments ----
    segments = {}
    for key, seg in cfg.get("segments", {}).items():
        model, out = models[key], {}
        n = len(sources[key]["years"])
        for gname, g in seg["groups"].items():
            after = 0
            for acol, alabel in g.get("anchors", []):
                after = model.find_row(seg["sheet"], acol, alabel, after=after)
            series = {}
            for display, label in g["series"]:
                row = model.find_row(seg["sheet"], seg["labelCol"], label, after=after)
                series[display] = model.grab(seg["sheet"], row, seg["valueCol"], n,
                                             scale=g.get("scale", 1.0))
            out[gname] = series
        out["notes"] = {k: g["note"] for k, g in seg["groups"].items() if g.get("note")}
        out["mixOf"] = seg.get("mixOf", "revenue")
        segments[key] = out

    # ---- SOTP (free-form sheets -> explicit cells) ----
    sotp = None
    if "sotp" in cfg:
        sotp = {"groups": cfg["sotp"]["groups"], "sources": {}}
        for key, sp in cfg["sotp"]["sources"].items():
            model, sheet = models[key], sp["sheet"]
            parts = []
            for p in sp["parts"]:
                part = {
                    "name": p["name"],
                    "group": p["group"],
                    "value": clean(model.cell(sheet, p["value"])),
                    "basis": fmt_cells(model, sheet, p["basis"]),
                }
                if p.get("old"):
                    part["old"] = clean(model.cell(sheet, p["old"]))
                parts.append(part)
            stats = [{"label": st["label"],
                      "value": st["fmt"].format(v=model.cell(sheet, st["cell"]))}
                     for st in sp["stats"] if model.cell(sheet, st["cell"]) is not None]
            entry = {"parts": parts, "total": clean(model.cell(sheet, sp["total"])), "stats": stats}
            if sp.get("oldTotal"):
                entry["oldTotal"] = clean(model.cell(sheet, sp["oldTotal"]))
            sotp["sources"][key] = entry

    data = {
        "company": cfg["company"],
        "tickers": cfg["tickers"],
        "currency": cfg["currency"],
        "unitNote": cfg.get("unitNote", f"{cfg['currency']} mn unless stated"),
        "sources": sources,
        "metrics": metrics,
        "segments": segments,
    }
    if sotp:
        data["sotp"] = sotp
    return data


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    cfg_path = (HERE / sys.argv[1]).resolve() if not Path(sys.argv[1]).is_absolute() else Path(sys.argv[1])
    spec = importlib.util.spec_from_file_location("company_cfg", cfg_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cfg = mod.CONFIG

    data = extract(cfg)
    payload = json.dumps(data, ensure_ascii=False)
    assert "</" not in payload, "JSON payload would break out of its <script> tag"

    template = (HERE / "template.html").read_text()
    assert "__DATA__" in template
    out_path = HERE.parent / cfg["output"]
    out_path.write_text(template.replace("__DATA__", payload))
    kb = out_path.stat().st_size / 1024
    print(f"wrote {out_path}  ({kb:.0f} KB, {len(data['metrics'])} metrics, "
          f"segments: {list(data['segments'])}, sotp: {list(data.get('sotp', {}).get('sources', {}))})")


if __name__ == "__main__":
    main()
