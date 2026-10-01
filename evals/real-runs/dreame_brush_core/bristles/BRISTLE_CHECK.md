# BRISTLE_CHECK — dreame_brush_core + fitted bristle envelope

Independent QA of the soft-feature addition (bristle envelope fused to the verified core). All numbers are read from
`addons/bristles/qa/bristle_check.json` (written by `qa_report.py` from the step JSONs of `qa_step1_validity.py`, `qa_step1b_booleans.py`,
`qa_step2_scan.py`, `qa_step3_exact.py`, `qa_step4_farpoints.py`, `qa_step5_winding.py`, tessellation `qa_tess.py`; step JSONs in
`addons/bristles/qa/steps/`; own code, seeds in the JSON). Builder files
`addons/bristles/bristle_envelope.json`, `addons/bristles/*.py` and `measure/` were not used as expectations.
Scan sha256 `4be5e49d2ab6e2a930a41aa017551eac8f08b1974ddfd1294b1b1455961f011a` (matches `input/INPUT_HASHES.json`).

## Verdict: **PASS** (soft band ±3 mm)

**100.00 %** of the bristle scan points are inside the combined solid or within 3 mm of it
(refined set r > land radius: 100.00 %); max outside distance **1.71 mm**. Rule: ≥ 99 % inside or within 3 mm.

