# INTAKE CARD — cliff_bumper_sensor (robot cliff / bumper sensor housing)

Scan: `input/scan.stl` sha256 `618aeff99eee2303f68e5be03c7c31b5350641b6912f9a615f3fa9fcb159dc03`
(`input/INPUT_HASHES.json`). Working copy: `intake/work.stl` (497,471 → 250,000 faces,
work-vs-full p95 0.0017 / max 0.077 mm, seed 0; `intake/intake.json#decimation`).
Official gates run on the full-resolution original, never on the working copy.

## 0. Band regime (declared here, named again in the verdict)
Regime: **baseline-skill, material class plastic**: p95 ≤ 0.30 / max ≤ 0.80 mm
(`baseline/skills/stl2step-build123d/SKILL.md:87`). `intake/regime.json`.
Why: owner instruction "p95 plastik parça toleransı kullan" (2026-09-30, `DECISIONS.md` REGIME);
moulded consumer-plastic housing; scan-only (no calipers, `DECISIONS.md` MEASUREMENTS), so RE_SPEC
Tier-1 cannot run.

## 1. What it is (photos + mesh)
A cliff/bumper IR sensor module (photo_1..photo_5): black moulded body with a clear
(transparent) cover over most of it and a clear lens nose with two windows split by a black
centre rib; a wire harness leaves the black end (photo_5, bottom centre notch). Two side tabs
with guide rails slide into the host bumper (mounting interface). The rear black end carries a
shelf with three pockets open to the underside (connector/harness seats). Static part.
Two moulded pieces (clear cover + black body) are scanned as one closed envelope; the
deliverable is a single fused envelope solid (see §8).

## 2. Scan health (numbers from intake.json)
| Item | Value |
|---|---|
| Faces / verts (welded) | 499,218 / 251,181 |
| Bodies; kept; removed fragments % | 3; largest (497,471 faces); 0.3499 % (1,063 + 684-face fragments: wire stubs) |
| Scanner table removed % (rule used) | 0.0 (no table in the scan) |
| Watertight; open boundary edges / loops | no; 3,216 / 18 (working full: 2,997 / 16) |
| Normal orientation (method, verdict, flipped?) | ray vote 500 samples, seed 0: outward (0.97 against normal), not flipped |
| bbox raw; bbox datum (from alignment.json) | raw 18.49 × 41.51 × 42.81; datum 34.92 × 38.27 × 9.97 |
| Units verdict (CHK-SCALE) | FLAG: no calipers, units assumed mm, scale unverified, no scale applied |
| Noise floor (value, method, region) | 0.0275 mm, rms of RANSAC+SVD plane on the +Y side wall (4,986 faces), `intake/noise_sidewall.json`; top face whole: 0.038 (`noise_top.json`, includes crown + seam groove) |
| Artefact zones | lens windows: transparent, many holes, interior material seen through them; one irregular ~1.2 mm blob on the +Y tab (x −8.2..−7.1); wire slot roof not scanned |

## 3. Coverage / occlusion map (datum frame; `intake/coverage.json`)
17 open-boundary loops. The two largest (512 / 448 verts) sit in the lens windows
(x ≈ −27..−21, both sides of the rib): transparent plastic, partly scanned. One loop
(181 verts, r 1.1–5.4 about the z axis near the origin, z −8.1..−2.6) is the wire slot at the
rear bottom centre: its roof is not in the scan. The rest are small holes on the window faces.
Angular coverage is not meaningful for this prismatic part.

## 4. Functional surfaces & interfaces (each becomes a gate zone)
| Zone | Surface | Why functional | Caliper-coverable? | Band |
|---|---|---|---|---|
| Z-TAB | side tabs (y ±19.0, z −6.40..−4.56) and guide rails (y ±17.74) | slide into the bumper slot | yes (width over tabs, tab thickness) | regime p95/max |
| Z-TOP | top face z=0 | seats against the bumper pocket | yes (overall height) | regime |
| Z-POCKET | three underside pockets of the shelf | harness/connector seats | yes (pocket width/depth) | regime |
| Z-LENS | lens frame + centre rib plane, two recessed windows | optical window; transparent | frame yes, windows partly | regime, transparent-window artefacts expected |

