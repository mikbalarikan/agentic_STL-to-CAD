# R3 end-to-end — GMT-Master II 126713GRNR (record IN PROGRESS, no DXF)

Third recorded NX project: Rolex **GMT-Master II 126713GRNR** (GMT bezel, cyclops crystal,
**Jubilee** bracelet). Three capture sessions, 2026-08-30 (session 1) and 2026-09-04
(sessions 2–3).

> **Status framing — repeat it wherever an R3 number is used.** The maintainer's manual task
> is **unfinished**. `126713GRNR-RV04.prt` (68,316,141 B) is stamped **2026-09-05 00:01:32 UTC**,
> *after* session 3's last event (23:54:57 UTC), so the final state is not in the record.
> **No DXF exists. No bracelet piece exists in-record as of RV04.** Every claim below is
> "as of the snapshot in `tasks/NXLEARN-126713/run/SNAPSHOT_MANIFEST.md`", every R3-derived
> default is **PROVISIONAL** until the maintainer answers `run/RULINGS.md`, and there is no
> diff target to grade a port against. This is method learning only.

Primary distillations (do not re-derive from the raw journals):
`tasks/NXLEARN-126713/run/{SNAPSHOT_MANIFEST.md, session_1.md, session_2.md, session_3.md,
tcm_analysis.md, tcm_prototype_results.json}`. Corrections to the maintainer-authored task
pack: `run/RECORD_MAP_CORRECTIONS.md`. Screenshots are cited as `session N/screenshots/<file>`
(local read-only record folder); UTC throughout (the taskbar clock inside each screenshot is
local UTC+3).

---

## 1. Identity, snapshots, caveats

| item | value | source |
|---|---|---|
| sessions | `bf53841f80c7` (S1, 20:26–20:54 UTC 2026-08-30), `c4dbc89f48b4` (S2, 17:08–22:48 UTC 2026-09-04), `d2654b7a4440` (S3, 23:30:54–23:54:57 UTC 2026-09-04) | filenames, distilled TSVs |
| scan | `126713GRNR.stl`, 180,982,134 B, mtime 2026-08-18 | SNAPSHOT_MANIFEST |
| part revisions | `126713GRNR.prt` → `-RV02` (17:26:03) → `-RV03` (17:42:08) → `-RV04` (20:49:49, final on-disk 2026-09-05 00:01:32) | S2 snapshots; manifest |
| final captured tree | **113 features, 33 bodies (32 sheets + 1 solid), 35 faces, 143 edges** @ 22:45:27 | `session_2_last_feature_tree.txt`, `_last_snapshot.json` |
| feature-type census (final RV04) | 50 Spline · 20 Through Curves · 14 Mirror Geometry · **1 Through Curve Mesh** · 4 Extrude · 2 Revolve · 2 Trim Sheet · 2 Trim Curve · … | same |
| flattening | S3 only, **8–12 sheets flattened (inferred)**, only 3 named `Apply` clicks resolvable, final state uncaptured | session_3.md §3, §8 |
| DXF | **none** | — |

**Capture-tool caveats that shape every count** (see also `run/RECORD_MAP_CORRECTIONS.md`):
two concurrent NXOpen journals ran in S2, so every *raw* event count is ≈2×; S1's features were
flushed at save time in two bursts (`detection_method: feature_inference`), so creation
timestamps are not authoring times and ≥9 alignment scaffolding features never reached the
timeline at all; S3's bridge file was missing (`bridge.exists=false` while
`bridge.was_active=true`), so S3 has **zero** `nx_feature_*` events.

**Measurement caveat (this analysis, not the record).** The mesh numbers quoted throughout come
from a *second* pass: the first produced two plausible-looking but wrong fits (a circle fit on a
filled disc; the wrong down-facing cluster taken as the caseback plane). Both are written up as
method lessons in **§6.4** and are now in SKILL.md Stage 0.

---

## 2. Alignment (session 1) — the R3 variant of Stage 0

The part opened with `Datum Coordinate System(0)` + `Convergent Body(1)` already present
(feature_count = 2 at 20:28:29): the mesh import happened before the record starts.

Executed chain (28.7 min): command-search for the Fit tools → **Fit Surface (Fit Plane) ×54**
→ **Datum Plane ×70** (type Inferred, offset 0) → Section Curve ×12 → Fit Curve ×4 → Point ×9
→ Project Curve ×35 → a single **Datum CSYS** visit (20:35:38) → **Move Object "CSYS to CSYS"**
→ `Remove Parameters` ×11 + Delete (bulk scaffolding purge) → save. Surviving output:
`Datum Coordinate System(19)` — the working frame.

Two confirmed differences from the R1/R2 recipe, both patched into SKILL.md Stage 0:

- **Fit rejection 0.03 mm, not 0.07.** `session 1/screenshots/dc_viewport_20260830_203047.png`
  shows Rejection Threshold = **0.03 mm** on a Fit-Surface/Fit-Plane dialog. One instance only,
  and the zoomed target region is a sharply faceted/ridged area that is **not** obviously the
  crystal — so the value is confirmed, its target is not. 0.07 mm remains the R1/R2 default;
  declare the value **per fit** in the run manifest rather than assuming a constant.
- **Move Object was Associative.** `dc_viewport_20260830_203718.png` shows *Associative =
  checked* on the CSYS→CSYS move — R1/R2 used non-associative. Either way the port persists the
  transform `T`; associativity is an NX housekeeping choice, not a geometric difference.

Also new in R3: far more reference geometry than a crystal-plane + lug-axis pair implies
(≥9 named scaffolding features visible in Part Navigator: `Datum Plane(3,5,7,8,9)`, two
`Fit Surface(Plane)`, `Fit Curve(10)`, `Point(11)`, a `Projected Curve`), and one Project Curve
aimed at the **crown top face**. Plausibly the GMT bezel/crown-guard massing needed it —
**inferred**, the exact "two lug-end facets" pick was never screenshotted.

