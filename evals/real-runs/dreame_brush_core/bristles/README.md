# Add-on: brush core + fitted bristle envelope (ONE solid)

Owner request (2026-10-01): "to know what max volume occupied I need to also add the brush wires as single body only fitted".
The verified core (`build/`, `qa/`, verdict BAND_NOT_MET accepted) is unchanged; this add-on is built on top of it.

## Files (`out/`)
| File | What |
|---|---|
| `dreame_brush_core_with_bristles_datum.step` | core + bristle envelope fused, ONE valid closed solid, datum frame |
| `dreame_brush_core_with_bristles.step` | same solid in the original scan frame |
| `dreame_brush_core_with_bristles_cad.stl` | mesh of the same (scan frame) |
| `bristle_envelope_only_datum.step` | helper: the envelope alone (2 solids, one per tuft row) |
| `volumes.json` | volumes (numbers below are copied from it) |

## Volumes (mm³, from `out/volumes.json`)
| | mm³ |
|---|---|
| core (verified part) | 28 732 |
| bristle envelope (total − core; includes the filled tuft holes) | 17 416 |
| **core + bristles, one body** | **46 148** |
| space swept while rotating about the axis (Σ π r_max(z)² dz) | 169 967 |

Max bristle radius 19.30 mm, overall length 169.75 mm.

## How it was fitted
Bristle scan points (outside the core, datum frame) per tuft row, in the untwisted frame of the core twist:
cross-section (r, Δθ) and axial start/end ramps (r, z) from the 0.2 / 99.8 % percentiles per 1 mm radius bin
(`b03_envelope_polys.py` → `bristle_envelope.json`); each row = that section extruded with the core twist and trimmed
by its revolved ramp profile; tuft holes filled as bristle roots; fused with the core (`model_bristles.py`).

## Independent check (`qa/BRISTLE_CHECK.md`, separate agent, own code)
Verdict **PASS** on the declared soft band ±3 mm. See the check for containment (all bristle points inside or within
3 mm; points outside are single filament tips) and for how conservative the envelope is (over-fill distances).

## Limits
Free-state, splayed bristles from a decimated scan → inspection only. Not a plastic volume, not the loaded/worn bristle
shape. Reproduce: `python3 addons/bristles/model_bristles.py --params measure/params.json --envelope
addons/bristles/bristle_envelope.json --alignment intake/alignment.json --out addons/bristles/out --scripts
<skills>/stl-re-rebuild-build123d/scripts` (from the run root; re-run 2026-10-01: identical volume).


## Tufted model ("topak topak", owner request 2026-10-01)
`out_tufts/dreame_brush_core_with_tufts_datum.step` (datum frame) and `out_tufts/dreame_brush_core_with_tufts.step`
(scan frame): the same core with **54 individual tufts** fused into ONE valid solid (`model_tufts.py`).
Each tuft: a cone from its Ø2.0 hole to a tip radius 1.68 mm (measured p10..p90 tuft half-width near
the tips), leaning +Z by 0.575 mm and along the arc by 0.075 mm per mm of radius, with a dome whose
top reaches that tuft's own tip radius (16.71..19.26 mm, from the fitted envelope, so the row-end tufts are shorter).

| | mm³ (`out_tufts/volumes.json`) |
|---|---|
| core | 28 732 |
| tufts (incl. hole fills) | 4 547 |
| **core + tufts, one body** | **33 279** |

This is the **appearance** model: the scanned bristles are splayed fans that fill the gaps between tufts, so
for "maximum volume occupied" use the envelope body above (`out/`), not this one.
Builder self-check (not independent QA, `qa_tufts/selfcheck_tufts.json`): 34 % of the scan bristle points
inside the tufts, 86 % within 1 mm, 99.4 % within 3 mm; the tuft surfaces lie p50/p95
0.47/1.33 mm from a real bristle. Lean is an aesthetic fit (the two rows' fits disagree,
`tufts_spec.json#lean_note`). Render: `render/render_tufts.png`.