## 5. Feature enumeration — interior included (CHK-ENUM)
| # | Feature | Seen in mesh (where) | Seen in photo (id) | Status |
|---|---|---|---|---|
| E01 | main box (clear cover) x −21.2..seam, y ±16.0, top z 0, bottom plane sloping 1.55° | all sections | 1, 3, 4 | both |
| E02 | top/bottom long-edge rounds R≈2.1 | x sections | 1, 4 | both |
| E03 | lens nose cup: bottom-side round R≈7.8, half-width 14.9, front plane 59.6° | x −27.6..−21.2 | 2, 4 | both |
| E04 | lens frame + centre rib on the front plane; two windows recessed ≈0.8 | nose depth map | 2, 4 (dark windows, black rib) | both |
| E05 | nose tip round R≈0.5 (front plane to bottom) | y sections | 2 | both |
| E06 | seam groove on the top between clear cover and black cap (x≈−1.07) | y sections | 1 (parting line) | both |
| E07 | rear black cap x seam..0, slightly wider (y +16.2 / −16.3) | x=−0.6 section | 1, 3, 5 | both |
| E08 | connector shelf x 0..7.07, z −0.08..−3.69 | y sections | 1, 5 | both |
| E09 | three pockets under the shelf (ceiling z −1.39) | x=3.5 section | 1 (three recesses on the black end) | both |
| E10 | side guide rails y ±17.74 (x −6.2/−6.4..0) with a taller rear part (x −0.88..0) | z sections | 3 | both |
| E11 | side tabs y ±19.0, z −6.40..−4.56 | z=−5.4 section | 1, 3, 4 | both |
| E12 | rear-bottom wire slot, width ≈3.06, roof not scanned | x=−0.3 section, coverage loop | 5 (wires leave there) | both (roof occluded → provenance: scan-extent) |
| E13 | two bottom ramps (wedges) at y ±(1.95..4.03), x −19.6..−14.9, 0.63 proud | z=−9.35 section | not visible in photos | mesh-only → explained: coherent symmetric pair, flat faces, clearly moulded |
| E14 | irregular blob on the +Y tab, x −8.2..−7.1, ≈1.2 mm tall | y=18.5 section | not resolvable in photos | mesh-only → investigated: single component, no flat top, not mirrored → not modelled, open question (§8) |
| E15 | material seen behind the lens windows | nose depth map | 2, 4 show the lens is clear | mesh-only → explained: interior visible through transparent plastic |

CHK-ENUM result: every photo checked (photo_1..photo_5); every mesh-only item has an explanation
(E13 real, E14 open question, E15 transparency). No unexplained cluster.

## 6. Datum plan and result (from alignment.json, status OK)
- Primary (levels): top face, clear-cover plateau (raw-frame crop sphere r 6.5 mm; excludes the
  cover/cap seam groove and the crowned cap) → XY @ z = 0, material −z. WHY: largest continuous
  moulded flat, seats against the bumper pocket. Fit rms / max: 0.0120 / 0.0685 mm (6,624 faces;
  untrimmed rms 0.0120).
- Secondary / clock: +Y side wall (between nose blend and tab) normal → +Y. Fit rms / max
  0.0156 / 0.0608. WHY: the long side walls carry the mounting tabs.
- Origin X: lower-body rear wall (single plane, rms 0.0222). Origin Y: mid-plane of ±Y side walls
  (rms 0.0156 / 0.0231); wall-to-wall 31.95 mm at the crop.
- Origin: top face ∩ side-wall mid-plane ∩ lower-body rear wall.
- Tilt (CHK-TILT): 0.345° = the +Y wall's out-of-perpendicularity to the top plane (prismatic
  part, no coaxial stations); **finding** (> 0.3° reference, report-only). Read as wall draft.
- Sanity landmarks: primary at z=0 (0.002), lowest point = bottom-rib tips −9.902 (expected
  −10.0 ± 0.3), shelf rear end 7.348 (7.1 ± 0.3), nose tip −27.568 (−27.3 ± 0.5), tab tip
  19.195 (19.0 ± 0.3): all OK.
- History: try 1 (whole top face, whole walls) → STOP (top rms 0.038 > wall noise 0.0275: the top
  is two moulded pieces with a ~0.1 mm crown, not noise) → `alignment_try1_STOP.json`; try 2 with
  clean-region crops → CHECK_LANDMARKS because the "bottom face" landmark's stat (zmin) lands on
  the two bottom ramps, not the face → landmark redefined to the ramp tips →
  `alignment_try2_CHECK_LANDMARKS.json`; try 3 OK. The datum itself did not change between
  try 2 and try 3.
- Skill change used: `align.py` gained `origin.xy_planes` (plane origin for prismatic parts) and
  raw-frame `crop_point_raw` / `crop_radius` on plane fits (this run, 2026-09-30).

## 7. Rebuild strategy summary
Additive boxes + one cup body, all analytic: body box with long-edge rounds; nose cup (box with
R 7.8 bottom-side rounds) cut by the measured lens plane; cap and shelf boxes; rails and tabs as
boxes fused to the side walls; subtractive: bottom plane cut (1.55° slope), pockets, wire slot,
seam groove (cylinder), window recesses (inner cup ∩ slab behind the lens plane minus the rib).
Ramps as wedge prisms. No lofts, no symmetry forced where the sides measured differently.

## 8. Risk flags and operator declarations
- Two-piece assembly (clear cover + black body) delivered as one fused envelope solid — no
  internal geometry. (Orchestrate §6 lists a multi-body STEP as HALT; a single envelope solid is
  the supported case.)
- Transparent lens windows: scan partly sees through; verify should expect interior hits there.
- E14 blob on the +Y tab: debris or a real detent? Not modelled.
- Wire-slot roof height unknown (not scanned).
- No calipers: absolute scale unverified.

## 9. Measurement request → `intake/MEASUREMENTS.md`
Written with scan-predicted values; the owner supplied none (scan-only, `DECISIONS.md`).
