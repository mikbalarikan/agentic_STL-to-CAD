# Mask policy (CHK-MASK)

A mask removes points from a deviation statistic. Masks are legitimate when the removed points
are not a surface deviation of the modelled part. A PASS that exists **only** because of a mask is
a limitation, never a clean pass (`analysis/SYNTHESIS.md` E5, CHK-MASK).

## Rules

1. **Named and justified.** Every mask has a `name`, a `why` (the physical reason), and `evidence`
   (a path, photo id, or assumption id). `verdict.py` refuses a mask with no `why`.
2. **Fraction reported.** For each mask, report the fraction it removes in each direction, plus the
   stats of the points *inside* it. This is the DRM format:
   `snap_masked_gate.json#masks.*.{n, frac, p50, p95, max}`.
3. **Masked and unmasked side by side.** Report both for the whole part and for every zone. Never
   report masked numbers alone.
4. **Sensitivity sweep.** Run leave-one-out per mask. Run a radius sweep for open-boundary masks.
   The golden radii were 0, 0.2, 0.4, 0.8, 1.5 and 2.5 mm (B02 `q20_tier2.py:181-190`, parameters).
5. **Mask-dependent pass.** A gated item that passes masked and fails unmasked is listed in
   `deviation.mask_dependent_passes`. It forces `APPROVED_WITH_LIMITATIONS` at best, and the
   limitation text must say that the pass is masked, with the unmasked number.
6. **Masks do not delete evidence.** The scan file is never edited. Region masks select points;
   they do not remove triangles from the gate's reference mesh. The one exception is the ICP
   reference in `tier2_icp.py --scan-masks`, for unmodelled bodies such as bristles or a COTS
   screw, as B02 did (`q20_tier2.py:32-46`). That removal is recorded with face counts.
7. **Locate from the scan, not from the CAD.** A coverage-gap mask is measured on the scan. B02
   located the hex-wall gap from scan faces with a wall-only normal filter (`q20_tier2.py:122-138`).
   Including the pocket floor made every azimuth look covered, and the mask became a no-op.
8. **Masking never turns a FAIL into a PASS silently.** The DRM snap is the counter-example that
   stays honest: 6 artefact masks removed 4.9 %, but the max stayed 1.246 > 0.80, and the official
   `overall_pass: false` stands (`analysis/golden/dreame_brush-caps.md` §7, §9).

## Mask types (`qa/masks.json`)

```json
{"masks": [
 {"name": "M1 bristles", "type": "region", "applies_to": "scan", "select": {"r": [38.5, null]},
  "why": "soft bristles, not modelled", "evidence": "ASSUMPTIONS A10"},
 {"name": "M3 open boundary", "type": "open_boundary", "applies_to": "cad", "radius_mm": 0.8,
  "why": "distance to a scan hole EDGE is not a surface deviation", "evidence": "q20_tier2.py:9-10"},
 {"name": "M4 skin normal", "type": "normal_disagreement", "applies_to": "cad", "angle_deg": 70,
  "why": "occluded interior correspondence is not an outer-skin deviation", "evidence": "q20_tier2.py:11-12"}
]}
```

`applies_to`:
- `scan`: the mask is evaluated on scan→CAD points.
- `cad`: the mask is evaluated on CAD→scan points. `open_boundary` then measures from the
  closest scan point.
- `both`: both directions.

## Golden examples

| Project | Mask | Why | Fraction | Effect |
|---|---|---|---|---|
| B02 | M1 bristles r > 38.5 | soft, not modelled (A10) | 18.8 % of scan faces | reference only |
| B02 | M2 screw head + end | COTS, not modelled (A9) | 19,222 faces (log) vs 16,610 (verdict): conflict, see QUESTIONS B | reference only |
| B02 | M3 open boundary < 0.8 mm | hole edge ≠ surface | drops 20.76 % | hex pocket passes only with M3 + A6. Unmasked max **1.624**, 0.824 over the 0.8 band. |
| B02 | M4 skin \|n·n\| < cos 70° | occluded correspondence | drops 5.91 % | none |
| B02 | A6 hex coverage gap | scan saw 263/360° of the wall | 43.4 % of the hex zone | "masked pass", declared |
| DRM snap | 6 artefact regions (bore-edge fuzz 1.44 %, OD top burr 0.93 %, hook fringe 0.20 %, hook underside 0.92 %, table remnant 1.21 %, flat-corner skirt 0.22 %) | scanner artefacts | 4.9 % total | max still 1.246 > 0.80. **FAIL stands.** |

Sources: `analysis/golden/OOM-B02.md` §7, §9; `analysis/golden/dreame_brush-caps.md` §7, §9.

## Wording for a masked pass (copy the pattern, fill the numbers from gate.json)

> "The hex-pocket PASS is a **masked** pass: with the open-boundary mask (0.8 mm) and the scan-
> located coverage-gap mask it reads max 0.316; **unmasked it reads 1.624, 0.824 over the 0.8
> band**, on the feature with no caliper reading. **Re-run trigger:** one caliper reading on F01."
> — modelled on `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:138-145`.

Wording for a band not met despite masks:

> "Scan→CAD max 1.226 > 0.80 (band not met). Six named artefact masks (4.9 %) do not clear it: the
> residual is a floating scan flap at the 150° leg top (315 of 570k points > 0.8 mm). Delivery needs
> a recorded human acceptance." (modelled on the dreame README artefact list)
