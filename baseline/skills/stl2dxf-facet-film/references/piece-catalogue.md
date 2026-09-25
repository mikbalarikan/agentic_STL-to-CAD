# Piece catalogue — the worked facet-film kits

All dimensions mm, measured from the captured STEP artifacts / delivered DXFs
(not nominal). Kits 1–2 are usable as templates for new watches **and** as
regression fixtures when re-running the same scans (`STL Library for Tests`:
`Daytone 126500 v2.stl`, `228235.stl`). **Kit 3 (126713GRNR) is a record in
progress** — inventory and method evidence only, never a fixture: no DXF exists
and its final state was saved after the capture ended.

> **Ruling namespace.** `NXLEARN-228235 Rn` = **decided 2026-09-05**, a rule (Kit 2);
> `NXLEARN-126713 Rn` = **still open**, so the Kit-3 default it guards is PROVISIONAL. Bare
> **R1/R2/R3 are record labels** (Daytona / Day-Date / GMT-Master), never ruling ids.

## Recipe classes

| class | construction | development |
|---|---|---|
| A planar | fitted/typed outline + clearance, face made directly in 2D | none needed |
| B prismatic | mid-plane profile spline × extrusion along facet axis | analytic (arc-length × span) |
| C ruled | ruled sheet between two boundary splines, ends trimmed by closing-curve cutters | strip unroll (gate K, ΔA, Δedge) |
| N curve-network | Coons patch through 2 primary + 2 cross curves with exactly coincident corners (NX "Through Curve Mesh"); for facets whose transverse ends are themselves curved | **LSCM** — the patch is not ruled, so strip unroll is 8 % wrong in area |
| D patterned | one class-B/C template + measured pitch + per-instance trim | as template |

## Kit 1 — Daytona 126500 (R1; delivered RV02 = 67 pieces, 24 distinct shapes, sheet 123 × 85 mm, 4114 mm²)

| piece (suggested id) | class | n | size / area | construction facts | notes |
|---|---|---|---|---|---|
| BEZ_TOP (annulus) | A | 1 | Ø38.80/Ø30.00, 475 mm² | typed circles | slope not developed (simplification) |
| CRYSTAL | A | 1 | Ø29.30, 674 mm² | Ø30 − 2×0.35 clearance | nests inside BEZ_TOP hole (0.35 gap) |
| CASEBACK | A | 1 | Ø26.54, 553 mm² | fitted edge arc R13.469 − 0.2 | 3-point circle on flat-centre boundary |
| LINK_C_* centre links | B/D | 10 | 7.315 × 8.75, 64.0 mm² each | profile y=0 × span −3.7…+5.05 | DXF = exact rectangle, pitch 11.0 (bodies ~10.25 mesh pitch); top face only, 1.4 mm bevels dropped |
| LINK_O_* outer links | B/D | 20 | 7.4–7.5 × 4.88/4.25/3.81/3.30 (4 size classes) | profile y=∓7/+6 × spans −2…+2.55 / −3.1…+1.7; extrude dir = fitted side-plane normal (taper 4–5° links 1–2 only) | per-link width re-trim; end link length-trimmed to 9.0 |
| FLANK_9 (lug-to-lug) | C | 1 | 49.0 × 7.1, 244 mm² | ruled, 46.9 mm lug tip to lug tip, K̄ 5.7e-4 | closes only at 0.06 mm (defect); 3 ref POINTs nearby |
| FLANK_3_* crown-side | C | 2 | 14.98 × 6.48, 66.7 mm² | ruled + pusher-end closing spline cutter (−4.5…+5.9, dir = fitted pusher plane normal) | mirror pair |
| LUG_SIDE_* | C | 4 | 5.02 × 13.93, 31.6 mm² (DXF) / 32.9 (sheet) | ruled; arcs R22.4/38.6/52.1/64.8 in DXF | redrawn ~0.7 mm smaller in sketch |
| LUG_INNER_* | C | 4 | 7.8 × 4.7, 30.7 mm² | ruled between lug-edge splines | faces the end-link gap |
| LUG_END_* (between lugs) | B | 2 | 7.70 × 7.00, 53.9 mm² | one profile spline extruded 7.7 across the gap | exact development |
| LUG_UNDER_* | C | 4 | 4.29 × 2.11, 6.6 mm² | 2-point splines (lines) → ruled | worst ΔA 0.38 % |
| GUARD_* crown guards | C | 2+2 | 22.8 and 13.9 mm² | ruled; K̄ up to 1.4e-2 (gate-defining piece) | mirror pairs |
| PUSHER_RECT_* | A | 2 | 5.75 × 3.75, 21.6 mm² | typed rectangles on z=0 | |
| CROWN_FLANK (logo) | A | 1 | 5.7 × 8.3 − logo, 28.7 mm² | section outline projected + fit + 0.15 offset | 36-pole spline survives in DXF |
| CLASP_COVER | B | 1 | 23.2 × 7.6, 166 mm² | profile × (−4.1…+3.5), ends trimmed by 2 spline cutters (−6…+3.5) | |
| CLASP_* others | B/A | 1+2+2+2 | 5.44 × 8.25 / 4.84 × 2.8 ×2 / 44.7 mm² ×2 / 13.2 ×2 | extrudes 8.25 and 4.6…7.4 spans; ruled clasp sides nearly planar | |
| HORN_* lug outer flanks | ? | 4 | ~11.8 × 6.6, 25.3 mm² | added 08-20, source unrecorded | delivered OPEN (0.715 mm) with 0.73 mm tip — the defect archetype. **Same facet as Kit 3's `LUG_SHOULDER` (recipe N)**: R3 is the first record that shows one being built. Whether it belongs in a kit at all is **NXLEARN-126713 R1 (open)** |