**The crystal circle was typed, not fitted**: `Arc26`, r = 14.35 → **Ø28.7 mm** (a round number,
not a fit residual) — the same fallback the skill already documents for R1/R2 crystal discs.

### 2.1 First sheet: crystal disc + cyclops **lens**

`SKETCH_000:Sketch(19)` → `Extrude(20)` (p9 = p10 = 0, zero depth) = recipe A. Face 607.31 mm²,
9 edges (1 outer + an 8-edge inner loop — the cut-out is a hole in the same sketch, not a
boolean). Reconstructed from `session_1_last_snapshot.json`:

- `Arc26` centre (0,0) r 14.35 → **Ø28.7 crystal disc** (p4).
- `Arc21` r 899.053 / `Arc23` r 905.153, both centred (−0.68, 902.09): two near-flat arcs
  **6.1 mm apart** (p0) = the lens's long sides. (Sagitta ≈0.02 mm over ~6 mm — plausibly three
  near-collinear picks with the Arc tool instead of Line; **inferred**.)
- `Arc24` (8.98, 0.02) r 3.5 / `Arc25` (9.44, 0.06) r 3.5 = the lens end-caps, offset toward the
  crown/date side (x ≈ 5.5…12.9).
- `Arc27–30` r **0.3** = four corner fillets.
- Cut-out clearance **+0.15 mm outward** (`dc_viewport_20260830_204349.png`, Offset Curve
  Distance field) — identical to R2's cyclops clearance.

So the R3 cyclops cut-out envelope is **6.1 × 3.5-radius lens ≈ 6.1 mm tall**, *not* R2's
rounded rectangle (~7.1 × 5.8, side arcs R3.41/3.54, fillets R1.0). An intermediate screenshot
at 20:47:20 shows a **filleted rectangle** 5.0 × 6.1 that was later reworked into the lens
(the `p3` slot is reused 5.0 → 3.5). **Cut-out shape is per-watch; do not carry one forward.**

---

## 3. Surface set (session 2) — 5 h 39 m, 113 features

### 3.1 Revision hops and the "21 deletions"

| snapshot (UTC) | doc | features | bodies |
|---|---|---|---|
| 17:09:48 | 126713GRNR (inherited) | 5 | 2 |
| 17:26:03 | **RV02** (Save As) | 13 | 4 |
| 17:42:08 | **RV03** (Save As) | 16 | 5 |
| 17:58:05 / 20:10:11 | RV03 resave | 35 / 38 | 9 / 10 |
| 20:49:49 | **RV04** (Save As) | 53 | 15 |
| 20:59:07 / 22:20:17 / 22:45:27 | RV04 resave | 61 / 107 / **113** | 18 / 28 / **33** |

`nx_feature_deleted` fires 42 raw times = **21 unique names × 2 journals**, and *only* at
17:26:03/15 and 20:49:49/50 — precisely the two document changes. Every lost name maps 1:1 onto
a gained name of the same NX type with identical expressions (e.g. `Through Curve Mesh(18)` →
`(17)`, parents `Spline(14–17)` → `Spline(13–16)`). **Zero real deletions**: `Save As` compacts
the feature-timestamp counter, and RV03's counter had holes (no `(10)`, `(21)`, `(30)`).
*(Hole-compaction is inferred; the observed −1/−2/−3 shifts are consistent with it and nothing
else. Features created and removed **inside** a revision between journal polls left no timeline
row and cannot be enumerated.)*

Corollary for any distillation tool: `session_2_feature_timeline.tsv` keys on feature **name**,
so a name reused across revisions collapses two features into one row and reports *last-seen*
parents. Resolve identity from `model_snapshot.feature_tree`, never from that TSV's parents.

### 3.2 Sheet ledger (final kept bodies)

No body↔feature key exists in the topology export, so facet names are **inferred** unless marked
[confirmed]. Full table in `session_2.md` §3; summary:

| feature | facet | class | confidence |
|---|---|---|---|
| `Extrude(3)` (from inherited `Sketch(2)`) | crown-area / crystal-logo sheet | A | [confirmed] inherited from S1, expressions unchanged |
| `Through Curves(6)` + `Mirror Geometry(8)` + `Move Object(9)` | **crystal-disc candidate**, built over the crystal/bezel bore | C (2 curves) | [confirmed visually] `dc_viewport_20260904_172459.png` |
| `Through Curves(12)` | 9-o'clock flank band, 243.80 mm², runs y −23.74…+23.66 | C | measured in the STEP (`q10`), facet name inferred |
| **`Through Curve Mesh(17)`** + `Mirror Geometry(18),(19)` | **lug outer flank / case-shoulder transition**, 41.851 mm², ×4 lugs | **N** | see §4 — STEP-measured |
| `Through Curves(27),(30)` + `Mirror Geometry(31)` | flank/lug family | C | inferred |
| `Through Curves(34)`, `(53)` (3-section variant), `(60)` | flank/lug family | C | inferred |
| `Extrude(37)` (from `Arc(35)` + `Offset Curve(36)`) | **CASEBACK disc** | A | [confirmed] z ≈ −12.15…−12.20 |
| `Revolve(44)`, `Revolve(49)` (0–360°) | **check solids**, not film pieces | — | inferred from geometry type (§3.4) |
| `Extrude(47)` (typed Ø30.0 / Ø35.4) | bezel **or** crystal annulus | A | [confirmed typed], role unresolved |
| `Through Curves(75..81)` (7), `(96)`, `(101..104)`, `(106)` | lug-top / lug-under family, built **per side** (not mirrored) | C | inferred from the 22:18 sprint + the failed-Extrude screenshot |

