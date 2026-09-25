---
name: stl2dxf-facet-film
description: Turn a scanned watch STL into a manufacturing-ready DXF cutting kit of flat protective-film pieces (facet-film kit) — one developable piece per watch facet, no seams, no mesh-ARAP stretching. Distilled from the maintainer's recorded Siemens NX sessions (Daytona 126500 + Day-Date 40 228235, both delivered as DXF kits, + GMT-Master II 126713GRNR, record in progress) into a tool-agnostic method implemented with trimesh + build123d/OCP + shapely + ezdxf. Use for ANY scan-to-cutting-template task — watch films, TPU covers, per-facet skins, "STL to DXF", flattening a 3D surface patch to a 2D outline, or building/validating the kit DXF — and whenever Phase-2 stages 3–8 (partitions, surface, flattening, compensation, DXF) of the watch-cover pipeline need the proven construction recipes, parameter values, or acceptance gates.
---

# stl2dxf-facet-film

Build the cover as a **kit of flat film pieces, one per facet** — never as one
stretched membrane. Each piece is a *design-intent developable sheet* constructed
ON the scan (circle, extruded profile, or ruled surface between two boundary
curves), then developed to 2D **exactly**, regularised, nested, and written as a
validated DXF. This is the method the maintainer proved manually in NX over two
delivered watches and five delivered DXFs (four Daytona revisions + the 228235
kit); the numbers below are measured from that record, not invented. A **third
watch (GMT-Master II 126713GRNR, record "R3") is recorded but unfinished** — no
DXF, no bracelet piece, final state uncaptured — so every record-R3 value here is
marked PROVISIONAL and its open questions live in
`tasks/NXLEARN-126713/run/RULINGS.md`. Mesh-parameterisation flattening
(LSCM/ARAP of mesh patches) is the fallback, not the default — it fights
partition boundaries and strain; design-intent sheets sidestep both. (Exception:
a recipe-N network patch is not ruled, so it develops with LSCM — Stage 3.)

**Ruling namespace — read once.** Two record-learning tasks both numbered their
rulings R1…Rn, so ids here always carry the task. **`NXLEARN-228235 Rn` = decided
by the maintainer 2026-09-05 — those decisions are rules.** **`NXLEARN-126713
Rn` = still open — every default they guard is PROVISIONAL** until the maintainer
answers. A bare **R1 / R2 / R3 is a *record* label**, never a ruling id:
record R1 = Daytona 126500, record R2 = Day-Date 40 228235, record R3 =
GMT-Master II 126713GRNR.

Deep evidence lives in `references/` (read when you need exact values or doubt a
step): `nx-method-evidence.md` (full reconstructed procedure + every parameter),
`piece-catalogue.md` (every piece of all three watches, dimensions, recipes),
`dxf-contract.md` (output contract, defect list, regression fixtures),
`e2e-228235-manual-diff.md` (the delivered 228235 manual kit measured against ours + the record facts
that complete that watch's method) with `e2e-228235-manual-rulings.md` (**NXLEARN-228235 R1–R10, all
decided by the maintainer 2026-09-05** — those decisions are the rules stated below),
`method-synthesis-full.md` (the exhaustive 10-stage synthesis with the ~45-entry
parameter table, 13 dead ends, per-stage API mapping, and open questions —
consult it before deviating from any recipe), and `e2e-126713-method.md` (the
record-R3 end-to-end reconstruction: recipe N, the caseback sign conflict, the
flattening evidence, and every record-R3 parameter with its method) with
`tasks/NXLEARN-126713/run/RULINGS.md` (**NXLEARN-126713 R1–R11, all still open**).
Bundled code: `scripts/ruled_sheet.py` (ruled sheet build / developability gate /
exact unroll — tested), `scripts/curve_network_sheet.py` (recipe-N Coons patch
from a 2×2 curve network + the recipe-C-vs-N trigger measurement + LSCM
development; self-test reproduces the archived prototype numbers, needs OCP),
`scripts/dxf_kit_writer.py` (deterministic DXF writer +
hard-gate validator — tested), `scripts/render_progress.py` (2D kit plot from
the DXF + 3D sheets-over-scan walkthrough views via pyvista when available).
Import them; do not rewrite them. So the walkthrough renders are possible,
persist each recipe-C/D piece's matched boundary samples in its piece record as
`"curves3d": {"A": [[x,y,z]...], "B": [...]}` — the maintainer follows builds
through these images; produce them at every milestone, not only at the end.

## Pipeline

```
0 align mesh to canonical frame        (trimesh + numpy)
1 facet inventory / piece spec         (human-confirmable list BEFORE geometry)
2 per-facet sheet construction         (5 recipes: planar | extruded | ruled |
                                        curve-network | patterned)
3 develop each sheet to 2D + gates     (scripts/ruled_sheet.py)
4 regularise outlines                  (idealise, unify, fillet — this step is REAL, the
                                        maintainer redrew, not traced)
5 nest + write DXF + validate          (scripts/dxf_kit_writer.py)
```

Never read raw STL bytes into context; all mesh facts come from short scripts
printing compact summaries (`trimesh.load(path, process=False)` reads 149 MB in
~1 s).

