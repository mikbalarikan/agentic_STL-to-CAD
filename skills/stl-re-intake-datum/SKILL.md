---
name: stl-re-intake-datum
description: Intake and datum alignment for STL-to-STEP reverse engineering - scan hash and health, working copy, fragment/table removal, scale and noise checks, occlusion map, feature enumeration from mesh and photos, measurement request, and a named datum frame written to alignment.json. Use at the start of any scan-to-CAD job or when the datum must be redone.
---

# stl-re-intake-datum

Stage 1 of the `stl-re-*` pipeline (orchestrator: `stl-re-orchestrate`). Input: `<run>/input/`
(scan, photos, any caliper sheet). Output, all in `<run>/intake/` (paths and keys fixed by
`../stl-re-orchestrate/references/run-contract.md` §1, §3):

| File | Written by |
|---|---|
| `intake.json`, `work.stl` | `scripts/intake.py stats` |
| `noise_*.json` | `scripts/datum_fit.py noise` |
| `alignment.json`, `aligned_work.stl` | `scripts/align.py` |
| `coverage.json` | `scripts/intake.py coverage` |
| `INTAKE_CARD.md` | you, from `references/intake-card-template.md` |
| `MEASUREMENTS.md` (the request) | you, from `references/measurements-template.md` |

Hand-off: `stl-re-measure-intent` starts only when `alignment.json#status` is `OK` and the intake
card declares a band regime. This skill does no dimension extraction beyond what the measurement
request and the datum need.

Path abbreviations used below: `DRM/` = `golden-examples/dreame_brush-caps/`, `B02/` =
`golden-examples/OOM-B02_side-brush-3-arm/`, `P03/` = `golden-examples/OOM-P03_mop-pad-bracket/`;
`SYNTHESIS` = `analysis/SYNTHESIS.md`; `RE_SPEC.md` = `baseline/oomwoo-re-pipeline/RE_SPEC.md`.

Requirements: Python 3.10+, `numpy`, `trimesh`, `scipy`, `rtree` (proximity and ray tests),
`fast_simplification` (decimation). All scripts are seeded (default `--seed 0`) and write the
common JSON header (run-contract §2). Never print raw mesh data into the conversation. Read
the scripts' JSON summaries (facet-film T1, `analysis/baseline/facet-film-transferable.md`).

## Non-negotiables

1. **Never modify `input/scan.stl`.** Weld, fragment/table removal and normal flips happen on the
   working copy only, and they are logged (SYNTHESIS A5, §3 "default mesh repair" rewritten; facet-film T4).
2. **Scale before datum, datum before measuring.** Never datum an unverified-scale mesh
   (RE_SPEC.md:105-107). Never read radii or extents in the raw frame: P03 read a raw-frame OD of
   139 mm against a true 128.6 (`analysis/golden/OOM-P03.md` §3).
3. **Primary datum = functional or mating surface, or the axis of an axis-primary part.** The
   "largest facet" default is DROPPED (SYNTHESIS §3; DRM largest facets are ~0.27 mm² fragments).
4. **No bbox fallback, no hard-coded tilt.** `align.py` exits 3 when no origin feature is found
   (golden `align.py:82` silently used the bbox centre) and measures tilt (golden hard-coded 0, CHK-TILT).
5. **STOP when a datum fit residual exceeds the measured noise floor** (RE_SPEC.md:126-129).
   `align.py` writes `status: "STOP"` and exits 2. Do not force the datum onto warp, wear or
   artefact. Pick a cleaner region or report. rms is gated, max is reported (RE_SPEC says
   "RMS + max"; see QUESTIONS §C): a plane primary's `fit_untrimmed` stats show the residual
   before the |d| < 2·tol widen/refine, next to the trimmed (gated) rms/max.
6. **Record, don't grade, on decimated copies.** The repo's `*_scan_decimated.stl` copies deviate up to
   0.028 mm (`golden-examples/README.md`). Official gates run on the full-resolution original
   (SYNTHESIS A3).

## Procedure

### Step 1 — Intake stats and hash (SYNTHESIS A1, A2, A4, A5)

```bash
python scripts/intake.py stats input/scan.stl --out-dir intake --work-faces <N> \
    [--keep largest|all] [--table-dir x,y,z --table-below <offset>]
```