The crown-side flank sheet is `Through Curves(6)`'s neighbour family, **93.763 mm²**, and it
**stops at y = −6.30 where the crown interrupts it** — while the −X (9-o'clock) flank runs the
full lug-tip-to-lug-tip span. That asymmetry is the measured form of the standing crown-side
rule (see `run/RULINGS.md` R2).

### 3.3 Error dialogs → three new pitfalls

| dialog | ×  | message | reading |
|---|---|---|---|
| **Save Failed** | 7 | "…failed to save … No write access" | Google-Drive-mapped `H:` write lock; the dialog sat open 17:24:59 → 17:40:39 (~15 min lost). Environment, not modelling. |
| **Cannot add to section** | 7 | "Selected objects will result in a self intersecting section." | a self-intersecting section/trim curve (around `Spline(28)`/`Trim Curve(23)`) — fix the curve, don't retry. |
| **Alert Dialog** | 3 | "Cannot extrude. The distance or direction may be incompatible with the section." | a zero-depth Extrude attempted on a **doubly-curved lug-root saddle**: recipe A needs a *planar* section. Use a ruled or network sheet there. `dc_viewport_20260904_221808.png` |
| Input Validation | 2 | "Incorrect value in Degree: 0…Replacing with the value: 0" | cosmetic auto-correct, no geometric change. |

Also abandoned without leaving a feature: **`Swept`** (4 dialog events) and a 22-second
**`Flattening and Forming`** trial at 20:33:43 (no flatten-typed feature in the final tree —
development is entirely session 3).

### 3.4 Caseback: the opposite clearance sign from Kit 1

`Arc(35)` is a **3-point fit ON the flat-centre boundary**, expressions p137–p145:
P1 (−10.4388, 1.98907, −12.1565), P2 (6.8691, −8.08819, −12.1447), P3 (6.82964, 7.95533, −12.1951).
Circumcircle (computed by the orchestrator from those three points, not read off screen):
centre **(−0.058, −0.083)**, **R 10.586 → Ø21.17**, z −12.165. `Offset Curve(36)` then offsets
**+0.15 mm outward** → **Ø21.47**, which lands on Kit 2's typed caseback Ø21.5.

So the record contains **two conventions**, distinguished by which boundary is fitted:

| reference boundary | operation | example |
|---|---|---|
| caseback **rim edge** arc (R 13.469) | **−0.2 mm inset** → Ø26.54 | Kit 1 / R1 `Offset Curve(194)` |
| caseback **flat-centre boundary** (R 10.586) | **+0.15 mm outward** → Ø21.47 ≈ typed Ø21.5 | Kit 3 / R3 `Offset Curve(36)` |

Both are self-consistent: the rim edge is *outside* the film's target, the flat-centre boundary
is *inside* it. **The sign is not universal — it follows the reference.** Which boundary should
be the standard, and therefore which sign, is **ruling R4**; the Kit-1 default (fitted rim edge
− 0.20 mm) stays in the parameter card until answered.

**Mesh reframing (§6.3).** The independent measurement puts this watch's caseback flat boundary
at **R 11.24** (r99; **11.20** by the > 0.1 mm departure criterion, ±0.3) on a plane at
z −12.164 — the same plane the operator fitted, to 0.001 mm. His 3-point arc **R 10.586**
therefore sits **≈0.65 mm *inside* the mesh-defined flat boundary**, and even after the +0.15 mm
outward offset the film edge (Ø21.47) is still **≈0.5 mm inside** it (mesh flat **Ø22.48**). So
**both conventions are net insets from the mesh boundary** — R4 is not "inset vs outset", it is
*which curve was fitted, and by how much*: mesh flat boundary − 0.5, rim edge − 0.2, or fitted
3-point arc + 0.15. Note that a 3-point circumcircle has no residual and cannot report this
error itself; only an independent estimator exposes it.

### 3.5 Working aid: revolved check solids (new, inferred)

Two full `Revolve` features (0°→360°) consume splines built from **offsets of flat-facet
boundaries** — `Revolve(44)` from `Offset Curve(39)` of the same caseback `Arc(35)`,
`Revolve(49)` from an independent spline — and produce **solid**, not sheet, bodies. No dialog
text states intent; the inference (from geometry type + timing) is that they are **visual
cross-checks of a typed/fitted 2D profile against the scan** before committing the flat sketch,
i.e. the R3 sibling of R1's freeform-surface guide. Only **one** solid body survives in the
final topology though two Revolves exist — unresolved. Recommending them as standard practice
is **ruling R7**.

---

## 4. The kept `Through Curve Mesh` — recipe N

### 4.1 Which facet (session-2 label superseded)

`session_2.md` §3 labels this sheet "crown-side flank (FLANK_3 crown side) … draped over the
crown boss and its guards", from `session 2/screenshots/dc_viewport_20260904_174845.png`.
**That label is superseded.** Measuring the RV04 STEP
(`session-c4dbc89f48b4_e6ee61dc_126713GRNR-RV04_20260904_235653.step`, 241,438 B,
sha256_16 `26f98ede7b1e9920`; `q12`, `q14`) puts the four identical **41.851 mm²** faces at

    x ∈ ±[10.27, 16.61]   y ∈ ±[11.67, 23.93]   z ∈ [−10.87, −4.18]

i.e. **one per lug**, symmetric in *both* x and y — a crown-side piece could not be. Frame
calibration from the same STEP: bezel = surface of revolution **Ø38.20** at z ∈ [−1.19, −0.43];
caseback **Ø27.30** at z ∈ [−12.13, −11.30] plus a plane at z = −12.16; so z = 0 is the case top,
z ≈ −12.2 the caseback, case Ø ≈ 38.2 mm, crown side = +X.

**Canonical name: the lug outer flank + the case shoulder it grows out of** — the doubly-curved
saddle where the round case flank turns into the lug and falls from z = −4.2 to z = −10.9 on the
way to the lug tip at y ≈ 23.8. Not a plain FLANK strip, not a LUG_TOP: the transition between
them, bounded inboard by a near-horizontal case contour (z ≈ −4.25) and outboard by the lug-tip
end wall.

**Why this matters beyond R3:** Kit 1's `HORN_*` pieces are exactly this facet — "lug outer
flanks, added 08-20, **source unrecorded**", delivered **open by 0.715 mm with a 0.73 mm tip**,
the defect archetype in `references/dxf-contract.md`. R3 is the first record that shows how the
maintainer *builds* one. It also collides with the standing maintainer rule from E2E-228235
("lug outer walls = flank-sheet ends, never separate pieces") — **ruling R1**; the hub rule wins
until answered and this document does not resolve it.

### 4.2 The curve network

Parents: `Spline(14),(15),(16),(17)` (RV03 names; `(13)…(16)` after the RV04 hop), all Studio
Spline points snapped onto the Convergent body between 17:42 and 17:47. **`Spline(17)`'s own
parents are `Spline(14);Spline(15)`** — it was built as a **bridge curve across the ends of the
two long splines**, which is exactly what guarantees the corner coincidence a network surface
needs. 2 primary + 2 cross is the only reading consistent with 4 parents and G0 on *First/Last*
of **both** sets (the captured dialog frame shows only "Primary (1)/Cross (0)" mid-selection) —
**inferred**, together with which two are primaries (the long, shape-defining pair).

Boundary curves, measured on the `x<0, y>0` copy (`q14_frame.py`):

| role | length | from → to (x, y, z mm) |
|---|---|---|
| primary, outer | **15.701** | (−16.61, 11.67, −4.23) → (−13.20, 23.72, −10.87) |
| primary, inner | **9.924** | (−10.34, 17.31, −4.29) → (−10.27, 23.92, −10.63) (x constant to 0.13 mm) |
| cross, case end | **8.541** | (−10.34, 17.31, −4.29) → (−16.61, 11.67, −4.23) |
| cross, lug tip | **2.952** | (−10.27, 23.92, −10.63) → (−13.20, 23.72, −10.87) |

Dialog settings read off `session 2/screenshots/dc_viewport_20260904_174721.png`:
Continuity → **Apply to All unchecked**; First/Last Primary and First/Last Cross all
**G0 (Position)**; Preview checked; selection filter `Infer Curves`. All four G0 ⇒ a **Coons
boundary patch**, no tangency to neighbours. *Output Surface Options / Settings were collapsed
in every captured frame → `MISSING: Emphasis / Intersection tolerance / Spine / Construction
alignment`; NX defaults assumed.*

**Mirrors.** `Mirror Geometry(18)`,`(19)` reflect across the model YZ and XZ datum planes
(`p65 = 0.0 mm`, parent `Datum Coordinate System(0)`), giving the same piece on all four lugs.
Per the skill's own mirroring policy those copies would still need per-side registration on a
real scan; the record does not show that step **for this piece**.

### 4.3 Why the 2-curve ruled sheet was not enough here

Every `Through Curves` sheet in the part is a degree-3/3 B-spline with **4 poles in v** — a
single Bézier span across, i.e. straight rulings. The TCM is the only surface with more
(**12 × 11**). That pole count is a usable discriminator on any imported STEP.

| feature | area mm² | poles u×v | boundary lengths mm | K_abs_max (analytic) |
|---|---|---|---|---|
| `Through Curves(6)` crown-side flank | 93.763 | 27×4 | 26.78, 19.19, 0.37, **0.00** | 6.69e-3 |
| `Through Curves(12)` 9-side flank | 243.800 | 37×4 | 55.25, 49.55, 0.33, **0.00** | 3.09e-3 |
| `Through Curves(…)` caseback-rim band | 82.361 | 39×4 | 26.07, 24.88, 3.01, 1.75 | 9.81e-3 |
| `Through Curves(…)` crown-guard patch | 32.262 | 19×4 | 11.54, 9.10, 6.21, 5.17 | 2.72e-2 |
| **`Through Curve Mesh(17)`** | **41.851** | **12×11** | 15.70, 9.92, 8.54, 2.95 | **1.10e-1** |

The two big flank bands have **degenerate ends** (0.00 / 0.33 and 0.00 / 0.37 mm — their section
splines converge to a point), so a straight end ruling costs them nothing. The TCM facet's ends
are real curves of 8.541 and 2.952 mm. Building the recipe-C candidate on its two primaries
(`ruled_sheet.ruled_face` / `BRepFill.Face_s`) and comparing with the kept surface (`q12`):

| measurement | value | skill gate |
|---|---|---|
| ruled area vs TCM area | 48.490 vs 41.851 mm² = **+15.86 %** | area error ≤ 0.4 % |
| TCM surface → ruled sheet, max deviation | **1.985 mm** (mean 0.511, p95 1.450) | — |
| cross curve 1 (8.541 mm) → ruled sheet | **max 2.293 mm** (mean 1.079) | — |
| cross curve 2 (2.952 mm) → ruled sheet | max 1.346 mm (mean 0.671) | — |
| sagitta, case-end cross | **0.590 mm** (arc/chord 8.541/8.434 = 1.0127) | a straight ruling must accept it |
| sagitta, lug-tip cross | 0.046 mm (1.0018) | negligible |

Two independent reasons, in this order: (1) the transverse ends are curved and a 2-section loft
can only put a straight chord there — 0.59 mm of outline error at that edge alone; (2) the
interior is doubly curved and the primaries are not parallel enough — straight rulings cut the
corner by up to 1.985 mm and over-state area by 15.86 %.

**The record does not show a failed ruled attempt on this facet.** `Through Curves(13)` (built
six minutes earlier, 17:42:08) is the 243.80 mm² 9-o'clock flank band and survives to the final
tree as `Through Curves(12)` — a *different* facet. The maintainer went straight to a network.

### 4.4 Open→cancel cycles and the real time cost

7 `Through Curve Mesh` dialog sessions, 217 events, **180.0 s** total dwell
(`q15_dialog_sessions.py`, 20 s gap clustering):

| # | window (UTC) | dwell | outcome |
|---|---|---|---|
| S1 | 17:47:19 → 17:47:41 | **21.9 s** | **OK → `Through Curve Mesh(18)` created — the only kept one** |
| S2–S7 | 17:58:39 → 20:23:42 | 158.1 s total | all cancelled |

`dc_viewport_20260904_175946.png` (inside the 74.7 s S3) shows why the later attempts failed:
**Primary Curves (1) / Cross Curves (1)** — a 1×1 network on a much larger region spanning the
bezel — with NX's Alerts panel reading **"Output is self-intersecting."** and a visibly folded
preview. Same failure family as R1's abandoned "1 primary + 3 cross" attempt: **under-specified
network for the region**, not an unusable operation.

| dialog | sessions | total dwell | kept features | per kept feature |
|---|---|---|---|---|
| Studio Spline | 35 | 2110.2 s (35.2 min) | 50 | 42.2 s |
| Through Curves | 23 | 412.3 s (6.9 min) | 20 | **20.6 s** |
| Through Curve Mesh | 7 | 180.0 s (3.0 min) | 1 | **180.0 s** |

The headline 8.7× is misleading: **the session that produced the network took 21.9 s —
indistinguishable from the 20.6 s mean of a kept ruled sheet.** 88 % of the cost is the six
exploratory re-opens on *other* facets. Deciding *where* a network is needed is expensive;
building one is not. Curve drawing (35.2 min, 63 % of the three dialogs) remains the dominant
manual cost, exactly as `nx-method-evidence.md` §6 already says.

### 4.5 OCP mapping and the prototype

Prototype now bundled as `scripts/curve_network_sheet.py`; archived measurements in
`tasks/NXLEARN-126713/run/tcm_prototype_results.json`. Deterministic on the VPS venv (OCP 7.9.3):
two consecutive runs gave a byte-identical `results.json` (sha256 `688c01eb…b139a2`). Measured on
a **synthetic** facet shaped like the real one (15.4 × 5.4 mm, 74.198 mm²) — synthetic because
the real face lives in a maintainer STEP that is not repo data.

| NX construct | OCP mapping | ran? | measured |
|---|---|---|---|
| TCM, 2 primary + 2 cross, all G0 | `GeomFill_BSplineCurves(p0, c1, p1, c0, GeomFill_CoonsStyle)` → `BRepBuilderAPI_MakeFace` | **yes** | boundary deviation **3.2e-15 … 1.9e-14 mm** (400 samples/curve, tol 1e-4); corner gaps **exactly 0.0**; deg 3/3, 10×8 poles |
| same, as an N-sided plate | `BRepFill_Filling`, 4 edges `GeomAbs_C0, IsBound=True` | **yes** | boundary deviation **5.465e-4 mm** — it *approximates*; area 84.641 mm² = **14.07 %** different interior; K_abs_mean 1.945e-2 (worse than Coons 1.118e-2) |
| ≥3 primaries (Gordon) | no OCC primitive; prototype uses `BRepFill_Filling` + middle primary as an **interior** `IsBound=False` constraint | **yes** | middle-curve deviation **0.135 mm**, boundary **0.104 mm** — ~0.1 mm loose, **not** good enough for a 0.2 mm-class film boundary |
| true Gordon | loft(primaries) + loft(crosses) − tensor-product interpolation on knot-compatible B-splines; prior art **TiGL `CTiglInterpolateCurveNetwork`** (DLR, Apache-2.0) | **no — cited only** | — |

**Use `GeomFill_CoonsStyle` for a 2×2 network.** It is the only one of the three that reproduces
the input curves exactly, and the input curves *are* the cut outline. Corner coincidence is a
**precondition, not a check**: build the cross curves *from* the primaries' endpoints (as the
maintainer did) so corners are shared points, not nearby points.

