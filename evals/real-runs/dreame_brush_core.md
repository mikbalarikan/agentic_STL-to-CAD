# Real run: Dreame main brush-roll core with bristles (2026-09-30 → 2026-10-01)

Second run of the v1 skills on a part with no golden record. Owner supplied one STL
(`..._decimated_20MB.stl`, 391,998 faces), no photos, no calipers, and asked for the "p95 plastic-part
tolerance". Records copied under `dreame_brush_core/`; the full run folder and STEPs went to the owner as
the delivery zip (+ `_part1.zip` with the scan).

## Inputs and decisions
- Regime: baseline-skill plastic, p95 ≤ 0.30 / max ≤ 0.80 mm (owner instruction).
- Scan-only and inspection-only (decimated export, no full-res): both recorded as "delegated to agent".
- Bristles: soft feature, not modelled, named mask (B02 precedent). Scanner table under the hub removed at intake.

## Part and model
- Core = ONE profile (Ø14.93 base circle, 4 T-slots, 2+2 grooves) extruded with a constant twist of
  ≈ −1.597 °/mm (`Solid.extrude_linear_with_rotation`, valid single solid over ≈261°), 2 × 27 tuft holes,
  4-blade pinwheel drive dog, two hub discs, idler counterbore/bore with an end round from a revolved envelope.
- Datum: hub drive face primary, hub cylinder r15.2 origin (the core lands as XY feature were STOP: ovality
  0.065 rms > circle noise), 4-fold blade clock; core-axis tilt 0.051° measured separately over 140 mm.

## Result
- it1 → REVISE: verify found the slot undercut (T-slot foot) missing — a CHK-ENUM miss at intake (the foot is
  only visible through the 1.24 mm neck). Routed `measure`; it2 changed only the slot profile (+2 params).
- it2 → BAND_NOT_MET, accepted by the owner (ACCEPT-BAND cites gate `830ff7000088`). Scan→CAD masked p95
  passes; its max is set by an unmodelled local recess at 1 of 4 slot entries (no photo to classify it).
  Observable CAD→scan misses on slot foot/floor surfaces the decimated scan never saw. Numbers: `dreame_brush_core/gate.json`.
- Delivery: README, MANIFEST, repro (reproducible), zip. The first zip was 107 MiB, over the 30 MiB chat
  upload limit → `package_zip.py --max-zip-mb` added (companion zips), `*.npz` made regenerable.

## Skill defects found (status on this branch)

| # | Where | Defect | Status |
|---|---|---|---|
| 1 | `stl-re-deliver/scripts/package_zip.py` | No way to stay under the 30 MiB chat upload limit; `*.npz` verifier caches not treated as regenerable | fixed: `--max-zip-mb`, `--part-file-mb`, `*.npz` in REGENERABLE |
| 2 | `stl-re-intake-datum/scripts/align.py` | CHK-TILT reports `pass` from a single 0.75 mm-span feature; a meaningful tilt needed a separate script | open |
| 3 | `stl-re-intake-datum/scripts/datum_fit.py noise`, `measure-intent/scripts/pattern_count.py` | negative CLI numbers need `" -225"` quoting; `--orders` takes `a,b` not `a-b` | open (known since OD-H22) |
| 4 | `stl-re-measure-intent/scripts/param_table.py` | every scan `count` must cite "order/FFT"; a linear pattern (tuft rows) had to be counted by an FFT along z to pass | open (rule wording) |
| 5 | intake skill | no guidance for twisted/helical profiles (untwist by entropy minimisation was improvised) and for undercuts seen only through a narrow neck | open |
| 6–17 | `stl-re-verify` scripts | 12 defects listed in `dreame_brush_core/VERDICT.md` "Skill defects found" (observability OOM and CAD masks, cluster list on unmasked points, zones ungated under baseline-skill, no helical mask term, ICP cap 60 too low for a screw-sliding part, …) | open |

## Add-on (2026-10-01): bristles as one fitted body ("max volume occupied")
- Owner asked for the brush wires as a single fitted body. Built in `<run>/addons/bristles/` on top of the verified
  core (build/ and qa/ untouched): per tuft row, a 0.2/99.8 % percentile (r, Δθ_u) section extruded with the core
  twist and trimmed by a revolved (r, z) ramp profile; tuft holes filled as roots; fused with the core → one valid
  solid. Volumes and the independent containment check (PASS on the ±3 mm soft band): `dreame_brush_core/bristles/`.
- Defects/lessons: OCC returned nothing for fin ∩ revolve at some revolve-seam angles (retry with a turned seam,
  logged); the fins closed the tuft-hole mouths and left 26 internal voids until the holes were filled as roots;
  the main zip went over 30 MiB because of two CAD STL meshes → `package_zip.py` now moves large deliverable
  meshes to the companion zips as well.
