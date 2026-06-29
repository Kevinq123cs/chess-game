# Plan: Finish converting Weichai vault notes → Excalidraw (RESUME)

## Context
User asked to convert every remaining note in the Obsidian vault folder
`/Users/kq/Desktop/Econ Learning/real world practical research/Weichai Power - 2338 HK/`
(7 top-level + 6 `sub-business/`) into its own Excalidraw board, same visual style as the
two existing boards, and place them in that folder's `excalidraw/` subfolder. The batch was
interrupted mid-way. This plan finishes it.

## Status
**Built & verified (in repo root, NOT yet in vault):**
weichai-power-overview · weichai-legacy-vs-growth-rally · weichai-bull-case-sizing ·
weichai-aidc-competitive-landscape · weichai-aidc-product-spec · weichai-us-global-strategy ·
weichai-questions-answers.
**Already in vault `excalidraw/`:** cat-cmi-genset-sotp · weichai-aidc-capex-landscape.

**Remaining 6 boards to build** (note → file):
- Powertrain - Engines → weichai-powertrain-engines.excalidraw
- Power & Energy - New Energy → weichai-power-energy-new-energy.excalidraw
- Powertrain - Components → weichai-powertrain-components.excalidraw  (small)
- Commercial Vehicles → weichai-commercial-vehicles.excalidraw  (small)
- Intelligent Logistics → weichai-intelligent-logistics.excalidraw  (small)
- Agricultural Equipment → weichai-agricultural-equipment.excalidraw  (tiny)