### 4.6 The trigger threshold (PROVISIONAL, n = 1)

Recipe N is chosen by measuring the recipe-C candidate *before* accepting it: build the ruled
sheet on the two long boundary curves, then measure the facet's transverse **closing** curves
(recipe C step 2 already requires them) against it. Trigger if **either**

- max distance from a closing curve to the ruled sheet **> 0.20 mm**, or
- **sagitta** of a closing curve **> 0.20 mm** (R3 case end: 0.590 mm, arc/chord 1.0127).

Measure the sagitta on the **mesh-derived** closing curve, never on the built sheet: the end of
any 2-section loft is a straight ruling, so its sagitta is identically 0 **by construction** —
gating on it would be self-referential.

Justification for 0.20 mm: the observed positive reads **2.293 mm** and **0.590 mm**; the four
kept ruled sheets in the same part have straight-by-construction ends (0.00 / 0.33 / 0.37 mm end
iso-lengths on the flank bands, 1.75–3.01 and 5.17–6.21 mm on the caseback-rim and crown-guard
patches), i.e. the operator only chose recipe C where a straight end was acceptable — an order of
magnitude below the 0.590 mm that forced a network. 0.20 mm sits above the 0.05–0.15 mm sheet-lift
noise floor of the record and far below the positive. Resolution honesty (gate-integrity rule 2):
the B-rep projection itself resolves ~1e-9 mm, but the *mesh-derived closing curve* it is measured
against carries the 0.2–0.5 mm boundary-extraction uncertainty of recipe C step 1 — the same order
as the threshold. So readings in 0.20–0.50 mm are a grey zone that needs a human call; only readings
≥ 0.5 mm (R3: 2.293 / 0.590 mm) are decisive on their own.
**n = 1 positive example — ruling R6 before this becomes a hard gate.**