## Stage 0 — Canonical frame (the record-R2 recipe; reproducible)

Origin = crystal centre, +Z = crystal normal (out of dial), +Y = 12 o'clock,
+X = crown side. The scans arrive tilted 12–15° with origins ~240 mm off — always
re-align first; every recipe below assumes this frame.

1. **Crystal plane**: select up-facing facets, take the dominant normal/height
   cluster, least-squares plane with **0.07 mm** outlier rejection — the
   record-R1/R2 default (plane, circle, spline). **Not a constant of the method:**
   record R3 shows a Fit-Plane dialog at **0.03 mm**
   (`session 1/screenshots/dc_viewport_20260830_203047.png`; one captured
   instance, target region uncertain). Declare the rejection value **per fit** in
   the run manifest rather than assuming one number (**NXLEARN-126713 R11, open**).
2. **Origin**: fit a circle to the flat-crystal boundary ring (crystal flat
   radius: 14.65 mm on the 126500, ≈15.5–16.5 on the 228235); centre projected
   onto the plane = origin.
3. **12–6 axis** (lug-midpoint recipe): fit planes to the two lug-end facets of
   one bracelet end → intersect each with the mesh → fit a line to each
   intersection → take midpoints → the line through the two midpoints is the 3–9
   direction at that end; the 12–6 axis is its in-plane perpendicular through the
   origin. (PCA of the bracelet point cloud is a decent cheap substitute; crown
   side = the larger in-plane protrusion, e.g. +23.0 vs −18.8 mm on the 228235.)
4. `mesh.apply_transform(T)`; persist T, then purge the fit scaffolding. (In NX
   the CSYS move was **non-associative in records R1/R2 but Associative in record
   R3** — an NX housekeeping choice; the port persists T either way.) Expect
   multiple mesh components (the 126500 scan has a detached 78 k-facet bracelet
   tail) — keep them, don't "repair".
5. Sanity line before proceeding (this catches sign/axis mistakes cheaply):
   after alignment the crown protrudes at **+X**, the 9-o'clock flank is at
   **−X**, the bracelet runs along **±Y**, crystal top at z = 0, caseback at
   z ≈ −12. Print these five checks; the smoke test caught a wrong-side flank
   extraction purely because this line existed.
   Measurement definitions (so numbers are comparable across runs): *crystal
   flat radius* = r99 of vertices within |z| < 0.15 of the crystal plane;
   *caseback flat boundary* = radius where the surface departs its plane fit by
   > 0.1 mm (the rim is a smooth blend — an undefined criterion costs ±0.15 mm).
   Two fits fail silently: a Kåsa circle fit on a **filled** disc converges on
   an arbitrary inner ring — take the percentile radius of all near-plane
   points, or fit a thin annulus at it; and find the caseback plane by an
   **area-weighted z-histogram of down-facing faces**, not the lowest
   down-facing cluster (on the 126713GRNR: another surface, −10.12 vs −12.164).

## Stage 1 — Facet inventory first

Before any geometry, write the piece list (id, facet, recipe class, clearances)
and get it confirmed. The operator did exactly this mid-project (a screenshot
collage with red outlines per facet — "one piece per facet, round the corners")
and productivity jumped afterwards. Typical watch kit: crystal disc (with cyclops
cut-out if present), bezel annulus, caseback disc, case flanks (crown side split
at the crown guard; 9-side one piece lug-tip-to-lug-tip), 4 lug tops, lug
sides/undersides as needed, crown-guard facets, bracelet-link pieces per link,
clasp facets. See `references/piece-catalogue.md` for the two complete worked
kits, plus Kit 3 (126713GRNR) as a PROVISIONAL inventory — record in progress,
not a fixture.

Two maintainer-delivered kits anchor this: the 126500 (67 pieces) and the **228235 Day-Date 40, 58 pieces**
(measured in `references/e2e-228235-manual-diff.md`) — bezel annulus, crystal disc + cyclops hole, caseback
centre + rim annulus, 4 lug tops, 4 lug unders, one 9-side flank, **ONE** crown-side piece, 44 bracelet
pieces (7 links/run); **no** crown, clasp, lug-inner or lug-outer-wall pieces (a lug outer wall = flank end).
That manual kit is the **minimum scope, not the rule** (maintainer ruling 2026-09-05): ours carries **both**
crown-side halves (**NXLEARN-228235 R3a**), the **whole bracelet to the clasp**, every link the scan shows
counted from the mesh (**NXLEARN-228235 R5b**), and **all seven coverage extras** (**NXLEARN-228235 R8**).

## Stage 2 — Five construction recipes

Pick per facet. All sheets are built in 3D on the mesh so they can be *checked*
against it; only their developed outlines reach the DXF.