## Kit 2 — Day-Date 40 (ref 228235; the STL-library README mislabels it Sky-Dweller) (R2; **delivered 2026-08-30: 58 pieces, 3 180.6 mm² net film, sheet 63 × 160 mm**)

Corrected 2026-09-05 (NXLEARN-228235) from the delivered `228235STL Converted.dxf`
and the two 08-30 capture sessions — the earlier "3D pieces complete, kit never
flattened in-record" reading is wrong. "delivered" columns are arc-exact
measurements of that DXF; see `e2e-228235-manual-diff.md`. Corner fillets in the
delivered kit are **R 0.3 on 206 of 217 sub-2 mm arcs (95 %)** with **R 0.4 only
on the two flank pieces** — that split is now the rule: **R 0.3 on links, lugs
and tabs, R 0.4 on long flank pieces** (maintainer ruling 2026-09-05, **NXLEARN-228235 R7**; R 0.2
stays rejected). Rows below are **measurements of the delivered kit**; where a
2026-09-05 ruling differs (BEZEL, FLANK_3C, LINK, lug templates) the ruling is
the rule and the measured number is only a fact about that one kit.

| piece | class | n | delivered flat dims / area | construction + provenance |
|---|---|---|---|---|
| BEZEL (annulus) | A | 1 | **Ø35.50 / Ø29.85, 290.0 mm²**, width 2.825 | flattened from a full 360° `Revolve(155)` (3D flat 35.712 × 35.711, 294.9 mm², 2 wires), then redrawn ≈0.21 mm smaller in Ø. Outer stops **before the flutes** and its bore lies **0.437 mm inside the crystal edge = an overlap** — both are **measured facts of this kit, not the rule**: ruled 2026-09-05 (**NXLEARN-228235 R2a/R2b**) that the bezel outer **runs to the case edge** over the fluting and the seam is a **0.35 mm gap**, so **our Ø38.36 / Ø31.50 stands** |
| CRYSTAL + cyclops hole | A | 1 | disc **Ø30.724**, hole **7.353 × 6.095**, **net 702.5 mm²** | typed Ø30.8 circle (3D flat measured Ø30.91) — 30.8 is the construction value, 30.72 delivered. Cyclops = tangent-fillet outline: four **R 1.349** corner fillets about their own corner centres + two **R 3.691** flank arcs + 3.20 mm straights, centre offset **(+10.073, −0.148)** from the disc centre; +0.15 mm outward clearance (CLOSED R4) |
| CASEBACK_CENTER | A | 1 | **Ø21.448, 361.3 mm²** | typed Ø21.5 circle on the caseback plane (3D flat 21.576 × 21.579, 362.0 mm²) |
| CASEBACK_RIM (annulus) | A | 1 | **Ø27.85 / Ø22.00, 229.0 mm²**, width 2.925 | built (Revolve/Through Curves) and flattened (230.8 mm², OD 27.86/ID 22.0); its own two loops concentric to **0.000000 mm**; seam to the caseback centre disc 0.276 mm radial. A **standard piece, not an extra** (ruled 2026-09-05, **NXLEARN-228235 R1**): outer = the caseback flat-boundary radius, inner = centre disc Ø + 2×0.276 mm seam; the ±8 % area exemption is dropped |
| FLANK_9 (one piece) | C | 1 | **48.69 × 6.71, 204.2 mm²** | 2 degree-5 splines lug-tip-to-lug-tip → ruled → 0.1 mm lift; 3D flat 203.2 (ΔA 0.003 %); 10 ARC + 1 LINE incl. a 27.054 mm straight. **Its ends are the lug outer walls** — those are never separate pieces |
| FLANK_3C crown-side | C | **1 delivered**; **2 by rule** | **22.75 × 5.25, 88.9 mm²** | + bridge-spline crown cutter (−2.5…+1.8); 3D flat 22.566 × 6.504, 88.1. Ends in a crown-hugging **arc R 2.895 about the crown axis** (sweep −75.48°, chord 3.545) on a 2.925 mm crown = **≈0 clearance** — **not a C**. Ruled 2026-09-05 (**NXLEARN-228235 R3**): **both halves belong** (FLANK_3C_12 + FLANK_3C_6, the 6-side one the mirrored template unless its mesh region differs — the missing half was an oversight) and the notch arc = **crown radius at the flank height − 0.15 mm, about the crown axis** (here r99 2.925 → **R 2.775**), replacing the manual −0.03 and our +0.30 |
| LUG_TOP_* | C | 4 | **4 identical**, 15.01 × 4.59, **35.15 mm²** each (spread 0.001 mm²) | 3D 35.80 each; + lug-root cutter (−22…+2.4); mirrored ×2 then nudged (1°/0.65°, 0.1–0.45 mm), then **idealised to one template** in 2D — now the rule for every family (**NXLEARN-228235 R5c**, ruled 2026-09-05); R 0.3 fillets only |
| LUG_UNDER_* | C | 4 | **4 identical**, 17.16 × 4.32, **42.23 mm²** each | 3 splines → ruled → 0.05 mm lift; 20 min of rotation fitting; R 0.3 fillets + one R 0.321 blend per piece. **One template for the family** (**NXLEARN-228235 R5c/R9**): our per-instance lug-unders ran +18…+25 % — regularise to the template |
| LINK_C_* centre links | D | **14** (13 identical + 1 case-end) | **7.793 × 4.047, 31.46 mm²** ×13; case-end **7.794 × 3.431, 24.33** (one edge R 21.352) | section → Fit Circle **R 2.8787** (28 pts, err ≤ 0.0097) → extrude −2.2…+2.5 / −2.3…+2.8 → in-surface margin **0.55/0.65/0.75/0.85 mm** (`Offset in Face` → `Divide Face`) → replicate. Delivered outline = exact rounded rectangle with **R 0.3 corner fillets about their own corner centres**, plus a **0.30 mm end inset per end** along the link axis; developed wrap **80.6°**. Ruled 2026-09-05 (**NXLEARN-228235 R5**): wrap **≈80°** (developed centre-link width ≈ 4.0 mm on R 2.88) is the rule, never the exposed ~150°; the kit runs the **whole bracelet to the clasp** (count links from the mesh — this kit's 7/run was partial); and each family is **one template**, mirrored/copied |
| LINK_S_* side links | D | **28** (14 per run × 2) | **L 5.295 constant**, W **4.896 → 3.197** in ≈0.23 mm steps then 3.197 ×4; end rows 4.896 × 3.696 ×2 and 5.457 × 2.753 ×2 (edges R 36.4 / R 93.7) | same loop on the outer rows; the **4.695 mm straight edge** is what the old "4.7" named — there is no 5.1 class. Sheet row pitch 7.993 is layout only. Side-link developed widths **3.2–4.9 mm per row** are the ≈80° wrap (**NXLEARN-228235 R5a**); one template per row family (**NXLEARN-228235 R5c**) |
| TAB_* | ? | 2 | 4.046 × 2.938, **8.885 mm²** | small 3-sided tabs at the top of the sheet, R 0.3 + R 11.676; source facet **unresolved — the record cannot answer** |

Not in the delivered kit: no crown, clasp, lug-inner or lug-outer-wall pieces —
the manual 228235 kit is **case + bracelet only**, i.e. the **minimum scope**.
Our seven extras (LUGWALL_12, LUG_INNER ×3, CROWN_BAND, CROWN_CAP,
CLASP_COVER_12) are **kept as coverage extras** (maintainer ruling 2026-09-05,
R8). Layout facts: min inter-piece gap **1.497 mm**;
the rim annulus is **nested inside the bezel bore at 1.000 mm** radial clearance,
which leaves a 1.000 mm scrap band that is not a piece.

Operator's spec notes for kit 2 (from the annotated collage): 3 clasp-end links
identical, the rest "slightly bigger"; lug-top corners "round it"; caseback gets
both a centre disc and an annular rim piece — **the rim was in fact built,
flattened and delivered** (see CASEBACK_RIM above).

## Kit 3 — GMT-Master II 126713GRNR (R3; **PROVISIONAL — record in progress, no DXF**)

> **Not a delivered kit.** `126713GRNR-RV04.prt` is stamped 2026-09-05 00:01:32 UTC, *after*
> the last captured event; **no DXF exists**, **no bracelet piece exists in-record**, and the
> final flattening/layout state was never captured. Everything below is "as of
> `tasks/NXLEARN-126713/run/SNAPSHOT_MANIFEST.md`". Use it as method evidence and as a
> starting inventory — never as a regression fixture. Full derivation:
> `e2e-126713-method.md`; open questions: `tasks/NXLEARN-126713/run/RULINGS.md`.

Final captured tree: **113 features, 33 bodies = 32 sheets + 1 solid**, 35 faces, 143 edges.
There is **no body↔feature key** in the topology export, so facet names are inferred unless
flagged. Confidence: **[confirmed]** = screenshot or typed expression; **[measured]** =
computed from the RV04 STEP by this analysis; **[inferred]** = construction order/pattern only.

| piece (suggested id) | class | n | size / area | construction facts | confidence |
|---|---|---|---|---|---|
| CRYSTAL + cyclops lens hole | A | 1 | Ø**28.7** typed; face **607.31 mm²**, 9 edges (1 outer + 8-edge inner loop) | S1 `SKETCH_000:Sketch(19)`→`Extrude(20)` (p9=p10=0), renumbered `Sketch(2)`→`Extrude(3)` at the RV02 hop with expressions unchanged. Lens cut-out: two near-flat arcs r 899.05/905.15 **6.1 mm** apart + two R**3.5** end-caps + 4×R**0.3** fillets, offset **+0.15 mm** outward, centred ≈x 9.2 (crown/date side) | **[confirmed]** S1 §4, two screenshots. *`session_2.md` §3's label "crown-area logo sheet" for `Extrude(3)` is **superseded** — the expressions (p4 = 28.7) are the crystal disc's* |
| CRYSTAL_BORE candidate | C (2 curves) | 1 (+1 mirror) | — | `Spline(4);Spline(5)`→`Through Curves(6)`, built directly over the crystal/bezel bore; `Move Object(7)` lift 0.15 → `Mirror Geometry(8)` → `Move Object(9)` lift 0.15 | **[confirmed]** visually over the bore (`session 2/screenshots/dc_viewport_20260904_172459.png`); *why* a second crystal candidate exists is unresolved (**NXLEARN-126713 R10, open**; record R1 also shipped two) |
| BEZEL_or_CRYSTAL annulus | A | 1 | typed Ø**30.0** / Ø**35.4** | `SKETCH_002:Sketch(46)`→`Extrude(47)` zero-depth (p169, p170) | **[confirmed]** typed; which facet it is, is unresolved (cf. R1's Ø30.0/38.8 bezel) |
| CASEBACK | A | 1 | Ø**21.47** (fitted R 10.586 + 0.15 outward), plane z −12.165 | `Arc(35)` 3-point fit **on the flat-centre boundary** (p137–p145, z −12.145/−12.157/−12.195; circumcircle centre (−0.058, −0.083)) → `Offset Curve(36)` **+0.15 outward** → `Extrude(37)`. Note the sign is opposite Kit 1's (**NXLEARN-126713 R4, open**) | **[confirmed]** z-range match; circumradius computed from p137–p145 |
| FLANK_3 (crown side) | C | 1 | **93.763 mm²**, 27×4 poles, boundary lengths 26.78 / 19.19 / 0.37 / **0.00** | ruled, degenerate end (section curves converge); **stops at y = −6.30 where the crown interrupts it** | **[measured]** RV04 STEP; facet assignment from the frame calibration (+X = crown) |
| FLANK_9 (lug-to-lug) | C | 1 | **243.800 mm²**, 37×4 poles, 55.25 / 49.55 / 0.33 / **0.00**; runs y −23.74…+23.66 | ruled, degenerate end; the R3 sibling of Kit 1/2's one-piece 9-side flank | **[measured]** |
| CASEBACK_RIM band | C | 1 | **82.361 mm²**, 39×4 poles, 26.07 / 24.88 / 3.01 / 1.75 | ruled, both ends real curves (1.75–3.01 mm) but straight-ruled ends were accepted | **[measured]**, name **[inferred]** |
| GUARD (crown-guard patch) | C | 1 | **32.262 mm²**, 19×4 poles, 11.54 / 9.10 / 6.21 / 5.17; K_abs_max 2.72e-2 | ruled | **[measured]**, name **[inferred]** |
| **LUG_SHOULDER** (lug outer flank ↔ case shoulder) | **N** | **4** (1 + 3 mirrors) | **41.851 mm²** each, **12×11 poles**, deg 3/3; at x ∈ ±[10.27, 16.61], y ∈ ±[11.67, 23.93], z ∈ [−10.87, −4.18] | `Spline(13..16)`→`Through Curve Mesh(17)` (2 primary 15.701/9.924 mm + 2 cross 8.541/2.952 mm, all **G0**, corners bridged from the primaries) → `Mirror Geometry(18),(19)` about the model YZ and XZ planes | **[confirmed]** by STEP measurement. *`session_2.md`'s "crown-side flank draped over the crown boss" label is **superseded** — the four copies are symmetric in both x and y.* Whether it is a piece at all is **NXLEARN-126713 R1 (open)**; it is Kit 1's undocumented `HORN_*` facet — and the delivered Kit 2 has **no** such piece, its one-piece `FLANK_9` ends being the lug outer walls |
| lug/flank ruled family | C | ~13 sheets | not individually measured | `Through Curves(27),(30),(34)`, `(53)` (**3-section** variant), `(60)`, `(75..81)` (a 22:18 sprint of 14 free-hand splines → 7 sheets, **built per side, not mirrored**), `(96)`, `(101..104)`, `(106)`. End closure: `Extrude(98)` cutter (span −1.7…+2.0) → `Trim Sheet(99)` → `Delete Body(100)`; `Trim Sheet(105)` using `Spline(86)` as cutter; `Trim Curve` chain feeding `(27)` | **[inferred]** — facet identity is construction-order only |
| *(working aids, not film pieces)* | — | 2 | — | `Revolve(44)` (from the caseback arc's second offset) and `Revolve(49)`, both 0→360° **solids**; only one solid survives the final topology (unresolved) | **[inferred]** purpose (**NXLEARN-126713 R7, open**) |

### Kit 3 — Jubilee bracelet (**mesh-measured; no record source**)

The record itself contains **no bracelet piece**: no link spline, no `Through Curves`, no
`Pattern Geometry`, and no typed pitch/span expression anywhere in session 2's 122 distinct
features (`run/RECORD_MAP_CORRECTIONS.md` §2 — the task pack's "full facet set for a Jubilee
bracelet" is false as of RV04). The only intent evidence is the operator's annotated collage
`126713GRNR.png`, which outlines **one Jubilee centre-row link** *and* **long dashed strips
running along the bracelet** — consistent with either scheme, so the piece scheme itself is
**NXLEARN-126713 R8 (open)**. Consequently **every number below is mesh-measured** from `126713GRNR.stl`
(3,619,641 triangles) in the canonical frame of `tasks/NXLEARN-126713/run/jubilee_geometry.md`
§1 (+ `.json`) — **operator-typed values: none exist for this facet**, and no row here may cite
the NX record. Fits use the record's 0.07 mm iterative outlier rejection unless stated.

**5 rows confirmed (2 outer + 2 inner + 1 centre)**, both arms. Row seams: the three
inner/centre seams are **not** visible in any single transverse height profile (the top surface
is nearly flush there, <0.3 mm step); they were found by pooling small periodic rivet/pin
witness dips (<0.1 mm deep, prominence > 0.06 mm) from ~70 stations per arm into a 0.2 mm
X-histogram and taking its four strongest peaks. Only the two outer boundaries have a direct
height signal — **the seam method is weaker-signal than the outer-row one; record which was
used** (`jubilee_geometry.md` §2, failure item 1).

| piece (suggested id) | class | n | size / pitch | construction facts (**all mesh-measured**) | confidence |
|---|---|---|---|---|---|
| LINK_O_* outer rows | D | 2 rows × ~8–9 links per arm | width **4.06 / 4.38 / 4.61** (three of four row×arm samples; the fourth, +Y OUTER(+), reads **3.50**); link length **4.85–4.98**; pitch **6.30–6.50** | **crowned, not flat**: Kåsa circle fit **R 5.40** (resid_max 0.067) on a transverse X–Z section at y = +60.52 in the canonical frame, **sagitta 0.296 over the 4.06 width**. Raw within-row z-range 1.57–1.81 — a *different* quantity (it includes the ~1 mm seam-edge drop), not a deeper dome. Gap 1.45–1.61 | **[measured]** ±0.07 fit / ±0.1–0.2 pitch |
| LINK_I_* inner rows | D | 2 rows × ~7–11 links per arm | width **2.80–3.00** (2.80 ×3, 3.00 ×1); link length **4.78–4.92**; pitch **6.20–6.55** (both excluding the flagged noise-band sample) | **No crown circle fit was made for these rows.** Only the raw within-row z-range exists (0.86–1.45), and it includes the seam-edge drop, so it is *not* comparable with the fitted sagittas above and must not be read as a crown radius. Gap 1.42–1.63 | **[measured]** width/pitch; crown **unmeasured** |
| LINK_C_* centre row | D | 1 row × ~8–10 links per arm | width **3.00** (both arms); link length **4.99 / 5.08**; pitch **6.40 / 6.55** | **crowned**: Kåsa circle fit **R 2.626** (113/164 pts, resid_max 0.069), centre (x 0.088, z −11.610) on a 0.6 mm-thick transverse slice at y = +67.12, X trimmed 0.15 in from each seam, points within 0.3 of the row's 98th-pct height; **sagitta 0.284 over 2.70**. Gentler dome than Kit 2's R 2.879 — two different models. Gap 1.32–1.56 | **[measured]** ±0.07 |
| CLASP_* | — | **0** | — | **Not present in this scan.** Both arms taper to a *narrower* end link (−Y: 12.9–13.2 mm over its last 4 mm; +Y: 9.0–12.6 mm over its last 3 mm, vs a 15.4–16.7 mm plateau) and the periodic link pattern runs to the cut edge — i.e. the bracelet was cut/opened at the clasp attachment pins. No clasp Y-location, extent or width can be reported | **[measured]** absence |

**Cross-row facts** (consolidated, `jubilee_geometry.md` §3):

- **Pitch 6.5 mm on every row** — median of 9 self-consistent row×arm medians spanning
  6.20–6.55. The tenth (+Y INNER(−), **4.40**) is corrupted by a ~6 mm-wide localized
  mesh-noise band at y ≈ 64–69 (it visibly disturbs all three inner/centre rows there) which
  also wrecks that row's link length (**2.82**); both excluded, not smoothed.
- **No half-pitch stagger.** Centre-vs-outer offset measured **0.0 ± 0.33 mm** (9 pairs, −Y
  arm; 0 % of pitch, jitter ≤ 7 %) — all five rows' peaks and valleys land at the same Y across
  the full width. **The classic Jubilee half-pitch assumption in the task pack is wrong for this
  bracelet**; reported as measured (CLAUDE.md hard rule 6).
- Gap **1.5 mm** median, link length = pitch − gap = **5.0 mm**.
- Taper: −Y (long, 93.2 mm) 19.93 wide at the case boundary → plateau 16.67 mean from
  y ≈ −49; +Y (short, 62.3 mm) 21.45 → plateau 15.45 from y ≈ +48. Case width at y = 0: 44.31.

**Uncertainty budget** (applies to every bracelet row): fits ±0.07 by construction (rejection
threshold); percentile-based radii ±0.3; pitch/length medians ±0.1–0.2 (except the flagged
4.4 outlier); seam X-positions ±0.1–0.2 (histogram bin). Kit-3 bracelet rows remain
**PROVISIONAL**: they describe the *scan*, and no piece has been built from them by anyone.

## Watch-level reference numbers

| quantity | 126500 | 228235 | 126713GRNR (**all PROVISIONAL**) |
|---|---|---|---|
| crystal flat radius (mesh) | 14.65–14.70 | ≈15.6–15.8 (cyclops +1.15 bump) | **14.68 mesh-measured** (r99 of vertices within ±0.15 of the crystal plane, ±0.3; boundary-ring circle fit 14.01, resid_max 0.070) — the disc was **typed** in-record (r 14.35, never fitted); the mesh brackets it, < 5 % |
| crystal film Ø | 29.30 | **30.724 delivered** (30.8 typed in 3D) | **28.7 typed** (**NXLEARN-126713 R10, open**); mesh cyclops centroid **(9.16, 0.06)**, extent x 5.55…12.76 / y ±2.90, max +1.18 proud — matches the record's "lens centred ≈ x 9.2" |
| caseback z / centre film Ø | −12.14 / 26.54 | −12.1 flat centre (mesh floor −12.4) / **21.448 delivered** (21.5 typed) | plane z **−12.164 mesh** vs −12.165 in-record (Δ 0.001 — independent confirmation of the feature); flat boundary **R 11.24 mesh** (r99; 11.20 by the > 0.1 mm departure criterion, ±0.3) vs the operator's 3-point arc **R 10.586**, i.e. his arc lies **≈0.65 inside** the mesh boundary and even after `Offset Curve(36)` **+0.15 outward** the film (Ø21.47) is still **≈0.5 inside** it (mesh flat Ø22.48). Both conventions are net *insets* — **NXLEARN-126713 R4 (open)** is about which curve is fitted, not the direction |
| caseback rim film Ø outer/inner | — (not a piece) | **27.85 / 22.00 delivered**, width 2.925 | — **no rim piece exists in-record**; the rim band’s measured dimensions are in the next row |
| case / bezel / caseback-rim Ø | — | — | 38.2 case; bezel surface of revolution **Ø38.20** at z −1.19…−0.43; caseback rim **Ø27.30** at z −12.13…−11.30 (RV04 STEP frame calibration). Mesh bezel outer R **15.71 / 17.00 / 18.51 at z −0.5 / −0.8 / −1.1** (Kåsa, 0.1 reject, centres within 0.06 of the origin) — a real measured slope; the typed Ø35.4 (R 17.7) lands on it, the Ø38.20 (R 19.1) sits below the sampled range. Crown protrudes to x **+24.04** absolute = **6.97 beyond** the mean bezel R |
| bezel film Ø outer/inner | 38.80 / 30.00 (typed) | **35.50 / 29.85 delivered** (outer stops before the flutes — a fact of that kit). **Rule (**NXLEARN-228235 R2a/R2b**, 2026-09-05): outer to the case edge, seam a 0.35 mm gap → Ø38.36 / Ø31.50** | typed **Ø35.4 / Ø30.0** annulus (`Sketch(46)`→`Extrude(47)`, zero-depth); **which facet it covers is unresolved** (cf. Kit 1’s Ø30.0/Ø38.8 bezel) — the measured bezel slope is in the previous row |
| lug-to-lug flank length | 46.9 | 46.5 | two definitions, both stated: ≈**47.4** = y-span −23.74…+23.66 of the 9-side flank **sheet** (RV04 STEP), vs **49.82 mesh** = lug-tip envelope (y −25.13…+24.69, first sustained width < 26). Δ 2.4 (5 %) is the definition, not a disagreement |
| flank sheet z-range | −11.5…−4.0 (bbox; the edges are CURVED ridges — z −4 is only the belly top, −11.5 only near the lug underside; do NOT extract boundaries as constant-z sections) | −10.65…−3.88 (same caveat) | per-flank range not separately measured; the lug-shoulder network face spans **z −10.87…−4.18**, bounded inboard by a near-horizontal case contour at z ≈ −4.25 (same caveat) |
| bracelet | link pitch ≈10.25, width 17.6→15.4 (taper stops after link 2), tops z −9.1…−9.5 | **mesh pitch 6.12 ± 0.10**; link crown R 2.88 (a 3D fit only — it never appears as a 2D radius); **developed centre-link width 4.047 = 80.6° wrap**. The old "pitch 6.8" is neither the mesh pitch nor the delivered sheet pitch (7.99, layout only) | Jubilee **5-row, all mesh-measured** (no bracelet piece exists in-record): pitch **6.5 on every row**, **no half-pitch stagger** (offset 0.0 ± 0.33), gap 1.5, link length 5.0; widths outer 4.06–4.61 (one sample 3.50) / inner 2.80–3.00 / centre 3.00; crown R **2.626 centre** (cf. Kit 2's 2.879) and **5.40 outer**; taper 19.9→16.7 (−Y) and 21.4→15.4 (+Y); **clasp absent from the scan**. Detail + uncertainties: `run/jubilee_geometry.md` |
| raw-scan tilt / offset | 12.3° / z ≈ −240 | 14.7° / z ≈ −230 | tilt **5.69° mesh-measured** (fitted crystal normal vs the nearest raw native axis); z offset **n/a** — the *record's* alignment scaffolding was purged and none of the 54 Fit-Surface / 70 Datum-Plane dialogs left a feature or expression trace |
