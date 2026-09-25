# DIFF REPORT — full_kit.dxf vs WatchCareES_Template_2_DXF_RV02.dxf

Date: 2026-08-27. Method: both files chained to closed loops (ours 0.01 mm; RV02 0.06 mm —
its flank corners mismatch 0.052 mm — plus **4 OPEN horn chains force-closed** across their
0.715 mm gaps for comparison). Position-independent shape matching: loops centred at
centroid, PCA dims, minimised Hausdorff over full rotation sweep + mirror; 1:1 greedy
assignment accepted at H ≤ 0.75 mm and |ΔA| ≤ 12 %. Labels from `WATCH_TPU` XDATA.
Artifacts: `work_diff/compare_kits.py`, `work_diff/diff_data.json`, `work_diff/side_by_side.png`.

## Headline

| | RV02 | ours |
|---|---|---|
| pieces | 67 (63 closed + 4 forced-closed horns) | 77 |
| holes | 1 (bezel bore Ø30, ΔH 0.007) | 2 (bezel bore Ø30 + CROWN_FLANK crown cut-out 5.6 × 5.8, no RV02 counterpart) |
| net cut area | 4215.4 mm² | 4442.8 mm² (+5.4 %, extra coverage) |
| sheet | 123.1 × 85.2 mm | 118.1 × 83.1 mm |
| matched 1:1 | — | 48 pairs; 35/48 within ±5 % area |

## 1. Per-shape-class table (matched pairs; Δ = ours − RV02)

| class | matched/ours | ΔA% mean | ΔA% worst | ΔL / ΔW worst (mm) | Hausdorff mean/max (mm) |
|---|---|---|---|---|---|
| BEZ_TOP (annulus Ø38.8/30.0) | 1/1 | +0.00 | +0.00 | 0.00 / 0.00 | 0.007 |
| CRYSTAL (Ø29.26 vs Ø29.30) | 1/1 | −0.27 | −0.27 | −0.04 | 0.021 |
| CASEBACK | 1/1 | **+7.15** | +7.15 | +0.93 (Ø27.47 vs 26.54) | 0.466 |
| PUSHER_RECT | 2/2 | −0.03 | −0.03 | 0.00 | 0.012/0.020 |
| LINK_C (centre links) | 10/10 | −0.01 | −0.01 | 0.00 | 0.015 |
| LINK_O (outer links) | 15/20 | +3.85 | **+8.24** | −0.62 W | 0.18/0.32 |
| FLANK (9-side + 2 crown-side) | 3/3 | −1.88 | −4.57 | −0.93 L | 0.59/0.69 |
| GUARD_B | 2/2 | −2.37 | −2.37 | −0.13 | 0.35 |
| LUG_END | 2/2 | +3.44 | +3.53 | −0.64 | 0.14 |
| LUG_UNDER | 4/4 | +2.25 | **+10.15** | +0.23 | 0.22/0.27 |
| CLASP_COVER / TONGUE | 2/2 | +1.3 | +1.5 | −0.21 | 0.03–0.45 |
| CLASP_SIDE | 2/2 | +5.04 | **+6.36** | +0.48 | 0.33/0.36 |
| CLASP_PAD / RECT1 / RECT2 | 3/6 | +1.9 | +8.90 | −0.34 | 0.17–0.21 |

13/48 matched pairs exceed ±5 % area: CASEBACK (+7.2 %), LINK_O rows 2–3 (+7.7/+8.2 % —
ours idealised to full rectangles, RV02 kept the taper; one −6.8 % cross-row pairing),
LUG_UNDER (+10.2/−6.2 %), CLASP_SIDE_6C (+6.4 %), CLASP_RECT1_6B (+8.9 %), LUG_UNDER_6C (+5.2 %).
Caveat: in the 23–34 mm² rounded-rect zone (outer links vs clasp rects) several RV02 shapes are
near-identical, so individual pairings there are partly interchangeable; class means are reliable.

## 2. Unmatched pieces