### 4.7 Flattening a network piece: LSCM, not `unroll_strip`

A Coons patch is **not** ruled, so developing it along rulings is no longer justified by
construction. Both paths measured on the **real 41.851 mm² TCM face** (`q13_flatten.py`) and
again on the synthetic patch:

| path | real TCM face | synthetic patch | gate |
|---|---|---|---|
| **A** — resample rulings → `ruled_sheet.unroll_strip` → `flattening_report` | iso-strain **0.833 %**, area error **8.22–8.30 %** (stable at n = 60/120/240) → **FAIL** | iso-strain 0.397 %, area error **7.81 %** → **FAIL** | ≤ 0.4 % / ≤ 0.4 % |
| **B** — LSCM on a sampled triangulation, area-normalised | area error **0.028–0.059 %** → PASS; edge strain max **1.066 %**, p99 1.013 %, mean **0.263 %** → FAIL on max | area error 0.033 % → PASS; strain max 2.855 %, p99 2.045 %, mean 0.671 % → FAIL on max | ≤ 0.4 % / ≤ 0.4 % |

LSCM cuts the area error from 8.22 % to 0.028 % — a factor of **290** — and its *mean* edge
strain (0.263 %) is inside the gate. Path A's 8.2 % is a **systematic** error that does not
shrink with sampling (identical at n = 60/120/240) because the ruled surface is simply a
different surface. Path A stays correct for recipe-C sheets, which are ruled by construction.
Adopting LSCM as the recipe-N default is **ruling R5**.

