# NX method evidence — what the operator actually did (corrected record)

Distilled from ~30 k captured events over 7 NX sessions (2026-07-31 → 08-19),
plus the two 2026-08-30 sessions (2 224 events) that complete R2; 55 STEP
artifacts (geometry re-measured with build123d/OCP), 5 delivered DXFs, and ~150
screenshots; every claim below survived an adversarial review pass against the
primary data. Two projects: **R1** = Daytona 126500 (35 MB scan, 734 k
facets, delivered 4 DXF revisions) and **R2** = Day-Date 40 (ref 228235; the STL-library README mislabels it Sky-Dweller) (149 MB scan,
2.98 M facets, refined 3D method). R2 is the *better 3D recipe* (the operator's
second, learned pass).

**Correction (2026-09-05, NXLEARN-228235): R2 did reach DXF.** It was flattened
(15 unique flats, session `9d37b4e756ee`, 08-30) and laid out in the same
session; its 2D stage is captured as far as the raw projected sketch (session
`0f041089bd6f`); the DXF was delivered 08-30 22:50 local — **61 loops / 58
pieces / 3 180.6 mm² net film**. Only the idealisation (spline → line/arc), the
fillet pass and the export itself are **uncaptured**. Measured kit and the full
record facts: `e2e-228235-manual-diff.md`; open questions:
`e2e-228235-manual-rulings.md` (**NXLEARN-228235 R1–R10, all decided 2026-09-05**).
Record R1 remains the only *fully captured* 2D/DXF
stage.

**R3 = GMT-Master II 126713GRNR (record IN PROGRESS).** Three sessions captured
2026-08-30 and 2026-09-04 (`bf53841f80c7`, `c4dbc89f48b4`, `d2654b7a4440`); final
tree 113 features / 33 bodies in `126713GRNR-RV04.prt`, whose on-disk stamp
(**2026-09-05 00:01:32 UTC**) is *after* the last captured event, so the end state
is outside the record. **No DXF, and no bracelet piece, exists in-record.** R3
adds the curve-network construction (recipe N) and a second flattening session;
every record-R3 value below is PROVISIONAL as of `tasks/NXLEARN-126713/run/SNAPSHOT_MANIFEST.md`
and pending `run/RULINGS.md` (**NXLEARN-126713 R1–R11, all open**). Full write-up: `e2e-126713-method.md`.

Frames: R1 worked with the bracelet along ±X, crown at −Y (rotate 90° for the
repo canonical frame). R2 worked directly in the canonical frame (+Y bracelet,
+X crown). Origin = crystal centre, z = 0 = crystal top, caseback at z ≈ −12.2
(both watches coincidentally).

## 1. Alignment (Stage 0)

R2 recipe (reproducible, preferred):
1. Fit plane to crystal facets — facet region painted, automatic point rejection
   **0.07 mm in R1/R2**. Raw-scan tilt measured: 12.3° (R1), 14.7° (R2).
   **R3 used 0.03 mm** on at least one Fit-Surface/Fit-Plane dialog
   (`session 1/screenshots/dc_viewport_20260830_203047.png`; single captured
   instance, target region uncertain) — the rejection threshold is **not** a
   constant of the method: declare it per fit in the run manifest (**NXLEARN-126713 R11, open**).
2. Fit circle to crystal edge — radius *operator-constrained* (14.75 R1 / 16.0
   R2; the free flat-crystal radius is 14.65–14.70 / 15.5–16.5): only the
   **centre** is the fitted output. Centre projected onto the plane = origin.