**A. Planar facet → parametric outline + typed clearance.** Flat facets are
drawn, not flattened: fit the boundary (circle or section outline), apply a
clearance, make the face directly in 2D.
- crystal disc = bezel bore Ø − 2×**0.35 mm** (126500: Ø30.0 → Ø29.3). The bore
  is a **declared/typed value, not fittable**: the crystal→bezel groove is
  scanner-bridged on real scans (verified — no separate loop exists at any z).
  Fallback: fitted crystal-flat boundary (per the Stage-0 definition) minus a
  derived edge margin (228235: Ø30.8 on a measured ≈Ø31.2–31.6 crystal, i.e.
  0.2–0.4 mm inside — derive, don't hard-code); the 228235 *shipped* at **Ø30.724** vs that typed 30.8
  (**NXLEARN-228235 R6, decided** — record 30.72 as delivered, 30.8 stays the construction value)
- caseback disc — **the clearance sign follows the reference boundary, state
  which you used**: record R1 fitted the caseback **rim-edge** arc (R 13.469) and
  **inset −0.2 mm** → Ø26.54 (default); record R3 fitted the **flat-centre
  boundary** with a 3-point arc (R 10.586, Ø21.17) and offset **+0.15 mm outward**
  → Ø21.47, landing on record R2's typed Ø21.5. Fit the flat patch's own plane;
  the mesh bbox floor sits ~0.3 mm lower. Which boundary is standard is
  **NXLEARN-126713 R4 (open)** — keep the record-R1 inset until answered. Note
  both are *insets* in practice: on the 126713GRNR the mesh flat boundary is
  R 11.24, so the record-R3 arc sits ≈0.65 mm inside it and the +0.15 mm offset
  still leaves the film ≈0.5 mm inset — the conflict is which curve was fitted,
  not the intent.
- cyclops / logo cut-out = section outline, smoothed, offset **+0.15 mm** outward as clearance,
  subtracted from the disc. The **shape is per-watch, not a template**: record R2's is a rounded
  rectangle (~7.1 × 5.8, arcs R3.41/3.54, fillets R1.0), record R3's is a **lens** (two near-flat arcs
  6.1 mm apart, R3.5 end-caps, R0.3 corner fillets, offset toward the crown/date side) — extract it per
  scan (**NXLEARN-126713 R9, open**); only the +0.15 mm clearance carries over. Delivered 228235
  outline (**NXLEARN-228235 R4, decided**): tangent-fillet lens **7.353 × 6.095**, four **R 1.349**
  fillets about their own corner centres + two **R 3.691** flank arcs about theirs, the lens centred
  **(+10.073, −0.148)** from the crystal-disc centre
- bezel film = flat annulus; the operator deliberately did NOT develop the sloped bezel (TPU tolerates
  ~2 mm of slope over 3 mm of width; flag this per watch). **Outer edge runs to the case edge, film over
  the fluting** (126500 typed Ø38.8/Ø30.0; 228235 Ø38.36); the bezel/crystal seam is a **0.35 mm gap** —
  crystal disc = bezel bore Ø − 2×0.35 (228235 typed bore Ø31.5 → Ø30.8): maintainer ruling 2026-09-05
  (**NXLEARN-228235 R2a, R2b**). The manual **Ø35.50 / Ø29.85** (outer stopping *before* the flutes, bore
  **0.437 mm INSIDE the crystal edge = an overlap**) is a measured fact of one kit, **not the rule**
- caseback rim = a standard annulus piece, not an extra: outer = the caseback flat-boundary radius,
  inner = centre disc Ø + 2×0.276 mm seam (228235: **Ø27.85 / Ø22.00**, width 2.925, 229.0 mm², its two
  loops concentric to 0.000000 mm); the ±8 % area exemption is **dropped** (**NXLEARN-228235 R1,
  decided 2026-09-05**)

**B. Prismatic facet → mid-plane profile × extrusion (K = 0 exactly).** For
facets with one straight generator direction (bracelet link tops, the lug-end
wall between lugs, clasp covers):
```python
sec = mesh.section(plane_origin=o, plane_normal=n_axis)  # mid-plane section
prof = fit_smoothing_spline(section_polyline, reject=0.07)  # outlier-rejecting fit
sheet = extrude(prof_edge, span, dir=side_plane_normal)  # BRepPrimAPI_MakePrism on a wire
```
Extrusion direction = normal of a plane fitted to the facet's *side* face (this
encodes the bracelet taper, ±4–5°); trim the sheet ends with planes normal to
the profile at its endpoints, side edges with the fitted side planes (offsets
0–0.5 mm). Development is analytic: profile arc-length × span — no solver.
The operator *tried* lofting between two noisy parallel sections first and threw
it away for this recipe; don't repeat that dead end.

**C. General curved facet → ruled sheet between two boundary curves.** For
flanks, lug tops, lug sides:
1. Extract the facet's two long boundary curves from the mesh. **This is where
   all the difficulty lives, and the downstream gates CANNOT catch a wrong
   boundary** — four plausible criteria on the real 126500 flank gave pieces of
   151–302 mm², all passing every gate. What worked in validation (smoke test):
   march the region in angular/arc-length bins (0.5° silhouette bins for a
   flank), in each bin take the extreme wall point filtered by normal
   (top edge: n_z ≤ +0.3; bottom: n_z ≥ −0.6), cap with z limits, apply a
   median-continuity filter, trim tips below min width; then
   `ruled_sheet.fit_smoothing_spline(pts, reject=0.07, degree=5)`. Naive
   dihedral-ridge thresholds fail — the edges are blend-rounded; the boundary
   criterion, not the fit, dominates accuracy (0.2–0.5 mm). **Therefore gate
   dimensions explicitly**: compare the developed piece's principal dimensions
   and area to the facet region's measured extents (and to
   `references/piece-catalogue.md` on known watches) before accepting.
