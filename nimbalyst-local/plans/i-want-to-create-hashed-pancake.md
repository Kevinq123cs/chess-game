# Plan: AI Data Center Capex — Interactive Comparison App (Part 1)

## Context

You want to build an app that visually presents company data, assembled **in parts**.
Part 1 is **AI data center capex** compared across several companies for **2024,
2025, 2026, and 2027e**. The app must show your reference figures *and* let you
override any number on the fly "for your own reference."

Decisions locked in from our Q&A:
- **Scope:** compare several companies (e.g. the hyperscalers — MSFT, GOOGL, AMZN, META) side by side.
- **Data source:** you feed the reference numbers; they are hardcoded as the baseline.
- **Overrides:** edit numbers live in the session; **a reload restores the reference baseline** (no localStorage). A "Reset" button reverts immediately without reloading.
- **Primary visual:** grouped bar chart.

This is Part 1 of a larger app, so the structure must make it cheap to **add more
sections/datasets later** (other metrics, other views) without a rewrite.

## Approach

Build a **single self-contained HTML file** — HTML + CSS + vanilla JS, **no build
step, no external dependencies**, runnable by double-clicking. This matches the
existing precedent in this repo, [chess.html](/Users/kq/Desktop/claudecode%20test/chess.html)
(self-contained, dark-themed, zero dependencies, works offline forever).

The grouped bar chart is **hand-rolled in SVG** — no Chart.js/CDN — so the app stays
fully offline and every pixel is under our control for the "tweak after" phase.

**File:** `ai-capex.html` at the repo root (alongside `chess.html`).

### Data model (top of the `<script>`, the only thing you edit to feed data)

```js
const UNITS = '$B'; // US$ billions
const YEARS = ['2024', '2025', '2026', '2027e']; // '2027e' rendered as an estimate
const REFERENCE = [
  { name: 'Microsoft', color: '#4C8BF5', capex: { '2024': null, '2025': null, '2026': null, '2027e': null } },
  { name: 'Alphabet',  color: '#34A853', capex: { '2024': null, '2025': null, '2026': null, '2027e': null } },
  { name: 'Amazon',    color: '#FF9900', capex: { '2024': null, '2025': null, '2026': null, '2027e': null } },
  { name: 'Meta',      color: '#C74FE8', capex: { '2024': null, '2025': null, '2026': null, '2027e': null } },
];
```

`null` values render as a "placeholder" baseline so the app is **runnable immediately**;
the first task once you send numbers is to fill these in. Adding a company = one array
entry. A future Part 2 = a second `REFERENCE`-style block + a second render call —
the render functions stay pure and reusable.

### State & editing

- On load, deep-copy `REFERENCE` into `state` (the live, editable copy).
- The chart reads from `state`. Editing a table cell updates `state` and re-renders the chart **live**.
- **Reset** button: `state = deepCopy(REFERENCE)` + re-render. (No reload needed.)
- Reload = fresh copy of `REFERENCE` ⇒ overrides discarded, per your choice.

### Layout (top → bottom)

```
┌─────────────────────────────────────────────────────────────┐
│  AI Data Center Capex            units: $B      [ Reset ]     │  header
│  Reference vs. your overrides · 2024–2027e                    │
├─────────────────────────────────────────────────────────────┤
│   ▆                                                           │
│   ▆ ▆        ▆ ▆            ▆ ▆ ▆          ▆ ▆ ▆ ░  ← grouped │  SVG chart
│   ▆ ▆ ▆ ░    ▆ ▆ ▆ ░        ▆ ▆ ▆ ░        ▆ ▆ ▆ ░    bars    │  (hero)
│   2024        2025           2026           2027e             │
│   ● Microsoft  ● Alphabet  ● Amazon  ● Meta   (legend)        │
├─────────────────────────────────────────────────────────────┤
│  Editable table  (click any cell to override)                │
│  Company    2024    2025    2026    2027e                     │
│  Microsoft  [   ]   [   ]   [   ]   [   ]                      │  editable
│  Alphabet   [   ]   [   ]   [   ]   [   ]                      │  inputs
│  ...                                                          │
│  Total      —       —       —       —                         │  computed row
└─────────────────────────────────────────────────────────────┘
```