### 4.8 Two gate-integrity problems this piece exposes

1. **The K gate is not reproducible as written.** SKILL.md states `K_abs_max ≤ 6.5e-2 mm⁻²`
   without naming a sampling. `ruled_sheet.developability(A, B, m=7)` measures on an **n × m
   grid with m = 7 by default**, where n is the number of matched boundary samples. On the
   *same* real face the angle-defect max reads **3.124e-2 (pass) at 41×7** and **8.710e-2
   (fail) at 41×41** — a 2.8× swing from the grid alone; the prototype reproduces it
   (5.701e-2 → 8.880e-2 → 9.128e-2 at 41×7 / 41×15 / 41×41). The **mean** is far more stable
   (9.007e-3 → 1.194e-2). Analytic `BRepLProp_SLProps` curvature (21×21 on the real face:
   K_abs_mean 1.31e-2, **K_abs_max 1.10e-1**) is grid-independent and is the reference the
   discrete number should be read against. SKILL.md now names the sampling; **moving the hard
   gate to analytic curvature is ruling R3** — thresholds are unchanged until then.
2. **The kept piece fails the current gates.** The maintainer accepted a surface with analytic
   K_abs_max **1.10e-1** (1.7× the gate) needing ≈**1.07 %** local strain to flatten. Either the
   Stage-3 gates need a documented network-piece variant or the facet must be sub-split —
   **ruling R2**. Corroboration that ~0.11–0.12 mm⁻² is the natural curvature of this facet
   family: `nx-method-evidence.md` §2 already records an R1 crown-flank Fit-Surface at
   "|K|max 0.12" that was **never flattened**. Per CLAUDE.md rule 6 no model resolves a
   hub-vs-record conflict alone; the existing thresholds stay the default.

---

## 5. Development (session 3) — 24 minutes, no captured end state

Zero `nx_feature_*` events (bridge gap), so everything is dialog/click/screenshot
reconstruction. **Confirms** `nx-method-evidence.md` §4 exactly: command
**Flattening and Forming**, **Type = Flattening** in every sampled screenshot (never `Forming`),
per-piece **ad-hoc Origin + U + V** picking, **Outer Boundary / Rip Edge / Transformation
Objects all unused (0 selected)**, **Constraint "Flattening with" = None**, Preview on,
flats land above their source and are then dragged aside. **Contradicts: nothing.**

Adds five things:

1. A **`Specify CSYS`** field in the orientation group (3 clicks) — an alternative to Origin+U+V
   not previously documented.
2. One **4-face compound Source Face** (`session 3/screenshots/dc_viewport_20260904_234300.png`,
   "Source Face (4)") — a stitched multi-patch sheet flattened in one operation; the other five
   named picks are "Select Face (1)".
3. A **"Convergent Face of Convergent Body(1)"** status-bar hit — the mesh body is still present
   and hoverable during flattening alongside NURBS sheets.