- Records sha256, faces/verts (raw and welded), bbox, watertight, winding, euler, open boundary
  edges/loops, body count with the top-5 body sizes.
- `--work-faces`: decimate when the mesh is large. RE_SPEC.md:347 says "> ~15 MB". Golden targets
  were 300,000 (DRM), 199,999 (B02) and 250,000 (P03). The seeded work-vs-full deviation is
  reported, not gated. Re-confirm any dimension you quote on the full mesh; B02 found agreement
  ≤ 0.06 mm (`B02/6_RE_work/INTAKE_CARD.md:5-7`).
- `--keep largest` drops scan fragments and reports `fragments_pct`. Use `--keep all` when a
  second body is a real part (look at the photos first). A decimated copy can split into many
  tiny bodies: the DRM screw decimated copy has 1,017 bodies (1.98 % of faces), while the
  full-res raw had 104 (`DRM/report/intake.json`).
- Scanner table: direction pointing from the table into the part, plus an offset below which
  up-facing faces are table. The golden rule was z-threshold + up-normal (`n_z > 0.7`,
  `DRM/report/source/fastgate.py:36-38`); DRM snap had 9.3 % table vertices. If the table direction
  is only known after levelling, run `align.py` once, then re-run `intake.py stats` with the datum-frame
  direction mapped back to raw (or remove it at the gate and say so).
- Normals: on a watertight mesh the signed volume decides. On an open mesh `intake.py` uses a
  seeded ray vote, because the signed volume of an open mesh depends on the origin: a part can
  measure with a negative signed volume while its normals are genuinely outward (see
  `references/datum-cookbook.md` §4 for the case that surfaced this). If
  `orientation.verdict` is `undecided`, stop and inspect.

### Step 2 — Units and scale: CHK-SCALE (SYNTHESIS A6; RE_SPEC.md:98-101)

When caliper or operator dimensions exist (at intake or when the filled sheet comes back):

```bash
python scripts/intake.py scale --pair ENV-X <caliper> <scan> <unc> ... --scan-noise <noise> --out intake/scale.json
```

- Needs ≥ 3 envelope dims (`ENV-*`). Fewer → decision `FLAG`: scale unverified, none applied,
  said in the card (a part with no envelope calipers and only a few mid-size ratios that disagree
  with each other is non-uniform, not scaled — see `analysis/golden/OOM-B02.md` for the worked
  case).
- **ONE uniform scale** only if every ratio agrees with the pooled ratio within its uncertainty
  (caliper uncertainty + noise) and all differ from 1. Pass it to `align.py` as `scale_factor`,
  and log it in `alignment.json` and the parameter table.
- Non-uniform → flag and apply no scale. The calipers drive their own dimensions (B02).
  Thin-section oversize is scanner dilation (an offset, not a scale) — thin ribs and arms can read
  measurably oversize on a scan versus caliper without that being a global scale error
  (`B02/6_RE_work/INTAKE_CARD.md` R6). A single axis check on one part alone is not enough to
  justify a scale factor (P03).
- No calipers at all (DRM, OD) → "units assumed mm, scale unverified" is a declared limitation.
  OD's unverified mm is why CHK-SCALE exists.

Record the result as `chk_scale` in the `align.py` spec so it lands in `alignment.json#checks`.

### Step 3 — Noise floor on a clean primitive (SYNTHESIS A7)

```bash
python scripts/datum_fit.py noise intake/work.stl --plane-normal x,y,z [--offset-range a b] \
    --region-desc "<surface>" --out intake/noise_primary.json
python scripts/datum_fit.py noise intake/aligned_work.stl --circle-z <z> --r-range r0 r1 \
    --region-desc "<bore>" --out intake/noise_circle.json      # after a first alignment
```

- Pick a moulded or machined surface free of texture, wear or bridging, never a velcro/textured
  field (P03, `INTAKE_CARD.md:42-44`).
- Golden noise floors vary by part and surface quality; see `analysis/golden/*.md` §"noise" for
  the recorded values if you need a reference point (SYNTHESIS A7). RANSAC tol ≈ noise, in the
  0.05–0.1 band (RE_SPEC.md:127).
- Measure the plane noise for plane fits and the circle noise for circle fits
  (`noise_secondary`). Plane rms is not comparable to section-circle residuals — the two metrics
  can differ by several times on the same part, so don't gate one against the other's floor.