2. `ruled_sheet.ruled_face(curve_a, curve_b)` (NX "Through Curves", 2 sections,
   G0, parameter alignment). Both curves must terminate on a common transverse
   *closing curve*; trim the sheet end by extruding that closing curve into a
   cutter sheet (the record's cutter spans: −2.5…+1.8, −22…+2.4, −4.5…+5.9 mm)
   and splitting.
3. **Gate before accepting**: `ruled_sheet.developability(A, B)` —
   `K_abs_mean ≤ 1.5e-2 mm⁻²` (worst piece the maintainer kept; typical pieces
   are 1e-4…1e-3). Above the gate the facet is not one film piece: split it at a
   ridge and re-run. These sheets are *near*-developable skew ruled surfaces,
   not exact developables — that is fine at watch-facet size (proven ≤0.4 %
   strain) but is why the gate exists.

**Crown-side flank (maintainer ruling 2026-09-05, NXLEARN-228235 R3a/R3b).** Build **both** halves,
FLANK_3C_12 + FLANK_3C_6 — the 6-side half is the mirrored template unless its own mesh region differs;
the manual kit's lone crown-side piece (**22.75 × 5.25 mm, 88.9 mm²**, *not* a C) was an oversight.
Crown notch arc = **crown radius at the flank height − 0.15 mm, about the crown axis** (film edge tucks
0.15 mm inside the crown edge; 228235: r99 2.925 → **R 2.775**), not the manual R 2.895 or our R 3.71.

**N. Curve-network facet → Coons patch from 2 primary + 2 cross curves.** For a
facet whose two transverse ends are *themselves curved*, a 2-section ruled sheet
cannot represent the ends and cuts the corner in the middle. Proven case: record
R3's lug-flank/case-shoulder transition (`Through Curve Mesh(17)`, 41.85 mm², one
piece mirrored to all four lugs). *Do not silently apply it to lug outer walls —
the standing rule is that those are flank-sheet ends, not separate pieces
(**NXLEARN-126713 R1, open**; corroborated by the delivered 228235 kit, whose
one-piece FLANK_9 ends **are** the lug outer walls).*
1. **Trigger — measure before committing to recipe C.** Build the recipe-C
   candidate on the two long boundary curves, then measure the facet's transverse
   closing curves (recipe C step 2 already requires them) against it. Use recipe
   N when **either** (a) max distance from a closing curve to the ruled sheet
   **> 0.20 mm**, or (b) the **sagitta** of a closing curve **> 0.20 mm**.
   Measure the sagitta on the **mesh-derived** closing curve, never on the built
   sheet — the end of a 2-section loft is a straight ruling, so its sagitta is 0
   by construction and the check would be self-referential. On the record-R3
   facet these read **2.293 mm** and **0.590 mm**, against 0.00–0.37 mm end
   iso-lengths on the ruled sheets the operator did keep. **0.20 mm is
   PROVISIONAL — n = 1 positive example (NXLEARN-126713 R6, open).** Resolution
   honesty: the B-rep projection itself resolves ~1e-9 mm, but a mesh-derived
   closing curve carries the **0.2–0.5 mm boundary-extraction uncertainty of
   recipe C step 1** — the same order as the threshold — so readings in
   0.20–0.50 mm are a grey zone that needs a human call; only readings ≥ 0.5 mm
   (record R3: 2.293 / 0.590 mm) are decisive on their own.
2. **Build** with `curve_network_sheet.py`: draw the two long primaries on the
   mesh, then build each cross curve *from the primaries' endpoints* so corners
   coincide exactly (0.0 mm, not "within tolerance" — this is a precondition, not
   a check); then `GeomFill_BSplineCurves(p0, c1, p1, c0, GeomFill_CoonsStyle)` →
   `BRepBuilderAPI_MakeFace`, which reproduces the input curves to 1e-14 mm. All
   four NX continuity fields were **G0 (Position)** — do not add tangency.
3. Use `BRepFill_Filling` only for N-sided (≠4) patches: it *approximates* the
   boundary (5e-4 mm) and gives a 14 % different interior. For ≥3 primaries OCC
   has no Gordon surface — port TiGL's `CTiglInterpolateCurveNetwork`; the
   Filling-with-interior-constraint shortcut is ~0.1 mm loose, not enough for a
   film boundary.
4. **Develop with LSCM, not `unroll_strip`** — the patch is not ruled (Stage 3).
5. Failure mode to avoid: every abandoned record-R3 attempt used **1 primary +
   1 cross** on an over-large region and NX answered *"Output is
   self-intersecting."* Cost note: the kept network took **21.9 s**, vs a 20.6 s
   mean for a kept ruled sheet — building one is cheap; *deciding* it is needed
   is what costs (six abandoned re-opens, 158 s).

