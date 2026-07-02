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

## Deep dives (driver detail with indicator chips)

`deepDives` config entries build focused pages from the banks' driver sheets
(e.g. the AIDC/data-center engine model). Design principle: **full claims
only, compressed with indicators** — each bank gets one complete claim card,
and unavoidable detail is reduced to chips and a compact assumptions table
instead of year-by-year dumps.

- Driver sheets are free-form, so series use explicit `row` numbers (like
  SOTP cells), with `col0`/`n`/`y0` describing the year columns and `scale`
  converting to RMB mn. `sumRows` adds several rows into one series.
- **Computed chips** (build.py, from the data): `actuals: Ny` (evidence
  depth; ≤3y flags amber, ≤1y red), `YYYYE aligned` / `YYYYE gap: +x%`
  (cross-bank agreement on the two series named by `compare`).
- **Authored chips** (config, editorial): margin path, scope caveats, SOTP
  weight, CAGR — anything that encodes judgment rather than arithmetic.
- `drivers` tables show each assumption as one row: last actual → first
  estimate → final estimate → CAGR, so a 20-column sheet reads in one line.

## Chinese / English toggle & section summaries

The app has an EN/中文 toggle in the masthead (remembered in localStorage).
UI chrome is translated by the template itself; data strings come from the
config's optional `*Zh` fields — `companyZh`, `nameZh`/`asOfZh` on sources,
`labelZh` on metrics, `categories` (en→zh map), the 3-tuple segment series
form `(en, zh, sheetLabel)`, `noteZh`, and on SOTP: `labelZh`, `nameZh`,
`basisZh` (same `{CELL:fmt}` refs as `basis`). Omit any of them and that
string simply stays in English.

`summaries` holds a short bilingual explainer per section — keyed by category
name plus `segments` and `sotp` — rendered in an "About this section" card
above the charts. This is where the investment logic lives (e.g. how each
bank builds its SOTP and what drives the AIDC valuation gap), so rewrite
these for each new company.

The output is fully self-contained (data embedded) — open it directly or serve
it; no dependencies at view time.
