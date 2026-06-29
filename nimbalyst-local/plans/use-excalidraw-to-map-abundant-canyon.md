# Map Weichai Holding Group relations in Excalidraw

## Context
You want a **rough first-pass sketch** of how Weichai Holding Group is connected — its
parent, its flagship listco, and the major operating subsidiaries / brand stakes — so you
can react and then give more specific instructions. This is intentionally a draft layout,
not a polished final. Stake percentages below are approximate and labeled as such; we'll
tighten them once you tell me the direction (e.g. focus on the powertrain stack, the
overseas M&A web, or the full SHIG sibling tree).

## Proposed structure (top → bottom org tree)

**Tier 0 — Ultimate owner**
- Shandong State-owned Assets (Shandong SASAC) → **Shandong Heavy Industry Group (SHIG)**

**Tier 1 — Weichai Holding Group** (core subsidiary of SHIG)

**Tier 2 — Weichai Power** (HK 2338 / SZ 000338) — flagship listed vehicle, plus
direct Holding-Group brands that sit beside it.

**Tier 3 — operating subsidiaries / stakes**, grouped by cluster:
- *Powertrain (China):* Weichai diesel engines · Fast Gear (transmissions) · Hande Axle
- *Commercial vehicles:* Shacman / Shaanxi Heavy-Duty Auto
- *Overseas M&A:* KION Group (Germany, ~46%) → Dematic + Linde Material Handling ·
  Linde Hydraulics (Germany, ~70%) · Baudouin (France, marine) · PSI / Power Solutions
  International (US) · VM Motori (Italy)
- *New energy / fuel cells:* Ballard Power (Canada) · Ceres Power (UK)
- *Other Holding-Group brands:* Ferretti (Italy, yachts, ~75%) · Weichai Lovol Smart
  Agriculture · Torch (spark plugs)

**Side cluster — SHIG sibling listcos** (controlled by SHIG, *not* under Weichai Holding;
drawn off to the side to show the broader group): Sinotruk / China National Heavy Duty
Truck · Weichai Heavy Machinery (000880) · Yaxing Bus (600213) · Shantui (000680)

## Visual approach
- New file: `weichai-holding-group-relations.excalidraw` in the workspace root.
- Top-down hierarchy, solid arrows = control/ownership, parent → child.
- Light color-coding by cluster (China powertrain, overseas M&A, new energy, other brands,
  SHIG siblings) so the relationship types read at a glance.
- Approximate stake % shown as small labels on the ownership arrows where known.
- One screenshot to confirm it rendered, then hand back for your next instructions.

## Verification
- Open the `.excalidraw` file and capture a single editor screenshot to confirm the tree
  renders and is legible.

## Sources (for accuracy of the relations)
- [Weichai Group — Wikipedia](https://en.wikipedia.org/wiki/Weichai_Group)
- [Shandong Heavy Industry — Wikipedia](https://en.wikipedia.org/wiki/Shandong_Heavy_Industry)
- [Weichai Power — Wikipedia](https://en.wikipedia.org/wiki/Weichai_Power)
- [Weichai Group — Our Brands](https://m.en.weichai.com/our_group/our_brands/)

## Open question for you
This first sketch shows the **full group tree**. Once you see it, tell me if you want to
narrow focus (e.g. just Weichai Power's subsidiaries, or just the overseas acquisition web)
or add detail (exact stakes, listing tickers, revenue/segment tags).

## Correction round — sibling-row ownership fix (approved)
Verified via sources that **SHIG is the parent of Weichai Holding** (largest wholly-owned
subsidiary) — the vertical spine is correct. But the "SHIG sibling" listco row had errors.
Approved approach = "Recommended fix":

1. **Reclassify Weichai Heavy Machinery (000880).** It sits *under* Weichai Holding (it was
   restructured by Weichai Holding in 2006), not beside it. Actions:
   - Remove the `SHIG → Weichai Heavy Machinery` arrow (arrow id
     `arrow-1782702868064-5eeakv2ab`).
   - Move the box from the left SHIG-sibling column to a position under the Weichai spine
     (approx `x=560, y=395`, left of Weichai Power), and recolor it to the Weichai-family
     blue (`#a5d8ff`) to signal it's now in the Weichai sub-tree.
   - Add arrow `Weichai Holding Group → Weichai Heavy Machinery (000880)`.
2. **Keep Sinotruk & Shantui** as genuine SHIG-level siblings (confirmed). Re-space the left
   column (Sinotruk, Yaxing, Shantui) so there's no gap where 000880 was.
3. **Yaxing Bus (600213):** keep as a SHIG-level sibling but annotate it — update the box
   label to flag the nuance, e.g. `Yaxing Bus (600213) — legally SHIG / ops Weichai`.

### Verification
- After edits, capture a single editor screenshot of
  `weichai-holding-group-relations.excalidraw` and confirm: (a) 000880 now branches off
  Weichai Holding, (b) only Sinotruk/Shantui/Yaxing remain in the SHIG sibling column,
  (c) Yaxing carries the nuance tag, (d) no dangling/overlapping arrows.

### Sources for the correction
- [Shandong Heavy Industry — Wikipedia](https://en.wikipedia.org/wiki/Shandong_Heavy_Industry)
- [Weichai Holding Group — Baidu Baike (EN)](https://baike.baidu.com/en/item/Weichai%20Holding%20Group%20Co.,%20Ltd./929404)
- [China National Heavy Duty Truck Group (Sinotruk) — Wikipedia](https://en.wikipedia.org/wiki/China_National_Heavy_Duty_Truck_Group)