**D. Repeated elements → one template + measured pitch + per-instance trim.**
Bracelet links: section one link transversely → fit circle (Kåsa/Pratt, 0.07 mm
rejection; e.g. link crown R 2.88 on the 228235, R 2.63 on the 126713GRNR
Jubilee centre row — whose five rows share one 6.5 mm pitch with **no stagger**,
measured 0.0 ± 0.33 mm) or profile → build recipe-B
sheet → replicate at the pitch **measured from the mesh** (gap minima of the
link-top profile — 126500 ≈10.25 mm; the operator eyeballed 10.0/10.5 and
drifted 0.5 mm by link 4) → re-trim each instance to its own link width (the
126500 tapers only over links 1–2, then parallel; widths 4.6→2.7 mm). In the 2D
kit the operator then *re-idealised* links as one rectangle per size class at a
uniform 11.0 mm pitch — see Stage 4.

*Link rule (maintainer ruling 2026-09-05, NXLEARN-228235 R5a/b/c).* A link piece wraps **≈80° of the
link crown, never the full exposed ~150°**: developed centre-link width **≈ 4.0 mm on R 2.88**, side
links **3.2–4.9 mm** per row. Construct it as the fitted crown arc **minus the in-surface insets** (the
record's Fit Circle sampled 28 section points at 0.15 mm ≈ **4.05 mm of arc** — *consistent with* that
width, not a proof of it). Cover the **whole bracelet to the clasp**, counting links from the mesh (the
manual's 7/run and our 5/run were both partial); build **one template per family**, regularise it,
mirror/copy for the rest, log measured → chosen — per-instance outlines only where a mesh region differs.
*Delivered 228235 link geometry (measured).* Every link is an **exact rounded rectangle**, R 0.3 corner
fillets about their own corner centres: centre **7.793 × 4.047** ×13 (= 80.6° wrap on R 2.8787) + one
case-end **7.794 × 3.431**; side **L 5.295 constant, W 4.896 → 3.197**, 14 rows/run. In-surface margin:
`Offset in Face` → `Divide Face` at **0.55 / 0.65 / 0.75 / 0.85 ×4 mm** (graduation unexplained — the
record cannot answer it) plus a **0.30 mm end inset along the link axis**. **Retire "pitch 6.8 × 10"**:
6.8 is neither the mesh pitch (**6.12 ± 0.10**) nor the delivered sheet pitch (**7.99**, layout only);
"4.7" is the side-link straight edge **4.695** and **no 5.1 class exists**. Apply that margin in Python
as a 2D inset of the *developed* outline: `shapely.buffer(-d, join_style="mitre")`.

**Mirroring policy**: scans are not symmetric — the record shows every mirrored
copy needed manual nudges (0.1–0.7 mm translations, 0.65–1.5° rotations).
Mirror the *outline* for kit symmetry (Stage 4), but if a 3D fit check matters,
build each side from its own mesh region instead of trusting `mirror()`.

**Small normal offsets** (0.05–0.15 mm sheet lifts in the record) were visual
aids only — a pure translation does not change the developed outline. Skip them.

## Stage 3 — Develop + fidelity gates

- Recipe A pieces are already 2D. Recipe B: analytic unroll.
- Recipe C/D: `fa, fb, dev, rep = ruled_sheet.unroll_face(face)` or
  `unroll_strip(A, B)` on matched samples; outline via `outline_polygon`.
- **Recipe N: develop with LSCM, not `unroll_strip`.** A Coons patch is not
  ruled, so unrolling it along rulings is not justified by construction: on the
  record-R3 network face the strip development is **8.22–8.30 %** wrong in area
  (systematic — identical at n = 60/120/240) while LSCM is **0.028–0.059 %**, a
  factor of 290. LSCM's mean edge strain there is 0.263 % (inside the gate); its
  **max is 1.066 % (outside)** — see the network-piece question below.
  `curve_network_sheet.flatten_paths` runs both paths side by side.
- **Hard gates** (fail the piece, not warn): `developability` pass =
  K_abs_mean ≤ 1.5e-2 **and** K_abs_max ≤ 6.5e-2 mm⁻²; `flattening_report`
  pass = interior **iso-curve strain ≤ 0.4 %** plus area error vs the
  independent B-rep face area ≤ 0.4 %. (The strip development is isometric to
  its own samples by construction — never "validate" it against itself; the
  bundled report measures interior strain and an independent area precisely for
  that reason.) Record per-piece {K_abs_mean, K_abs_max, iso_strain, area_err}
  in the run manifest. These gates check *development*, not *boundary choice* —
  the dimension cross-check of recipe C step 1 is a separate mandatory gate.
- **Report the K gate's sampling with the number — the discrete max is not
  grid-invariant.** `ruled_sheet.developability(A, B, m=7)` measures the angle
  defect on an **n × m grid with m = 7 by default**, n = the number of matched
  boundary samples; the thresholds above were set on that sampling. The *same*
  record-R3 face scores K_abs_max **3.12e-2 (pass) at 41×7** and **8.71e-2 (fail)
  at 41×41**. The mean is far more stable (9.0e-3 → 1.19e-2). The grid-independent
  **reference is the analytic curvature** (`BRepLProp_SLProps`; 1.10e-1 max on
  that face) — quote it alongside the discrete number, and whenever the two
  disagree treat the analytic value as the truth about the surface. Pinning the
  gate to a stated (n, m) or moving it to analytic curvature is **NXLEARN-126713
  R3 (open)**; thresholds are unchanged until then.
- **Open: network pieces fail these gates as written.** The record-R3 piece the
  maintainer kept has analytic K_abs_max 1.10e-1 (1.7× the gate) and needs ≈1.07 %
  local strain to flatten. Either recipe-N pieces get a documented variant gate
  or the facet must be sub-split — **NXLEARN-126713 R2 (open)**, no silent fix.
  Until then a network piece fails Stage 3 and the failure must be reported, not
  waived.
- Orientation: choose the development's U direction deliberately (watch axis
  along the piece) and keep each piece's outer-surface side up (+Z); the
  operator's ad-hoc per-piece orientation cost him 15° correction rotations in
  record R1, and in record R3 it was the single biggest friction of the
  flattening session — **34 U-direction clicks against 15 Origin picks, 8 V picks
  and 9 Reverse Direction toggles** in 24 minutes. Record a handedness flag per
  piece — which side is adhesive is a contract decision, not a guess.
