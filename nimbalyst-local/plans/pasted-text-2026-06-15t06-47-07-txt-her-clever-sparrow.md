# One-Time Quarterly Earnings Grid in Obsidian `Home.md`

## Context

Jeff wants a Markdown table in his Obsidian `Home.md` showing, for each company he
tracks, the projected earnings-call date for each of the next four quarters —
readable across a row (one company's year) or down a column (everyone reporting that
quarter). This is a **one-time fill**, not a maintained/scheduled program: when he
wants a refresh he'll just ask. Any code used is disposable scaffolding (nothing
installed, scheduled, or committed). Data comes from the API Ninjas earnings calendar.

### Confirmed decisions
1. **Scope** — auto-detect public companies across **all 7 sectors**.
2. **Ticker review gate** — before fetching any earnings, present the full
   **company → ticker → exchange** list for Jeff to review/correct. Nothing is
   filled until he approves.
3. **Tickers** — title-first: use the ticker already in each note title, normalize
   to API format, verify via `/v1/ticker` (ticker→name). Manually map the few
   no-ticker public names. Private/topic notes are skipped (but listed).
4. **Dates — estimates only.** No confirmed future dates exist on this key. For each
   ticker: pull history (last ~1–2 yrs primary, deeper as needed), find the typical
   reporting window for each quarter, project those windows forward, and mark **every**
   projected date as an estimate: `~2026-10-28 (est)`.
5. **Columns** — next 4 **calendar quarters** (Q3 2026 … Q2 2027) by report date;
   semi-annual reporters simply show blanks in their off-quarters.
6. **No maintained artifact** — no `.env`/`.gitignore`/`companies.csv`/launchd.

### Reviewed-and-approved company list (Jeff signed off)
- **Scope:** ~110 public companies across all 7 sectors. Private companies
  **excluded** entirely. China A-shares **included** (I resolve .SS/.SZ tickers).
- **Non-US coverage:** keep all non-US names; where API Ninjas returns nothing
  (European `.DE/.PA/.MI/.L/.SW/.AS`, Korea `.KS`, Taiwan `.TW`, China `.SS/.SZ`),
  those cells just stay blank. Only US, HK, and Japan (`.T`) are confirmed-covered.
- **Auto-fixes applied:** Vulcan `VMT`→`VMC`; dedupe Planet Labs (×2) and Reddit (×2)
  into single rows.
- **Line-item corrections from review:**
  - ASE Technology → `3711.TW` (local listing, not the ASX ADR)
  - INNIO → `INIO`
  - Fermi Inc (FRMI) → removed
  - SanDisk/Kioxia note → split into **SanDisk `SNDK`** + **Kioxia `285A.T`**
  - WDC/Seagate note → split into **Western Digital `WDC`** + **Seagate `STX`**
  - Cerebras → removed
  - Sky Perfect → removed

### Key facts from exploration
- Vault: `/Users/kq/Documents/Jeff's database (claude sorted)`; home note is
  `Home.md` (capital H — we write that existing file).
- Companies are scattered across all 7 sector `*_database` trees, nested up to ~6
  levels, mixed with topic notes (`Networking.md`, `光模块.md`), sub-notes
  (`…transcript.md`), and private firms.
- Most titles already carry the ticker, incl. international: `英诺赛科 - 2577HK`,
  `SK Hynix - 000660 KR`, `Largan Precision - 3008 TW`, `Fujikura - 5803 JP`,
  `万泽 - 000534 CH`, `Silergy 6415 TT` (formats inconsistent).
- API Ninjas: key works; `/v1/earningscalendar` returns ~50 historical quarters and
  **no** future dates; `/v1/ticker` does ticker→name (verification) only — there is
  **no name→ticker search**. International needs exact suffixes (`6981.T` ✅;
  `6981.JP`/bare → `[]`).
- Many private companies (Anthropic, OpenAI, SpaceX, Anduril, Databricks, Helsing,
  Scale AI …) have no earnings → skipped.

## Revision 2 (post-review) — single "next earnings" view, sorted soonest-first

Jeff found the 4-column grid bloated and wants a leaner view:
- **One date column instead of four.** For each company, project forward from its
  historical pattern and show only the **nearest upcoming** estimated date (the
  earliest projected date that is ≥ today). Still marked `(est)`.
- **Sort the whole table by that date, ascending** (closest to present at the top),
  across all sectors — not alphabetical by company.
- Keep the existing column order with the **date on the right**:
  `Sector | Company | Ticker | Next earnings (est)`. Do NOT move the date to the left.
  With one row per company the table is now ~185 short rows, not bloated.
- Companies with no usable projection (e.g. INNIO) sort to the bottom with a blank
  date so nothing silently disappears.
- Same `Home.md` marker block is rewritten in place; footnote updated to say
  "next estimated earnings date per company, soonest first."

Implementation: reuse the existing `/tmp/earnings_grid.py`; change only the
projection-to-cells step (pick `min(projected dates ≥ today)`) and the render/sort
step. Re-run, rewrite the marker block, report summary.