### Visual style spec
- **Theme:** dark, matching `chess.html` — bg `#1a1a2e`, light text `#eee`, `Segoe UI` font, generous letter-spacing on the title.
- **Bars:** per-company colors (above); rounded tops; a subtle hover that shows the exact value as a tooltip/label.
- **2027e = estimate:** rendered distinctly (translucent fill + hatched/dashed outline) and labeled "e", so the estimate is never confused with actuals.
- **Y-axis:** auto-scaled to the max value across `state`, with light gridlines and `$B` labels.
- **Edited cells:** highlighted (e.g. amber border) so you can see at a glance which numbers differ from the reference baseline.
- **Empty/placeholder (`null`):** drawn as a faint outlined "ghost" bar so the structure is visible before data is entered.

### Render functions (kept pure & small, for reuse in later parts)
- `renderChart(svgEl, dataset, years)` — draws the grouped SVG bar chart.
- `renderTable(tableEl, dataset, years, onEdit)` — builds editable inputs + computed Total row.
- `scaleY(value, maxValue, height)` — axis math.
- `deepCopy(dataset)` — baseline ↔ state isolation.

## Files to create
- `ai-capex.html` (repo root) — the entire app (HTML + CSS + JS in one file).

## Verification
1. Open `ai-capex.html` in a browser (I'll use the browser/preview MCP tools to load it and screenshot the result for you).
2. Confirm: grouped bars render for all four years; legend matches colors; **2027e bars look like estimates**; placeholder/ghost bars show where data is missing.
3. Edit a table cell → chart updates **live**; the edited cell is highlighted.
4. Click **Reset** → values + chart revert to the reference baseline.
5. Reload the page → overrides are gone (baseline restored), per your choice.
6. I'll share a screenshot inline so we can iterate on colors/layout/labels — the "tweak after" phase.

## Next step after you approve
You send me the 2024/2025/2026/2027e capex numbers (and which companies you want);
I populate `REFERENCE`, then screenshot the result so we can tweak the design.

---

# Update — Fix colo double-counting (genset section)

## Context
The genset-spending donuts (added last) currently derive **T3b Colo capex** as
`Math.max(0, Tier3_total − China)` — see `ai-capex.html:548`. That is wrong in two ways:
1. **Oversized.** It treats the *entire* Tier-3 remainder (sovereign + enterprise + colo)
   as colo — ~$96bn for 2027e. Real colo (Equinix + Digital Realty) is only ~$6–12bn/yr.
2. **Double-counts.** Colo capex overlaps the other tiers: when a hyperscaler leases
   capacity from Equinix, the *shell/power* (incl. gensets) is the colo's capex while the
   GPUs are the tenant's. So colo cannot be cleanly **added** on top of the Big-4 number —
   it's the same physical data center counted twice.

User decisions: **(a)** colo becomes a **memo, outside the donut total**; **(b)** colo is
scoped to **Equinix + DLR only**.

## Approach (single file: `ai-capex.html`)

**1. Main donut = cleanly additive only.** Reduce `GENSET_CATS` (currently 4, at
`ai-capex.html:544–549`) to the three owned-facility categories: **T1 Big-4, T2
Oracle/neocloud, T3a China**. `gensetYearTotal()` (`:553`) then sums only these, so colo
is automatically excluded from the headline total. New totals: ~**8.1 → 12.8 → 22.4 → 29.5 $B**.

**2. Colo as an explicit, separate memo.** Replace the `t3b` derived entry with a standalone
object plus an explicit, editable capex base (rough Equinix + DLR combined):
```js
const COLO_REF = { '2024': 6, '2025': 8, '2026e': 10, '2027e': 12 }; // US$bn, editable
const COLO = { key:'colo', name:'Colo (Equinix/DLR)', color:'#2DD4BF', pct:6.5, range:[5,8],
               memo:true, capex:(k) => COLO_REF[k] };
```
Colo genset memo $ = `COLO_REF[k] × pct/100` ≈ **0.4 → 0.8 $B/yr** (small, honest).
Remove the now-unused `CHINA_REF`-minus logic; `T3a China` keeps using `CHINA_REF` (`:543`).

**3. Render the memo beside each donut.** In `renderDonuts()` (`:~600`), draw **3 slices**
(the additive cats) and add a small caption under each donut card, below the year/badge,
e.g. `colo memo · +0.8` in colo teal — clearly *separate* from the centered total. Add a
`<title>`/footnote explaining colo overlaps other tiers and is not added in.

**4. Keep colo share editable.** Build a combined `SHARE_CATS = [...GENSET_CATS, COLO]` used
only by `renderGensetAssumptions()` (`:555`), `isDirty()` (`:527`) and the **Reset** handler
(`:533`) so the colo share input, its edited-highlight, and reset all keep working. The
assumptions row labels colo **"Colo (Equinix/DLR) · memo"**. `SHARE_BASE` replaces
`GENSET_BASE` for baseline/reset comparison.

**5. Legend + copy.** Genset legend lists the 3 additive categories; colo shown with a
distinct **"(memo)"** marker. Update the section footnote to state plainly: *colo overlaps
the other tiers (leased capacity) and is shown separately, not summed, to avoid
double-counting.*

## Reuse / touch points
- `gensetVal()` (`:552`) is reused unchanged for both slices and the colo memo.
- `renderDonuts`, `renderGensetAssumptions`, `isDirty`, reset handler, and `renderAll`
  (`:~640`) are the only functions touched; data-model edits are localized to
  `ai-capex.html:543–550`. No change to the bar chart or tier table.

## Verification
1. Reload `ai-capex.html` in the browser preview (MCP `browser_navigate` + `browser_evaluate`).
2. Assert via `browser_evaluate`: donuts now have **3 slices** each; `gensetYearTotal` =
   ~8.1 / 12.8 / 22.4 / 29.5; colo memo = ~0.4 / 0.5 / 0.65 / 0.8; colo is **not** in the total.
3. Edit a tier total (e.g. Tier 1 2027e) → the 3-slice donut + total update; colo memo
   unaffected (depends on `COLO_REF`, not tiers) — confirming the overlap is broken.
4. Edit the colo share → memo updates, headline total does **not**.
5. **Reset** → shares + tiers revert; screenshot the genset section inline for review.

---

# Update 2 — Replace "Data & overrides" table with a per-tier player rundown

## Context
The "Data & overrides" table just restates numbers the bar chart already shows, and the
tier-override workflow is no longer used — it's bloat. Replace it with a lean, descriptive
**player rundown**: each player gets a one-line profile and a **rough % contribution band**
(its share of global capex, low–high across 2024–2027e), kept **grouped by tier** so the
tier structure stays concrete. No editable numbers remain in this section.

## Approach (single file: `ai-capex.html`)

**1. HTML — swap the panel** (`ai-capex.html:173–178`). Replace the table panel with:
```html
<section class="panel">
  <div class="table-title">Who's who — players by tier</div>
  <div class="table-sub">Each player with a one-line profile and a rough share of global
    AI capex (low–high across 2024–2027e). Grouped by tier.</div>
  <div id="tier-rundown"></div>
</section>
```

**2. Data — add editorial copy to `TIERS`** (`ai-capex.html:~ TIERS def`). Add a `who` field
per tier and a `desc` per player:
- T1 *Mega-cap US hyperscalers — defined by sheer spend.* — Amazon "AWS; biggest single
  AI/cloud capex budget" · Microsoft "Azure + OpenAI buildout" · Alphabet "Google Cloud,
  TPU + DeepMind infra" · Meta "owned AI infra for ads + Llama".
- T2 *Oracle + the neocloud builders — the next rung down.* — Oracle "OCI GPU clouds;
  Stargate partner" · CoreWeave "pure-play GPU neocloud, fastest riser" · Other neoclouds
  "Nebius, Lambda, Crusoe, IREN".
- T3 *Everything smaller — China, sovereign, enterprise, colo.* — Chinese Big-4 "Alibaba,
  Tencent, ByteDance, Baidu" · Sovereign+enterprise+colo "gov clouds, on-prem, Equinix/DLR".

**3. JS — new `renderTierRundown()` replaces `renderTable()`.** For each tier: render a
header (tier name + `who` + the tier's combined share band), then a clean **list** of
players in the compact inline form **`Amazon (20–24%)`** — bold name + parenthesised
low–high band, with the one-line `desc` as muted text after a dash (no columns, no
right-aligned cells). Compute the contribution band from midpoints:
```js
function shareBand(valsByYear) {            // valsByYear: player.vals or tier totals
  const ps = [];
  YEARS.forEach(y => {
    const v = valsByYear[y.key];
    const m = Array.isArray(v) ? (v[0]+v[1])/2 : (typeof v === 'number' ? v : null);
    const g = yearTotal(y.key);             // reuse existing global-total fn (:~tier stack)
    if (m != null && g > 0) ps.push(m / g * 100);
  });
  return ps.length ? [Math.min(...ps), Math.max(...ps)] : null;   // string cells skipped
}
```
Format: `<1%` when below 1, else whole %, collapse to one number when low≈high. Expected
bands: T1 ~73–78% (A ~20–24 · MS ~17–24 · GOOG ~16–20 · Meta ~12–14); T2 ~3–12%
(Oracle ~2–7 · CoreWeave ~2–4 · other ~2); T3 ~15–19% (China ~7–13 · sovereign/colo ~6–9).
Reuse existing `yearTotal()`.

**4. Remove now-dead code.** Delete `renderTable()` (`:441–514`), `renderTotals()`
(`:519–524`), `markEdited()` (`:516–518`), the unused `BASELINE` const, and the
`renderTable();` call in `renderAll()` (`:681` → `renderTierRundown()`). Simplify
`isDirty()` (`:527`) and the **Reset** handler (`:533`) to genset shares only
(`SHARE_CATS`/`SHARE_BASE`) since tier totals are no longer editable; keep
`state = buildState()` for genset's capex reads.

**5. CSS.** Add a small ruleset for the rundown: `.tier-group` header (colored dot + tier
name + muted `who` + share band), and `.player-line` rendered inline as
`<b>Amazon (20–24%)</b> — <span muted>desc</span>` — a simple stacked list, NOT a grid
(this is the readability fix the user asked for). Remove table-only rules
(`tr.tier-row`, `td.tier-name`, `.tier-dot`, `.tier-access`, `tr.player-row`,
`td.player-name`, `tr.total-row`, `.range-hint`, `.conf-badge`, bare `table/th/td`).
**Keep** shared rules: `.table-title`, `.table-sub` (genset panel), `input.cell`
(genset inputs), `.conf-chip` (chart + donut badges).

## Reuse / touch points
- Reuse `yearTotal()` (global total per year) and `formatNum()`.
- Bar chart, genset donuts, and `state`/`TIERS`/`buildState()` are otherwise untouched —
  genset still reads `state[i].vals`, which stays at baseline (no editing).

## Verification
1. Reload preview; assert `#table` is gone and `#tier-rundown` renders 3 tier groups with
   9 player lines; no console errors.
2. Spot-check bands via `browser_evaluate` (e.g. Amazon ~20–24%, Meta ~12–14%, Oracle ~2–7%).
3. Confirm bar chart + genset donuts still render and compute (`gensetYearTotal` unchanged
   at ~8.1/12.8/22.4/29.5); **Reset** still works for genset shares.
4. Screenshot the new section inline for review.

---

# Update 3 — Genset section: macro reframe, colo back in the pie, section-level Reset

## Context
Three asks for the genset section: **(1)** reframe it as **macro** (drop the "Weichai TAM"
language — Weichai comes later); **(2)** bring **colo back into the pie as a 4th, distinctly
coloured slice that IS summed into the total** — T3a China and colo stay separate categories
(they're fundamentally different), and the small double-count is acceptable because both are
tiny; **(3)** give the pie section its **own Reset** so tweaking a share updates the donuts
but can be reverted to the original data. This reverses Update 1's "colo = memo" treatment.

## Approach (single file: `ai-capex.html`)

**1. Colo becomes a 4th additive category.** In the genset config (`ai-capex.html:491–506`):
- Fold colo into `GENSET_CATS` as a 4th entry (keep its `COLO_REF` base `:488` and teal
  `#2DD4BF`, which is already distinct from the blue/orange/purple tiers):
  `{ key:'colo', name:'Colo (Equinix/DLR)', color:'#2DD4BF', pct:6.5, range:[5,8], capex:(k)=>COLO_REF[k] }`.
- Delete the standalone `const COLO` (`:498`), `SHARE_CATS`/`SHARE_BASE` (`:501–502`), and
  `coloMemo` (`:506`). Add `const GENSET_BASE = GENSET_CATS.map(c=>c.pct);`.
- `gensetYearTotal` (`:505`) now sums all four (colo included) — no code change beyond the
  array; new totals ≈ **8.5 / 13.3 / 23.0 / 30.3 $B**.

**2. Remove the memo UI.** In `renderDonuts` (`:567`) delete the `dc-memo` caption block
(`:603–608`); the 4th slice now appears in the ring automatically. In `renderGensetLegend`
(`:543`) drop the separate dashed "(memo — not in total)" entry (`:552–557`) so the loop
over `GENSET_CATS` renders all four normally. In `renderGensetAssumptions` (`:508`) drop the
`· memo` tag (`:515`) and swap `SHARE_CATS`/`SHARE_BASE` → `GENSET_CATS`/`GENSET_BASE`. Delete
the now-unused `.dc-memo` / `.memo-dot` CSS (`:134–135`).

**3. Section-level Reset (replaces the header Reset).** The header `#reset` (`:147`) is now
the *only* global control and it only resets genset shares — move it into the genset panel:
- Remove `<button id="reset">` from the header (`:147`).
- In the genset panel (`:166–172`), put the title in a flex row with a `#genset-reset`
  button: `<div class="gs-head"><div class="table-title">…</div><button id="genset-reset"
  class="btn-reset" disabled>Reset</button></div>`.
- Reuse the existing reset button styling: rename CSS selector `button#reset` → `.btn-reset`
  (find in the header CSS block) and add `.gs-head{display:flex;justify-content:space-between;
  align-items:center;gap:16px;}`.
- Rewire `isDirty`/`updateResetState`/handler (`:472–480`): compare `GENSET_CATS` vs
  `GENSET_BASE`, target `el('genset-reset')`, and on click reset pcts + re-render just the
  genset bits (`renderGensetAssumptions(); renderDonuts(); updateResetState();`).

**4. Macro copy.** Retitle `:167` "Genset spending — Weichai TAM" → **"Genset spending"**;
rewrite the subtitle `:168` to macro framing ("Backup-power (genset) slice of data-center
capex = capex × genset share; donut centre = each year's total; shares are editable
assumptions, midpoints of the source ranges"). Replace the Weichai/memo footnote `:172` with
a short macro note: colo (Equinix+DLR) capex partly overlaps the hyperscaler tiers but is
small, so it's included as its own slice; edit a share to update the pies, Reset restores
originals. (The tier-chart legend's "where Weichai captures full value" at `:224` is left
as-is — out of scope; Weichai layer comes later.)

## Reuse / touch points
- Reuse `gensetVal`, `donutArc`, `renderDonuts`, `formatNum`, and the existing
  `.ga-*` / `.gl-*` / `.donut-card` CSS. Only the genset block + header button change.
- Post-change: update the `capex-app-purpose` memory to note the genset view is now macro
  (Weichai is a future layer), done during implementation (not in plan mode).

## Verification
1. Reload preview (`browser_navigate` + `browser_evaluate`).
2. Assert: each donut has **4 slices**; `gensetYearTotal` ≈ 8.5 / 13.3 / 23.0 / 30.3; no
   `.dc-memo` nodes; legend has 4 items incl. colo; header has no `#reset`, panel has
   `#genset-reset`.
3. Edit a share (e.g. colo 6.5→8) → donuts + total update, `#genset-reset` enables; click
   **Reset** → shares revert to base and donuts return to 8.5/13.3/23.0/30.3.
4. Confirm bar chart + player rundown unchanged. Screenshot the genset section inline.