3. Axis: fit planes to the two lug-end facets of one bracelet end (normals only
   5.6° apart though the lugs aren't parallel), intersect each plane with the
   mesh, fit a line to each intersection curve, take midpoints (t = 0.5), join
   the midpoints → 3–9 direction at that end; datum plane through that line at
   90° to the crystal plane = symmetry plane; 12–6 axis ⊥ in-plane.
   (R1 used bracelet-flank plane fits + datum axes — same result, less
   reproducible; the exact vector source wasn't captured.)
4. Move mesh CSYS→absolute, delete all scaffolding features (20 features deleted
   in one go in R2; R3 purged ≥9 with `Remove Parameters` ×11 + Delete). All
   construction thereafter happens in the clean frame with the absolute CSYS as
   the only datum. **Associativity differs by record: non-associative in R1/R2,
   Associative = checked in R3** (`session 1/screenshots/dc_viewport_20260830_203718.png`).
   Either way the port persists the transform `T`; associativity is NX
   housekeeping, not geometry.

Notes: the R1 scan has **two components** (78 k-facet detached bracelet tail) —
expect multi-component meshes. The bracelet centre-line sits ≈1 mm off the
crystal centre in R1 — mirrored bracelet pieces needed a +0.4 mm shift.

## 2. Working aids (not film pieces)

- **ROI crops**: sketch a footprint polygon on z = 0, extrude a prism (0…20 mm,
  0…19, −22…+1.8), split the facet body, delete the prism — sectioning and
  fitting then run on a ~1000-facet sub-body instead of the full scan.
  Footprints used: R1 link region x 30.5…47 × y −11…12.4; R1 clasp rectangles
  x −91…−72 and x −181.5…−141.7; R2 lug/end-link hexagon x −11.5…15.8 ×
  y 17.5…40.71.
- **Reference circles** Ø30/Ø38.8 sketched at the origin (z = 0) as visual
  registration for the flattened pieces.
- A **freeform surface fit** on the crown-side flank (R1) was used only as a
  guide to draw boundary splines, never flattened, deleted later.
- **Revolved check-solids (R3, inferred).** Two full 0°→360° `Revolve` features
  (`Revolve(44)`, `Revolve(49)`) consume splines built from *offsets* of
  flat-facet boundaries (the caseback arc; an independent spline) and produce
  **solid**, not sheet, bodies. No dialog text states intent — **inferred** from
  geometry type and timing: a visual cross-check of a typed/fitted 2D profile
  against the scan before committing the flat sketch. Only one solid survives in
  the final topology though two Revolves exist (unresolved). Whether to
  recommend this as practice is **NXLEARN-126713 R7 (open)**.
- The operator kept a **facet checklist collage** (screenshots + red outlines,
  one per intended piece: "these are identical", "slightly bigger →",
  "round it") and consulted a commercial film-kit photo
  (`reference template example.jpeg`) — the product model is explicitly the
  commercial facet-kit layout.

## 3. Facet construction (Stage 2) — as executed

### 3.1 Planar pieces (drawn, not flattened)
- Crystal (R1): Ø30 circle (typed) − 0.35 mm offset → Ø29.3 zero-depth face.
- Crystal (R2): Ø30.8 typed circle at origin (measured crystal r99 ≈ 15.6–15.8 →
  the disc sits 0.2–0.4 mm inside the edge; derive the margin from the measured
  boundary, don't hard-code); cyclops cut-out: rounded-rect lens outline ~7.1 × 5.8 mm
  (lines y = 2.75/−3.05, side arcs R 3.41/3.54, corner fillets R 1.0), offset
  **+0.15 mm** outward, subtracted → disc 706.1 mm² with 9 edges.
- Bezel (R1): flat annulus Ø30.0/Ø38.8 from typed circles (sloped bezel
  deliberately not developed).
- Caseback (R1): 3-point arc picked on the flat-centre boundary → R 13.469,
  offset −0.2 → R 13.269 disc; translated up by a *measured* 12.140 mm onto
  z = 0 (kept a 0.24° tilt — moved, not projected). Caseback (R2): typed circle
  Ø21.5 on a caseback datum plane.
- Clasp lever top (R1): mesh section of the crown logo projected into a z = 0
  sketch, spline-fitted, offset 0.15 mm; two 5.75 × 3.75 rectangles + an
  8.3 × 5.7 outline − logo; zero-depth extrudes.

Zero-depth extrusion of a closed curve = NX's "make a planar sheet"; in Python
just `make_face(wire)`.

### 3.2 Prismatic pieces (profile × extrusion; K = 0)
Bracelet link tops (R1, 3 sheets per link: outer −Y / centre / outer +Y):
1. Section Curve at the three link mid-planes (y = −7, 0, +6; typed distances),
   sampled points projected into sketches on those planes; **Fit Spline** with
   automatic point rejection + Symmetric; trim.
2. Extrude the profile across the link: spans −2…+2.55, −3.1…+1.7, −3.7…+5.05 mm.
   The extrusion *direction* = normal of a plane fitted to the link's outer side
   face (taper ±4–5° on links 1–2, ≈1° on 3–4) — the fit was inserted *after* a
   first default-direction extrude worked (direction is a refinement).
3. Trim: side = datum plane on the fitted side plane (offsets 0…0.5 mm);
   ends = planes **normal to the profile curve at its endpoints** (end tangents
   45°/65°, ~1 mm below the link top — the profile includes the edge blends).
4. Copies along the bracelet at eyeballed +10.5/+20/+30 (mesh truth: pitch
   ≈10.25 mm, outer/centre gaps staggered ~3 mm); each copy **re-trimmed** to
   its own link width; end link copied −10.5 and length-trimmed to 9.0 mm.
   Mirror about YZ (+0.4 mm y shift needed).
   Dead end first: loft between the y = 5 and y = 7 longitudinal sections —
   deleted within minutes (wavy); also an abandoned Through-Curve-Mesh attempt
   (1 primary + 3 cross sections). Under-specified networks are the failure
   mode: on the R3 126713 **every** abandoned attempt was 1 primary + 1 cross
   and produced the NX alert *Output is self-intersecting*; the one that was
   **kept** used 2 primary + 2 cross with exactly coincident corners (recipe N,
   `e2e-126713-method.md` §4).
Other recipe-B pieces: lug-end wall (one profile spline extruded 7.7 mm across
the lug gap); clasp cover (section-profile sketch extruded −4.1…+3.5, ends
trimmed by two boundary-spline cutter sheets extruded −6…+3.5); second clasp
facet (−4.35…+3.9).

### 3.3 Ruled pieces (two boundary curves)
Flanks, lug tops, lug inner faces, lug undersides, crown guards, clasp sides —
**except the lug-flank/case-shoulder transition, which needs recipe N** (R3:
ruling its two primaries misses the surface by 1.985 mm and over-states area by
15.86 %). Recipe C is valid only where a **straight** transverse end is
acceptable, because the end of a 2-section loft is a straight ruling; in the R3
part the two big flank bands even have degenerate ends (0.00 / 0.33 and
0.00 / 0.37 mm — their section curves converge to a point):
1. Two degree-5 splines drawn point-by-point ON the mesh (points snapped to
   facets) along the facet's top and bottom edges. (591 Studio-Spline dialog
   events in one session — the most manual step; automate via ridge extraction.)
2. Through Curves between them: 2 sections, G0, *Parameter* alignment,
   Preserve Shape off → ruled sheet (measured: cubic with 4 collinear poles per
   ruling = exactly ruled, but **skew** — Gaussian curvature negative,
   |K|max 0.001–0.039 mm⁻², so *near*-developable, not developable).
   Discriminator, measurable on any imported STEP: a 2-section `Through Curves`
   sheet is a degree-3/3 B-spline with **4 poles in v** (one Bézier span
   across); a `Through Curve Mesh` patch has many (R3: **12×11**). Use the
   v-pole count to tell recipe-C output from recipe-N output.
3. End closure: both boundary splines terminate on a common transverse closing
   curve (a line/bridge-spline/trimmed spline); the closing curve is extruded
   into a cutter sheet (spans −4.5…+5.9 R1; −2.5…+1.8 and −22…+2.4 R2; direction
   from a plane fitted to the adjacent facet) and the sheet is trimmed with it.
   Trim direction was wrong on the first try ("Reverse Direction") routinely.
4. R2 lifts each sheet 0.05–0.15 mm off the mesh (visual separation only — the
   sheets measure ON the scan skin; a translation doesn't change the outline).
5. Mirror across the datum planes for the symmetric copies, then nudge each copy
   onto the scan by eye: 0.1–0.7 mm translations, 0.65–1.5° rotations — scans
   are not symmetric at that level. (Port: build each side from its own region.)

### 3.4 Patterned pieces (bracelet links, R2 refinement)
Transverse Section Curve (sampled points, 0.15 mm spacing, 0.010 mm tol) on one
link → **Fit Circle** (28 pts, rejection 0.07, R = 2.8787, max err 0.0097) →
extrude the arc along the link axis (typed −2.2…+2.5, −2.3…+2.8 mm) → **margin
the patch: `Offset in Face` → `Divide Face`** → Pattern along the bracelet →
per-copy nudges. The developed piece of a cylinder patch is exactly (R·θ) × L —
a rounded rectangle.

**Margin values — corrected 2026-09-05 from the surviving feature tree (session
`9d37b4e756ee`); supersedes the earlier "~0.25–0.3 mm" reading.** Seven
`Offset in Face` + seven `Divide Face` pairs, ids 74–80 on Body(66–72), at
**0.55 / 0.65 / 0.75 / 0.85 ×4 mm**. Each `Divide Face(N)` reuses its sibling
`Offset in Face(N)`'s expression (both id-74 features share `p171 = 0.55 mm`) —
Divide Face carries no value of its own, it splits the face along the curve
Offset-in-Face just produced. Downstream: `Offset Region(81)` (16.0 mm reach) →
`Mirror Geometry(83)` → patterned instance bodies. All fourteen already exist at
the session's first snapshot, so **the session that built and debugged them is
untraced (between 08-19 and 08-30) and the record cannot answer why the values
are graduated.** A separate **0.30 mm end inset along the link axis** shows up in
the delivered 2D (our 8.400 → manual 7.7930 = 2 × 0.3035 mm).

**Pitch and size classes — corrected.** "pitch iterated to 6.8 mm, count 10" is
not what shipped: the delivered kit carries **14 rows per run at a 7.99 mm SHEET
pitch** (layout only — the piece is 4.047 mm tall, so the inter-piece gap is
3.947), and 6.8 matches neither the sheet pitch nor the mesh pitch
**6.12 ± 0.10** (E2E-228235 F-03). Nor are there "4.7/5.1 size classes": every
mid-row side link is **L 5.295 with a 4.695 mm straight edge** — that straight
edge is what "4.7" actually named — and **no 5.1 exists**. Delivered link
outlines are pure rounded rectangles, R 0.3 corners, centre 7.793 × 4.047 ×13.
See `e2e-228235-manual-diff.md` §3 (**NXLEARN-228235 R5, decided 2026-09-05**).

## 4. Development (Stage 3) — as executed

NX "Flattening and Forming", type Flattening, no rip edges, no constraints,
orientation from a picked origin + U/V per piece (ad hoc; one piece needed a 15°
fix-up rotation afterwards — pick U deliberately). Target = the z = 0 datum
plane; flats land in place above their source, then dragged aside.
Measured fidelity on all 24 kept sheets: ΔA ≤ 0.07 % (worst 0.38 % on a 6.6 mm²
piece), Δperimeter ≤ 0.43 %, max boundary-edge change 0.087 mm — the source of
this skill's gates. Extrusion pieces developed exactly (ΔA 0).

**R2 (added 2026-09-05, session `9d37b4e756ee`) — same settings, confirmed on a
second record (record R3 below makes it three).** 18 `Flattening and Forming` create-events = **15 unique flats + 3
duplicates** (features 185/187/193: the duplicate event's timestamp is 0.09 s
after the original, while its linked screenshots are 23–33 s apart, so these are
capture duplicates or immediate edits — **the record cannot say which**; no
human re-runs a dialog in 0.09 s). Dialog live-captured
on F&F(189) and uniform across all 15: type **Flattening**, Outer Boundary none,
Constraint Group "Flattening with" **None**, Rip Edge none, Transformation
Objects none, Distortion Map **None**. **All 15 flats land on z = 0.0000 mm**,
measured on the last STEP export — in place above their source, then dragged
aside. Fidelity ΔA **0.003 %** (FLANK_9, 203.1532 vs 203.1470), **0.002 %**
(3-face patch, 25.9644 vs 25.965), **0.18 %** (LUG_UNDER candidate, 11.4293 vs
11.409) — inside R1's worst case, so the gates stand. Only **4–5 of the ~36
bracelet-link bodies were individually flattened**: one representative per size
class, not every copy. 6/15 flat identities are high-confidence; **9/15 are
unresolved** because the Flattening dialog's Source-Face pick is never logged as
typed data and four source parents are leaf bodies with no ancestry — the record
cannot answer which face fed them.

**R3 (session `d2654b7a4440`, 24 min) confirms every line above and contradicts
none** — same command, Type = `Flattening` in all 7 sampled screenshots, Outer
Boundary / **Rip Edge** / Transformation Objects all unused, Constraint
"Flattening with" = None, Distortion Map never enabled, Preview on, flats land
above their source and are then dragged aside. It adds five facts:
(a) the orientation group also offers **`Specify CSYS`** (3 clicks) beside
Origin/U/V; (b) one **4-face compound Source Face** was flattened in a single
operation (`session 3/screenshots/dc_viewport_20260904_234300.png`), the other
five named picks being "Select Face (1)"; (c) the Convergent mesh body is still
present and hoverable during flattening; (d) a Measure→Point→Measure excursion
suggests the operator sometimes *places* a reference point to plan the next
Origin/U pick; (e) **U-direction churn is the dominant friction — 34 U clicks vs
15 Origin picks, 8 V picks and 9 Reverse Direction toggles**, far more than R1's
single 15° fix-up. Pick U deliberately.
Layout was **100 % dynamic mouse-drag Move Object with no typed distances** (the
whole 1,440-event session logs one `text_input`, and it belongs to an unrelated
licence window). **8–12 sheets flattened (inferred**: only 3 clicks resolve to
the name "Apply"; 71 more resolve to a generic fallback name). No regularisation
(Stage 4) was observed — **unknown, not absent**: R3 never reached the 2D redraw
stage, and its final state was saved after the capture ended.

## 5. 2D kit assembly (Stages 4–5) — record R1 fully; record R2's opening captured; record R3 never reached it

1. In the 3D part: originals of mirrored sets deleted; whole kit mirrored about
   YZ for the second side; spacing nudges 0.5–2.1 mm; 46 flat sheets at z = 0.
2. Copy/paste all flat sheets into a fresh `_DXF` part (75 unparameterised
   bodies; first batch of 12 + an Extend-Sheet/Sew repair discarded). Group
   moves — 25 bodies by exactly (−48, +48) — some pieces rotated 90°; nest
   reaches 124 × 80 mm, gaps 0.6–2.2 mm.
3. One sketch on the XY plane; **Project Curve** (449 objects, tol 0.010,
   non-associative) traces the sheet edges; then the **idealisation pass**:
   - fold/bevel edges deleted — only each strip's main face becomes a piece
     (~70 of 129 faces, the 1.4 mm bevels, were dropped);
   - centre links re-drawn as one exact 7.315 × 8.75 rectangle, patterned
     5 × 11.0 mm (bodies sat at 12.1/11.5/11.5/11.0);
   - outer links unified to one outline per size class and mirrored to the
     other row (the other row's own traces discarded);
   - lug tops/flank redrawn slightly smaller; one piece drawn at round
     coordinates; projected 4-pole "splines" (straight edges) later removed;
   - sketch curves moved/rotated *inside the sketch* (dynamic, 5° snap) — DXF
     positions ≠ body positions.
4. Corner fillets R 0.2 in the sketch; hide bodies; export via NX 2D Exchange →
   AutoCAD 2004 DXF (reads the *saved* part — an intermediate save exported
   pre-fillet as v1). Five days later: 4 "horn" pieces added (lug outer flanks,
   left open by 0.715 mm, 0.73 mm tip), fillets doubled to **R 0.4** → RV02 =
   final. RV02 geometry exists only in the DXF (the part was never re-saved).

**R2's 2D stage (added 2026-09-05, session `0f041089bd6f`) — the same shape of
process, captured only up to the raw projection.** Layout first: all 17 new
`Move Object`s carry `expressions: []` (Motion Dynamic, Associative on, Move
Original) — pure drags, against 45 pre-existing moves that each carry a typed
scalar; `Move Object(197)` is a **group move** of 4 flats at once (the analogue
of R1's 25-body (−48, +48) move, but untyped). Then **exactly one sketch**,
SKETCH_005 (id 204) on the global Datum CS(0), view Top, and **Project Curve**
with **Associative OFF, Output Curve Type Original, Tolerance 0.010 mm** — the
same settings as R1's 449-object pass (R2's final object count was never logged;
the running count reached ≥13). `nx_sketch_entered` reports **65 entities, of
which ≥19 splines**, and the delivered DXF has **zero** splines — so an
idealisation pass exactly like R1's happened, but **in the uncaptured window**,
together with the fillet pass and the replication of the link representatives
into the 44 bracelet pieces. A **save hang** interrupted the session ("Saving
50 %", a ~3.2 s "Save Failed", recovery by NX restart, no backup on disk).
Export (log only, no session): NX2206.9140 → AutoCAD 2004 2D Exchange,
**195 Line / 261 Arc / 6 Circle in**, +6 translator Layout objects out, CPU 1 s.
Delivered file: layer "1" only, no SPLINE/POLYLINE, all 61 loops closed at
0.06 mm — and, like R1, **no labels at all**.

## 6. Time profile (where automation pays)

Manual hotspots by event volume: Studio-Spline boundary drawing (≈600 dialog
events), Move Object layout/nudging (≈200 features + 42 dialog visits),
mirrored-copy rotation fitting (~35 retries in one hour), Pattern pitch
iteration (10 tries), Divide-Face margin attempts (6 offsets, repeated errors on
08-19 — the pair **did** converge later, see §3.4).
Total wall time ≈ 4 working days for watch 1 + ≈ 2 for watch 2's 3D stage, plus
watch 2's captured 08-30 finish (3 h 25 m of flatten + layout + 2D, then ~4 h of
uncaptured refinement to the delivered DXF).
The automated port should spend its sophistication on: ridge/boundary-curve
extraction, per-instance link measurement, and deterministic nesting.

## 7. Open questions the record cannot answer (carry into runs as declarations)

- Adhesive-side/handedness convention per piece (DXF mirrored or not for the
  cutter) — contract decision.
- Clearance policy — **no longer open, decided 2026-09-05** (NXLEARN-228235):
  crystal/bezel seam = **0.35 mm gap** (the delivered 228235 kit's 0.437 mm
  overlap was a one-off, R2b); crown notch = **crown radius at the flank height
  − 0.15 mm, about the crown axis** (R3b); corner fillet **R 0.3 on
  links/lugs/tabs, R 0.4 on long flank pieces** (R7). The remaining values stay
  per-facet-class defaults to confirm per job: caseback 0.2, cut-outs 0.15, and
  the R2 link margins measured **0.55 / 0.65 / 0.75 / 0.85 mm in-surface** plus
  a **0.30 mm** end inset (graduation still unrecorded).
- Whether the bezel annulus simplification (no development of the slope) is
  acceptable per watch model.
- Which facets belong in a kit for a given watch — always the Stage-1 inventory
  confirmation.
- 12 o'clock sign on the R1 bracelet.
- The R2 steps that no session captured, and that therefore stay inference:
  (a) the **margin session** where `Offset in Face`/`Divide Face` was built and
  debugged (between 08-19 and 08-30 — it is why the graduated 0.55–0.85 values
  have no rationale); (b) the **idealisation** of the 65-entity, ≥19-spline raw
  projection into 195 Line / 261 Arc / 6 Circle; (c) the **fillet pass**;
  (d) the **replication** of the 4–5 flattened link representatives into 44
  bracelet pieces; (e) the **RV3 → RV7 saves and the export** (captures end
  08-30 21:32 local; RV3–RV7 are stamped 21:45 → 22:49 and the DXF 22:50).
- **The eleven record-R3 questions are all still open** — `NXLEARN-126713 R1–R11`
  (`tasks/NXLEARN-126713/run/RULINGS.md`): lug-outer-flank piece or flank-sheet end (R1),
  network-piece gate vs sub-split (R2), K-gate sampling vs analytic curvature (R3), caseback
  reference boundary and sign (R4), LSCM as the recipe-N development of record (R5), the
  0.20 mm C→N trigger (R6), revolved check-solids as practice (R7), the Jubilee piece scheme
  (R8), cyclops shape per watch (R9), typed vs derived crystal Ø (R10), and 0.03 vs 0.07 mm fit
  rejection (R11) — all ids in the `NXLEARN-126713` namespace. Until each is answered the skill
  keeps its existing default and the record-R3 value stays PROVISIONAL. Record R3 also leaves its
  **final flattening/layout state uncaptured** (`126713GRNR-RV04.prt` is stamped after the last
  captured event) and has **no DXF and no bracelet piece**.
