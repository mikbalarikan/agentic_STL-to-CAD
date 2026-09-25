# DXF output contract — from the maintainer's accepted kit, defects removed

Basis: the four delivered Record-1 DXFs (`WatchCareES_Template_2_DXF*.dxf`).
The maintainer's cutter consumed AC1018, mm, loose LINE/ARC/CIRCLE primitives on
NX layer "1", no polylines, no labels. RV02 (08-20, R0.4 fillets) is the final
accepted geometry — and it exists ONLY as DXF (the .prt predates it).
`scripts/dxf_kit_writer.py` implements this contract; use it rather than
re-deriving.

## What the delivered files teach

### Revision history (measured loop-by-loop)
| rev | change | lesson |
|---|---|---|
| v1 (08-15 18:48) | raw sketch export: sharp corners, 32 duplicate degenerate "splines" (straight edges), stray 0.054 mm sliver | the translator exports the *saved* part; save before export |
| v2 (+7 min) | +233 corner fillets R 0.2, duplicates removed; rect pieces shrink exactly 4·(1−π/4)·r² | fillets applied in sketch |
| RV01 (08-20 01:18) | 63 pieces byte-identical; +4 "horn" pieces (open by 0.715 mm, 0.73 mm tip), +5 POINTs | kit was incomplete after physical test; new pieces rushed |
| RV02 (+17 min) | ALL fillets R 0.2 → **R 0.4**; nothing else | 0.2 mm corners failed physically; since the 2026-09-05 ruling (R7) 0.4 is the *flank* value and 0.3 the links/lugs/tabs value |

### Defect census (what our validator must catch)
- open chains: flank corners mismatched 0.052 mm (closes only at 0.06 mm
  tolerance); horn pieces open 0.715 mm — would not release from the cutter;
- micro-entities: R 0.0042 mm arcs (0.013 mm long), 0.054/0.221 mm slivers;
- POINT entities on the cut layer (some drivers read them as drill ops);
- `$EXTMIN/$EXTMAX` bogus NX defaults (−0.5…5) — consumers must not trust them;
- no labels at all: 67 pieces identified by shape only;
- narrow feature: a shipped piece tapers to 0.73 mm — a largest-inscribed-circle
  "min width" misses this; use the buffer-erosion test;
- handedness never declared (which side is adhesive / whether to mirror for the
  cutter).
- **F-A — a gap in OUR output, not the maintainer's**: our r2 228235 kit was written fully
  polygonised — 8 237 chords, **0 non-zero bulges**, min segment 0.080 mm — against rule 3's
  exact-bulge-arc promise and the ground truth's 195 LINE / 261 ARC / 6 CIRCLE. Writer or
  kit-builder defect; **separate fix task**, not fixed in the NXLEARN-228235 patch.

### Layout facts
Sheet 123.1 × 85.2 mm, 39 % fill; crystal disc nested inside the bezel annulus
hole at 0.35 mm radial clearance; min piece gap 0.62 mm, median ≈1.3; bracelet
links in 5-column rows, centre-link pitch 11.0 (Pattern), rows mirrored about
y = 0 and y = 48; free-form mirror pairs placed wherever room allowed.

## The contract (our writer)

1. **Format**: ezdxf R2004 (AC1018) — R2010 fine; `$INSUNITS=4`,
   `$MEASUREMENT=1`, `$LUNITS=2`; real extents; modelspace only; z = 0;
   arc extrusion (0,0,1). Deterministic:
   `ezdxf.options.write_fixed_meta_data_for_testing = True`, sorted entity
   order. (R12 cannot carry LWPOLYLINE/$INSUNITS — only fall back to
   R12+POLYLINE on explicit machine requirement.)
2. **Layers**: `CUT_OUTER` (red, closed CCW LWPOLYLINE per piece), `CUT_INNER`
   (blue, CW holes), `LABEL` (green TEXT ids, 1.5 mm, at pole of
   inaccessibility), `REG` (magenta, optional crosses/frame), `REF` (grey,
   never on cut layers). No POINT/SPLINE/TEXT on cut layers.
3. **Entities**: one closed LWPOLYLINE with bulge arcs per loop (bulge =
   tan(Δθ/4) — exact arcs, no polygonisation); free-form edges sampled at
   0.02 mm chord tolerance to vertices. First==last implied by `closed=True`.
4. **Corner fillets**: **R 0.3 on links, lugs and tabs; R 0.4 on long flank
   pieces** (maintainer ruling 2026-09-05, NXLEARN-228235 R7 — this replaces the
   blanket R 0.4; R 0.2 was physically rejected). Set `corner_radius` per piece
   family, not once per kit. Concave: sharp or ≥0.2.
