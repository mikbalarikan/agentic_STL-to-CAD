# Datum cookbook: plane-primary vs axis-primary

Read this before you write the `align.py` spec. Each example shows the *method* the golden
project used and the *lesson* it teaches; it does not restate the golden numbers. If you need
the actual figures for comparison, they live in the golden report and in `analysis/golden/*.md`
— reading those on a blind run defeats the point of the run, so treat them as answer-key files,
not skill references. Paths are abbreviated: `DRM/` = `golden-examples/dreame_brush-caps/`,
`B02/` = `golden-examples/OOM-B02_side-brush-3-arm/`, `P03/` = `golden-examples/OOM-P03_mop-pad-bracket/`,
`OD/` = `golden-examples/OD-H12_delonghi-dedica-pump/`.

## 1. The DOF ladder (RE_SPEC.md:109-124)

| Step | Kills | Plane-primary part | Axis-primary part |
|---|---|---|---|
| Primary | 3 DOF (plane) or 4 DOF (axis) | functional flat → XY, z = 0 | functional axis → +Z, through (0,0) |
| Secondary | 1 rotation (plus 2 translations if it is an axis) | bore/cylinder axis pins X/Y | a plane or feature clocks about Z |
| Clock | 1 rotation | named feature → +X, explicit rule | (secondary does this) |
| Origin | what is left | named intersection, e.g. "bore axis ∩ top face" | named plane or feature along Z |

Rules (all SYNTHESIS §1B):
- Primary = the functional or mating surface, or the axis of an axis-primary part. **Never the
  largest facet by default.** On a raw decimated scan, arbitrary connectivity can leave the
  largest trimesh facets as tiny fragments unrelated to any real feature
  (`DRM/report/intake.json#top_facets`; SYNTHESIS §3) — always pick the primary by function, and
  verify by area, not the reverse.
- Axis from section circle fits (Kåsa or IRLS) or from normals with the **correct** eigen form:
  axis = eigenvector of the smallest eigenvalue of Σ n nᵀ. The baseline form
  "smallest eigenvector of Σ(I − n nᵀ)" is wrong (`analysis/baseline/stl2step-skills.md` §5.1).
  bbox centres are forbidden (RE_SPEC.md:120-122); `align.py` exits 3 instead of falling back.
- Every datum gets a functional WHY (RE_SPEC.md:124) and every fit its rms/max.

## 2. Plane-primary worked examples

### 2.1 DRM screw cap (plane-primary, functional flat)

Method (`DRM/report/source/align.py`): primary from an area-weighted, RANSAC+SVD-refined plane
fit on a functional flat face, restricted to faces near an approximate normal given up front;
XY origin from Kåsa circle fits on a drive-hole feature sampled over many Z stations, filtered
by a radius hint; clock from the phase of a polygonal-flat feature aligned to +X; tilt was not
independently measured in the golden run (hard-coded to 0) — see `analysis/golden/DRM.md` §2
and `DRM/report/screw_alignment.json` for the exact fit values, radius, clock angle and any
follow-up tilt estimate.

Spec shape used for the replay:

```json
{"mesh": "intake/work.stl", "raw_scan": "input/scan.stl", "intake_json": "intake/intake.json",
 "out_dir": "intake", "seed": 0,
 "noise": {"from": "intake/noise_primary.json"},
 "primary": {"type": "plane", "approx_normal": [0, 0, 1], "material_side": "-z",
             "desc": "top disc face", "why": "flat top face; the delivered datum frame (DRM README)"},
 "origin": {"xy": {"method": "kasa", "r_hint": "<see DRM/report; not restated here>", "r_tol": 0.1, "rms_max": 0.2,
                   "z_range": "<golden report>", "stations": 25, "desc": "double-D drive hole F06"},
            "definition": "drive-hole axis ∩ top face"},
 "clock": {"rule": "polygon_flat", "n": 5, "z": "<golden report>",
           "desc": "pentagon flat centre -> +X", "why": "drive flats are parallel to a pentagon flat"}}
```