**RV02-only (19):**
- 4× lug-top strips 13.9 × 5.0 bbox (A 31.55) — our kit partitions each lug into
  LUG_SIDE + LUG_INNER (+ LUG_UNDER) instead of one top strip. Different partition, not a miss.
- 4× horns (forced-closed; A 25.3, 13.2 × 4.0) — our HORN pieces exist but are much smaller
  (7.5–10.0 × 1.4–2.1, A 7.5–10.1): ours trace only the narrow lug outer-flank facet; RV02's
  rushed RV01 horns wrap a larger region (and were open + 0.73 mm tip). **Largest geometric
  divergence in the kit — needs maintainer adjudication.**
- 3× outer-link row 1 (7.5 × 4.88, A 33.85) — our row-1 links are 9.0 × 4.88 (A 43.8, +29 %):
  we kept the measured longer end-link; RV02 idealised all rows to 7.5 mm length. (4th row-1
  absorbed a cross-match.)
- 4× free-form ~8.0 × 5.45 (A 30.4–30.7) — closest ours family is LUG_INNER (A 21–26, −16 %):
  same facets, different idealisation/coverage.
- 2× curved strips 9.66 × 4.29 (A 22.04) — same area as our CLASP_CRESC (22.5/23.5) but
  different outline: clasp crescents redrawn differently.
- 1× spline free-form 8.3 × 5.7 (A 28.5, crown region) + 1× 4.84 × 2.8 (A 13.4) — crown-guard
  area we cover with CROWN_FLANK (A 58.1) + GUARD_A ×2 (A 23.5) instead.

**Ours-only (29):** 4× CLASP_SLIVER (bbox 3.68 × 2.17 identical to RV02's smallest piece, but
A 7.74 vs 6.36, +21.7 % — ours fuller/straighter; the matcher paired RV02's 4 curved slivers
with our LUG_UNDER instead, identity ambiguous), 4× HORN (see above), 4× LUG_SIDE, 4×
LUG_INNER (2 unpaired), 4× LINK_O row 1 (longer), GUARD_A ×2, CROWN_FLANK, CLASP_CRESC ×2,
CLASP_PAD_6C (−30 % vs RV02's), CLASP_RECT1_6C/RECT2_6B, LINK_O_12B_3.

## 3. Verdict vs the contract regression gate

**FAIL as a strict shape-for-shape regression** (`dxf-contract.md`: counts exact, areas ±5 %):
piece count 77 ≠ 67; 13/48 matched areas outside ±5 %; 19 RV02 shapes have no direct
counterpart. **The failure is dominated by a deliberate re-partition** of the lug and clasp
regions (one-piece-per-facet vs RV02's larger idealised patches) plus three real dimensional
deviations to adjudicate: **CASEBACK Ø27.47 vs Ø26.54 (+7.2 %)**, **outer-link row 1 length
9.0 vs 7.5 mm (+29 %)**, **rows 2–3 rectangle-vs-taper (+8 %)**. The core kit — bezel,
crystal, caseback nest, all 10 centre links, pushers, flank set, lug ends, clasp cover/tongue
— reproduces RV02 at Hausdorff ≤ 0.7 mm with 35/48 areas within ±5 %.

RV02's own recorded defects that our kit intentionally fixes (not regressions): 4 open horn
chains (0.715 mm) and 0.052 mm flank corner gaps → all our 79 loops closed at 0.01 mm;
micro-segments (min seg 0.061 vs RV02's 0.013 mm arcs); 8 POINT entities on cut layers → none;
no labels (67 pieces by shape only) → TEXT + XDATA ids; bogus $EXTMIN/EXTMAX → real extents;
R0.4 fillets retained.

## 4. Visual

Visual: side_by_side.png (kept outside git at C:/spk/fullkit/work_diff/side_by_side.png; also embedded in the Facet Sheet Walkthrough artifact)
RV02 left, ours right; colour = matched shape class, grey bold = unmatched. Inspected: matched
families sit coherently on both sheets; RV02's grey top-left cluster (lug tops + horns + lug
free-forms) mirrors our grey lug/clasp band — the partition difference, not matcher noise.
