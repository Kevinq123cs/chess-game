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
