# Datum cookbook: plane-primary vs axis-primary, with golden numbers

Read this before you write the `align.py` spec. Each example shows what the golden project
did, the numbers it recorded, and what the new skill changes. Paths are abbreviated:
`DRM/` = `golden-examples/dreame_brush-caps/`, `B02/` = `golden-examples/OOM-B02_side-brush-3-arm/`,
`P03/` = `golden-examples/OOM-P03_mop-pad-bracket/`, `OD/` = `golden-examples/OD-H12_delonghi-dedica-pump/`.

## 1. The DOF ladder (RE_SPEC.md:109-124)

| Step | Kills | Plane-primary part | Axis-primary part |
|---|---|---|---|
| Primary | 3 DOF (plane) or 4 DOF (axis) | functional flat → XY, z = 0 | functional axis → +Z, through (0,0) |
| Secondary | 1 rotation (plus 2 translations if it is an axis) | bore/cylinder axis pins X/Y | a plane or feature clocks about Z |
| Clock | 1 rotation | named feature → +X, explicit rule | (secondary does this) |
| Origin | what is left | named intersection, e.g. "bore axis ∩ top face" | named plane or feature along Z |

Rules (all SYNTHESIS §1B):
- Primary = the functional or mating surface, or the axis of an axis-primary part. **Never the
  largest facet by default.** On the DRM raw scan the largest trimesh facets are ~0.27 mm²
  fragments (`DRM/report/intake.json#top_facets`; SYNTHESIS §3).
- Axis from section circle fits (Kåsa or IRLS) or from normals with the **correct** eigen form:
  axis = eigenvector of the smallest eigenvalue of Σ n nᵀ. The baseline form
  "smallest eigenvector of Σ(I − n nᵀ)" is wrong (`analysis/baseline/stl2step-skills.md` §5.1).
  bbox centres are forbidden (RE_SPEC.md:120-122); `align.py` exits 3 instead of falling back.
- Every datum gets a functional WHY (RE_SPEC.md:124) and every fit its rms/max.

## 2. Plane-primary worked examples

### 2.1 DRM screw cap (the only unmasked clean pass, SYNTHESIS §0.1)

Golden (`DRM/report/source/align.py`, `DRM/report/screw_alignment.json`):
- Primary: top disc face. Faces within 10° of an approximate normal given on the CLI,
  area-weighted offset histogram (0.1 mm bins), peak bin ±0.15 mm, RANSAC tol 0.05 / 300 iters /
  seed 0, widen to 2·tol, SVD refine. 19,219 faces, 33.09 mm², **rms 0.0072, max 0.055 mm**.
- Origin X/Y: Kåsa circles on 25 Z stations filtered by radius hint; **10 stations,
  r_mean 1.873** (this is the double-D drive hole: arcs r 1.949, flats ±1.64, `DRM/README.md` F06).
- Clock: `pent@z` 5-fold phase of r-peaks, flat centre → +X, **clock −34.23°**.
- Tilt: **hard-coded 0.0** (`align.py:79`) → CHK-TILT.

Replay with this skill on the decimated inspection copy
(`DRM/dreame_brush_screw_cap_scan_decimated.stl`; labelled inspection only, never a regrade):

```json
{"mesh": "intake/work.stl", "raw_scan": "input/scan.stl", "intake_json": "intake/intake.json",
 "out_dir": "intake", "seed": 0,
 "noise": {"from": "intake/noise_primary.json"},
 "primary": {"type": "plane", "approx_normal": [0, 0, 1], "material_side": "-z",
             "desc": "top disc face", "why": "flat top face; the delivered datum frame (DRM README)"},
 "origin": {"xy": {"method": "kasa", "r_hint": 1.87, "r_tol": 0.1, "rms_max": 0.2,
                   "z_range": [-2.5, -0.1], "stations": 25, "desc": "double-D drive hole F06"},
            "definition": "drive-hole axis ∩ top face"},
 "clock": {"rule": "polygon_flat", "n": 5, "z": -1.5,
           "desc": "pentagon flat centre -> +X", "why": "drive flats are parallel to a pentagon flat"}}
```