## Revision 3 (post-review) — split into per-sector tables

Jeff wants the single soonest-first table broken into one table per vault sector.
- **One `### <Sector>` heading + table per sector**, in the vault's `Home.md`
  Sectors-list order, using the vault's display names:
  AI Hardware industry → Semi → Big Tech & CSPs → Aerospace & Defense → Software →
  Industrials Materials → Internet. **AI Application omitted** (no public companies).
- Map internal labels → vault names: `AI Hardware`→`AI Hardware industry`,
  `Big Tech`→`Big Tech & CSPs`, `Industrial & Materials`→`Industrials Materials`;
  the rest match.
- **Drop the now-redundant Sector column.** Each table: `Company | Ticker |
  Next earnings (est)`, rows sorted soonest-first within the sector (blank-date rows
  to the bottom).
- Keep the single nearest-upcoming `(est)` date per company from Revision 2.
- One shared "last updated / estimated" footnote after the last table.
- Same `Home.md` marker block rewritten in place; rest of note untouched.

Implementation: reuse `/tmp/earnings_grid.py`; change only the render step (group
`results` by sector, emit a heading+table per sector in the fixed order). Re-run.

## Approach (original 4-quarter build — superseded by Revisions 2 & 3)

### Step 1 — Resolve the company → ticker → exchange list (read-only)
1. Walk all 7 sector `*_database` trees.
2. Keep a note as a company candidate if its title matches `Name - TICKER` /
   trailing-ticker, **or** it's in a small built-in map of known no-ticker public
   names (Apple→AAPL, Google→GOOGL, Meta→META, Tesla→TSLA, Netflix→NFLX, TSMC→TSM,
   ASML→ASML, Samsung→005930.KS, …). Everything else → skipped (still listed).
3. Normalize the ticker from the title and map exchange code → API suffix:
   `HK→.HK`, `JP→.T`, `TW/TT→.TW`, `KR→.KS`,
   `CH→.SZ|.SS` (000/002/300→.SZ, 60→.SS), `GR→.DE`; US tickers pass through.
4. Verify each via `GET /v1/ticker?ticker=<norm>`; on failure try alternate
   suffixes; capture the official name for cross-check.
5. **Present to Jeff** a table: `Sector | Company | Ticker | Exchange | Verified name
   | Status` (ok / unverified / private / skip), plus the skipped/private lists.
   **STOP and wait for approval/corrections.** Messy titles
   (`Sandisk - SNDK Kioxia 285A JP`, `TTM Technologies - TTMI 迅达科技`) get fixed here.

### Step 2 — Fetch history & project (after approval)
1. Compute the 4 target calendar quarters from today (Q3 2026 … Q2 2027).
2. For each approved ticker: `GET /v1/earningscalendar?ticker=<t>` → past dates.
3. **Estimate engine:** group historical dates by calendar quarter; for each target
   quarter use the typical recent reporting window (most recent year in that slot,
   projected forward by ~364 days to preserve weekday; deeper history as fallback).
   No history in a slot → leave the cell **blank** (this is what correctly blanks
   semi-annual reporters' off-quarters). Format every value `~YYYY-MM-DD (est)`.
4. Robustness: per-ticker try/except; API errors / `[]` / bad tickers are skipped and
   collected; small delay between calls for rate limits.

### Step 3 — Write the grid into `Home.md`
- Render table sorted by sector then company:
  `Sector | Company | Ticker | Q3 2026 | Q4 2026 | Q1 2027 | Q2 2027`.
- Below it: `_Last updated: YYYY-MM-DD — all dates estimated from historical pattern._`
- Insert between `<!-- EARNINGS:START -->` and `<!-- EARNINGS:END -->` only (regex
  replace; rest of `Home.md` untouched). If markers are absent, append the section
  (with markers) to the end.
- Print a summary: # estimated, # blank, and the skipped/failed list with reasons.

### Implementation notes
- A throwaway Python 3 script (stdlib `urllib`/`json` only) written outside the repo
  (e.g. `/tmp`), run once; the API key is passed via an env var at run time — never
  hardcoded into a file and never committed. Deleted after.
- Nothing is committed unless Jeff asks.

## Verification
- Step 1: Jeff reviews the printed company→ticker→exchange list (esp. HK/JP/KR/TW/CN/DE
  suffixes verified, private/topic notes correctly skipped) and approves/corrects.
- Step 3: read back / `capture_editor_screenshot` of `Home.md` to confirm the table
  renders, markers wrap only that block, the rest of `Home.md` is intact, every date
  carries `(est)`, semi-annual names show expected blanks, and the timestamp is present.
  Spot-check 2–3 rows against the API history.
- Re-running rewrites only the marker block (idempotent).

## Open risks
- International suffix guesses (`.TW/.KS/.SZ/.SS/.DE`) are verified live in Step 1; any
  that don't resolve surface as `unverified` for Jeff to fix.
- A handful of messy titles need a manual ticker at the review gate.
- The API key was pasted in chat — it's only used transiently via env var, never
  written to a committed file; rotate if it was ever exposed elsewhere.
