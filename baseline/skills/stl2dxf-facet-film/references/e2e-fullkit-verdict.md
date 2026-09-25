# VERDICT — full_kit.dxf independent review (2026-08-27)

**PASS_WITH_FINDINGS.** Reviewer: skeptical pass; independent scripts in `work_verdict/`
(`verify.py`, `links_check.py` — own chaining/PCA/area code, not reused from `work_diff/`).

## What I independently reproduced (all consistent with DIFF_REPORT + REPORT)

- `validate_kit(full_kit.dxf, expect_pieces=77)` re-run: **ok:true**, 79 loops (77 outer + 2
  inner), min_seg 0.0605, min_gap 0.370 (single tight pair = crystal-in-bezel nest, ≥0.35
  gate), real extents [0,0]–[118.07,83.14], $INSUNITS=4, 11 narrow-feature reports.
- sha256 `0803da5c…` matches REPORT. Manifest: 77 pieces, 8 regularisations logged (crystal
  −0.14% + 7 fillet micro-seg fixes) — honest disclosure.
- Matched pairs re-measured (ours vs RV02, my own numbers): BEZ_TOP Ø38.800/30.000 vs
  Ø38.800/30.000 exact; CRYSTAL Ø29.260 vs 29.300 (−0.27% A); CASEBACK Ø27.470 vs 26.538
  (**+7.1% A**); LINK_C ×10 A 63.86 vs 63.87; PUSHER_RECT ×2 A 21.42 vs 21.42; LINK_O rows:
  43.78 vs 33.85 (**+29%**), 31.56 vs 29.30 (+7.7%), 28.17 vs 26.02 (+8.3%), 24.34 vs 23.85
  (+2.1%); FLANK_9 A 252.7 vs 244.0 (+3.6%, PCA width 7.81 vs 7.14). DIFF_REPORT's claims
  are accurate — including its own FAIL-as-strict-regression verdict.
- PNGs inspected: full_kit.png — 77 labelled pieces, crystal concentric in bezel bore with
  visible clearance ring, mirror pairs adjacent, no overlaps. side_by_side.png — matched
  classes correspond across sheets; grey clusters are the lug/clasp re-partition as described.

## Findings

1. **MAJOR — contract regression not met (adjudication required, not silently mergeable).**
   `dxf-contract.md` fixtures: 67 pieces, areas ±5%. Delivered: 77 pieces, 13/48 matched
   pairs outside ±5%, 19 RV02 shapes with no counterpart, net area 4442.8 vs ≈4114 (+8%).
   Dominated by deliberate re-partition (lug tops → SIDE/INNER/UNDER, crown free-forms →
   CROWN_FLANK/GUARD_A). Fix: maintainer sign-off on the new partition as the intended
   facet-film evolution, or rebuild affected families to RV02 patches.
2. **MAJOR — CASEBACK Ø27.47 vs accepted Ø26.54 (+0.93 mm, +7.1% area).** Independently
   confirmed; a badly-sized disc, not a partition choice. Fix: re-fit from the caseback
   facet or adopt 26.54 unless the scan justifies 27.47.
3. **MAJOR — HORN coverage 2.5–3× smaller than RV02** (A 7.5–10.1 vs 25.3; ours trace only
   the outer-flank facet). RV02's horns were defective (open 0.715 mm) so intent is unclear —
   physical-fit adjudication needed; validator itself flags horns as delicate (~1.6–2.1 mm).
4. **MODERATE — outer-link row 1 length 9.0 vs 7.5 mm (+29%)**, rows 2–3 idealised to
   rectangles (+7.7/+8.3%). Confirmed exactly. Fix: adjudicate measured-vs-idealised.
5. **MINOR — CLASP_SLIVER ×4 RECONSTRUCTED/UNLOCATED**, A 7.74 vs RV02 6.36 (+21.7%);
   GUARD_A iso-strain FAILED-in-source carried through. Flagged in manifest but count
   against confidence for those 6 pieces.
6. **MINOR — link pitch 10.05–10.18 vs fixture 11.0** (my measurement); layout fixture only.
7. **INFO — CRYSTAL 29.26 vs fixture 29.30**: disclosed regularisation with sound rationale
   (polygonised bore vs 0.35 clearance gate); achieved nest gap 0.370.

**Bottom line:** internally valid, honestly reported, deterministic kit; core geometry
(bezel/crystal/links/pushers/flanks) reproduces RV02 tightly. It is **not** a passing
regression against the accepted RV02 contract — findings 1–4 need maintainer adjudication
before this DXF is treated as manufacturing-ready.