## Approach (per board)
Create empty `.excalidraw` in repo root → `excalidraw_add_elements` (color-coded panels:
grey title/section headers, folded notes inside each content box, generous box heights to
avoid the linter's auto-grow overflow) → `capture_editor_screenshot` to verify → fix only
gross overlaps (prefer `clear_all` + re-add over surgical moves; `update_element` newLabel
does not apply to container-bound text). Match the established palette
(blue=US/scale, red/orange=competitor, green=Weichai/thesis, yellow=headline, purple=SOFC).

## Final placement (decided: MOVE)
Move ALL Weichai boards (7 already built + 6 new) from repo root into
`…/Weichai Power - 2338 HK/excalidraw/`, removing them from the repo root (`mv`). The two
boards already copied into the vault (cat-cmi-genset-sotp, weichai-aidc-capex-landscape) stay;
just move the repo-root copy of weichai-aidc-capex-landscape out too (de-dup, overwrite).
End state: vault `excalidraw/` holds all 13 Weichai boards + cat-cmi-genset-sotp; repo root has
no `weichai-*.excalidraw` files left.

## Verification
`ls` the vault `excalidraw/` folder shows all 13 Weichai boards + cat-cmi-genset-sotp; open a
couple in the Nimbalyst editor to confirm they render.

---

# Plan: CAT vs CMI Genset SOTP Carve-out — Excalidraw Board

## Context

The user is researching the backup-diesel genset market and the public-equity angle on
its two leading suppliers, **Caterpillar (CAT)** and **Cummins (CMI)**. They have built a
segment-level financial model and asked me to use it as the **data backbone** for a
presentable Excalidraw visual.

Backbone file:
`/Users/kq/Desktop/Econ Learning/real world practical research/CAT_CMI_Backup_Genset_Model.xlsx`
(sheets: Cover, CMI Power Systems, CAT Power & Energy, Market & Comps, SOTP Carve-out).

Confirmed scope: the board centers on the **SOTP valuation story** — the carve-out chain
`reported base → diesel/recip share → carved revenue → EBITDA → implied genset EV`, plus
the multiple-sensitivity ladder and the Generac comp anchor, CAT vs CMI side by side.
(This supersedes the earlier "blank capacity & lead-times scaffold" — real data now exists.)

Outcome: a single, presentable `.excalidraw` board that tells the carve-out story at a
glance, with the model's key figures baked in and the editable assumptions visually flagged.

## Deliverable

New file: `cat-cmi-genset-sotp.excalidraw` at repo root
(`/Users/kq/Desktop/claudecode test/cat-cmi-genset-sotp.excalidraw`).

Built with the Excalidraw MCP tools (`excalidraw_add_frame`, `excalidraw_add_rectangle`,
`excalidraw_add_elements`, `excalidraw_add_arrows`, `excalidraw_add_row`/`add_column`).
Convention echoing the model: **blue** = editable assumption (share, margin, multiple),
**CMI = Cummins red**, **CAT = Caterpillar yellow**. As-of 2026-06-26, $mm.

## Data backbone (from SOTP Carve-out sheet)

| Step | Operation | Cummins (CMI) | Caterpillar (CAT) |
|---|---|---|---|
| Reported genset revenue base (FY2025) | — | 4,731 | 10,275 |
| Diesel/recip share *(blue)* | × | 100% | 60% |
| **Carved genset revenue** | = | **4,731** | **6,165** |
| EBITDA margin *(blue, est.)* | × | 24% | 24% |
| **Genset EBITDA** | = | **1,135** | **1,480** |
| EV/EBITDA multiple *(blue)* | × | 20× | 20× |
| **Implied genset EV** | = | **22,709** | **29,592** |
| Parent EV | ÷ | 105,144 | 486,898 |
| **Genset EV as % of parent** | = | **21.6%** | **6.1%** |

Multiple-sensitivity ladder — implied genset EV ($mm):

| Multiple | CMI | CAT |
|---|---|---|
| 14× | 15,896 | 20,714 |
| 16× | 18,167 | 23,674 |
| 18× | 20,438 | 26,633 |
| **20× (base)** | **22,709** | **29,592** |
| 22× | 24,980 | 32,551 |

Comps anchor (Market & Comps sheet, EV/EBITDA): **GNRC 19.3× · CMI 19.5× · CAT 29.5×**;
multiple anchored to Generac (~18–19×), conservative diversified-industrial 12–15× shown
in the ladder.

## Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ SOTP CARVE-OUT · Backup-Diesel Genset Business — CAT vs CMI   $mm · as-of 26 Jun 2026 │
├────────────────────────────────┬─────────────────────────────────────┤
│  CUMMINS (CMI)  [red]          │  CATERPILLAR (CAT)  [yellow]        │
│  Reported base      4,731      │  Reported base       10,275         │
│        │ ×100% (blue)          │        │ ×60% (blue)                │
│  Carved revenue     4,731      │  Carved revenue       6,165         │
│        │ ×24% margin (blue)    │        │ ×24% margin (blue)         │
│  Genset EBITDA      1,135      │  Genset EBITDA        1,480         │
│        │ ×20× mult. (blue)     │        │ ×20× mult. (blue)          │
│  IMPLIED GENSET EV 22,709      │  IMPLIED GENSET EV   29,592         │
│        ÷ parent EV 105,144     │        ÷ parent EV   486,898        │
│  = 21.6% of parent             │  = 6.1% of parent                  │
├────────────────────────────────┴─────────────────────────────────────┤
│  SENSITIVITY LADDER (14–22×)        │  COMPS ANCHOR                   │
│  14× 15,896 / 20,714                │  GNRC 19.3×  CMI 19.5×  CAT 29.5×│
│  …  20× base row highlighted        │  anchor: Generac ~18–19×        │
│  22× 24,980 / 32,551                │                                 │
├──────────────────────────────────────────────────────────────────────┤
│  ASSUMPTIONS / CAVEATS (sticky): CMI base = FY2025 power-gen quarters, │
│  ~100% gensets (mostly diesel). CAT base = Power Generation app FY2025,│
│  includes Solar gas turbines → recip/diesel share assumed 60%. EBITDA  │
│  margins are estimates (segment ~20–22%; genset/DC mix assumed 24%).   │
└──────────────────────────────────────────────────────────────────────┘
```

### Elements to create
1. **Title band** — full width, with $mm / as-of date subtitle.
2. **Two carve-out flow columns** (CMI left = red header, CAT right = yellow header). Each
   is a vertical waterfall of 5 value boxes connected by downward arrows; each arrow is
   labeled with its operation (`×100%`, `×60%`, `×24%`, `×20×`, `÷ parent EV`). The three
   assumption operations are tinted **blue** to flag editability. The "Implied genset EV"
   box is emphasized (bold/larger). End each column with the "% of parent EV" result chip.
3. **Sensitivity ladder** (bottom-left) — a 3-column mini table (Multiple | CMI | CAT) via
   `excalidraw_add_row`, with the **20× base row highlighted**.
4. **Comps anchor** (bottom-right) — three chips GNRC/CMI/CAT EV/EBITDA + an anchor note.
5. **Assumptions/caveats sticky** (bottom strip) — the carve-out caveats verbatim-ish.

### Styling
Rounded rectangles, light fills so numbers read clearly; align CMI and CAT rows
horizontally so each carve-out step reads straight across; consistent box sizing.

## Files
- **Create:** `cat-cmi-genset-sotp.excalidraw` (repo root) — only file changed.
- **Read-only backbone:** the `.xlsx` model (not modified). No edits to `ai-capex.html`.

## Verification
1. Open `cat-cmi-genset-sotp.excalidraw` in the Nimbalyst editor.
2. `capture_editor_screenshot` to confirm: title band, two aligned carve-out columns with
   labeled blue assumption arrows, emphasized implied-EV boxes + % chips, the highlighted
   20× sensitivity row, comps chips, and the caveats sticky.
3. Spot-check numbers against the table above (e.g. CMI EV 22,709 / CAT EV 29,592; % of
   parent 21.6% / 6.1%) and confirm elements are individually movable/editable.

## Follow-up (later, user-driven)
If wanted, add the demand-side context (capacity 35→55GW, backlog, DC orders) or a second
board for the segment revenue trends. Out of scope for this pass.

## Commit
Per repo `CLAUDE.md`: after creating the file, commit and push to `origin main`
(e.g. `feat: add CAT/CMI genset SOTP carve-out Excalidraw board`).