4. A **Measure → Point → Measure** excursion (23:46:15–16) — the operator sometimes places a
   reference point to plan the next Origin/U pick instead of eyeballing it. No numeric readout
   was captured (Measure's result is a read-only label).
5. **U-direction churn: 34 U-direction clicks vs 15 Origin picks, 8 V picks, 9 Reverse Direction
   toggles** — far more than R1's single "15° fix-up rotation". This is the strongest evidence
   yet for SKILL.md Stage 3's "choose the development's U direction deliberately".

Layout is **100 % mouse-drag**: 201 Move Object events over 40 visits, Motion = Dynamic (also
Distance seen once), Result = Move Original / Layout Original / Associative on; the **whole
session logs exactly one `text_input`, and it belongs to the unrelated Router licence window** —
no typed coordinates or distances anywhere. Objects were sometimes picked from the Part
Navigator tree rather than the viewport.

**Sheets flattened: 8–12 (inferred range).** Only **3** clicks resolve to the name "Apply"
(23:44:38, 23:49:22, 23:49:36); another **71** Flattening-dialog clicks resolve only to the
generic fallback name "NX 2206" and certainly include further confirms. The last screenshot
(23:54:38) shows **8 flat panels in two staggered rows** still tilted in 3D near the model — an
in-progress staging arrangement, **not** a nested 2D layout. RV04 was written to disk ~7 min
after the session's last event, so **the final layout is outside the record**.

**No regularisation (Stage 4) was observed — that is "unknown", not "absent"**: this record
never reaches the 2D redraw stage that R1 documents.

---

## 6. Jubilee bracelet — and the independent mesh measurement

### 6.1 The record contains no bracelet piece

`RECORD_MAP.md`/`TASK.md` state that R3 contains "a full facet set for a Jubilee bracelet".
**That is false as of RV04.** No spline, `Through Curves`, or `Pattern Geometry` feature in the
122 distinct session-2 features has a parent/child chain touching a link-row profile, and no
typed pitch/span expression resembling recipe D (cf. R2's pitch 6.8 mm × 10) appears anywhere.
The only bracelet evidence is visual: the operator's annotated checklist `126713GRNR.png` marks
**one Jubilee centre-row link** and **long dashed strips along the bracelet** as targets, and
several screenshots show small yellow highlight patches on link edges (visual survey, no
construction). See `run/RECORD_MAP_CORRECTIONS.md`.

Kit 3's bracelet geometry therefore comes **only** from an independent measurement of the scan
mesh (`tasks/NXLEARN-126713/run/jubilee_geometry.md` + `.json`) plus that collage intent —
never from the record. The Jubilee's five-row architecture makes the piece scheme itself an open
question (one piece per centre-row link vs. long strips per row): **ruling R8**.

### 6.2 Measured structure (`126713GRNR.stl`, 3,619,641 triangles)

Frame recovered independently of the record and cross-checked against it: crystal plane fit
rms **0.0087 mm** (68,171/68,538 inliers, 0.07 rejection), crystal/caseback disambiguated by an
interior cyclops-bump test (2,885 bump points vs 0), 12–6 axis from PCA of the aligned XY cloud
(eigenvalue ratio **12.5** — the ~200 mm bracelet dominates the ~44 mm case), crown side = the
larger case-band X extent. Five sanity checks pass: crown **+24.04**, 9-flank **−20.28**,
extent X 44.31 / Y **205.25**, crystal mean z **0.000**, caseback z **−12.164** (record:
−12.165). Raw-scan tilt **5.69°**. +Y is the **shorter** arm (62.3 mm), −Y the longer (93.2 mm);
with no clasp in the scan, which one is 12 o'clock is **not claimed**.

**5 rows confirmed: 2 outer + 2 inner + 1 centre.** Method matters here — a single transverse
height profile shows **no** sustained step at the three inner/centre seams (the top surface is
nearly flush, < 0.3 mm), and direct peak-finding on one profile was tried first and failed.
The seams were recovered by pooling small periodic **rivet/pin witness dips** (< 0.1 mm deep,
prominence > 0.06 mm) from ~70 stations per arm into a 0.2 mm X-histogram and taking its four
strongest peaks. Only the two outer boundaries have a direct height signal, so the two methods
are **not** of equal strength — state which produced a given seam.

| row | width (mm) | pitch (mm) | link length (mm) | crown |
|---|---|---|---|---|
| OUTER ×2 | 4.06 / 4.38 / 4.61 (+ one sample 3.50) | 6.30–6.50 | 4.85–4.98 | fitted **R 5.40**, sagitta **0.296** over 4.06 (Kåsa, resid_max 0.067, transverse X–Z section at y = +60.52) |
| INNER ×2 | 2.80–3.00 | 6.20–6.55 (one corrupt, below) | 4.78–4.92 | **not fitted** — only a raw within-row z-range 0.86–1.45, which includes the seam-edge drop and is not a crown radius |
| CENTRE ×1 | 3.00 | 6.40–6.55 | 4.99 / 5.08 | fitted **R 2.626**, centre (x 0.088, z −11.610), sagitta **0.284** over 2.70 (113/164 pts, resid_max 0.069) |

**Consolidated: pitch 6.5 mm on every row, gap 1.5 mm, link length 5.0 mm.** The pitch is the
median of 9 self-consistent row×arm medians (6.20–6.55); the tenth (+Y INNER(−), **4.40**) is
corrupted by a ~6 mm-wide localized mesh-noise band at y ≈ 64–69 that also wrecks that arm's
inner link length (2.82) — excluded, not smoothed. Taper: −Y 19.93 wide at the case boundary →
16.67 plateau from y ≈ −49; +Y 21.45 → 15.45 from y ≈ +48.

**No half-pitch stagger — this is the headline correction.** The centre-vs-outer offset measures
**0.0 ± 0.33 mm** (9 pairs; 0 % of the 6.55 mm pitch, jitter ≤ 7 %): all five rows' peaks and
valleys land at the same Y across the full width. The task pack's classic-Jubilee assumption of
a staggered centre row is **wrong for this bracelet**, and the measurement was reported as-is
rather than corrected toward the expectation (CLAUDE.md hard rule 6).

**The clasp is not in this scan.** No region of either arm deviates > 2 mm from the 15.4–16.7 mm
plateau width, and both free ends *narrow* (−Y to 12.9–13.2 over its last 4 mm, +Y to 9.0–12.6
over its last 3 mm) while the periodic link pattern continues to the cut edge — a tapered end
link, not a cover plate. The arms were most likely cut at the clasp attachment pins. **No clasp
rows exist in Kit 3**, and no clasp location, extent or width can be reported.

### 6.3 Head numbers: mesh vs record

Same watch, two independent routes. Where they differ it is a **definition** difference
(automatic boundary criterion vs. a manual 3-point or typed value), which is a ruling, not a bug.

| quantity | mesh (this measurement) | record | note |
|---|---|---|---|
| crystal flat radius | **14.68** (r99, ±0.3); boundary-ring fit 14.01 | typed **14.35** (`Arc26`, never fitted) | mesh brackets the typed value, < 5 % |
| cyclops centroid | **(9.16, 0.06)**, x 5.55…12.76, y ±2.90, +1.18 proud | lens centred ≈ x 9.2, 6.1 mm arc spacing | agrees |
| caseback plane z | **−12.164** | **−12.165** (`Arc(35)` p137–p145) | Δ 0.001 — the feature is unambiguously the same |
| caseback flat boundary R | **11.24** (r99) / **11.20** (> 0.1 mm departure) | **10.586** (3-point circumcircle) | **0.65 (6 %)** — see §3.4 |
| bezel outer R | **15.71 / 17.00 / 18.51** at z −0.5 / −0.8 / −1.1 (Kåsa, 0.1 reject) | typed Ø35.4 (R 17.7); STEP Ø38.20 (R 19.1) at z −1.19…−0.43 | a real slope; the typed R 17.7 lands on it, R 19.1 is below the sampled range |
| lug-to-lug | **49.82** (lug-tip envelope, y −25.13…+24.69) | **47.4** (FLANK_9 sheet y-span) | different definitions — quote both |
| crown protrusion | **+24.04** absolute, **6.97** beyond the mean bezel R | — | — |

### 6.4 Two measurement bugs worth carrying forward (both now in SKILL.md Stage 0)

The first pass of this measurement produced crystal r99 = 10.59 and caseback z = −10.12 /
R 19.02. Both were **wrong**, both looked plausible, and both were caught by a visual diagnostic
rather than by a residual — the fits converged happily on the wrong feature:

1. **A circle fit on a filled disc finds an inner ring, not the edge.** A Kåsa fit over *all*
   near-plane points has no reason to prefer the boundary; it settled on an arbitrary interior
   sub-ring. Fix: take the **percentile radius of all near-plane points** (r99 here) and reserve
   the circle fit for a **thin annulus at that radius** — the true boundary ring. Confirmed by a
   radius-vs-z diagnostic plot and by the record's own typed r 14.35.
2. **The lowest down-facing cluster is not necessarily the caseback.** The alignment pass's
   caseback candidate was a different down-facing case surface entirely. Fix: locate the plane
   with an **area-weighted z-histogram of down-facing face centroids** (normal_z < −0.9, r < 20)
   and take its dominant peak (−12.179 → refit −12.164), which then matched the record to
   0.001 mm.

Both are logged in `T_canonical.json`. The lesson generalises past this watch: a fit that
converges is not a fit that found the intended feature — grade it against an independent
estimator (here: the record, and a radius-vs-z plot), never against its own residual.

---

## 7. R3 parameter table

Every row is PROVISIONAL (record in progress). "typed" = operator-entered; "fitted" = NX fit
output; "measured" = computed by this analysis from the STEP/expressions.

| parameter | value | method | source |
|---|---|---|---|
| Fit Surface rejection threshold | **0.03 mm** | dialog | S1 `dc_viewport_20260830_203047.png` (1 instance, target region uncertain) |
| Datum Plane offset | 0 mm | dialog | S1 `dc_viewport_20260830_203017.png` |
| Move Object CSYS→CSYS | **Associative = checked** | dialog | S1 `dc_viewport_20260830_203718.png` |
| crystal disc Ø | **28.7** | typed | `Sketch(19)` p4 (= 2 × Arc26 r 14.35) |
| cyclops lens height / end-cap radii / corner fillets | 6.1 / 3.5, 3.5 / 0.3 mm | typed | `Sketch(19)` p0, p1, p3, p5–p8 |
| cut-out clearance | **+0.15 mm outward** | typed | S1 `dc_viewport_20260830_204349.png` Offset Curve |
| zero-depth extrude limits | 0 / 0 mm | typed | `Extrude(20)` p9, p10 |
| crystal-sheet face area | 607.31 mm², 9 edges | measured | `session_1_last_snapshot.json` FACE_66328 |
| sheet lift (×2) | 0.15 mm | typed | `Move Object(7)` p23, `(9)` p33 |
| mirror datum offset | 0.0 mm | typed | `Mirror Geometry(8)` p32, `(19)` p65 |
| caseback 3-point arc | P1 (−10.4388, 1.98907, −12.1565), P2 (6.8691, −8.08819, −12.1447), P3 (6.82964, 7.95533, −12.1951) | fitted (3-point) | `Arc(35)` p137–p145 |
| → caseback circumcircle | centre (−0.058, −0.083), **R 10.586 (Ø21.17)**, z −12.165 | measured from p137–p145 | this analysis |
| caseback clearance | **+0.15 mm outward → Ø21.47** | typed | `Offset Curve(36)` p148 (and `(39)` p149 for the check-solid path) |
| bezel/crystal annulus | **Ø30.0 / Ø35.4** | typed | `SKETCH_002:Sketch(46)` p169, p170 |
| Revolve sweep | 0°→360° (both) | typed | p163/p164, p173/p174 |
| cutter extrude span | −1.7 … +2.0 mm | typed | `Extrude(98)` p182, p183 |
| case Ø / bezel Ø / caseback rim Ø | 38.2 / 38.20 / 27.30 mm | measured | RV04 STEP `q14_frame.py` |
| caseback flat plane z | −12.16 mm | measured | same |
| TCM face | 41.851 mm², 12×11 poles, deg 3/3 | measured | RV04 STEP `q10`, `q11` |
| TCM boundary lengths | 15.701 / 9.924 / 8.541 / 2.952 mm | measured | `q14_frame.py` |
| TCM K (analytic 21×21) | K_abs_mean 1.31e-2, **K_abs_max 1.10e-1** | measured | `BRepLProp_SLProps` |
| TCM K (discrete) | 41×7: 9.007e-3 / 3.124e-2 · 41×41: 1.194e-2 / 8.710e-2 | measured | angle defect, `ruled_sheet` formula |
| ruled-vs-network deviation on that facet | area +15.86 %, surface 1.985 mm, cross curves 2.293 / 1.346 mm, sagitta 0.590 / 0.046 mm | measured | `q12_ruled_vs_tcm.py` |
| recipe-N trigger | closing-curve deviation **> 0.20 mm** or sagitta **> 0.20 mm** | derived, **n = 1** | §4.6, ruling R6 |
| flatten dialog | Type = Flattening; Rip Edge / Outer Boundary / Constraints unused; Distortion Map None; Preview on | dialog | S3, 7 screenshots |
| flatten orientation picks | 34 U · 15 Origin · 8 V · 9 Reverse · 3 CSYS | click counts | `session_3_dialogs.tsv` |
| sheets flattened | **8–12 (inferred)**; 3 named Applies + 71 unnamed icon clicks | inferred | S3 §3 |
| layout | 100 % dynamic mouse-drag; 1 `text_input` in 1,440 events (unrelated) | measured | S3 §4 |

---

## 8. Open rulings

Full text, options, provisional defaults and evidence pointers:
**`tasks/NXLEARN-126713/run/RULINGS.md`** — R1 lug-outer-flank piece vs flank-sheet end ·
R2 network-piece developability gate · R3 K-gate sampling · R4 caseback reference boundary and
sign · R5 LSCM as the recipe-N development · R6 the 0.20 mm network trigger · R7 revolved check
solids as recommended practice · R8 Jubilee piece scheme · R9 cyclops cut-out shape ·
R10 crystal Ø28.7 typed vs bezel-bore-minus-clearance · R11 fit rejection 0.03 vs 0.07.

Until each is answered the skill keeps its existing default and marks the R3 value PROVISIONAL.