This is a **fitted max-occupancy envelope of splayed, free-state bristles** (two twisted fins from the 0.2/99.8 % percentiles of the
scan's bristle points + filled tuft holes) measured on a **decimated scan — inspection only**. It is not a moulded/solid-plastic
volume, not the bristles' loaded or worn shape, and not a dimensional gate. The rigid-core verdict stays as in `qa/VERDICT.md`
(BAND_NOT_MET, owner-accepted); this check does not change it.

## 1. Validity
| File | solids | shells | closed | BRepCheck valid | volume mm³ | bbox min → max (mm) |
|---|---|---|---|---|---|---|
| `addons/bristles/out/dreame_brush_core_with_bristles_datum.step` | 1 | 1 | True | True | 46147.634 | (-18.89, -19.30, -6.47) → (19.30, 18.89, 163.28) |
| `addons/bristles/out/dreame_brush_core_with_bristles.step` | 1 | 1 | True | True | 46147.634 | (-26.05, -64.32, -253.82) → (16.29, 49.27, -99.19) |
| `build/dreame_brush_core_datum.step` | 1 | 1 | True | True | 28731.545 | (-16.44, -16.44, -6.47) → (16.44, 16.44, 163.28) |
| `addons/bristles/out/bristle_envelope_only_datum.step` | 2 | 2 | True | True | 17540.795 | (-18.89, -19.30, 2.29) → (19.30, 18.89, 144.99) |

- Frames: datum STEP moved by inverse(`matrix_4x4`) vs scan-frame STEP: volume rel. diff 4.7e-16,
  bbox max |diff| 3.6e-11 mm → agree.
- Core containment (OCC booleans, datum frame): **core − combined = 0.0000 mm³**;
  combined − core = 17416.09 mm³ (builder `volumes.json` bristle_envelope_mm3 17416.08);
  envelope-only − combined = -4.6e-12 mm³.
- `bristle_envelope_only_datum.step` is 2 solids / 2 shells
  (one per row) — a helper file, not a single body; the deliverable bodies are single solids.

## 2. Containment of the scan bristles (max-occupancy purpose)
Raw scan × `matrix_4x4`, 2,000,000 seeded area samples + 210,548 vertices
(mean spacing 0.098 mm). Bristle points = signed distance to the core STEP > 0.15 mm
(1,115,697), minus table remnants z < −3 & r > 16.5 (97,772)
→ **1,017,925 points**. Signed distance: KD tree over 0.044 mm-spaced CAD surface samples;
cross-checked exactly with the OCC classifier on 2000 random points (agreement 99.95 %)
and with BRepExtrema on 400 outside points (all confirmed outside, |KD − exact| p95 0.008 mm).

| Set | n | inside | ≤ 0.25 mm | ≤ 0.5 mm | ≤ 1 mm | ≤ 3 mm | outside p50 / p95 / p99 / max (mm) |
|---|---|---|---|---|---|---|---|
| all bristle points | 1,017,925 | 92.30 % | 97.26 % | 99.64 % | 99.98 % | 100.00 % | 0.21 / 0.49 / 0.73 / 1.71 |
| refined: r > 7.565 (land r 7.465 + 0.1) | 970,195 | 96.73 % | 99.10 % | 99.76 % | 99.98 % | 100.00 % | 0.18 / 0.57 / 0.93 / 1.71 |

Where the outside points are (27,844 points > 0.25 mm outside):
- **19,152 at r ≤ 7.565** — inside the land circle: slot occupants (lodged debris, DECISIONS 2026-10-01) and
  the core's own scan residuals (the core is BAND_NOT_MET); not bristles, and the envelope is not meant to hold them.
- 1,702 at the hub (z < 2.3) and 786 at the idler end (z > 145): core-surface residuals beyond the rows.
- **6,204 in the bristle rows** (z 2.3..145, r > 7.565): mostly sub-mm, at the fin flanks and tips.
- Beyond 1 mm: only **222 points**, in 12 small clusters (largest 79 points, extent ≤
  1.11 mm), all at r 18.9..20.7 mm
  within 11° of a row (one isolated point at r 7.52).
  z: 8..16 mm: 7, 24..32 mm: 2, 32..40 mm: 22, 40..48 mm: 36, 48..56 mm: 118, 120..128 mm: 37. → **stray single filament tips past the 99.8 % fit percentile**, not a
  systematic under-fit (no z slab or angle sector is consistently missed; envelope r_max 19.30 mm vs scan
  bristle r p99.8 19.16 / max 20.71 mm).
- Per 10 mm z-slab every slab is 100 % within 3 mm; the low "inside" fractions at z < 10 and z > 130 come mostly from core residuals (r ≤ 7.565, hub, idler end) and the row ends
  (`step2_scan.containment_by_z`).

## 3. Over-fill (how conservative the envelope is)
- Envelope skin (combined surface > 0.025 mm off the core, 9575 mm²) → nearest bristle scan point:
  **p50 1.16 / p95 3.04 / max 5.00 mm**; within 1 mm 41.4 %, within 3 mm 94.7 %.
- Envelope volume (Monte-Carlo, generalized winding number on the tessellations, 8000 seeded points in the r ≤ 19.4 cylinder):
  17863 ± 639 mm³ (boolean 17416 mm³).
  Distance of envelope interior points to the nearest bristle point: **p50 0.55 / p95 2.13 / max 3.51 mm**;
  71 % of the volume is within 1 mm of a scanned bristle, 93 % within 2 mm,
  1.1 % is > 3 mm away.
- Far pockets: of 4,000 seeded candidates ≥ 4 mm from every bristle point, **0 lie inside the envelope**
  (winding number). The OCC solid classifier had reported 15, including points outside the bbox → classifier
  false positives; those results (step3 e, step4) are superseded and kept only for the record.
- Caveat: an optical scan sees only the outer surface of each tuft; tuft interiors are unseen, so "far from a bristle point" is an upper
  bound on empty space. As a max-occupancy body the envelope is conservative by ≈ 1 mm typical (skin p50), ≈ 3 mm at p95, 5 mm at worst.

## 4. Rigid core unchanged
- 1,000,000 seeded core-surface samples vs the combined surface (tol 0.025 mm = 2 × 0.01 mm tessellation):
  90.57 % on the combined surface, 9.20 % covered by the envelope (rows + tuft holes).
- Away from the rows (416,326 samples: z outside the envelope span or > 60° from both rows): 99.84 % within tol by KD;
  the 660 flagged were re-measured exactly: max 0.0036 mm (tessellation artefacts).
- Core points flagged "outside the combined": 2,303; exact check of 600: max distance outside
  0.0036 mm. With core − combined = 0.0000 mm³ the core is contained and unchanged.

## 5. Limitations
- Decimated scan, inspection only; no photos/calipers; bristles scanned in their free, splayed state — the envelope is the occupied space in
  that state, not under load or rotation (builder's swept-rotation figure `volumes.json` swept_rotation_envelope_mm3 was not re-checked).
- By construction (0.2/99.8 % percentiles) a fraction of the outermost filament tips lies outside (max 1.71 mm).
- Signed distances on tessellations (0.01 mm chord) + KD sampling; key numbers cross-checked exactly on the B-reps (step 3, BRepExtrema / classifier near the surface) and by winding numbers (step 5).
  The step-2 KD-sign volume Monte-Carlo and the OCC-classifier far-field results (step 3 e, step 4) are superseded (see `superseded` in the JSON).