- If the only clean primitive is the primary itself (DRM), the STOP rule is trivially met for the
  primary. Say so in the card.

### Step 4 — Coverage / occlusion map (SYNTHESIS A9)

After the first `align.py` run:

```bash
python scripts/intake.py coverage intake/aligned_work.stl --out intake/coverage.json
```

- Open-boundary loops with r / z / θ ranges fill the occlusion table. Expect several distinct
  loops on a part with multiple occluded features (a hex wall, a cup wall, a labelled hole, etc.)
  — see `references/datum-cookbook.md` §2.2 for the worked case and loop count.
- `radial_bands[].theta_covered_deg < 360` on a round part is partial angular coverage. State it
  in the card, not first in the report (P03 "~270°" was only in the report, `analysis/golden/OOM-P03.md` §3).
- The map cannot see scanner-bridged cavities (DRM hook underside, P03 socket). Add those from
  photos and sections.
- Soft or deformable features (bristles) get a declared radius or zone and a soft band, and they
  are excluded from the gate. Model to the rigid anchor (heuristic, n=1: B02, `INTAKE_CARD.md` R4).

### Step 5 — Feature enumeration from mesh AND photos: CHK-ENUM (SYNTHESIS A8)

List every feature, interior included, in the card §5. For each, record where it is seen in the
mesh and in which photo.

- Look at every profile/side photo and list what stands proud, including anything above the
  feature you expect to be topmost. P03 missed its drive stem, even though photo
  `IMG_20260729_140345.jpg` shows it, and fixed ENV-Z at the hex tip (`analysis/golden/OOM-P03.md` §8).
- Use `coverage.json#radial_bands` (z extents per radius band). Material on the axis or above the
  last enumerated feature is a feature until disproven: count the points, look for a flat top, check
  the photos (CHK-CLUSTER in measure/verify; P03 had 158k coherent verts).
- Look through every opening for ribs, bosses and webs (baseline template §4). B02 enumerated
  9 interior items and a 3-fold break (SAF-1) by sector comparison.
- **CHK-ENUM fails** when a photo-only or mesh-only feature has no explanation. Then add the feature, or
  write the question for the operator. Do not continue to the measurement request with an open
  CHK-ENUM item.

### Step 6 — Measurement request with scan-predicted values

Write `intake/MEASUREMENTS.md` from `references/measurements-template.md`:

- Envelope first, then every caliper-coverable functional interface, then walls.
- Each row gives jaw placement with a photo reference, the datum reference, and **the scan-predicted
  value** (RE_SPEC.md:197-202). A reading far from the prediction is caught at the bench. This is the
  early catch for CHK-ACHIEVABLE: B02 F06 was misattributed and only caught after the build.
- Lobed or non-round features get two rows (max/min, B02 M4/M5). Features the scan cannot see get
  "not visible — needs …" (B02 M11: screw removal).
- The statuses in the template include `caliper-photo` (±0.1 effective; B02 `MEASUREMENTS.md:24`) and
  `scan-authority` (ungated). A dimension without a reading is **absent, not passed**.
- If calipers will not come (scan-only job), say so in the card. The orchestrator decides whether to
  proceed (B02 and P03 proceeded on a recorded operator directive).

### Step 7 — Band regime declaration (owner decision Q1)

In the card §0, declare the band regime (RE_SPEC / baseline-skill / project-spec) with its source.
There is no silent default (run-contract §9). What the goldens used: B02 and P03 → RE_SPEC; DRM and
OD → baseline-skill (SYNTHESIS Q1). Regime numbers are in the card template.

Run this command to write the canonical declaration to `intake/regime.json` (run-contract §12):

```bash
python scripts/intake.py regime --name RE_SPEC --out-dir intake --why "<why this regime applies>"
python scripts/intake.py regime --name baseline-skill --class plastic --out-dir intake --why "..."
python scripts/intake.py regime --name project-spec --bands '{"p95_mm": 0.5, "max_mm": 1.0}' \
    --source "<path:line>" --out-dir intake --why "..."
```

`regime.json#bands` is always the canonical flat object `{p95_mm, max_mm, tier1_abs_mm,
interface_max_mm}` (run-contract §12), `null` for a band the regime does not gate: RE_SPEC
fills all four, baseline-skill only `p95_mm`/`max_mm` and records the chosen class as
`regime.json#material_class` (`plastic|machined`).