- **The dialog defaults are confirmed twice over.** Type *Flattening*, no Outer
  Boundary, Constraint Group "Flattening with" **None**, no Rip Edge,
  Transformation Objects none, Distortion Map off — uniform across all 15 of the
  228235's flats (live-captured on F&F(189)) and all 7 sampled record-R3
  screenshots. Record R3 adds that a `Specify CSYS` alternative to the ad-hoc
  Origin+U+V exists and that a **compound multi-face source** can be flattened in
  one operation. Layout in both was 100 % mouse-drag with no typed distances — a
  port should type them.
- **228235 development facts** (`e2e-228235-manual-diff.md` §7): all **15/15** flats landed in place
  on **z = 0**; ΔA **0.003 %** (FLANK_9), 0.002 % (a 3-face patch), 0.18 % (a lug-under candidate),
  all inside the gates above. 3 of the 18 create events duplicate features 185/187/193 (event
  timestamps 0.09 s apart, linked screenshots 23–33 s apart) — capture duplicates or immediate edits;
  the record cannot say. Only **4–5 representative link instances of ~36 link bodies** were flattened:
  one template per size class, replicated in Stage 4.

## Stage 4 — Regularise (the step naive ports skip)

The delivered DXF is NOT a raw trace of the developed sheets — the reviews
proved only ~40/63 loops match a flattened face verbatim. The maintainer:
- kept only each strip's **main face** (dropped the 1.4 mm edge-bevel faces);
- redrew near-rectangular pieces as exact rectangles/trapezoids, unified the
  four outer-link rows to one outline per size class, re-spaced centre links to
  a clean 11.0 mm pitch;
- replaced developed spline edges with arcs (cutters dislike splines);
- made the +Y row a mirror of the −Y row instead of using its own noisier trace.

So: snap developed outlines to primitives when within scan noise (lines, arcs,
circles; symmetry about the piece axis), unify pieces whose outlines differ by
less than the cut tolerance, and *log every regularisation* (measured → chosen),
exactly like the stl2step skill's snapping rule. Then fillet every convex corner **R 0.3 on links, lugs
and tabs, R 0.4 on long flank pieces** — maintainer ruling 2026-09-05 (**NXLEARN-228235 R7**); R 0.2
shipped first and was physically rejected. The 228235 manual kit measures exactly that split: **R 0.3 on
206 of 217 sub-2 mm arcs (95 %)**, R 0.4 only on its two flank pieces.

**228235 shows how far this stage goes** (inferred — 2D pass uncaptured, §0 evidence caveat): one
idealised template per family — **the rule since the 2026-09-05 ruling (NXLEARN-228235 R5c)** — 4
identical lug tops **15.01 × 4.59**, 4 identical lug unders **17.16 × 4.32**, 13 identical centre links;
links redrawn as exact rounded rectangles, **zero splines**, crystal/bezel/caseback-centre redrawn
**0.1–0.2 mm smaller in Ø** than their flats. Per-instance outlines turn one lug-under delta into four
18–25 % area misses. (Record R3 never reached this stage — its 2D pass is *unknown, not absent*.)

## Stage 5 — Nest, write, validate

- Nest with explicit gaps: pieces ≥ **1.0 mm** apart (126500: median 1.3, min 0.62; 228235 manual: min
  **1.497**); nest a disc or annulus inside a hole at ≥ **1.0 mm** — **pass `nested_gap=1.0`
  explicitly** unless the nested piece is the hole's own coverage partner (the writer's default 0.35 is
  the Daytona crystal-in-bezel case; **NXLEARN-228235 R10, decided**; the 228235 nests its rim annulus
  in the bezel bore at exactly 1.000 mm). Group by family (link rows together, mirror pairs adjacent,
  mirrored about a visible axis); slender pieces may rotate 90°. Sheet footprints: 126500 123 × 85;
  228235 **62.97 × 160.01 mm**.
