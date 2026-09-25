# VERDICT — OOM-P03 Mop Pad Bracket · Independent QA

**VERDICT: APPROVED** (rebuild iteration 2/3)

Verifier: independent QA (re-derived every number; modeler self-check numbers not trusted).
Date: 2026-07-29 · Tools: build123d/OCP 0.10, trimesh 4.12.2, scipy 1.17 · CAD under test: `4_STEP/OOM-P03.step` (it2, overwritten in place).
All mesh ops on local scratch copies. Bands per `_PIPELINE/RE_SPEC.md` §4 (Tier-1 ≤0.15 mm; Tier-2 p95 ≤1.6, max ≤4.0; non-caliper functional interfaces ≤0.8).
it1 verdict was REVISE (missing central drive stem); this re-verify confirms the fix.

---

## Gate 1 — Solid validity: PASS
- 1 solid, 1 shell, **BRepCheck IsValid = True**. Volume 35535.0 mm³ (positive), 500 faces / 2986 edges.
- BBox X 127.540 / Y 127.540 / Z −3.010…+18.560, **dz 21.570** (= re-derived ENV-Z). Concentric (COM x,y = 0).

## Gate 2 — Tier-1 calipers: PASS (worst |Δ| = 0.00 mm)
Re-measured directly from STEP feature queries (analytic radii, opposite-flat plane distances, cap-plane Z), never echoed.

| ID | Feature | Caliper | CAD re-measure | \|Δ\| | Query | Verdict |
|---|---|---|---|---|---|---|
| ENV-D1 | solid-rim OD | 127.54 | 127.540 | 0.000 | cyl29 r=63.770 | PASS |
| F01 | hex AF | 13.95 | 13.950 | 0.000 | flats at ±6.975 | PASS |
| F03 | hex protrusion | 11.05 | 11.050 | 0.000 | shoulder z+13.90 − floor z+2.85 | PASS |
| F05 | pad boss OD | 33.46 | 33.460 | 0.000 | cyl498 r=16.730 | PASS |
| F06 | hub disc OD | 68.61 | 68.610 | 0.000 | 8× arc cyl r=34.305 | PASS |
| F07 | mid-ring OD | 89.33 | 89.330 | 0.000 | cyl97 r=44.665 | PASS |
| W01 | rim/plate wall | 3.27 | 3.270 | 0.000 | rim z +2.85−(−0.42) | PASS |

All reproduce the caliper authority to <0.005 mm. F03 still governs the hex; the added stem sits above it and does not disturb Tier-1.

## Gate 3 — Tier-2 scan skin: PASS (p95 0.971 / max 2.949)
Fresh independent trimmed KDTree ICP (120k pts, 30 iters), re-converged. 900k raw-scan surface samples → 700k CAD-surface KDTree; normal-based outer-skin mask (scan·CAD-normal > 0.3).

| Bucket | n | p95 | max | Band | Result |
|---|---|---|---|---|---|
| **Outer skin (gated)** | 769 k | **0.971** | **2.949** | p95≤1.6 / max≤4.0 | **PASS** |
| Skin, central axis r<9 | 37 k | 0.882 | 2.949 | — | it1 defect resolved |
| Skin, excl. axis r<9 | 731 k | 0.972 | 2.604 | — | body form clean |
| Interior/occluded (reported) | 131 k | 2.101 | 2.968 | not gated | openings/undercut |

**Zero skin points > 4.0 mm** (was 4907 at r<6.4/z~18 in it1 — the missing stem, now modeled). Points >1.6 mm = 0.26%, scattered (velcro texture, opening edges), not concentrated.
Functional zones (skin): rim OD p95 0.296/max 0.565; pad boss p95 0.241; hex r6–12 p95 0.689; **stem r<7 z>13 p95 0.810 / max 2.424**. Stem-zone max 2.424 is at the photo-inferred square socket the scanner bridged (couldn't see into) — expected intent deviation, correct per §4, not chased.

## Gate 4 — Photo plausibility: PASS
- Topology complete: 8 kidney openings, hex coupling boss (AF 13.96), fine tread (~51), round Ø33.46 pad boss w/ central mold-gate dimple only (F04 solid), **and the central drive stem+socket now present**. No hallucinated features (clean disc bbox, no stray solids).
- **Stem/socket vs profile photos 140345/140347:** the squarish socketed stem standing proud of the hex is now reproduced. Modeled hex AF 10.96 + square socket 5.5 sq × 2.5 deep.

## it1-finding closeout & stem validation
- **it1 Finding 1 (missing stem): FIXED and independently validated.** STEP has a hexagonal stem AF 10.96 (flats r5.48, shoulder z+13.90 → top +18.56), solid top, square drive socket (walls at ±2.75, floor z+16.06 = 2.5 deep). Independent scan check of the stem cross-section: **angular FFT of raw-scan radius(θ) in the stem band is dominant at order 6 (mag 9.41) = hexagonal** (NOT square); scan radius min 5.54 (flats) / max 6.87 (corners) matches hex AF 10.96. Stem fits the scan at p95 0.810. Confirmed correct.
- **it1 Finding 3 (alignment.json): resolved.** My fresh best-fit ICP now sits **0.154° / 0.600 mm** from the refined `alignment_v2.json` (was 1.651 mm at it1) — within tolerance for the doc-overlay render (<1 mm on a 127 mm part).
- ENV-Z overall height 21.570 (STEP) = intake scan ~21.5.

## FINDINGS
1. **[closed]** Central drive stem+socket added, hexagonal AF 10.96, top +18.56 — matches scan (6-fold, radius) and profile photos; resolves the it1 REVISE and clears the Tier-2 max band (0 pts >4 mm).
2. **[note, non-blocking]** Square drive socket (5.5×2.5) is photo-inferred; scanner bridged it, so its scan deviation (stem-zone max 2.424) is expected and correct, not a defect. Depth is a shallow photo-set value — flag for physical confirmation if the coupling interface is ever manufactured to fit.
3. **[note, non-blocking]** `alignment.json` now 0.600 mm off my best-fit; adequate for renders. No action needed.

## DISPOSITION
All four gates pass. **APPROVED.** Cleared for DOCS (renders + RE report). No open blocking items.