Then append a `REGIME` line to `DECISIONS.md` (run-contract §10) recording the choice and its
evidence path.

### Step 8 — Datum (SYNTHESIS B1–B7, B11; RE_SPEC.md:109-129)

Plan the DOF ladder in the card §6 first, then write `intake/datum_spec.json` and run:

```bash
python scripts/datum_fit.py planes intake/work.stl --out intake/planes.json   # candidates only
python scripts/align.py intake/datum_spec.json      # exit 0 OK, 2 STOP, 3 spec/geometry error
```

Worked specs and golden numbers are in `references/datum-cookbook.md`. Rules:

1. **Primary.**
   - Plane-primary parts: `level_plane` near an approximate normal. The golden recipe, reused as
     defaults: faces within 10°, area-weighted offset histogram with 0.1 mm bins, peak bin ±0.15, seeded
     RANSAC (tol 0.05, 300 iterations), widen to 2·tol, SVD refine. `material_side` says where
     the material is relative to the outward normal.
   - Axis-primary parts (turned bodies with no functional flat, e.g. OD): normals-eigen axis over
     faces nearly perpendicular to the approximate axis. Crop to one clean cylinder
     (`crop_point`/`crop_radius` are required). The gated residual is the RADIAL residual of the
     cropped cylinder faces about the fitted axis vs the median radius, compared with
     `noise_secondary` (a circle noise floor) — not the normal-line distance vs the flat noise
     floor, which is a different metric (review B1; `normal_line_dist` is kept as a diagnostic).
   - Record `why` for every datum (RE_SPEC.md:124).
2. **Secondary / origin X-Y.** Circle fits on a true circle:
   - Kåsa on closed section loops, or IRLS (Cauchy, golden scale 0.30) when outliers are present.
   - `wall_faces` for occluded walls whose sections never close (B02 cup bore).
   - A non-circular feature (DRM double-D) gives a valid centre by symmetry, but its residual is
     shape error. Use a true circle for the residual check, or declare it.
3. **Clock.** Name the feature and the rule, and store the angle:
   - `polygon_flat`: e.g. a pentagon flat feature (DRM screw; see `analysis/golden/DRM.md` for
     the measured clock angle).
   - `min_radius`: e.g. a flat cut nearest a minimum radius (DRM snap; angle in the golden report).
   - `fourier_mass`: B02 arms. State the label rule, because the candidates are mod 360/n.
   - `plane_normal`: OD side plate.
   - `none`: only a fully axisymmetric part, with a `why`.
   - Choose a section z on straight flats, away from a fillet or chamfer transition — picking a z
     near such a transition measurably shifts the clock angle (see `analysis/golden/DRM.md` §2 for
     the worked sensitivity).
   - P03 never recorded its clock (B6).
4. **Origin.** A named intersection ("bore axis ∩ top face"), never "the centre".
5. **CHK-TILT.**
   - `align.py` fits a COMMON slope with a PER-FEATURE intercept through the circle centres
     (so a constant offset between features is not read as tilt) and reports
     `tilt_deg.value ± stderr_deg` over `z_span_mm`. Use ≥ 3 stations over the longest clean
     coaxial span; a list of coaxial features is allowed. Fewer than 3 stations = "not measured"
     = a finding.
   - Every feature with its own ≥ 3 stations also gets an independent fit in
     `tilt_deg.per_feature` (`value`, `stderr_deg`, `direction_deg`). When two per-feature tilt
     vectors differ by more than their combined 1σ stderr, `tilt_deg.resolvable` is `false` and
     the CHK-TILT note reads "not resolvable" (a heuristic disagreement test, review M2) —
     record it rather than reporting the pooled number as a single fact.
   - The result is `finding` above the 0.3° audit reference (RE_SPEC.md:241), or when it is
     not resolvable. That band is report-only (owner decision Q2).
   - **When CHK-TILT flags a finding:**
     - If the stderr is comparable to the value, or the span is short, or the arcs are partial,
       re-measure on a longer clean span.
     - If it persists, record it. Decide from function whether the bore or the plane is primary,
       and tell measure/rebuild. Never silently re-level.
     - On the DRM screw, two independent per-feature tilt fits disagreed by roughly an order of
       magnitude more than their combined stderr, so tilt was **not resolvable** from those two
       features (`reviews/stl-re-intake-datum.md` M2; the golden run had assumed 0 — see
       `analysis/golden/DRM.md` §2 for the fitted values). On B02, partial angular coverage
       similarly made tilt unresolvable depending on which features were used (see
       `analysis/golden/OOM-B02.md`). Report it as such, never as a single measured value.