- Write with `dxf_kit_writer.write_kit(...)`: R2004, mm, closed LWPOLYLINEs
  (CCW outer on `CUT_OUTER`, CW holes on `CUT_INNER`), TEXT ids on `LABEL`,
  XDATA piece ids, real `$EXTMIN/EXTMAX` (NX wrote bogus ones). Byte-identical
  re-runs require **`PYTHONHASHSEED=0`** in the environment (ezdxf object
  ordering follows hash randomization) on top of the writer's fixed-metadata
  switch. Neither NX kit carries **any labels** (126500: 67 pieces; 228235: 58, drawn as exact
  **195 LINE / 261 ARC / 6 CIRCLE** on a single layer) — ours always labels. **Finding F-A: our own r2
  228235 kit came out fully polygonised (8 237 chords, 0 bulges, min segment 0.080 mm) against this
  contract — logged as a separate fix task, not fixed here.**
- Gate with `dxf_kit_writer.validate_kit(...)`; `ok: False` = do not deliver.
  It enforces the defects actually observed in the delivered kit: open chains
  (0.052 mm corner mismatches, 0.715 mm horn gaps), micro-segments (0.013 mm
  arcs), POINTs on cut layers, overlaps, min gap, and a **narrow-feature
  erosion test** (a shipped piece had a 0.73 mm-wide tip that a
  largest-inscribed-circle check cannot see).
- Emit a sidecar `kit_manifest.json`: piece id → outline source (facet, recipe,
  regularisations), area/bbox/perimeter, mirror partner, gates passed, DXF
  SHA-256. Bind to the run bundle per repo rules.

## Parameter card (measured defaults — override per watch, never silently)

| Parameter | Value | Source |
|---|---|---|
| fit outlier rejection (plane/circle/spline) | 0.07 mm (record-R1/R2 default; record R3 shows 0.03 on ≥1 plane fit — declare it **per fit**; **NXLEARN-126713 R11, open**) | records R1/R2 dialogs; record R3 S1 screenshot 20:30:47 |
| section sampling / tolerance | 0.15 mm / 0.010 mm | Section Curve dialogs |
| boundary spline degree | 5 | every Studio Spline |
| bezel outer edge / crystal-in-bezel seam | outer runs **to the case edge**, film over the fluting (228235 Ø38.36); seam = **0.35 mm radial gap**, crystal disc = bezel bore Ø − 2×0.35 — **NXLEARN-228235 R2a/R2b, decided 2026-09-05**. The manual Ø35.50 stop-before-flutes and its **−0.437 mm overlap** are measured facts of that kit, **superseded as rules** | Offset Curve(229); 228235 loops #55/#59/#60 |
| caseback disc clearance | **−0.20 mm inset off the fitted RIM-EDGE arc** (record-R1 default, R 13.469 → Ø26.54); **+0.15 mm outward off the fitted FLAT-CENTRE boundary** (record R3, R 10.586 → Ø21.47). Sign follows the reference — state which (**NXLEARN-126713 R4, open**) | Offset Curve(194); record-R3 `Arc(35)` p137–p145 + `Offset Curve(36)` p148 |
| cut-out (cyclops/logo) clearance | +0.15 mm outward; **outline shape extracted per watch** (**NXLEARN-126713 R9, open**) | record-R2 sketch offset, record-R1 crown logo |
| crown notch radius | crown radius at the flank height **− 0.15 mm**, **about the crown axis** — **NXLEARN-228235 R3b, decided**; 228235: r99 2.925 → **R 2.775**. Supersedes our +0.30 mm and the manual R 2.895 | 228235 loop #2 |
| link wrap | **≈80° of the link crown**: developed centre-link width **≈ 4.0 mm on R 2.88**, side links 3.2–4.9 mm per row — **NXLEARN-228235 R5a, decided**; never the exposed ~150° | 228235 delivered links (7.793 × 4.047) |
| link-piece edge margin | **0.55–0.85 mm in-surface** (Offset in Face → Divide Face, 228235 final tree; graduated 0.55/0.65/0.75/0.85, cause unrecorded) + **0.30 mm end inset** along the link axis (2D) | 228235 feature tree + delivered DXF |
| trim-plane offsets from fitted side planes | 0–0.5 mm | link trims |
| corner fillet | **R 0.3 on links/lugs/tabs, R 0.4 on long flank pieces** — **NXLEARN-228235 R7, decided**; R 0.2 physically rejected. Matches the 228235 census (0.3 on 95 % of corners, 0.4 on the flanks) | RV01→RV02; 228235 arc census |
| piece gap in nest / nested-in-hole gap | ≥1.0 mm / ≥1.0 mm — pass `nested_gap=1.0`; the writer's 0.35 default is only for a hole's own coverage partner (Daytona crystal-in-bezel). 228235 manual: min **1.497**, nest **1.000** (rim in the bezel bore) | delivered kits (**NXLEARN-228235 R10, decided**) |
| recipe C→N trigger | closing-curve deviation from the ruled candidate **> 0.20 mm**, or closing-curve sagitta **> 0.20 mm**, measured on the mesh-derived curve — **PROVISIONAL, n = 1** (**NXLEARN-126713 R6, open**) | record R3: 2.293 / 0.590 mm observed vs 0.00–0.37 mm on kept ruled sheets |
| developability gate | K_abs_mean ≤ 1.5e-2 AND K_abs_max ≤ 6.5e-2 mm⁻², **measured on the n×7 angle-defect grid `ruled_sheet.developability` uses**; quote the analytic (`BRepLProp_SLProps`) value beside it — the discrete max swings 2.8× with the grid (**NXLEARN-126713 R3, open**) | worst kept sheet; record-R3 grid study |
| network-piece curvature/strain (NOT a gate) | record R3's accepted network sheet: analytic K_abs_max 1.10e-1, LSCM strain max 1.066 % / mean 0.263 % — **fails the gates above**; variant gate vs sub-split is **NXLEARN-126713 R2, open** | record-R3 RV04 STEP + prototype |
| development strain gate | iso-curve strain ≤ 0.4 %, area vs B-rep ≤ 0.4 % | worst kept piece |
| min segment / narrow-feature width | 0.05 mm / 1.5 mm (warn) | defect census |

