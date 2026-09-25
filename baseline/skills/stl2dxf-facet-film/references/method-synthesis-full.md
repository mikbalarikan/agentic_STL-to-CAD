# METHOD SYNTHESIS — The maintainer's STL → DXF facet-film method

**Status: COMPLETE (2026-08-23).** Unified, tool-agnostic description of the method the
maintainer performed manually in Siemens NX across two recorded projects, distilled from six
extraction reports and six skeptical reviews. Wherever a review CORRECTED or REFUTED a report
claim, the corrected fact is used here (the correction is noted inline as `[RVn]`).

Sources (all in `…/scratchpad/analysis/`):
`R1_part1_method.md` + `_review.md` (RV-P1), `R1_part2_method.md` + `_review.md` (RV-P2),
`R1_part3_part4_layout.md` + `_review.md` (RV-P34), `R2_method.md` + `_review.md` (RV-R2),
`DXF_contract.md` + `_review.md` (RV-DXF), `STEP_geometry.md` + `_review.md` (RV-STEP).

Records:
- **Record 1 (R1)**: Rolex **Daytona 126500** (`Daytone 126500 v2.stl`, 36 MB, 734,459 facets,
  2 shells — main body 655,899 facets + detached bracelet-tail 78,574 facets). Full pipeline
  executed: alignment → facet sheets → flattening → 2D layout → 4 delivered DXFs (v1, v2,
  RV01, RV02).
- **Record 2 (R2)**: Rolex **Day-Date 40, ref. 228235** [RV-R2: NOT "Sky-Dweller 42 mm"]
  (`228235.stl`, 149 MB, 2,979,045 facets). Refined 3D facet-extraction method (better
  alignment recipe, bracelet-link recipe, clearance offsets). The 08-19 sessions stop before
  flattening — the earlier "never reached flattening or DXF" reading is **superseded**: **R2 was
  flattened, laid out and delivered as DXF on 2026-08-30** (61 loops / 58 pieces / 3 180.6 mm²
  net film) — corrected 2026-09-05, see `e2e-228235-manual-diff.md`. Its ten rulings
  (**NXLEARN-228235 R1–R10**) were **all decided by the maintainer 2026-09-05** and are rules.
- **Record 3 (R3)**: Rolex **GMT-Master II 126713GRNR** (Jubilee bracelet), captured 2026-08-30
  and 2026-09-04 — added after this synthesis was frozen and **still in progress**: no DXF, no
  bracelet piece as of `126713GRNR-RV04.prt`, final state uncaptured. It confirms most of this
  document and corrects four things: the `Through Curve Mesh` dead end (§E.1), the fit-rejection
  and caseback-clearance rows (§D), and the CSYS-move associativity (§B2 step 4). §B8
  (flattening) it **confirms and extends**, contradicting nothing — and record R2's own 08-30
  flattening session (15 flats, uniform dialog) confirms it a second time. Its own end-to-end
  write-up is `e2e-126713-method.md`; every record-R3 number is PROVISIONAL pending
  `tasks/NXLEARN-126713/run/RULINGS.md` (**NXLEARN-126713 R1–R11, all still open**).

> **Ruling namespace.** `NXLEARN-228235 Rn` = decided 2026-09-05, a rule; `NXLEARN-126713 Rn` =
> open, so the default it guards is PROVISIONAL. Bare **R1/R2/R3 are record labels** (Daytona /
> Day-Date / GMT-Master), never ruling ids.

