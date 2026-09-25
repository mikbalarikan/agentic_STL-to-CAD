# INTAKE CARD — OOM-P03 Mop Pad Bracket (rotating mop-pad carrier plate)

<!-- Produced by re-mesh-analyst. Presented verbatim at the external gate. -->
Intake date: 2026-07-29 · Analyst: re-mesh-analyst · Tool: trimesh 4.12.2 / build123d

## 1. What it is (from photos + mesh)
A **rotating mop-pad carrier plate** for the OOMWOO robot mop — the round spinning disc
that the disposable circular mop cloth attaches to and that is driven in rotation by the
mop-lift/spin motor. Styled to look like an alloy wheel/airless tyre (molded
**"FlexiArm Design"** text, red index ring, castellated "tread" rim), but functionally a
thin dished plate, ~Ø127 mm, ~21.5 mm tall, molded white ABS/PP.

Two functional faces (both visible in `images.jpg`):
- **DRIVE face (top):** spoked structure with two rings of through-openings; a central
  **raised male hexagon coupling boss** (~13.95 mm across flats) that engages the motor
  drive output and transmits torque. Cosmetic molded graphics (red ring, "FlexiArm Design",
  QR code, "A2" cavity mark) live on this face.
- **PAD face (bottom):** large flat/lightly-dished circular field with a fine grippy
  texture (hook-and-loop / velcro grip zone) in concentric bands + radial slots, with a
  central raised round boss (~Ø33.5 mm) that carries the hex coupling on its far side.
  This is where the round microfiber mop cloth is retained.

Motion: **rotates** about the central hex axis; static relative to the pad it carries.
Mounts to chassis only through the central hex drive coupling (no screw flange seen).

## 2. Scan health
- **Units:** mm — plausible (Ø≈127 mm, H≈21.5 mm matches a robot-mop pad plate; confirmed
  later by ENV calipers). No scale flag from units.
- **Working mesh coords:** RAW scanner coordinates — part sits at bounds Z≈−305…−195 mm,
  disc tilted (disc normal ≈ [0.334, 0.846, −0.415]). Needs datum transform (§5).
- **Raw → working tri count:** 4,187,542 → **250,000** tris (quadric-decimated working copy
  `2_mesh_cleaned\OOM-P03_work_250k.stl`; source `2_mesh_cleaned\OOM-P03.stl` is 209 MB and
  was exported UNWELDED — verts = 3×faces, every edge a boundary; merges to 2,101,931 verts
  as a single body).
- **Watertight:** **NO.** After vertex merge: single connected component, winding-consistent,
  euler −129, **16,578 open boundary edges** = localized occlusion holes, NOT a torn soup.
- **Hole/occlusion map (where the ~16.5k boundary edges concentrate):** deep between-"tread"
  rim slots; undercut beneath the central hex boss; inner corners of the kidney openings;
  and the fine velcro texture on the PAD face (scanner cannot resolve the micro-texture →
  noisy shell + pinholes there).
- **Artifact vs real:** red ring line, "FlexiArm Design", QR, "A2" = printed/engraved
  cosmetics, NOT geometry to model. Dark patches inside the kidney openings in the photos =
  table/shadow showing through, not black inserts. Velcro micro-texture = real but modeled
  as a nominal flat/grooved face, not tuft-by-tuft.
- **Envelope sanity:** raw AABB extents [121.2, 59.1, 109.6] mm. With the disc tilted, the
  121.2 mm X-extent back-solves to an outer Ø ≈ 127–129 mm, matching the 127.5 mm photo
  caliper. (A naive PCA radial p99.9 read 139 mm — inflated by axis tilt/noise, disregarded.)

## 3. Functional surfaces & interfaces (each becomes a gate zone)
| Zone | Surface | Why functional | Caliper-coverable? |
|---|---|---|---|
| Z1 | Central male hex coupling boss (AF ≈13.95) | Torque drive from motor — critical fit | YES (AF + across-corners + height) |
| Z2 | Hex boss root / tip face + any central bore | Axial seat / possible retention screw | YES (depth gauge for bore) |
| Z3 | PAD face plane (flat mop-attach face) | Mop-cloth seating plane; sets pad flatness | YES (overall height ref) |
| Z4 | Pad-side central boss Ø≈33.5 | Locates cloth centre / houses coupling | YES (OD) |
| Z5 | Outer rim OD (across solid rim) ≈127.5 | Sweep envelope; pad-cloth diameter match | YES (2 orthogonal ODs) |
| Z6 | Rim / plate wall thickness ≈3.2–3.3 | Mold wall; stiffness | YES (jaw on rim edge) |
| Z7 | Concentric structural rings (hub Ø≈68.6, spoke-disc Ø≈89.3) | Stiffening ring diameters | YES (OD each) |