| Quantity | Golden (full-res) | This skill (decimated work copy, 300k faces) |
|---|---|---|
| Primary rms / max | 0.0072 / 0.055 | 0.0069 / 0.031 (17,997 faces) |
| Origin stations, r_mean | 10, 1.873 | 25, 1.886 (z window differs; golden window not recorded) |
| Clock | −34.23° | −34.25° (z = −1.5); −34.75° at z = −1.0 (chamfer/fillet zone; pick a z on straight flats) |
| Matrix vs golden | — | rotation 0.020°, point disagreement max 0.014 mm (60k seeded pts) |
| Tilt | 0 (not measured) | double-D alone **0.72° ± 0.11°** (dir 117°, 25 stations over 2.4 mm); counterbore F08 alone **2.82° ± 0.56°** (dir −111°, span 0.8 mm) — the vectors differ by ~1.1°, over 10× the combined stderr, so **not resolvable** from these two features (review M2). Do not pool them into one number. |

Lessons:
- The DRM origin feature is not a circle: the double-D Kåsa residual is ~0.11 mm median. The
  centre is right by symmetry, but the residual is shape error, not noise. With a clean-circle
  noise reference (counterbore F08 IRLS rms 0.031 mm) `align.py` STOPs on it. Use a true circle
  (counterbore) for the residual check, or use the double-D only for the centre and say so.
- The two independent tilt estimates (double-D 0.72°, counterbore 2.82°) disagree by more than
  their combined stderr, so CHK-TILT reports `resolvable: false`, not a single measured value.
  A 0.7°–2.8° tilt over the 5.12 mm part height is 0.06–0.25 mm lateral: small, but it was
  assumed 0 in the golden. Record the disagreement; do not re-level the part on it unless the
  bore is the functional primary, and do not silently pool short and long spans into one number.
- Tilt from a short span is noisy: the counterbore alone (0.8 mm span) gave 2.82° ± 0.56°.
  Prefer the longest clean coaxial span, and always report per-feature, not pooled-only.

### 2.2 B02 side brush (plane primary with material in +Z)

Golden (`B02/6_RE_work/INTAKE_CARD.md` §5, `B02/2_mesh_cleaned/alignment.json`, `B02/6_RE_work/qa/q03_datum_full.py`):
- Primary (A): cup rim annulus → XY, z = 0, material +Z. Plane rms **0.052** over 30,342 raw faces;
  QA re-fit rms 0.0080 (`_datum_indep.json`).
- Secondary (B): common axis of cup bore + skirt + hex → +Z, "iterated rim-plane fit + robust circle fit".
  QA used an IRLS Cauchy circle fit on the cup-bore wall faces, inner wall separated by the sign of
  n·r̂: **bore R 10.2419**.
- Clock (C): arm 1 → +X. QA used the 3-fold Fourier phase of the angular mass in r 20–34.
- Scale: none; four photo-caliper ratios 0.984–0.996 judged non-uniform (CHK-SCALE flag).
- Independent audit vs the frozen frame: **0.429° / point disagreement max 0.451 mm** (VERDICT.md:153-163).

Replay with this skill on the full-resolution scan `B02/2_mesh_cleaned/OOM-B02.stl` (work copy 199,999 faces):

```json
{"primary": {"type": "plane", "approx_normal": [0.3207, -0.3428, -0.8830], "material_side": "+z",
             "desc": "cup rim annular face", "why": "axial seat against the motor boss (F02)"},
 "origin": {"xy": {"method": "wall_faces", "wall": "inner", "perp_max": 0.30, "r_min": 9.0,
                   "r_max": 14.0, "r_hint": 10.35, "r_tol": 0.4, "rms_max": 0.3,
                   "z_range": [0.3, 2.2], "stations": 5, "desc": "cup bore wall faces"},
            "definition": "cup bore axis ∩ rim plane"},
 "clock": {"rule": "fourier_mass", "n": 3, "r_range": [20, 34], "pick_nearest_deg": 0.0,
           "desc": "arm 1 centreline -> +X", "why": "arms carry the sweep; SAF-1 labels arm 1"}}
```

| Quantity | Golden | This skill |
|---|---|---|
| Rim plane rms | 0.052 (intake), 0.0080 (QA) | 0.0186 (6,091 work faces) |
| Bore radius | 10.2419 (QA, faces z 0.3–2.2) | 10.39 mean over 5 slabs (10.48 → 10.21 up the draft) |
| Matrix vs frozen golden | QA audit 0.429° / max 0.451 | 0.428° / mean 0.187, p95 0.398, max 0.526 mm |
| Normals | "volume −2434 → inward, flip" | ray vote: **outward** (7 % vs 73 % hits); no flip. See §4. |
| Open boundary loops | 21 | 21 (hex wall r 2.45–4.09, cup wall r 9.67–10.59, SAF-1 hole r 11.96–14.81) |
| Tilt | not measured | not resolvable: 9.2° ± 2.9° (bore, 1.5 mm span) and 2.9° ± 0.46° (bore + hex) — partial coverage biases centres (hex centre sits ~0.2 mm off the bore centre) |