Product intent (confirmed by the operator's own reference image `reference template
example.jpeg` and his Paint spec sheets `Untitled.png` in both records): a **FACET-FILM KIT**
— one flat protective-film piece per watch facet (bezel, crystal, caseback, lug tops, case
flanks, per-link bracelet pieces, clasp pieces), no seams, no stretching, no darts/relief
cuts. Not a single wrapped cover.

---

## A. Pipeline overview

| Stage | Input | Operation | Output |
|---|---|---|---|
| **A0. Import** | scanned binary STL (35–150 MB, raw scanner frame, dial tilted 12–15° from Z, possibly multiple shells) | load mesh as facet body; never convert whole scan to B-rep | mesh in memory |
| **A1. Canonical alignment** | raw mesh | fit plane to crystal facets (outlier rejection 0.07 mm) → Z; fit circle to crystal edge (centre only; radius operator-constrained) → origin; derive in-plane axis from planar fits (R1: bracelet flanks+top; R2: two lug-tip planes of one end); build frame; rigid-transform mesh; discard scaffolding | mesh in canonical frame: origin = crystal centre, z = 0 = crystal top plane, caseback z ≈ −12.1…−12.4 |
| **A2. Facet inventory (spec)** | aligned mesh + operator knowledge | enumerate the facets that get a film; annotate boundaries, margins, "round it", per-family notes | facet list (≙ repo `approved_anatomy_manifest`) |
| **A3. ROI isolation** | mesh | crop regions of interest (bracelet link, clasp, lug region) with a sketched-polygon prism → split → delete tool | small sub-meshes (~10³ facets) for sectioning/fitting |
| **A4. Per-facet 3D sheet** | sub-mesh + facet spec | one of 4 constructions: (P) planar sketch piece, (E) extruded-profile developable, (R) ruled loft between 2 boundary splines, (C) fitted-arc cylindrical patch | one B-rep sheet per facet, lying on/near the scan skin |
| **A5. Trim** | sheet + boundary geometry | trim ends/edges: fitted side planes (offset 0–0.5 mm) or extruded boundary/bridge-spline cutter sheets | trimmed facet sheet |
| **A6. Replicate** | trimmed sheet | mirror about canonical XZ/YZ planes + manual nudges (0.1–0.7 mm, 0.65–1.5°) for scan asymmetry; copy along bracelet pitch; re-trim per link for taper | full piece set in 3D |
| **A7. Flatten** | 3D sheets | develop each sheet onto z = 0 (no rip edges, no constraints, explicit origin/U/V frame); planar pieces skip this | flat pieces at z = 0 (ΔA ≤ 0.07 %, worst 0.38 %) |
| **A8. 2D layout** | flat pieces | collect the flat sheets in one 2D context; group-move/rotate into a nest (~1–2 mm gaps, sheet ≈ 123 × 85 mm) | nested layout |
| **A9. Outline idealisation** | nested sheets | trace outlines into 2D curves, then **manually regularise**: keep only main faces, redraw links as rectangles/trapezoids, re-space rows to a clean pitch, mirror rows, hand-draw problem outlines, fillet all convex corners (final R0.4) | clean 2D curve set |
| **A10. DXF export** | 2D curves | export AC1018 (AutoCAD 2004), mm, loose LINE/ARC/CIRCLE(+1 SPLINE) on one layer | cutting DXF |

Stage A9 is the least automated and most under-appreciated stage: the delivered DXF is **not**
a faithful trace of the flattened sheets — it is a manually idealised drawing that uses the
flattened outlines as a guide [RV-DXF #9, RV-P34 #12]. A re-implementation must decide
explicitly whether to emit raw developed outlines or regularised primitives; the maintainer's
accepted kit is the latter.

---

## B. Stage-by-stage procedure

Frames. R1 working frame (all R1 numbers below): origin = crystal centre, z = 0 = crystal
top, **bracelet along ±X, crown/pushers at −Y, 12 o'clock = +X**; repo canonical frame is
this rotated: `X_repo = −Y_NX, Y_repo = +X_NX` (Rz(+90°)). R2 working frame **equals the repo
canonical frame** directly: +X = crown, ±Y = bracelet (12–6), z = 0 = crystal top
[RV-P1 #1, RV-STEP #17]. Which bracelet end is 12 o'clock was never annotated in either
record (open question H-1).

### B1. Import (A0)

- Load the STL as a facet body. R1: 734,459 facets in **two shells** (watch+bracelet
  655,899 facets / 8,128 mm²; detached bracelet tail 78,574 facets / 971 mm² at raw
  x −180…−143) — a pipeline must expect multiple components and not assume one watertight
  shell [RV-P1 #3]. R2: 2,979,045 facets, one relevant body; loads in 1.3 s with
  `trimesh.load(process=False)`.
- Raw frames measured: R1 bounds x 22.4…87.4, y −135.8…124.7, z −276.7…−236.1; crystal-plane
  tilt **12.33°** from raw Z (normal (−0.19148, −0.09470, 0.97692)) [RV-STEP #2]. R2 bounds
  x −27.4…46.9, y −26.2…146.3, z −259.4…−207.3; tilt 14.8° (normal (0.0309, 0.2536, 0.9668)).

### B2. Canonical alignment (A1)

Both records use the same skeleton; R2's axis recipe differs from R1's. All construction
features are deleted after the move — alignment is a throw-away scaffold; only the
transformed mesh is kept.

1. **Z axis / XY plane**: fit a plane to the crystal-top facets. Facet selection was done by
   **brush-painting a facet region**, with **Automatic Point Rejection, threshold 0.07 mm**
   (0.07 is an outlier-rejection threshold on the painted region, NOT a fit tolerance)
   [RV-STEP #4]. The recurring expression 13.75 on every plane fit is an NX patch-size
   default, not a design choice [RV-STEP corrected facts].
2. **Origin**: fit a circle to the crystal/bezel inner edge points, same 0.07 mm rejection.
   **The radius was operator-CONSTRAINED** (R1: `Radius` checkbox + typed 14.75 mm; R2: 16.0
   mm); **only the centre is fitted** [RV-STEP #3]. Free-fit crystal flat radius measured on
   the meshes: R1 14.65–14.70 mm; R2 ≈ 15.5–16.5 mm (r99 15.6–15.8) [RV-R2 #2]. Rationale:
   the selectable edge points cover only a ~100° arc, whose free LSQ radius is unstable
   (R1: free fit gave 13.7 mm with 1.7 mm residual) — constraining the radius stabilises the
   centre. Centre is then projected onto the fitted plane (`Point` + `Projected Curve`).
3. **In-plane axis**:
   - R1 recipe [RV-P1/RV-STEP #5 — recoverable from screenshots, contrary to the report]:
     planar fits to the **first bracelet link's two side flanks and the bracelet top** →
     datum axes/planes → full orthogonal datum frame. Bracelet direction = X.
   - R2 recipe (refined) [RV-STEP #6 — corrected]: planar fits to the **two lug tips of the
     SAME bracelet end** (centres 20.6 mm apart, normals within 5.6°); each lug-tip plane ∩
     mesh → a chord between two picked points on the intersection curve → chord midpoints →
     a line through the two midpoints = the **3–9 direction** at that end; a datum plane
     through that line at 90° to the crystal plane; the **12–6 axis = that plane's normal**
     through the projected crystal centre. (The extractor's "midpoints of the two 12- and
     6-end lugs" version is wrong; both planes are at one end.)
4. **Rigid transform**: build a datum CSYS from (origin, Z, axis), Move Object CSYS→CSYS
   (non-associative **in R1/R2; R3 used Associative** — housekeeping, not geometry),
   Remove Parameters, delete all 20-odd construction features. Verified
   result: R1 crystal centroid (−0.001, 0.025), z_top 0.00, caseback median z −12.20; R2
   crystal z ≈ −0.02, centre (−0.67, 0.07), caseback flat centre z ≈ −12.1 (mesh floor
   −12.39 — use the flat-patch plane, not the bbox floor) [RV-R2 #6].
5. **Persist the transform** (repo Stage-1 rule); the record itself never stored it — a
   deliberate improvement for the pipeline.

### B3. Facet inventory (A2)

The operator maintained a hand-annotated collage (`Untitled.png`, both records): cropped
viewport screenshots with red hand-traced outlines per facet plus text notes — R2's says
"these are identical" (first 3 clasp-end links), "slightly bigger →" (remaining links),
"round it" (lug-piece corners). This is the human-in-the-loop **facet manifest**: which
facets get film, roughly where each boundary runs, per-family notes. Maps directly onto the
repo's operator-approved anatomy manifest.

### B4. ROI isolation (A3)

Sketch a closed polygon on z = 0 → extrude a prism → split the facet body → delete the prism.
Recorded ROI footprints [RV-STEP #7]:
- R1 link region: 13-line polygon x 30.5…47.0 × y −10.98…12.39 (with notches), prism 0…20 mm.
- R1 clasp regions (one op, two rectangles): x −91…−72 × y −10…11 and
  x −181.5…−141.7 × y −13.47…10.03, prism 0…19 mm.
- R2 lug/bracelet-end region: hexagon (−11.5,32)→(−11.5,17.5)→(15.8,17.5)→(15.8,30.4)→
  (12.25,40.71)→(−12.65,40.71), prism −22…+1.8 mm.
Purpose: all later fits/sections run on a ~10³-facet sub-body instead of the full mesh
(NX visibly slow otherwise). In Python this is a cheap `slice_plane`/submesh, still useful
for robustness of fits.

### B5. Per-facet 3D sheet construction (A4) — four families

**(P) Planar pieces — sketch + zero-depth extrude.** For facets that are already flat and
parallel to a reference plane, the piece is drawn as a closed 2D profile and turned into a
planar sheet with a **zero-length extrude** (start = end = 0). No flattening needed. Used for:
crystal disc, bezel annulus, caseback disc, clasp-lever top rectangles, crown-logo cut-out
piece. Key detail [RV-DXF #4]: the R1 bezel annulus (Ø38.8/Ø30.0) and crystal disc
(Ø29.3 = 30.0 − 2×0.35) are **parametric typed circles** (sketch p3=30, p4=38.8; Offset
Curve 0.35 mm), not measurements of a flattened surface — the bezel film is a deliberate
flat-annulus simplification of the sloped ceramic bezel (Δz ≈ 1.9 mm over r 16→22; open
question H-6). The R2 crystal disc is Ø30.8 (typed), sitting 0.2–0.4 mm inside the measured
crystal edge; caseback disc Ø21.5 (typed).

**(E) Extruded-profile developables (K = 0 exactly).** For singly-curved facets whose
cross-section is constant along one direction (bracelet link tops, lug-end wall, clasp
cover, clasp facets):
1. Section the sub-mesh with the facet's mid-plane (Section Curve, sampled points; R2 sample
   distance 0.15 mm, tolerance 0.010 mm).
2. Project the section polyline into a sketch on that plane; fit a smoothing spline
   (Fit Curve, automatic point rejection, options Closed/Symmetric as needed); trim to the
   facet length. R1's link-profile end trims are datum planes **normal to the profile curve
   at its end points** (end tangents 45°/65°), not vertical planes [RV-P1 #6].
3. **Extrude the profile across the facet width**. Direction: for the tapering bracelet the
   operator fitted a plane to the link's **side face** and extruded along that plane's normal
   (taper ±4–5°); the fit was actually inserted *after* a first default-direction extrude —
   direction is a refinement, not essential [RV-P1 omission 2]. Recorded spans: link sheets
   −2…+2.55 / −3.1…+1.7 / −3.7…+5.05 mm; lug-end wall 0…7.7 mm; clasp cover −4.1…+3.5 mm
   (width 7.6); clasp facet −4.35…+3.9 (8.25); clasp pair band +4.6…+7.4 (one-sided, width
   2.8) [RV-P34 #3].
4. Trim the sheet with the fitted side plane (datum-plane offsets 0, 0.1, 0.2, 0.25, 0.4,
   0.5 mm — per-link edge adjustments) and/or with extruded boundary-spline cutters.

**(R) Ruled lofts between two boundary splines.** For general curved facets (case flanks,
lug tops, lug inner faces, lug undersides, crown-guard/pusher facets, clasp side flanks):
1. Draw the two long boundary curves **directly on the mesh**: Studio Spline, *Through
   Points*, **degree 5**, points snapped onto the facet surface ("Point on Surface —
   Convergent Face"). 2-point splines degenerate to lines (lug-tip underside).
2. Loft a **ruled sheet** between the two curves (Through Curves, 2 sections, continuity G0,
   alignment *Parameter*, Preserve Shape off). Verified: every such sheet is **exactly ruled**
   (degree 3×3 B-spline with 4 poles per ruling, collinear to 0.0 mm) [RV-STEP #9].
3. **End closure**: both boundary curves must terminate on a common transverse curve. R1
   closed the crown-flank loft with explicit end curves — `Line` joining the u=0 ends,
   a `Spline` joining the end of curve A to curve B at parameter 0.9287, and a Trim Curve
   of B at that spline — before lofting [RV-STEP #10]. R2 simplified this to a **bridge
   spline** between the two boundary splines (tangent magnitudes 1.0/1.0) around the
   feature to be excluded (crown guard, lug root), **extruded into a thin cutter sheet**
   (crown: −2.5…+1.8 mm along the flank normal; lug root: −22…+2.4 mm vertical wall) →
   Trim Body → delete cutter.
4. Caveat: these ruled sheets are **not developable** — Gaussian curvature is negative with
   |K|max 0.001–0.039 mm⁻² (Gaussian radius ≥ ~5 mm) [RV-P1 #13]. NX's Flattening strains
   them; area conservation (<0.1 %) is a necessary but weak check. The worst pieces
   (|K|mean ≈ 1e-2: lug flank 32.9 mm², crown guard 22.8 mm²) showed −0.38…−0.43 %
   perimeter distortion. Acceptable at facet sizes ≤ ~50 mm and ≤ 0.1 mm error.
5. Optional cosmetic offset (R2): translate the finished sheet 0.05 / 0.10 / 0.15 mm.
   Measured effect: the sheets end up ~0.03–0.10 mm *inside* the scan skin (the ruled sheet
   between edge curves is a chord of a convex facet), i.e. this mostly re-centres the sheet
   and kills viewport z-fighting. **A pure translation does not change the developed
   outline** — irrelevant for the DXF, relevant only for 3D fit checks.

**(C) Fitted-arc cylindrical patches (R2 bracelet-link recipe — the refined link method).**
1. Section the (split-off) bracelet body with its longitudinal centre plane (YZ offset
   −0.25 mm; sampled points 0.15 mm / tol 0.010).
2. Fit a circle to the sampled crown of one link: 28 points, rejection 0.07 mm, free fit →
   **R = 2.8787 mm** (max err 0.0097, avg 0.0039).
3. Extrude the arc along the link axis into a cylindrical sheet: link 1 −2.2…+2.5 mm
   (length 4.7), link 2 −2.3…+2.8 mm (length 5.1) — two link sizes ("identical" clasp-end
   links vs "slightly bigger" rest). **Corrected 2026-09-05: no 4.7/5.1 size classes reach the
   delivered kit** — 4.695 mm is the side-link *straight edge* (bbox L 5.295) and no 5.1 exists
   (`e2e-228235-manual-diff.md` §3, **NXLEARN-228235 R5**).
4. Inset the patch from the link edges ~**0.3 mm** (Offset Curve in Face 0.25→0.3, Trim to
   Face Edges; Divide Face trials 0.2–0.85 mm mostly failed **on 08-19**).
   **Corrected 2026-09-05: the pair converged in a later, untraced session** — the delivered 228235
   tree carries 7 `Offset in Face` + 7 `Divide Face` at **0.55 / 0.65 / 0.75 / 0.85 mm**, plus a
   **0.30 mm end inset** along the link axis (`e2e-228235-manual-diff.md` §7).
5. Replicate along the bracelet: Pattern Geometry, Linear, **pitch 6.8 mm × count 10**
   (pitch typed 10× before settling), then per-copy nudges (±0.1 mm, 0.1–2 ° rotations).
   **Corrected 2026-09-05: 6.8 × 10 is not what shipped** — the delivered kit has **14 rows per
   run** (7 links/side); 7.99 mm is the sheet pitch (layout only) and the mesh pitch is
   6.12 ± 0.10 mm (`e2e-228235-manual-diff.md` §3, **NXLEARN-228235 R5**).
   Evidence caveat: all 08-19 link geometry rests on screenshots + decoded keystrokes only
   (no captured B-rep) [RV-R2 omission 1].
   Note the developed pattern of a cylindrical patch is an exact rectangle (R·θ × L), so in
   2D this whole family reduces to rounded rectangles.

R1's link construction (family E: profile-extrude per link row, copy at ~10 mm pitch,
re-trim each copy to the local width) is the older equivalent; R2's family C is the
refinement. Mesh truth for R1: link pitch ≈ **10.25 mm** (operator eyeballed 10.5/10/10);
bracelet width 17.6 → 16.2 → 15.4 → 15.4 → 15.4 mm at x = 37…77 — **the taper stops after
link 2**; outer/centre link gaps are staggered ~3 mm [RV-P1 #9, #10]. Derive pitch and
taper from the mesh, never hard-code.

### B6. Trimming (A5) — summary of mechanisms

| Mechanism | Used for | Values seen |
|---|---|---|
| datum plane on a fitted side plane, offset | link sheet edges (taper) | offsets 0 / 0.1 / 0.2 / 0.25 mm |
| datum plane off the body's own edge | end-link length trims (x ≈ 32.0), link-4 inner edge (y = −5.52) | offsets 0.4 / 0.5 / 0.25 mm [RV-P1 #11] |
| extruded boundary-spline cutter + Trim Body + Delete Body | ruled-sheet ends, clasp-cover ends | extrudes −4.5…+5.9, −6…+3.5, −2.5…+1.8, −22…+2.4 mm |
| profile-end datum planes normal to the curve | link profile length | at profile end tangents (45°/65°) |
| Extend Sheet 0.2 mm + Sew | one-off gap repair after a trim (Body(55), R1 link 3) | 0.2 mm — avoid by trimming once correctly |

### B7. Replication & symmetry (A6)

- Mirror Geometry about the canonical CSYS planes (offset always 0): XZ plane (y → −y,
  crown↔9-side or lug pair at one end) and YZ plane (x → −x, bracelet 12↔6 halves). Both
  orders occur: mirror-3D-then-flatten and flatten-then-mirror — equivalent because the
  flattening is (near-)isometric [RV-STEP omission 10].
- **Scans are not mirror-symmetric.** Every mirrored copy needed manual nudges: R1 lug-tip
  copies Δ(−0.20,−0.52), (−0.10,+0.13), (+0.35,+0.71) mm; whole mirrored bracelet set
  +0.4 mm in Y (the mesh's two halves are yawed 0.5–0.7°, offset ≈ 1 mm) [RV-P1 #12];
  R2 nudges 0.2/0.45/0.15 mm and 0.65/1/1.5° per copy — the single most time-consuming
  manual activity (~35 angle entries in one session). **Pipeline consequence: build each
  side/lug from its own mesh region (or mirror then re-register by ICP against the local
  mesh) instead of trusting symmetry.**
- One flattened lug piece needed a **15° in-plane rotation** after flattening to register
  with its facet — flattening orientation must be a free layout parameter.

### B8. Flattening (A7)

- NX "Flattening and Forming", Type = **Flattening**, Outer Boundary / Constraint Group /
  Rip Edge / Transformation Objects / Distortion Map all **None** (pure development, no
  rips), orientation = explicitly picked origin + U + V + CSYS on the source face (U = "the
  Y axis" in the one legible case). Target plane = z = 0 (the crystal plane / `Datum
  Plane(3)`); results land at z = 0 in place above the source footprint.
- Measured fidelity (developables ΔA ≤ 0.05 %, Δedge ≤ 0.001 mm; ruled sheets ΔA ≤ 0.07 %
  — worst 0.38 % on a 6.6 mm² chip — Δperimeter ≤ 0.43 %, max Δedge 0.087 mm). Use these
  as acceptance thresholds.
- Planar pieces (family P) skip flattening; the caseback disc was **translated** up by the
  measured caseback-to-crystal distance (`distance_measurement260` = **12.140223 mm**,
  an associative Measure result — compute, never hard-code) and retains a 0.24° tilt /
  0.112 mm z-residual (fit and rebuild it flat instead).

### B9. 2D layout (A8)

R1 evidence (the only record that reached this stage):
- All flat sheets were **copy/pasted into a fresh 2D part** as unparameterised bodies, in
  model coordinates (everything at z = 0). Two pasted "operations" the extractor read as
  new work (Extend Sheet+Sew "repair", an "abandoned mirror") are in fact **pasted copies
  of 3D-part features** carried with their expressions [RV-P34 #8,#9]. The first paste
  batch (the original un-mirrored link set) was deleted; the kept kit = the mirrored,
  re-spaced set.
- L/R kit: original link set deleted in the 3D part (Delete Body(244), 41 parents — the
  whole part1/2 original set), the spread mirrored set kept, and the whole kit re-mirrored
  about x = 0 (Mirror Geometry(246) → 22 bodies) for the second bracelet half. **Only one
  bracelet half was ever flattened; the other is a verbatim mirror** [RV-DXF omission 4].
- Nesting: purely manual, 22 Move Objects — one group move of 25 bodies by exactly
  (−48, +48) mm, a trio by (−81, +75), pieces rotated 90° into a right-hand column, then
  ~16 fine drags. Spacing nudges 0.5–2.1 mm typed. Result: 63 sheets in
  x −87.97…36.16, y −19.39…61.0 (**≈124 × 80 mm**), no overlaps, min inter-piece gap
  0.62 mm (median ≈ 1.3–2 mm), crystal disc nested inside the bezel annulus hole at
  0.35 mm radial clearance.

### B10. Outline idealisation (A9) — the hidden manual stage

All in one sketch on the XY plane of the 2D part (R1_part4 created **zero features** — this
stage is pure sketch work [RV-DXF #10]):
1. **Project** the sheet edges into the sketch: Project Curve, 449 objects, **associative
   off, output type Original, tolerance 0.010 mm**.
2. **Delete fold lines / select faces**: multi-face link sheets (top + two ~1.4 mm bevel
   faces) are reduced to the **flat top face only** — ~70 of 129 flattened faces
   (≈400–500 mm² of film) were deliberately not cut [RV-DXF #9, omission 2]. The pipeline
   needs an explicit "which faces become pieces" rule (best: don't model bevels at all).
3. **Regularise** (measured against the source bodies):
   - centre links: one exact 7.315 × 8.750 LINE rectangle (= top face), **re-spaced by
     Pattern Curve, Linear, count 5, pitch 11.0 mm** (bodies kept irregular 12.1/11.5/11.5/
     11.0 pitch);
   - outer links: **five standardized outlines** (7.55×4.90, 7.51×4.28, 7.48×3.83,
     7.47×3.31 ×2) reused for all four rows via Mirror Curve about y = 0 + copies — rows
     4–5 enlarged ~20 % vs their source faces; the +y row's own (different-sized) faces
     were discarded [RV-P34 #12, RV-DXF #8];
   - lug tops and case flank redrawn slightly smaller (−0.6…−0.7 mm);
   - one flank outline drawn by hand from arcs (R20 end arcs, R137.2/R416.0 long edges);
   - projected curves were also moved/rotated **inside the sketch** (27–31 objects at a
     time, Z-rotation with 5° snap) — DXF positions ≠ body positions [RV-P34 omission 1].
4. **Fillet every convex corner**: R0.2 first (v2, 235 arcs), later **doubled to R0.4**
   (RV02, 251 arcs) — presumably after a physical test cut. v1's 33 "splines" were 32
   collinear duplicate edges + 1 genuine 36-pole spline (crown-logo cut-out); **no
   spline→arc refit ever happened** [RV-P34 #15].

### B11. DXF export (A10)

NX "2D Exchange" (UGTODXF) → AutoCAD 2004: the translator reads the **saved .prt** and dumps
sketch curves 1:1 (no joining, no polylines). Bodies were hidden (not deleted) first so only
curves export. Four revisions: v1 (08-15, no fillets — exported from a pre-fillet save), v2
(+7 min, R0.2 fillets, duplicates removed), RV01 (08-20, +4 new "horn" pieces + construction
points), RV02 (+17 min, all fillets R0.2→R0.4). The RV02 geometry exists **only in the DXF**
— the .prt on disk predates it [RV-DXF #12]. Full contract in §F.

---

## C. Facet catalogue

Every film piece produced across both records. Family: P = planar sketch, E = extruded
profile, R = ruled 2-spline loft, C = cylindrical fitted-arc. Areas/dimensions in mm/mm²,
measured from STEP/DXF. "Kit" = present in the delivered R1 DXF (RV02, 67 intended pieces,
24+1 distinct outlines).

### C1. Record 1 (Daytona 126500)

| Facet | Fam | Boundary source | Construction | Trim | Mirror/copies | Flatten | 3D area | Final DXF piece | Kit |
|---|---|---|---|---|---|---|---|---|---|
| **Bezel top** | P | typed circles Ø30 / Ø38.8 on z=0 | zero-depth extrude of annulus | — | — | n/a | 475.5 | annulus Ø38.80/Ø30.00 | ✔ |
| **Crystal** | P | Ø30 circle − Offset Curve 0.35 mm | zero-depth extrude | — | — | n/a | 674.3 | disc Ø29.30, nested in bezel hole (0.35 clearance) | ✔ |
| **Crystal variant / caseback** | P | 3-point arc on caseback edge → circumcircle **R 13.469**, centre (0.237, 0.025, −12.196), tilt 0.24° [RV-STEP #11] | Offset Curve −0.2 mm → zero-depth extrude → translate +12.140223 (measured) | — | — | n/a (moved, 0.112 z-residual) | 553.2 | disc Ø26.54 | ✔ |
| **Bracelet centre link** ×5/side | E | mid-plane section y=0 → sketch fit-spline profile | extrude −3.7…+5.05 (width 8.75) | none (full width) | copies at 10.5/10/10 pitch; −10.5 end link; YZ mirror + 0.4 mm y-shift | ✔ (ΔA −0.005 %) | 88.66 each (3 faces; top face 64.0) | 7.315 × 8.75 rect ×10, re-spaced to 11.0 pitch | ✔ |
| **Bracelet outer link (+Y "red")** ×5/side | E | section y=+6 profile | extrude −2…+2.55 along fitted side-plane normal (taper +4.9°) | fitted side plane, offsets 0…0.25 | as above | ✔ | 42.26→26.42 (taper 4.58→3.83→2.98→2.72; end link 9.0 long) | 5 outlines 7.5×4.88…7.42×3.30 reused on all 4 rows | ✔ |
| **Bracelet outer link (−Y "carrot")** ×5/side | E | section y=−7 profile | extrude −3.1…+1.7 (taper −3.4°) | fitted side plane + link-4 inner-edge trim y=−5.52 | as above | ✔ | 42.03→33.68 (4.37→3.29) | (same 5 outlines, mirrored) | ✔ |
| **Case flank, 9-side (non-crown), lug-to-lug** | R | 2 deg-5 splines on mesh (bezel edge / caseback edge) | Through Curves, ruled, \|K\|max 1.0e-3 | none | — | ✔ (ΔA +0.03 %, ΔP −0.05 %) | 250.9 | 49.04 × 7.09 "boat hull" silhouette, redrawn from arcs (R20/R137/R416), closes to 0.052 mm | ✔ |
| **Crown-side flank, lug→pusher** | R | 2 splines; freeform-fit helper surface (72 mm², never flattened) used as guide only | Through Curves(118) with explicit closure Line+Spline(u 1.0/0.9287)+Trim Curve | pusher-end cutter: Spline(116) extruded −4.5…+5.9 along fitted-plane normal (0.39,0.92,−0.05) | YZ mirror | ✔ (ΔA −0.02 %) | 66.69 ×2 | 13.9 × 7.7 crescent pair | ✔ |
| **Crown-guard / pusher facets** | R | 2 splines each | Through Curves; the 22.8 piece is the least developable (\|K\|max 0.039, Rmin 1.7) | — | YZ mirror (both flats) | ✔ (ΔP −0.38 %) | 13.93, 22.79 ×2 | 6.1×4.7 and 4.9×10.3 pairs | ✔ |
| **Lug flank (9-side)** | R | 2 splines | Through Curves, \|K\|max 0.025 | — | mirrors ×4 | ✔ (ΔP −0.43 %, worst) | 32.93 ×4 | 5.02 × 13.93 curved strips ×4 (arcs R22.4/38.6/52.1/64.8) | ✔ |
| **Inner lug face** | R | 2 deg-5 splines | Through Curves | — | XZ then YZ mirror ⇒ ×4 | ✔ (ΔA +0.02 %) | 30.67 ×4 | 7.54 × 4.66 near-rectangles | ✔ |
| **Lug-end wall (between lugs)** | E | 1 profile spline on the case end wall | extrude 0…7.7 across the lug gap (K=0) | — | YZ mirror ⇒ ×2 | ✔ (ΔA 0) | 53.90 ×2 | 7.82 × 7.00 quads | ✔ |
| **Lug-tip underside** | R | 2 two-point splines (→ lines) | Through Curves | — | XZ + YZ mirrors + nudges 0.1–0.7 mm; 15° flat rotation | ✔ (ΔA +0.38 %) | 6.62 ×4 | 3.68 × 2.17 slivers ×4 (smallest pieces) | ✔ |
| **Clasp lever top** ×3 | P | crop clasp ROI; two typed 5.75 × 3.75 rectangles + 8.3 × 5.7 rectangle with crown-logo section curve projected, fit, **offset 0.15 mm** | zero-depth extrude of sketch regions | — | Mirror Curve in-sketch | n/a | 21.56 ×2 + 28.72 | rectangles + crown-notch piece (the kit's only real SPLINE) | ✔ |
| **Clasp cover (curved top)** | E | cross-section sketch (Section→Project→Fit Curve Closed/Symmetric) + 2 edge splines | extrude −4.1…+3.5 (width 7.6) | 2 spline cutters −6…+3.5 + Trim Body | — | ✔ | 166.1 | 7.60 × 22.60 strip with concave end | ✔ |
| **Clasp facet 2** | E | SKETCH_009 profile | extrude −4.35…+3.9 (8.25) | — | — | ✔ | 44.9 | 5.44 × 8.25 rectangle | ✔ |
| **Clasp facet pair** | E | SKETCH_010 profile | extrude +4.6…+7.4 (one-sided band, width 2.8) [RV-P34 #3] | — | YZ mirror before flatten | ✔ ×2 | 13.55 ×2 | 4.84 × 2.80 rectangles | ✔ |
| **Clasp side flanks** | R | 2 splines | Through Curves (almost planar, \|K\| 1.4e-5) | — | XZ mirror before flatten | ✔ ×2 (ΔA −0.02 %) | 44.72 ×2 | 11.04 × 4.94 pair | ✔ |
| **"Horn" pieces (lug outer flanks?)** ×4 | ? (added 08-20, unrecorded) | unknown — arc-composed outline (R18.57/27.12/31.19/330.3) | — | — | 4 rotated copies | ? | — | ≈11.8 × 6.6, tip 0.73 mm wide (R0.364 tip arc), **open by 0.715 mm** | ✔ (defective) |

Not cut although flattened: all link bevel faces; the +y outer-link row's own faces; the
Extend-Sheet/Sew-patched body; Mirror(176)'s duplicate pieces.

### C2. Record 2 (Day-Date 40, 228235) — 3D as captured 08-19; flattened and delivered 08-30

**Corrected 2026-09-05 (NXLEARN-228235).** This table is the **08-19 3D state**, not the kit. R2
*was* flattened (15 flats, all on z = 0) and laid out on 08-30 and delivered as DXF the same
evening — 61 loops / 58 pieces / 3 180.6 mm² net film. Delivered per-piece dimensions:
`e2e-228235-manual-diff.md` and `piece-catalogue.md` Kit 2.

| Facet | Fam | Construction | Values | Result |
|---|---|---|---|---|
| Crystal | P | typed circle Ø30.8 at origin, zero-depth extrude; **cyclops cut-out**: rounded-rect profile x 8.46…11.76, y −3.05…+2.75 (≈7.1 × 5.8 centred (10.07, −0.15)), side arcs R3.407/3.540, corner fillets R1.0, whole profile **offset outward 0.15 mm** (→ R1.15, R3.56/3.69) then cut | disc 745.06 → 706.12 | 1 piece |
| Caseback | P | typed circle Ø21.5 on caseback plane (z ≈ −12.1), zero-depth extrude | | 1 piece |
| Case flank 9-side | R | 2 deg-5 splines lug-tip-to-lug-tip → Through Curves → cosmetic 0.1 mm offset | 46.7 long × 6.8 tall, 203.1 | 1 piece |
| Case flank crown-side | R | same + **bridge spline** (tangents 1.0/1.0) around the crown guard → extrude −2.5…+1.8 → Trim → XZ mirror + 1.5° nudge | 88.11 ×2, crown gap y −2.2…+1.7 | 2 pieces |
| Lug tops ×4 | R | 2 splines → Through Curves → 0.1 offset → bridge spline at lug root → extrude −22…+2.4 → trim → YZ mirror + XZ mirror + nudges (0.2/0.45/0.15 mm, 1/0.65°) | 35.80 each, 28.6° tilt | 4 pieces |
| Lug undersides | R | 3 splines → Through Curves → 0.05 mm offset → mirror + ~35 rotation nudges | | pieces (screenshot-only evidence) |
| Bracelet links | C | section (0.15 mm sampling) → Fit Circle **R 2.8787** → extrude −2.2…+2.5 / −2.3…+2.8 → inset 0.3 mm (Offset Curve in Face) → Pattern pitch **6.8 × 10** + nudges — **corrected 2026-09-05: delivered margins are 0.55–0.85 mm in-surface + a 0.30 mm end inset, and the kit ships 14 rows/run, not pitch 6.8 × 10** (`e2e-228235-manual-diff.md` §3 + §7, **NXLEARN-228235 R5**) | 08-19: ~10 centre + ~20 side patches; delivered: **14 centre + 28 side** | one half tiled 08-19; full kit delivered 08-30 |

---

## D. Parameter table

Confidence: **H** = typed value or independently re-measured; **M** = measured from
STEP/screenshot at save granularity; **L** = inference.

| Value | Unit | Meaning | Source | Conf |
|---|---|---|---|---|
| 0.07 | mm | automatic point-REJECTION threshold on brush-painted facet regions — **every plane/circle fit of R1 and R2**; NOT universal, see the next row | R1 12:06Z dialogs; RV-STEP #4 | H |
| 0.03 | mm | same threshold on **R3** (126713GRNR) Fit Surface / Fit Plane — one captured instance, target region uncertain. Declare the rejection value **per fit** in the run manifest; do not assume a constant (NXLEARN-126713 R11 (open)) | R3 S1 `dc_viewport_20260830_203047.png` | M |
| 13.75 | mm | NX Fit-Surface patch-size default — NOT a design value | RV-STEP | H |
| 14.75 / 16.0 | mm | operator-CONSTRAINED crystal-circle radius (R1/R2); only the centre is fitted | RV-STEP #3 | H |
| 14.65–14.70 / 15.6–15.8 | mm | free-measured crystal flat radius (R1/R2) | mesh histograms | H |
| 12.33° / 14.8° | deg | raw-scan crystal-plane tilt (R1/R2) | STEP normals | H |
| 30 / 38.8 | mm | R1 bezel film inner/outer Ø (typed) | Sketch(4) p3/p4 | H |
| 0.35 | mm | crystal-film ↔ bezel-film radial clearance (typed Offset Curve) → crystal Ø29.3 | Offset Curve(229) | H |
| 0.2 | mm | caseback-disc **inset** from the fitted **rim-edge** arc (R 13.469 → 13.269, Ø26.54) — R1 convention, still the default | Offset Curve(194) | H |
| +0.15 | mm | caseback-disc **outward offset** from the fitted **flat-centre boundary** (3-point arc R 10.586, Ø21.17 → Ø21.47 ≈ R2's typed Ø21.5) — R3 convention. The sign follows the reference boundary; which boundary is standard is NXLEARN-126713 R4 (open) | R3 `Arc(35)` p137–p145, `Offset Curve(36)` p148 | H |
| 13.469 / (0.237, 0.025, −12.196) | mm | caseback edge circumcircle R / centre (0.24 mm eccentric, 0.24° tilt) | RV-STEP #11 | H |
| 12.140223 | mm | measured crystal-plane → caseback distance (R1), used as the disc lift | `distance_measurement260` | H |
| 30.8 / 21.5 | mm | R2 crystal / caseback film Ø (typed) | SKETCH p0 / p86 | H |
| 0.15 | mm | outward clearance offset of cut-out profiles (R2 cyclops; R1 crown logo) | p85; SKETCH_007 | H/M |
| 5 | — | Studio Spline degree for all hand-drawn boundary splines | dialogs | H |
| G0 / Parameter / Preserve-Shape off | — | ruled-loft (Through Curves) settings | dialogs | H |
| 1.0 / 1.0 | — | bridge-curve tangent magnitudes (cutter curves) | p11/p12 etc. | H |
| −2…+2.55, −3.1…+1.7, −3.7…+5.05 | mm | R1 link profile extrusion spans (sheet widths 4.55/4.8/8.75) | Extrude 28/36/41 | H |
| 0…7.7 | mm | lug-end wall extrusion span | Extrude(166) | H |
| −4.1…+3.5, −4.35…+3.9, +4.6…+7.4 | mm | clasp piece extrusion spans (widths 7.6 / 8.25 / 2.8) | Extrude 209/219/223 | H |
| −4.5…+5.9, −6…+3.5, −2.5…+1.8, −22…+2.4 | mm | boundary/bridge-spline cutter extrusion spans | Extrudes | H |
| 0 / 0.1 / 0.2 / 0.25 / 0.4 / 0.5 | mm | trim-plane offsets (link edges, end-link length) | Datum Planes | H |
| 0.2 | mm | Extend Sheet before Sew (one-off gap repair) | Extend Sheet(71) | H |
| 10.25 (mesh) vs 10.5/10/10 (used) | mm | R1 bracelet link pitch — derive from mesh gap autocorrelation | RV-P1 #9 | H |
| 17.6/16.2/15.4/15.4/15.4 | mm | R1 bracelet width by link — taper only links 1–2 | RV-P1 #10 | H |
| 6.8 × 10 (typed; **not what shipped**) | mm × count | R2 link pattern pitch and count — corrected 2026-09-05: delivered = **14 rows/run**, sheet pitch 7.99 (layout only), mesh pitch 6.12 ± 0.10 | numpad decode; `e2e-228235-manual-diff.md` §3 (**NXLEARN-228235 R5**) | H |
| 2.8787 | mm | R2 centre-link crown radius (free fit, 28 pts, err ≤ 0.0097) | screenshot | H |
| −2.2…+2.5 / −2.3…+2.8 | mm | R2 link patch extrusion spans (lengths 4.7 / 5.1) — corrected 2026-09-05: **no 4.7/5.1 size classes reach the delivered kit**; 4.695 is the side-link *straight edge* and no 5.1 exists | typed; `e2e-228235-manual-diff.md` §3 (**NXLEARN-228235 R5**) | H |
| **0.55 / 0.65 / 0.75 / 0.85** (08-19 trials 0.2–0.85 "failed") | mm | R2 link-patch **in-surface** edge margin — **corrected 2026-09-05** to the values that survive in the delivered tree; plus a separate **0.30 mm end inset** along the link axis | Offset in Face + Divide Face; `e2e-228235-manual-diff.md` §7 | H |
| 0.15 / 0.010 | mm | Section Curve sample distance / tolerance | dialog | H |
| 0.05 / 0.1 / 0.15 | mm | cosmetic sheet offsets after ruled loft (no effect on developed outline) | Move Objects | H |
| 0.1–0.7 mm, 0.65–1.5° | mm/deg | manual nudges of mirrored copies = measured scan asymmetry | both records | H |
| 15 | deg | post-flatten in-plane rotation of one lug piece (orientation is free) | Move(186) p209 | H |
| ≤ 0.07 % (worst 0.38 %) / ≤ 0.43 % / ≤ 0.09 mm | — | flattening ΔA / Δperimeter / Δedge achieved — acceptance thresholds | STEP measurements | H |
| \|K\|max 0.001–0.039 | mm⁻² | Gaussian curvature of accepted **ruled** sheets (accept mean \|K\| < 1.5e-2) | STEP sampling | H |
| \|K\|max 0.110 (analytic), mean 0.0131 | mm⁻² | Gaussian curvature of the accepted **network** sheet (R3 `Through Curve Mesh(17)`, 41.851 mm²) — 17× the max gate, and it needs ≈1.07 % local strain to flatten. Whether recipe-N pieces get a variant gate or must be sub-split is **NXLEARN-126713 R2 (open)**; the discrete angle-defect max is grid-dependent (3.12e-2 at 41×7 vs 8.71e-2 at 41×41 on the same face, **NXLEARN-126713 R3 (open)**) | R3 RV04 STEP, `BRepLProp_SLProps` 21×21 | H |
| 0.010 | mm | Project Curve tolerance (sheet edges → sketch) | dialog | H |
| 11.0 | mm | DXF centre-link pattern pitch (idealised; bodies at 12.1/11.5/11.5/11.0) | Pattern Curve | H |
| R0.2 → **R0.4** | mm | convex-corner fillet radius, v2 → RV02 (final; 0.2 rejected) | DXF census | H |
| 0.35 / 0.62 / ~1.3–2 | mm | layout gaps: disc-in-ring / min piece gap / median | shapely | H |
| 123.1 × 85.2 | mm | delivered kit sheet extents (RV02) | DXF | H |
| 4114 / 67 / 24+1 | mm²/count | total film area / intended pieces / distinct outlines (RV02) | DXF | H |
| AC1018, $INSUNITS 4, $MEASUREMENT 1 | — | DXF format actually consumed | headers | H |
| 0.052 / 0.715 | mm | flank micro-gaps (closable) / horn opening (defect) in delivered DXF | ezdxf | H |

---

## E. Lessons learned / dead ends

1. **Loft through multiple mesh sections → abandoned.** R1's first link sheet was a loft
   between the y=5 and y=7 longitudinal mesh sections (+ the sketch profile) [RV-STEP #8];
   deleted within minutes for the single-profile extrusion (exactly developable; mesh
   sections are noisy). `Through Curve Mesh` was opened twice **on the 126500** and abandoned
   both times. **On the 126713GRNR (R3, session `c4dbc89f48b4`, 2026-09-04) it was opened
   7 times and the FIRST attempt was kept** — `Through Curve Mesh(18)`→`(17)`, 4 parent
   splines, 41.85 mm², mirrored to all four lugs, present in every snapshot from 17:48:42 to
   the 22:45:27 final tree. The six later attempts were abandoned; the one screenshotted
   (`session 2/screenshots/dc_viewport_20260904_175946.png`) used **1 primary + 1 cross** on an
   over-large region and NX reported *Output is self-intersecting.* Read the failure as **too
   few cross curves for the region**, not as the operation being unusable. Full construction,
   dialog settings, the measured reason a 2-curve ruled sheet fails there, the OCP mapping and
   the prototype numbers: `e2e-126713-method.md` §4 (recipe N).
2. **Freeform surface fit is only a guide.** Fit Surface(Freeform) on the crown flank
   (72 mm², |K|max 0.12) was built, trimmed, never flattened, and superseded by the direct
   2-spline ruled loft. Boundary curves straight from the mesh beat surface fitting.
3. **Mirroring is never enough.** Every mirrored copy required manual registration
   (0.1–0.7 mm / 0.65–1.5°); R1's bracelet halves are yawed ~0.5–0.7° and offset ~1 mm.
   → build each side from its own mesh region.
4. **Synchronous-modelling tools failed on sheets — on 08-19**: Offset Region + Replace Face
   created and deleted; Divide Face threw "Dividing objects do not divide selected faces" through
   6 offset trials before Offset Curve in Face (0.3 mm) worked. **Corrected 2026-09-05: the
   `Offset in Face` → `Divide Face` pair DID converge later** — 7 + 7 features at 0.55–0.85 mm
   survive in the delivered 228235 tree, built in an untraced session between 08-19 and 08-30
   (`e2e-228235-manual-diff.md` §7). In Python still apply margins as a 2D inset after development.
5. **Extend Sheet 0.2 + Sew** — one-off patch of a bad trim; the patched body was later
   discarded anyway. Trim once, correctly, with a small outward offset instead.
6. **Eyeballed pitches drift**: copies at 10.5/10/10 vs mesh 10.25 pitch drift ≤0.5 mm by
   link 4; R2 typed 10 pitch values before landing on 6.8 — which is **not** what shipped either
   (delivered: 14 rows/run, sheet pitch 7.99, mesh pitch 6.12 ± 0.10; `e2e-228235-manual-diff.md`).
   Measure pitch from the mesh.
7. **Two crystal-disc candidates** (Ø29.3 parametric and Ø26.54 fitted+offset) were both
   exported — the operator left alternatives in the kit rather than deciding.
8. **The 2D stage is a redraw, not a trace** (§B10). The flattened bevel faces and the +y
   outer-link row were discarded; outlines were standardised, re-spaced, mirrored, enlarged
   up to 20 %. Decide and document the regularisation policy.
9. **v1 → v2 (7 min)**: 32 duplicate collinear "splines" removed, 235 × R0.2 fillets added
   — v1 was exported from a stale save (the exporter reads the .prt on disk). Automate the
   export from in-memory state.
10. **RV01 (5 days later)**: 4 horn pieces added (probably after a physical test cut showed
    missing facets), left open by 0.715 mm — an open outline would not release from the
    cutter. RV02 (17 min later): **all fillets doubled R0.2 → R0.4** (0.2 presumably tore
    or the cutter couldn't follow); RV02 exists only as DXF (never saved to .prt).
11. **Defects that survived into the final deliverable** (a validator must catch these):
    0.052 mm endpoint mismatches, a 0.054 mm sliver line (v1/v2), two 0.013 mm micro-arcs,
    a 0.73 mm-wide horn tip, open horn outlines, bogus $EXTMIN/$EXTMAX, POINT entities on
    the cut layer, no labels of any kind.
12. **Operator practice worth keeping**: colour-coding each facet family (→ layers/ids);
    a written spec sheet between sessions (→ anatomy manifest); reference circles Ø30/Ø38.8
    on z=0 as orientation datums; ROI cropping before any fit; per-save export snapshots
    (→ run artifacts).
13. **R2 improvements over R1** (adopt these): lug-tip alignment axis recipe; bridge-spline
    cutters instead of drawn closure chains; typed clearance offsets (0.15 crystal cut-out,
    0.3 link inset); cylinder-fit link recipe; spec-sheet-driven facet list.

---

## F. DXF output contract

What the maintainer actually consumed: AC1018 (AutoCAD 2004), `$INSUNITS = 4` (mm),
`$MEASUREMENT = 1`, everything in modelspace on NX-numbered layer `1` (colour override 163)
+ one origin POINT on layer `61`, **bogus `$EXTMIN/$EXTMAX`**, no blocks/text/dimensions/
polylines — a loose bag of LINE/ARC/CIRCLE (+1 spline) that must be endpoint-chained; z = 0
everywhere, arc extrusion (0,0,1) (no OCS mirroring). 67 intended pieces / 24+1 outlines /
sheet 123.1 × 85.2 mm / 4114 mm² film / 39 % fill.

The pipeline's writer should reproduce the intent, not the defects:

1. **Format**: ezdxf `R2004` (AC1018) or newer — **NOT R12** (R12 cannot carry
   LWPOLYLINE/$INSUNITS; repo memory). `$INSUNITS=4`, `$MEASUREMENT=1`; **recompute
   `$EXTMIN/$EXTMAX`** from geometry. Deterministic output (fixed handle seed, fixed
   TDCREATE/TDUPDATE, sorted entity order — repo ezdxf-determinism switch).
2. **Layers**: `CUT_OUTER` (closed loops, CCW), `CUT_INNER` (holes, CW), `LABEL` (TEXT piece
   ids, height 1.5, at pole of inaccessibility), `REG` (optional registration/frame), `REF`
   (reference points — never POINT on a cut layer).
3. **Entities**: one **closed LWPOLYLINE with bulges** per loop (arcs exact via bulge =
   tan(Δθ/4); lines as segments); free-form edges sampled at 0.02 mm chord tolerance —
   no SPLINE entities on cut layers.
4. **Topology gates (fail-hard)**: every loop exactly closed (first == last); shapely-valid
   simple polygons; no overlaps; min vertex spacing 0.05 mm (kills micro-arcs/slivers);
   holes depth ≤ 1, disc-in-hole allowed only at ≥ min_gap.
5. **Corner fillets**: every convex corner **R = `corner_radius_mm`, default 0.4** (0.2 was
   rejected by the maintainer); concave corners sharp or ≥ 0.2.
6. **Feature-size gates**: replace "largest inscribed circle" with a **narrow-feature test**
   (area lost by `buffer(−r).buffer(+r)`, r ≈ 0.4–0.75 mm) [RV-DXF #13 — the horn's 0.73 mm
   tip passes a naive minW gate]; min piece area ≥ 5 mm² (smallest accepted piece
   3.68 × 2.17, minW 1.99); warn < 1.5 mm width, fail < 1.0.
7. **Layout**: min inter-piece gap `min_gap_mm = 1.0` (maintainer went to 0.62; 0.35 only
   for disc-in-ring nesting); pieces axis-aligned; mirror pairs adjacent; link rows grouped
   at uniform pitch; sheet origin bottom-left; optional target blank size with row wrap.
8. **Identity**: stable canonical piece ids from the anatomy manifest (e.g. `BEZ_TOP`,
   `CRYSTAL`, `CASEBACK`, `FLANK_9`, `FLANK_3_CROWN`, `LUG_TOP_12C`, `LINK_C_12_1`,
   `LINK_O_12_1L`, `CLASP_COVER` …) as (a) TEXT on `LABEL`, (b) XDATA app `WATCH_TPU`
   (piece_id, facet_id, mirror_of, area_mm2, source hash), (c) sidecar
   `kit_manifest.json`. The NX kit had none — 67 unlabeled pieces.
9. **Handedness**: record explicitly which side of each film faces up (the NX flats had
   mixed ±Z normals — centre links systematically −Z [RV-P34 omission 7]); normalise all
   pieces to +Z = outer/adhesive-opposite side and set a global `mirror_for_cutter` flag.
   Never mirror silently.
10. **Regularisation policy field**: per piece, `outline_source ∈ {developed, regularised,
    parametric}` — the maintainer's kit mixes all three (traced top faces, standardized
    rectangles, typed circles).
11. **Round-trip validation**: re-read the written DXF with ezdxf (edgeminer/edgesmith
    chaining at 0.01 mm) → must reproduce the manifest's piece count/areas; record SHA-256
    in the run bundle.
12. **Regression fixtures from the delivered kit**: bezel Ø38.80/Ø30.00; crystal Ø29.30;
    disc Ø26.54; flank 49.04 × 7.09; centre link 7.315 × 8.750 ×10 @ 11.0 pitch; outer links
    7.5 × 4.88 / 4.25 / 3.81 / 3.30; lug tops 5.02 × 13.93 ×4; smallest 3.68 × 2.17;
    sheet 123.1 × 85.2; total 4114 mm².

---

## G. Python / build123d implementation mapping

Environment: system Python 3.13 has build123d 0.11.1 / OCP 7.9.3 / ezdxf 1.4.4 / trimesh
4.12 / numpy / shapely; `C:/spk/v/Scripts/python.exe` has libigl 2.5.1 + trimesh 5 but NO
build123d. MAX_PATH breaks installs/writes under the Drive/Temp long paths — stage heavy
I/O under short paths (e.g. `C:/spk/...`), as the analysis runs already did.

### G1. Stage mapping

| Stage | Operation | Python API | Pitfalls |
|---|---|---|---|
| A0 | load mesh | `trimesh.load(path, process=False, force='mesh')` | never read the STL as text/context; expect multiple components (`mesh.split(only_watertight=False)`) |
| A1 | crystal plane | facet selection = normal clustering + region grow (`mesh.face_normals`, `trimesh.graph.face_adjacency`); plane = SVD/`trimesh.points.plane_fit` with RANSAC-style 0.07 mm inlier rejection | replicate the *rejection-threshold* semantics, not a fit tolerance |
| A1 | crystal circle | boundary loop of the inlier patch → project to plane → Kåsa/Pratt LSQ circle; fit centre with radius fixed to a rounded/declared value if the edge arc < ~180° | free radius unstable on partial arcs (R1: 13.7 ±1.7 on 100°) |
| A1 | in-plane axis | R2 recipe: fit planes to the two lug-tip patches of one end → `trimesh.intersections.mesh_plane` → chord midpoints → line = 3–9 direction; 12–6 = in-plane normal. Simpler fallback: PCA of the bracelet point cloud = Y; crown side = larger in-plane protrusion (+23.0 vs −18.8 in R2) | sign of 12 o'clock needs operator declaration (H-1) |
| A1 | transform | `mesh.apply_transform(T)`, `T = [X Y Z \| c]⁻¹`; persist T + input hash in the run manifest | repo units rule: never silently infer |
| A3 | ROI crop | `mesh.submesh(face_mask)` from a 2D polygon containment test, or 4× `slice_mesh_plane` | keep the crop polygons from §B4 as templates |
| A4-P | planar pieces | `build123d.Circle(r)`, `make_face(wire)`, holes via boolean `cut` or inner wires; offsets via `offset(wire, ±d)` (`BRepOffsetAPI_MakeOffset`) or `shapely.buffer` in 2D | cyclops/crown cut-outs: offset the *closed profile* outward 0.15 before cutting |
| A4-E | profile extrude | section: `mesh.section(plane_origin, plane_normal)` → `Path3D.to_planar()` → resample → smoothing B-spline (`scipy.interpolate.make_smoothing_spline` / `GeomAPI_PointsToBSpline` with rejection) → `build123d.Spline` / `Edge.make_spline_approx`; sheet: `BRepPrimAPI_MakePrism(edge_or_wire, gp_Vec(dir*w))` (two prisms for ±spans) → `Geom_SurfaceOfLinearExtrusion`, K = 0 exactly | extrusion direction = fitted side-plane normal (post-hoc refinement; default facet-transverse works) |
| A4-R | ruled loft | `OCP.BRepFill.BRepFill.Face_s(edge1, edge2)` (guaranteed ruled) or `BRepOffsetAPI_ThruSections(isSolid=False, ruled=True)` with 2 wires; build123d `loft([w1, w2], ruled=True)` | boundary curves from mesh ridge extraction (`face_adjacency_angles > 30–40°` → ordered polylines → spline) replaces 468 manual dialog events; ensure both curves terminate on a common transverse curve (bridge spline: `GeomAPI_Interpolate` with end tangents) |
| A4-C | cylinder patch | LSQ circle on link section (expect R ≈ 2.88) → arc edge → `BRepPrimAPI_MakePrism(arc, axis*L)` | developed pattern is an exact R·θ × L rectangle — can skip 3D entirely and emit rounded rectangles |
| A5 | trims | `BRepAlgoAPI_Splitter` / build123d `split(sheet, tool)` with plane or extruded-cutter sheet; keep the side facing the facet | equivalently trim the (u,v) parameter range of the ruled surface — simpler and robust |
| A5 | fitted side plane | plane fit on the side-face patch (0.07 rejection) → `Plane(origin, normal)` offset 0…0.5 mm | |
| A6 | mirror/copies | `mirror(shape, about=Plane.XZ/YZ)`, `shape.moved(Location(...))` | then **re-register against the local mesh** (ICP of the piece outline onto the local section curves) or rebuild per side — the 0.1–0.7 mm nudges prove blind mirroring fails |
| A7 | flatten, family E/C | exact analytic unroll: arc-length parameterise the profile (`GCPnts_AbscissaPoint` on `BRepAdaptor_Curve`) × straight extent | zero-distortion; no mesh methods needed |
| A7 | flatten, family R | discretise rulings and lay consecutive triangles isometrically (ruling-by-ruling development), or LSCM on a fine triangulation (`igl.lscm`) | **`igl.arap` SEGFAULTS on Windows** (libigl 2.5.1, repo memory) — do not use ARAP; validate with the §B8 thresholds (ΔA ≤ 0.1 %, Δperimeter ≤ 0.5 %, Δedge ≤ 0.1 mm); \|K\| gate mean < 1.5e-2 mm⁻² before accepting a ruled sheet (`BRepLProp_SLProps.GaussianCurvature`, check `IsCurvatureDefined()`) |
| A7 | offsets | skip the 0.05–0.15 mm cosmetic sheet offsets (no effect on the pattern). Do NOT offset the raw mesh for clearances — a raw-mesh normal offset self-intersects (repo Lane-B spike); apply clearances as 2D `shapely.buffer` on the developed outline instead | |
| A8 | nesting | keep each flat piece as `shapely.Polygon` + metadata; deterministic shelf/row packer by family (links in rows at uniform pitch, mirror pairs adjacent, big circles first, slender pieces rotatable 90°); `STRtree` min-gap check ≥ 1.0 mm; disc-in-ring nesting at 0.35 mm | no manual moves; the maintainer's 22-move session is what we automate away |
| A9 | regularise | per `outline_source` policy: `shapely` simplify/minimum_rotated_rectangle for links; fillets = `Polygon.buffer(−r).buffer(+r)` (round join) or build123d `fillet(face.vertices(), 0.4)` for true arcs | keep true arcs where bulge export is wanted |
| A10 | export | `ezdxf.new("R2004")`; `msp.add_lwpolyline(pts, format="xyb", close=True)`; `add_circle`; TEXT labels; XDATA; `ezdxf.bbox.extents` → `$EXTMIN/$EXTMAX`; validate by re-read + `ezdxf.edgeminer`/`edgesmith` chaining | R12 forbidden (no LWPOLYLINE/$INSUNITS); deterministic-output switch per repo memory |

### G2. STEP-import notes (for validating against the NX artifacts)

- `build123d.import_step` → `Compound`; the NX artifacts contain **sheet bodies only**
  (0 solids) — iterate `TopExp_Explorer(shape, TopAbs_SHELL)`; each film piece is an
  `OPEN_SHELL` of 1–6 faces.
- NX colours survive as `STYLED_ITEM → COLOUR_RGB` names; coloured sheets = film pieces,
  "medium midnight" = construction helpers (reliable heuristic in these files).
- Surface types via `BRepAdaptor_Surface(face).GetType()`: 0 PLANE / 1 CYLINDER /
  6 BSPLINE / 8 EXTRUSION; ruled check = 4 collinear poles per v-column.
- Free boundaries: `ShapeAnalysis_FreeBounds(shell, 1e-4).GetClosedWires()`; edge lengths
  `GCPnts_AbscissaPoint.Length_s(BRepAdaptor_Curve(edge))`.
- Flattened pieces: planar faces at |z| ≤ 0.112, normal ±Z.
- When validating the DXF, compare against the **DXF itself and the manifest**, not the
  STEP body positions — the sketch stage moved/redrew outlines (§B10).

### G3. Suggested data model

```
FacetSpec {
  id: str                      # canonical name (repo frame: bracelet_12 …)
  family: 'planar'|'extruded'|'ruled'|'cylinder'
  roi: Polygon                 # mesh crop region (canonical XY)
  boundary_sources: [...]      # section planes / ridge specs / typed circles
  profile_plane / extrude_vector / spans_mm
  cutters: [BridgeCutterSpec]  # bridge-curve + extrusion span
  trim_planes: [(plane, offset_mm)]
  clearance_mm: float          # 2D outline offset (0.15 cut-outs, 0.3 link inset, 0.35 disc-in-ring)
  outline_source: 'developed'|'regularised'|'parametric'
  replicate: {mirrors: [XZ|YZ], pitch_mm, count, register: 'icp'|'none'}
  flatten: {method: 'unroll'|'ruling'|'lscm', gates: {dA%, dPerim%, dEdge_mm, Kmax}}
}
```
The bracelet = one `FacetSpec` per link row × measured pitch × per-link trim widths.

---

## H. Open questions + suggested measurements

1. **12-o'clock sign.** Neither record annotates which bracelet end is 12. → Operator
   declaration in the anatomy manifest (Stage-1 contract already requires this); heuristic
   candidate: the clasp half (detached tail in R1) is the 6 side — confirm with maintainer.
2. **Clearance policy is inconsistent** (crystal −0.35 mm radial R1 vs ≈ −0.2…−0.4 R2;
   caseback −0.2; link inset −0.3; side trims 0…0.5; cut-out +0.15 outward). → Maintainer
   decision: one table of `clearance_mm` per facet class; propose 0.3 default inset,
   0.15 cut-out clearance, 0.35 disc-in-ring.
3. **Bezel as flat annulus** despite the 1.9 mm bezel slope (true development would be an
   annular sector ≈ 4.8 mm slant width): intentional (TPU stretch) or oversight? → test-cut
   both; measure bezel cone angle from the mesh (z(r) fit over r 15–19.4).
4. **Which pieces are the canonical kit** (two crystal-disc variants; lug-underside chips
   and inner-lug faces that are hidden under the end link; the 4 horns). → Maintainer
   review of the 24+1 outline classes against the facet manifest.
5. **Horn-piece provenance** (added 08-20, unrecorded; no matching face in any STEP; arcs
   suggest an arc-fitted flattened edge). → Rebuild lug outer flanks from the mesh and
   compare to the horn outline (Hausdorff) to identify them.
6. **R0.4 fillet finality** (changed from 0.2 five days in; reason unrecorded — cut
   quality/peel/cutter limits). → keep `corner_radius_mm` configurable, default 0.4;
   ask maintainer for cutter model/material.
7. **Cutter tolerances** (accepted 0.052 mm gaps; open horns presumably failed): join
   tolerance, kerf, min radius of the physical cutter unknown. → ask; until then the
   fail-hard closure gates of §F stand.
8. **Handedness / adhesive side** never recorded (mixed ±Z flat normals). → Define +Z =
   outside; add `mirror_for_cutter` flag; confirm with one physical cut.
9. **Exact boundary-spline point picks** are unrecoverable (only resulting sheets known).
   Non-issue for the port: ridge extraction from dihedral angles replaces hand picking,
   validated against the recorded sheet bboxes/areas (§C).
10. **R2 completion**: `_RV2.prt` modified 08-21 uncaptured; final Day-Date piece list,
    flattening settings, link wrap angle (Divide-Face result) unknown. → Measure the link
    wrap angle directly from the mesh section (angle subtended by the visible link crown,
    ~120° of R 2.88 in screenshots) instead of recovering it.
11. **Meaning of the 3 flank POINTs** in the DXF (asymmetric — not spring-bar axes
    [RV-DXF #14]) and the p45/p46/p47 orphan expressions (37.54, 6.0, −9.22): unknown,
    ignorable (reference data, never cut).
12. **Sub-facet selection rule** (top face only; bevels dropped): adopt "never model bevel
    faces" or an explicit per-facet `faces: main_only` flag — needs a one-line maintainer
    confirmation since it changes covered area by ~10 %.

Suggested concrete measurements to run next (all scriptable, < 3 min each):
(a) link-gap autocorrelation on both meshes → pitch + per-link widths table;
(b) bezel z(r) profile → cone angle & true developed annulus;
(c) ridge-extraction prototype on the R1 crown flank → compare spline boundaries to the
recorded sheet (66.7 mm², bbox known);
(d) ruling-development prototype on the recorded worst sheet (22.8 mm², |K|max 0.039) →
verify ≤ 0.4 % perimeter distortion is reproducible without ARAP;
(e) horn-piece identification per H-5.