## 4. INTERIOR structure (mandatory — v1 lesson: ribs were missed)
Enumerated explicitly (through openings + `images.jpg` both faces):
- **Radial spokes/webs** on the DRIVE face connecting central hub → outer rim, separating
  the openings. Count ≈ **6-fold** primary polar symmetry (≈6 large outer oval/kidney
  cutouts + ≈6 smaller inner openings). Confirm exact count from the scan section.
- **Concentric ring walls** (3 nested cylinders): central hub disc (Ø≈68.6), mid spoke-disc
  ring (Ø≈89.3), outer rim (Ø≈127.5) — these are the load path and stiffeners.
- **Castellated "tread" rim:** a fine **polar pattern of radial slots** around the outer rim
  (~30–40 slots). Real geometry (decorative but molded-through), not scan noise.
- **Central hex boss** is a raised MALE hexagonal coupling on the drive side; on the pad
  side it corresponds to the Ø≈33.5 boss. **Check for a central bore / screw hole** at the
  boss tip (a small circle is visible at the pad-side centre in `IMG_20260729_140419.jpg`) —
  could be a mold gate OR a retention-screw bore. FLAG to confirm with depth gauge.
- **Molding ribs** likely on the underside of the spokes (draft/stiffening) — inferred, not
  directly visible; expect thin (~1–2 mm) ribs. Verify in section.

## 5. Datum plan
- **Primary axis (Z):** the central hex / rotation axis → align disc normal
  [0.334, 0.846, −0.415] to **+Z**, with +Z pointing toward the DRIVE (hex-boss) side.
- **Primary flat (XY, Z=0):** the PAD-attachment face sits on Z=0.
- **Origin:** on the rotation axis at the pad face; enforce concentricity of all rings + hex
  to this axis.
- Composite raw-scan→datum transform to be written to `2_mesh_cleaned\alignment.json` as
  `matrix_4x4` by the modeler (per OOM-E01 lesson).

## 6. Rebuild strategy per region
- **Base body:** REVOLVE the concentric cross-section profile (pad face → hub → mid ring →
  rim, incl. the ~3.2 mm walls and dish) about Z.
- **Drive-face openings:** POLAR-PATTERN extrude-cut of the outer kidney cutouts and inner
  openings (≈6-fold).
- **Tread rim:** POLAR-PATTERN extrude-cut of the ~30–40 rim slots.
- **Central hex:** EXTRUDE hexagon (AF from caliper) for the boss; add central bore if
  confirmed; revolve the pad-side boss.
- **Pad grip field:** nominal flat/concentric-groove revolve; micro-texture NOT modeled
  (cosmetic — note in param table).
- **Symmetry:** rotationally symmetric plate; 6-fold polar features + finer tread pattern;
  hex boss = 6-fold. No mirror plane. Fillets last, from sections.

## 7. Risk flags
- **Not watertight (16.5k boundary edges)** — occlusion holes under the hex boss, in tread
  slots, kidney corners, and across the velcro texture. Interior/occluded buckets will be
  reported, not gated (per §4 tiers).
- **OD reconciliation:** scan radial metric read high (139 mm) vs 127.5 mm photo caliper —
  attributed to disc tilt; ENV must give TWO orthogonal ODs to confirm roundness/scale and
  rule out a soft/tilt/chord error (§2 non-uniform-scale check). Also clarify OD *across the
  solid rim* vs *over the tread castellations*.
- **Hex boss:** central bore present or not (retention screw vs mold gate) — unresolved,
  needs depth-gauge check.
- **Velcro texture face:** cannot scan-resolve; will be a noise floor on the PAD face — model
  nominal, exclude texture from gate.
- **Exact polar counts** (spokes / kidney openings / tread slots) to be locked from the scan
  section before patterning.

## 8. MEASUREMENT REQUEST (→ pre-filled into 5_reference\MEASUREMENTS.md)
Priority order: 3 envelope dims first (scale/roundness check), then functional dims from §3,
then walls. Photo references cite `Context images\IMG_20260729_*.jpg`. See MEASUREMENTS.md for
the empty caliper sheet.