5. **Hard gates** (`validate_kit`): all loops closed & shapely-valid; loop
   count == manifest; zero overlap; min gap ≥ 1.0 mm. **Nested-in-hole: pass
   `nested_gap=1.0` explicitly** — `validate_kit`'s parameter default is 0.35,
   which is the Daytona crystal-in-bezel case; the ≥ 0.35 mm relaxation applies
   **only to a hole's own coverage partner** (CLOSED R10,
   `e2e-228235-manual-rulings.md`). Then min segment ≥ 0.05 mm; narrow-feature erosion test at 1.5 mm
   width (report area lost; fail < 1.0 mm); `$INSUNITS==4`; round-trip re-read
   reproduces the same loops at 0.01 mm; DXF SHA-256 into the run manifest.
6. **Labelling**: stable ids (canonical frame names: `LUG_TOP_12C`, `FLANK_9`,
   `LINK_C_12_1`, …) as TEXT + XDATA (`WATCH_TPU`: piece id, area) + sidecar
   `kit_manifest.json` (piece → source facet, recipe, regularisations,
   gates, bbox/area/perimeter, mirror partner, handedness flag).
7. **Handedness**: declare per kit whether the file is viewed from the adhesive
   or outer side; mirror-partner pieces must be true mirror outlines.

## Regression fixtures (when re-running the 126500)

67 pieces / 24 distinct shapes; bezel Ø38.80/30.00; crystal Ø29.30; caseback
Ø26.54; flank 49.0 × 7.1; centre link 7.315 × 8.75 ×10; outer links 7.5 × 4.88 /
4.25 / 3.81 / 3.30 (×20); lug tops 5.02 × 13.93 ×4; smallest piece 3.68 × 2.17
(minW 1.99); total area ≈4114 mm²; sheet ≤ 125 × 90 mm; link pitch 11.0.
Match areas within ±5 % and counts exactly (minus the 4 defective horns, which
our pipeline should produce CLOSED — from the lug outer-flank facets, recipe C).

## Regression fixtures (when re-running the 228235)

Measured from the maintainer's delivered `228235STL Converted.dxf` (2026-08-30 22:50 local);
every number traces to `references/e2e-228235-manual-diff.md`, which carries the arc-aware
chaining (0.06 mm endpoint tolerance) these come from. These are measurements **of the delivered
file**; how it was drawn is only partly recorded — RV3→RV7 and the export are uncaptured and the
margin session is untraced, so read that file's §0 evidence caveat before citing any 2D-stage
*process* claim from this watch.

**Fixtures, not rules.** Four choices visible in these numbers were **superseded by the maintainer's
2026-09-05 rulings** and must not be used as build targets: (a) the **bezel diameters** Ø35.50/Ø29.85
(rule: the outer edge runs **to the case edge** over the fluting, Ø38.36 here — R2a); (b) the
**bezel/crystal seam as a 0.437 mm overlap** (rule: a **0.35 mm gap**, crystal disc = bezel bore Ø −
2×0.35 — R2b); (c) **7 links per run** (rule: the **whole bracelet to the clasp**, links counted from
the mesh — R5b); (d) **one crown-side flank** (rule: **both halves**, the 6-side one mirrored, notch arc
= crown radius at the flank height − 0.15 mm **about the crown axis** — R3a/R3b). Everything below stays
a valid fixture for re-measuring *the manual file*; a kit rebuilt under the rulings legitimately shows a
larger bezel, both crown-side halves and more link pieces, so compare those families against the rules,
not against this file.

**61 closed loops = 58 piece outlines + 3 holes.** The holes are the bezel bore, the caseback-rim
bore and the cyclops. Separately, the 1.0 mm sliver left when the rim annulus is nested inside the
bezel bore is scrap, not a handleable part — it is bounded by two existing loops (the bezel bore
and the rim's outer circle), it is **not** a 62nd loop, and it is excluded from the 58. **A loop
count is never a piece count.** Net film **3 180.6 mm²** against a **5 418 mm²** sum of loop areas.

- circles, r: **17.750 / 15.362 / 14.925 / 13.925 / 11.000 / 10.724** = bezel outer / crystal /
  bezel inner / caseback-rim outer / caseback-rim inner / caseback centre;
- **273 arcs**: R 0.300 ×206, R 0.321 ×4, R 0.400 ×3 (both flank pieces only), R 1.349 ×4
  (cyclops corners);
- entity census **195 LINE / 261 ARC / 6 CIRCLE**, all on layer `"1"`, **no SPLINE, POLYLINE or
  TEXT**, no labels; every loop closes at **0.06 mm**;
- sheet **62.97 × 160.01 mm**; min inter-piece gap **1.497 mm**; rim annulus nested in the bezel
  bore at **1.000 mm** radial clearance.

So **"all loops closed, no splines" is an achievable target, not an aspiration** — a human hit it
on this watch with loose primitives. Match **areas within ±5 %** on the discs and annuli and
**counts exactly per family** (4 lug tops, 4 lug unders, 13 + 1 centre links, 28 side links,
2 tabs, 2 flanks); per-piece dimensions are in `references/piece-catalogue.md`, Kit 2.