Lessons:
- A non-circular origin feature (here, a double-D flat-sided hole) still has a well-defined
  centre by symmetry, but its Kåsa fit residual is shape error, not noise, and is typically much
  larger than a clean-circle fit on the same part. Don't gate that residual against a clean-circle
  noise floor; use a genuinely round feature for the noise reference, or use the flat-sided
  feature only for the centre and say so.
- When a part offers two independent short-baseline tilt estimates (e.g. two separate coaxial
  features), they can disagree by more than their combined standard error. In that case CHK-TILT
  should report `resolvable: false` rather than a single pooled value — see
  `analysis/golden/DRM.md` §2 for the worked disagreement and the part-height context that makes
  it material.
- Tilt estimated from a short axial span is noisy. Prefer the longest clean coaxial span, and
  always report per-feature, not pooled-only.

### 2.2 B02 side brush (plane primary with material in +Z)

Method (`B02/6_RE_work/INTAKE_CARD.md` §5, `B02/2_mesh_cleaned/alignment.json`,
`B02/6_RE_work/qa/q03_datum_full.py`): primary from the cup rim annulus (material above the
plane); secondary from the common axis of the cup bore, skirt and hex, found by an IRLS
(Cauchy) circle fit on the bore wall faces, inner wall selected by the sign of n·r̂; clock from
the 3-fold Fourier phase of angular mass, arm 1 aligned to +X; no single global scale factor
(photo-caliper ratios were judged non-uniform, CHK-SCALE flag). The independent audit against
the frozen frame is reported in `VERDICT.md` — see `analysis/golden/OOM-B02.md` for the actual
angular/point-disagreement figures rather than restating them here.

Spec shape used for the replay (`B02/2_mesh_cleaned/OOM-B02.stl`):

```json
{"primary": {"type": "plane", "approx_normal": "<measure from the planes survey>", "material_side": "+z",
             "desc": "cup rim annular face", "why": "axial seat against the motor boss (F02)"},
 "origin": {"xy": {"method": "wall_faces", "wall": "inner", "perp_max": 0.30, "r_min": 9.0,
                   "r_max": 14.0, "r_hint": "<measure from D-08>", "r_tol": 0.4, "rms_max": 0.3,
                   "z_range": [0.3, 2.2], "stations": 5, "desc": "cup bore wall faces"},
            "definition": "cup bore axis ∩ rim plane"},
 "clock": {"rule": "fourier_mass", "n": 3, "r_range": [20, 34], "pick_nearest_deg": 0.0,
           "desc": "arm 1 centreline -> +X", "why": "arms carry the sweep; SAF-1 labels arm 1"}}
```

Lessons:
- Wall-face IRLS survives partial angular coverage where section loops never close
  (`allow_open_arcs` is the fallback for sections). Expect several open boundary loops on a
  part like this (hex wall, cup wall, a labelled hole) — count them at intake, don't assume a
  closed ring.