Lessons: wall-face IRLS survives partial angular coverage where section loops never close
(`allow_open_arcs` is the fallback for sections). The arm label is a convention: `fourier_mass`
returns all n candidates; state the label rule (the golden compared mod 120°).

### 2.3 P03 mop bracket (what not to do, and partial coverage)

Golden (`P03/2_mesh_cleaned/alignment.json`, `analysis/golden/OOM-P03.md` §3):
- Primary: disc normal from **PCA** of flat-face vertices (126k), z = 0 on the textured velcro
  field median (scanner-unresolvable surface, `INTAKE_CARD.md:42-44`). No rms/max recorded.
- Origin X/Y: Kåsa rim circle, **resSD 0.039**.
- Clock: **not recorded**; tread slots given phase 0 ("phase unaligned", TRACKER.md:31).
- Refinement: the matrix was ICP-refined **to its own CAD** (0.405° / 0.093 mm) → CHK-CIRCULAR.
  The verifier's own fit still sat **0.154° / 0.600 mm** away.
- Coverage: "partial scan ~270°" appeared only in the report, not at intake (A9).
- A raw-frame PCA radial p99.9 read OD 139 mm (tilt-inflated); the datum frame gave 128.6.

What the skill does instead: RANSAC+SVD plane with rms/max on a clean functional face (not a
textured field), a stated clock rule, `intake.py coverage` at intake (angular coverage per radial
band), never measure radii before the datum, and never touch `alignment.json` after the build.

## 3. Axis-primary worked example: OD-H12 pump

Golden (`OD/README.md:14`, `OD/report/alignment_T1.json`, `analysis/golden/OD-H12.md` §3):
- Primary: pump revolution axis → +Z (outlet −Z, inlet barb +Z). Secondary: side-plate normal → +X.
  Origin "on the axis"; the z origin is not a named feature.
- Fit method and residuals: **not recorded** (bare 4×4). Noise: **p95 0.13** on a "clean cylinder"
  self-fit (which cylinder is not recorded). Coil kept 0.2 mm off-axis, measured, not snapped.

Skill spec shape for this class (not replayed: the OD scan is 980k faces and the record has no
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

## 4. Normal orientation (correction to SYNTHESIS A5)

SYNTHESIS A5 and B02 `INTAKE_CARD.md:36` flip normals when the signed volume is negative. On an
open (non-watertight) scan the signed volume depends on the coordinate origin, so its sign is
not evidence. Measured on the B02 raw scan: in the golden datum frame the dome-top faces have
mean n_z **+0.93** and the rim faces **−0.99**, i.e. the normals are already outward, while the
volume is −2434 mm³ (and −5397 mm³ after the rigid transform). `intake.py` therefore uses the
volume sign only for watertight meshes and a seeded ray vote otherwise. If you flip on the B02
volume sign, the rim-facing faces end up pointing into the material and `level_plane` picks the
dome (z ≈ 11) instead of the rim. (This was found while testing this skill; it is listed as an
open question for the owner.)

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
| `origin.z` | axis primary only: `plane` (`approx_normal_datum`, `offset_range`) or `extreme` (`which` min/max) |
| `origin.definition` | the named intersection |
| `clock` | `polygon_flat`/`polygon_corner` (`n`, `z`), `min_radius` (`z`), `fourier_mass` (`n`, `r_range`, `z_range`, `pick_nearest_deg`, `label_rule`), `plane_normal` (`approx_normal_raw`), `none` (needs `why`) |
| `landmarks` | `[{"name", "stat": "zmax|zmin|rmax|xmin…", "r_range", "z_range", "expected", "tol", "tol_source"}]` |
| `tilt_reference_deg` | default 0.3 (RE_SPEC.md:241, report-only) |

Defaults marked with numbers are the values the golden code used (DRM `align.py`, B02 `q03_datum_full.py`);
they are parameters, not thresholds.
