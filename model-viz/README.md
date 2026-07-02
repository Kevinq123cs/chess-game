# model-viz — broker financial-model visualizer

Turns sell-side Excel models (Morgan Stanley / UBS style) into a single-file
interactive HTML explorer: metric catalog, source comparison, correlation views
(paired panels / overlay / indexed / scatter), segment stacks, and a
sum-of-the-parts (SOTP) valuation page.

## Files

- `template.html` — the generic app shell. Company-agnostic: everything (name,
  tickers, sources, metrics, segments, SOTP) comes from a JSON blob injected at
  the `__DATA__` placeholder. Don't hardcode company facts here.
- `build.py` — extracts data from the Excel models per a company config and
  writes the finished HTML to the repo root.
- `companies/<name>.py` — one config per company. The only file you touch to
  add a company.

## Build

```bash
cd model-viz
python3 build.py companies/weichai.py
# -> ../weichai-model-viz.html
```

Requires `openpyxl` (`pip3 install --user openpyxl`).

## Adding another company (with similar MS/UBS models)

1. Copy `companies/weichai.py` to `companies/<newco>.py`.
2. Point `file` at the new Excel models; set `company`, `tickers`, `output`.
3. Set each source's `years` (first/last annual column), `estFrom` (first
   estimate year), `metricSheet`, `labelCol` (column holding row labels) and
   `valueCol` (column of the first year).
4. Metrics: rows are found by **label text** (case/whitespace-insensitive,
   with startswith fallback), so most entries survive unchanged when the bank
   reuses its template. Use `(label, occurrence)` when a label repeats (e.g.
   MS reuses "P/E" for H- and A-share blocks). Set a source to `None` if that
   bank doesn't carry the metric — the app shows availability badges and
   handles gaps.
5. Segments: each group locates its block via `anchors` (labels scanned in
   order, each constraining the search to rows below the previous match), then
   finds each series by label. `scale` converts sheet units to millions.
6. SOTP: these sheets are free-form, so values use explicit cell refs
   (`"E9"`). `basis` strings may embed `{CELL:pyformat}` refs that are
   resolved from the sheet at build time. Assign each part to one of the
   shared `groups` so the same bucket wears the same color across banks.
7. Run the build; `build.py` raises a clear `KeyError` naming any label it
   can't find — fix those labels and rerun.

The output is fully self-contained (data embedded) — open it directly or serve
it; no dependencies at view time.