- The arm/feature label used for clocking is a convention, not a measurement: `fourier_mass`
  returns all n candidates, so the skill must state the label rule explicitly (the golden
  project compared candidates modulo the feature's own symmetry period).
- Normal direction should be settled by a ray vote on the actual mesh, not assumed from a
  volume-sign heuristic (see §4 below) — a naive flip can be wrong even when it looks confident.
- Two independent tilt estimates from different features on the same part can disagree enough
  that neither should be trusted alone, and partial angular coverage biases a feature's fitted
  centre; see `analysis/golden/OOM-B02.md` for the worked numbers.

### 2.3 P03 mop bracket (what not to do, and partial coverage)

Method used in the golden run, and what to avoid (`P03/2_mesh_cleaned/alignment.json`,
`analysis/golden/OOM-P03.md` §3):
- The primary plane was fit by PCA on a textured, scanner-unresolvable field (a velcro surface)
  rather than a clean functional face, and no rms/max was recorded for it.
- The clock rotation was never resolved and a feature was left at an arbitrary phase — flag
  this rather than silently defaulting.
- The datum matrix was refined post hoc using the part's own rebuilt CAD (an ICP fit "to match
  the verifier's frame") — this is circular (CHK-CIRCULAR) and must not happen after the build.
- Scan coverage (the mesh only spans part of the full revolution) was disclosed only in the
  report, not recorded at intake.
- A naive radial percentile computed in the raw (untilted) frame overstated the OD; measuring in
  the levelled datum frame corrected it. See `analysis/golden/OOM-P03.md` §3 for the actual
  figures.

What the skill does instead: RANSAC+SVD plane with rms/max on a clean functional face (not a
textured field), a stated clock rule, `intake.py coverage` at intake (angular coverage per radial
band), never measure radii before the datum, and never touch `alignment.json` after the build.

## 3. Axis-primary worked example: OD-H12 pump

Method (`OD/README.md`, `OD/report/alignment_T1.json`, `analysis/golden/OD-H12.md` §3): primary
from the shared revolution axis of the body/outlet-tube cylinders; secondary from a side-plate
normal; origin lives on the axis with no named z-zero feature. The golden record did not keep
the fit method or residuals for the primary axis, and its stated noise floor came from a self-fit
on an unnamed "clean cylinder" — treat an unnamed noise source as a gap to close, not a value to
reuse. See `analysis/golden/OD-H12.md` §3 for whatever figures were recorded.

Skill spec shape for this class (not replayed: the OD scan is large and the record has no
datum numbers to compare against):

```json
{"primary": {"type": "axis", "approx_axis": [ax, ay, az], "perp_max": 0.30,
             "crop_point": [px, py, pz], "crop_radius": R,
             "desc": "plastic body + outlet tube cylinders", "why": "pump axis; all ports are coaxial"},
 "origin": {"xy": {"method": "irls", "r_hint": r, "r_tol": t, "rms_max": m, "z_range": [z0, z1],
                   "desc": "outlet tube OD sections (tilt cross-check)"},
            "z": {"type": "plane", "approx_normal_datum": [0, 0, 1], "offset_range": [a, b]},
            "definition": "pump axis ∩ outlet flange face"},
 "clock": {"rule": "plane_normal", "approx_normal_raw": [nx, ny, nz],
           "desc": "sheet-frame side plate normal -> +X", "why": "frame plates carry the mounting screws"}}
```

For an axis primary, `crop_point`/`crop_radius` are required (crop to ONE clean cylinder; a
mixed crop makes the residual below meaningless). `primary.fit_rms_mm` is the RADIAL residual of
the cropped cylinder faces about the fitted axis (each face centre's distance from the axis,
minus the median radius), gated against `noise_secondary` (a circle noise floor) — never the
flat `noise` floor, which is a different metric (review B1). `normal_line_dist` (the distance of
the face-normal lines from the fitted axis, roughly radius × normal-angle noise) is kept only as
a diagnostic, not gated. `eig_ratio` (smallest/second eigenvalue) near 0 means a well-defined
axis. The `origin.xy` circle stations then give CHK-TILT as the angle between the normals-axis
and the line through the section centres (two independent estimators).

## 3.1 Prismatic plane-primary part with no round feature (cliff sensor, 2026-09-30)

A moulded box (sensor housing) has no bore or boss, so `origin.xy` circle fits have nothing to
fit. Use `origin.xy_planes`: primary = the broad functional flat, clock = a long side wall
(`plane_normal`, `target_deg: 90` to put its normal on +Y), Y origin = mid-plane of the two side
walls, X origin = a named end wall. Lesson from that run: the broad top face was two moulded
pieces with a ~0.1 mm crown, so the whole-face rms (0.038) exceeded the wall noise (0.0275) and
STOPped; cropping each datum plane to its clean flat (`crop_point_raw`/`crop_radius`) gave rms
0.012–0.023 and OK. A crop is a region choice, not a threshold: name the region and why in the
intake card. Worked spec: `evals/real-runs/cliff_bumper_sensor/datum_spec.json`.

## 4. Normal orientation (correction to SYNTHESIS A5)

SYNTHESIS A5 flips normals when the signed volume is negative. On an open (non-watertight) scan
the signed volume depends on the coordinate origin, so its sign is not evidence: a part can have
outward-facing normals on both a top feature and a rim feature while the signed volume still
reads negative (and can even change sign after a rigid transform). `intake.py` therefore uses
the volume sign only for watertight meshes and a seeded ray vote otherwise. Flipping on volume
sign alone can point rim-facing faces into the material and make `level_plane` pick the wrong
candidate face. See `analysis/golden/OOM-B02.md` (normals section) for the case that surfaced
this. (This was found while testing this skill; it is listed as an open question for the owner.)

## 5. Spec reference (`align.py`)

| Key | Meaning |
|---|---|
| `mesh`, `raw_scan`, `intake_json`, `out_dir`, `seed` | paths relative to the spec file; raw scan hashed only |
| `scale_factor` | 1.0 unless CHK-SCALE decided ONE uniform scale |
| `chk_scale` | `{"ran", "result", "note"}` copied into `checks` |
| `noise` | `{"value", "method"}` or `{"from": "<datum_fit noise JSON>"}` — **required** |
| `noise_secondary` | same, measured on a clean circle; enables the STOP check on circle residuals |
| `primary` | `plane`: `approx_normal`, `material_side` (`-z`: material behind the outward normal), `cone_deg` 10, `tol` 0.05, `bin_mm` 0.1, `halfwidth_mm` 0.15, `offset_range` · `axis`: `approx_axis`, `perp_max` 0.30, `crop_point`/`crop_radius` (required, review B1), `iters` 3 |
| `origin.xy` | one feature or a list: `method` `kasa`/`irls` (sections, `allow_open_arcs`) or `wall_faces` (`wall` inner/outer, `r_min`, `r_max`, `perp_max`); `r_hint`, `r_tol`, `rms_max`, `z_range`, `stations` |
| `origin.xy_planes` | plane primary, prismatic part with no round feature (added 2026-09-30, cliff-sensor run): `{"x": <plane> or [<plane>, <plane>], "y": ...}`; one plane = that plane is the origin, two opposed planes = their mid-plane. `<plane>` = `approx_normal_datum`, optional `offset_range`, `cone_deg`, `tol`, `desc`, crop keys. Needs `clock.rule: plane_normal`; the clock runs first. Each plane rms is STOP-checked against `noise`. CHK-TILT = the clock wall's out-of-perpendicularity to the primary (a draft reads the same; say so). |
| `crop_point_raw`, `crop_radius` | optional on `primary` (plane), on a `plane_normal` clock and on each `xy_planes` plane: fit only faces whose centre, mapped back to the RAW scan frame, lies in this sphere. Use it to restrict a datum plane to its clean flat (a crowned or two-piece face otherwise reads form error as fit residual and trips STOP). Record why in the card. |
| `clock.target_deg` | `plane_normal` only: where the wall normal should point, 0 = +X (default), 90 = +Y |
| `origin.z` | axis primary only: `plane` (`approx_normal_datum`, `offset_range`) or `extreme` (`which` min/max) |
| `origin.definition` | the named intersection |
| `clock` | `polygon_flat`/`polygon_corner` (`n`, `z`), `min_radius` (`z`), `fourier_mass` (`n`, `r_range`, `z_range`, `pick_nearest_deg`, `label_rule`), `plane_normal` (`approx_normal_raw`), `none` (needs `why`) |
| `landmarks` | `[{"name", "stat": "zmax|zmin|rmax|xmin…", "r_range", "z_range", "expected", "tol", "tol_source"}]` |
| `tilt_reference_deg` | default 0.3 (RE_SPEC.md:241, report-only) |

The numeric defaults above (`cone_deg`, `tol`, `bin_mm`, `halfwidth_mm`, `perp_max`, `iters`,
`tilt_reference_deg`) are algorithm parameters cited from `RE_SPEC.md`/the golden code, not a
specific part's measured answers — they apply regardless of which part you are running.