6. **Sanity landmarks (B11; facet-film T3).**
   - `align.py` checks automatically that the primary lands at z = 0 within the noise floor.
   - Add 3–5 landmarks from the photos or the card, e.g. a dome apex or a part-bottom extreme
     compared against a predicted z (see `analysis/golden/OOM-B02.md` / `analysis/golden/DRM.md`
     for worked examples). Each `tol` needs a source.
   - `status: CHECK_LANDMARKS` means a landmark failed. Suspect the sign, side or feature choice
     before anything else.
7. **Freeze.** After `alignment.json` is OK, it is frozen. Never refine it by ICP against your own
   CAD (P03 did; CHK-CIRCULAR, SYNTHESIS B9). A later datum change resets measurement and rebuild
   (RE_SPEC.md:131-136). Angles downstream are recorded only in this frozen frame, with the
   sign convention stated (CHK-FRAME: an intake-stage angle and the frozen-frame angle for the
   same feature can differ in sign convention as well as value — declare the convention, don't
   assume it carries over; see `analysis/golden/OOM-B02.md` for the case this caught).

### Step 9 — Write the intake card

Fill `references/intake-card-template.md` from the JSON files. Copy the numbers; never retype them
(CHK-NUMBERS spirit). List anything the mesh cannot decide as operator declarations (facet-film T38).

## Failure handling

| Signal | Check | Do |
|---|---|---|
| `align.py` exit 2, `status: STOP` | fit rms > noise floor (RE_SPEC.md:126-129) | Pick a cleaner region, crop out wear or bridging, or use a true circle. If no clean region exists, report to the orchestrator with the numbers. Do not proceed. |
| `align.py` exit 3 | spec or geometry error (no origin feature, empty cone) | Fix the approximate normal, radius window or z range. Never substitute a bbox centre. |
| `status: CHECK_LANDMARKS` | sanity landmark off | Check `material_side`, the clock label rule and the feature choice. Re-run. |
| CHK-SCALE `FLAG` | fewer than 3 ENV dims, or non-uniform ratios | No scale. Declare it in the card; calipers drive their own dims. |
| CHK-TILT `finding` | tilt > 0.3° reference or not measured | Longer span → record → decide which datum is functional (step 8.5). |
| CHK-ENUM open item | photo-only or mesh-only feature | Add it, or ask. The measurement request waits. |
| `orientation.verdict: undecided` | ray vote tie | Inspect normals on a known outward face (e.g. a top face) and pass the decision explicitly. |

The iteration bound (3 loops per part, RE_SPEC.md:248-250) is counted by the orchestrator. A
re-datum triggered by verify counts as a loop.

## Heuristics (single-project evidence)

- Separate inner and outer coaxial walls by the sign of n·r̂ instead of radius windows
  (heuristic, n=1: B02 `qa/q03_datum_full.py`).
- Sign-free Fibonacci normal vote (`datum_fit.normal_vote`) to find the dominant flat direction
  with no prior normal (heuristic, n=1: B02).
- Offset-histogram plane grouping on noisy scans (`datum_fit.dominant_planes`, heuristic, n=1:
  DRM). Use it for candidates only.

## Scripts

| Script | Lifted from | What changed |
|---|---|---|
| `scripts/intake.py` | `DRM/report/source/intake.py` | no hard-coded paths; sha256; reported fragment/table removal; working-copy weld and orientation (ray vote for open meshes); seeded decimation provenance; `coverage` and `scale` subcommands (new) |
| `scripts/datum_fit.py` | `DRM/report/source/datum.py`, `align.py:fit_circle,level_transform`; `B02/6_RE_work/qa/q03_datum_full.py` | typed; corrected `axis_from_normals` (no-op line removed, explicit point solve); IRLS Cauchy circle; noise CLI; section chaining without networkx |
| `scripts/align.py` | `DRM/report/source/align.py` `__main__` | JSON spec; measured tilt; no bbox fallback; axis-primary; wall-face IRLS; Fourier and plane-normal clocks; STOP rule; landmarks; contract keys |

Each script has a provenance header and states its blind spots.