## Pitfalls (each cost the operator or a prior spike real time)

- **Loft through parallel noisy sections** → wavy sheet; use recipe B. (Deleted
  in-record within minutes.)
- **Synchronous face ops on open sheets**: the 08-19 Divide/Replace/Offset-Region attempts failed
  repeatedly, but the **`Offset in Face` → `Divide Face` pair DID converge** on the 228235 — 7 + 7
  features at 0.55–0.85 mm survive in its final tree, built in an untraced session between 08-19 and
  08-30. In Python still apply margins as a **2D inset of the developed outline**, not a surface op.
- **igl.ARAP segfaults** on the Windows libigl 2.5.1 wheel; igl.lscm works; a
  scipy local/global ARAP is deterministic — but with this skill's recipes you
  rarely need either.
- **Raw mesh normal offsets self-intersect** (5 % bad faces at 0.5 mm on real
  scans) — another reason to build sheets from curves, not offset meshes.
- **ezdxf determinism** needs `write_fixed_meta_data_for_testing = True`
  (handled by the bundled writer). **R12 cannot carry LWPOLYLINE/$INSUNITS** —
  target R2000+; only fall back to R12+POLYLINE if a machine demands it.
- **MAX_PATH on Windows**: stage STEP/venv work under a short path (`C:\spk`).
- **Zero-depth extrude on a doubly-curved patch fails**: record R3 hit *"Cannot
  extrude. The distance or direction may be incompatible with the section"* ×3
  trying to make a planar sheet from a curve drawn across a lug-root saddle.
  Recipe A needs a *planar* section; use a ruled or network sheet there.
- **Self-intersecting section curves**: *"Cannot add to section"* ×7 in record R3
  — fix the curve, don't retry the operation.
- **Cloud-mapped drives lock saves**: *"Save Failed … No write access"* ×7 on a
  Google-Drive-mapped `H:` in record R3, one dialog left open ~15 min. Work on a
  local path and sync afterwards.
- Feature-history noise ≠ method: NX renumbering, capture-tool "Information"
  spam, and idle reloads all masquerade as work in any session record — trust
  geometry artifacts over event counts. **Four capture-tool traps, measured
  across both records** (record R3:
  `tasks/NXLEARN-126713/run/RECORD_MAP_CORRECTIONS.md`; record R2: the 228235
  08-30 sessions): **(a) duplicate journals** — two concurrent NXOpen journals
  doubled every raw count, the same create/modify/delete cycle logged twice one
  second apart [record R3]; **(b) save-time batch flush** — all "created" timestamps
  collapse onto save instants (`detection_method: feature_inference`), so
  authoring times are wrong *and* ≥9 scaffolding features purged between flushes
  never appear at all [record R3]; **(c) Save-As revision replays** — 21 "deletions"
  that are pure renumbering, firing only at the two document changes, with
  expressions matching 1:1 across the hop [record R3; the 228235 record hit this
  independently]; **(d) session-open replay** — at session open the tool replays
  every pre-existing feature as a fake `nx_feature_created` event (167 in < 1 s
  on 08-30), so split the event stream at the max feature id of the first model
  snapshot before counting anything as new [record R2 / 228235]. Net effect on record R3:
  138 raw Splines → **50**, 47 Through Curves → **20**, "5 Through Curve Mesh" →
  **1**. De-duplicate against the final feature tree before drawing any
  conclusion.
- **A DXF loop count is not a piece count**: subtract holes, then discount scrap — the 228235's
  **61 loops = 58 piece outlines + 3 holes**; its 1.0 mm bezel-bore/rim band is scrap, not a 62nd loop.

## Definition of done

Every piece passed its developability + development-strain gates AND its
dimension cross-check (piece principal dimensions vs facet-region extents /
catalogue) — a recipe-N piece that fails is **reported, never waived**
(NXLEARN-126713 R2 is open); regularisations logged (one template per family,
measured → chosen); `validate_kit` ok (incl. real extents);
manifest written; DXF re-read round-trip reproduces the same loops at 0.01 mm;
byte-determinism verified under `PYTHONHASHSEED=0`; totals sanity-checked
against the reference kit numbers in `references/dxf-contract.md` when working
on the same watches.
