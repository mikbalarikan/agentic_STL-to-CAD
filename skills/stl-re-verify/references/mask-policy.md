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
4. **Sensitivity sweep.** Run leave-one-out per mask. Run a radius sweep for open-boundary masks
   (B02 `q20_tier2.py:181-190` has a worked set of sweep radii, as parameters not thresholds).
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
   stays honest: a handful of named artefact masks removed only a small fraction of points, the
   whole-part max stayed over its band regardless, and the official failing result stands
   (`analysis/golden/dreame_brush-caps.md` §7, §9 — see there for the actual fractions and max).

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

The kinds of masks each golden part used, and what they were for:

| Project | Mask | Why | Effect |
|---|---|---|---|
| B02 | bristles beyond a radius | soft, not modelled (A10) | reference only |
| B02 | a COTS screw head + end | not modelled (A9) | reference only — the golden's own records disagreed on the exact face count removed; a conflict like this is itself a finding (see QUESTIONS B) |
| B02 | open-boundary mask | hole edge ≠ surface | a critical hex-pocket feature passes only with this mask plus a coverage-gap mask; **unmasked, it misses the band** — see `analysis/golden/OOM-B02.md` §7 for the actual numbers |
| B02 | skin normal-disagreement mask | occluded correspondence | none (doesn't change the result) |
| B02 | hex coverage-gap mask | scan saw only part of the wall | "masked pass", declared |
| DRM snap | several named artefact regions (scanner fuzz, a burr, fringe/underside effects, a table remnant, a corner artefact) | scanner artefacts | removes only a small total fraction; **the whole-part max still fails the band. FAIL stands.** |

Sources: `analysis/golden/OOM-B02.md` §7, §9; `analysis/golden/dreame_brush-caps.md` §7, §9
(read these for the actual fractions and numbers).

## Wording for a masked pass (fill the numbers from gate.json — this is a pattern, not a template
with real numbers to copy)

> "The [feature] PASS is a **masked** pass: with the open-boundary mask and the scan-located
> coverage-gap mask it reads max <masked value>; **unmasked it reads <unmasked value>, <delta>
> over the band**, on the feature with no caliper reading. **Re-run trigger:** one caliper
> reading on [feature]." — modelled on
> `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:138-145` (read it for the real
> wording and numbers).

Wording for a band not met despite masks:

> "Scan→CAD max <value> > <band> (band not met). Several named artefact masks (<fraction>) do not
> clear it: the residual is a floating scan flap at one location (<point count> of <total> points
> over band). Delivery needs a recorded human acceptance." (modelled on the dreame README
> artefact list — read it for the real numbers)
