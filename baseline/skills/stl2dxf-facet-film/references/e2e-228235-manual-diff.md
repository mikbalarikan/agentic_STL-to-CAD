# E2E-228235 — the maintainer's manual Day-Date 40 kit, measured, vs our pipeline kit r2

Ground truth for the **second** worked watch. The maintainer's manual kit for the Rolex Day-Date 40 (ref 228235) was delivered as DXF on 2026-08-30 22:50 local. Every number here is measured from a file unless the row says otherwise. Open maintainer questions: `e2e-228235-manual-rulings.md`.

## 0. Provenance and evidence quality

Record root (maintainer's personal drive, **not** committed): `H:\My Drive\111 UP UP UP\Watch David STL to CAD\STL TO DXF SESSION record 2 228235.stl\` (the trailing `.stl` is part of the folder name). Files: `228235STL Converted.dxf` (284 KB, 08-30 22:50) = the delivered kit; `Watch_STL_to_DXF_RV7.log` = the UGTODXF export log; `Watch_STL_to_DXF_RV7.prt` (167 KB, 22:49) = the curves-only 2D part it came from; `Watch_STL_to_DXF_RV2…RV6.prt` (102 MB each, 18:42→22:45); `ugstep214.log` (the RV3/RV5 save stamps). Capture sessions: **`9d37b4e756ee`** — 1 765 events, 08-30 15:07:25–15:41:28 UTC (local = UTC+3), flattening + layout; **`0f041089bd6f`** — 459 events, 15:42:07–18:32:22 UTC, the 2D sketch stage. Ours = `daydate_kit_r2.dxf` (E2E-228235, 52 pieces, PASS_WITH_FINDINGS).

**Evidence-quality caveat — read before citing any 2D-stage claim.** Captures end 08-30 18:32 UTC (21:32 local); **RV3→RV7 and the export are uncaptured**, so the idealisation pass (spline → line/arc), the fillet pass, the replication of the link representatives and the export itself are inference from the part files + the export log, not from events. The **margin session is untraced**: the Offset-in-Face/Divide-Face features already exist at session 9d37's first snapshot, and the session that built and debugged them lies between 08-19 and 08-30 and is not in the record.

**Diff method.** Both DXFs chained to closed loops with an arc-aware chainer at 0.06 mm endpoint tolerance (LINE/ARC/CIRCLE kept as exact primitives, LWPOLYLINE bulges converted to true arcs; areas = shoelace + exact circular-segment corrections). Matching is position-independent (resample 0.05 mm, both mirrors, 360° sweep, coordinate descent) on **symmetric Hausdorff**, assigned 1:1 by Hungarian, class-constrained. Accept at **H ≤ 0.75 mm AND |ΔA| ≤ 12 %**; near-miss to H ≤ 1.5 mm.

## 1. Headline

| | manual | ours (r2) |
|---|---|---|
| entities | 195 LINE + 261 ARC + 6 CIRCLE, layer `1`, no labels | 55 LWPOLYLINE + 52 TEXT |
| closed loops (> 0.5 mm²) / open chains @ 0.06 mm | **61** / 0 | 55 / 0 |
| holes | 3 (bezel bore, caseback-rim bore, cyclops) | 3 (same three) |
| **pieces** | **58** (61 − 3 holes; 59 counting the 1.000 mm scrap band) | **52** |
| arcs | **273** — R 0.300 ×206, R 0.321 ×4, R 0.400 ×3, R 1.349 ×4 | **0** — 8 237 chords, 0 non-zero bulges, min segment 0.0801 mm |
| sum of loop areas | 5 418.24 mm² | 6 253.75 mm² |
| **net film area** | **3 180.61 mm²** (3 271.25 incl. scrap band) | **3 850.10 mm²** (+21.0 %) |
| sheet extents | **62.97 × 160.01 mm** (x −28.440…34.525, y −59.618…100.391) | 114.55 × 81.89 mm |
| min inter-piece gap | **1.497 mm** (loops #1/#60) | 1.300 mm |
| matched 1:1 | — | 6 accepted, 34 near-miss, 6 rejected |

Count decomposition (manual − ours = **+6**): bracelet **+14** (manual 44 pieces = 7 links per run; ours 30 = 5), our 7 `maintainer-confirmed-extra` pieces **−7**, our crown-side flank split in two against the manual's one **−1**. Case coverage is otherwise identical: 4 discs/annuli, 4 lug-top, 4 lug-under, 1 nine-side flank.

## 2. Per-class match

| class | manual n | ours n | matched | median H mm | median ΔA % | worst ΔA % |
|---|---|---|---|---|---|---|
| disc/annulus | 5 | 4 | 3 | 0.046 | +0.51 | +4.87 |
| flank | 2 | 3 | 2 | 0.512 | +1.16 | +2.39 |
| lug_top | 4 | 4 | 1 | 0.746 | +3.93 | +3.93 |
| lug_under | 4 | 4 | 0 | — | — | — |
| link_centre / link_side | 14 / 28 | 10 / 20 | 0 / 0 | — | — | — |
| lug_wall+inner / crown+clasp (ours only) | 0 / 0 | 4 / 3 | 0 / 0 | — | — | — |
| other (manual only) | 2 | 0 | 0 | — | — | — |
| **total** | **59** | **52** | **6** | 0.225 | +1.45 | |

(manual n counts `M55`, the 1.000 mm scrap band, under disc/annulus.)

## 3. Ruling evidence R1–R6

Loop ids `#N` are the chainer's indices in the manual DXF; piece id `M<NN>` = the loop that is its outer boundary. **All arc centres below are in the manual DXF's own sheet frame.**

**R1 — caseback rim is a real piece, not an extra.** Outer loop **#58** CIRCLE r **13.9250** (Ø27.8500); inner loop **#57** r **11.0000** (Ø22.0000); both centred exactly on (16.7754, 46.9435), centre-to-centre spread **0.000000 mm**; ring width **2.9250**, area **229.040 mm²**. Ours (CASEBACK_RIM) Ø28.181/Ø22.099, 240.18 mm² (**+4.87 %**), **H 0.168 — ACCEPT**. The record built the ring (Revolve/Through Curves) and flattened it (flat 230.80 mm², OD 27.86 / ID 22.0). CASEBACK_RIM was recorded as "no ground truth" / `maintainer-confirmed-extra`: **refuted**.

**R2 — bezel, our worst case-piece miss, and the seam sign flips.**

| | manual | ours (BEZEL) | Δ |
|---|---|---|---|
| outer | loop **#59** r **17.7500** (Ø35.5000) | r 19.1815 (Ø38.3630) | **+2.8630 mm dia (+1.4315 radial, onto the fluting)** |
| inner | loop **#55** r **14.9250** (Ø29.8500) | r 15.7495 (typed Ø31.5) | +1.6490 mm dia |
| centres | (16.7754, 46.9435), spread 0.000000 | concentric | — |
| width / area | **2.8250** / **289.991 mm²** | 3.4320 / 376.63 (**+29.88 %**) | **H 1.432 — REJECT** |

Manual bezel bore r 14.9250 vs manual crystal r 15.3620: the bore lies **0.4370 mm radially INSIDE the crystal edge**, so the two films **overlap** over 41.580 mm². Ours does the opposite — bore r 15.7495 vs crystal r 15.3995 = a **0.3500 mm radial GAP** (our validator's "CRYSTAL-in-BEZEL clearance 0.35"). On the caseback seam both agree in sign: manual centre disc r 10.7240 vs rim bore r 11.0000 = 0.2760 mm gap; ours 10.7495 vs 11.0495 = 0.3000 mm. **Nesting:** the manual nests the rim annulus inside the bezel bore at **1.000 mm** radial clearance (#55 r 14.9250 → #58 r 13.9250). Record: the ring was flattened from a full 360° `Revolve(155)` — flat 35.712 × 35.711, 294.944 mm², 2 wires — so the 2D redraw took ≈0.21 mm off the outer diameter.

**R3 — crown-side flank: ONE piece, not a C, at effectively zero crown clearance.** Manual loop **#2**: **88.909 mm²**, min-rot-rect **22.745 × 5.249**, axis-aligned bbox 22.331 × 6.454, **10 ARC + 3 LINE**. Against our FLANK_3C_12: **H 0.743 (mirrored), ΔA −0.08 % — ACCEPT**; our FLANK_3C_6 (94.96 mm², 23.828 × 5.434) has **no manual counterpart** (H 1.006; it is a near-mirror of our own _12 at H 0.450). The piece terminates at the crown with an arc **R 2.8950 about (11.7344, −18.4669)** — the crown axis — sweep −75.48°, arc length 3.8138 mm, chord 3.545 mm, blended in with two R 0.3000 fillets about their own corner centres. Recorded crown-body r99 = **2.925**, so the notch sits **0.030 mm inside the crown radius = effectively zero clearance**, against our R 3.71 about the mapped crown centre (**+0.815 mm larger in radius**). The severed-part-plus-clearance-arc topology is the one our F-21 chose: **F-21 corroborated by ground truth.** For contrast the 9-side flank matches cleanly: manual loop **#1** 204.158 mm², 48.687 × 6.705, 10 ARC + 1 LINE with a 27.054 mm straight, vs our FLANK_9 209.04 — **H 0.281, ΔA +2.39 %**.

**R4 — cyclops = a hole in the crystal disc, tangent-fillet outline (CLOSED).** Manual loop **#54**, parent **#60** (the crystal circle): **38.873 mm²**, min-rot-rect **7.3530 × 6.0949**, **6 ARC + 2 LINE** — **R 1.3490 ×4** about the four corner centres of the lens outline + **R 3.6910 ×2** about the two flank-arc centres, straights 3.201 / 3.191; min/max radius from its own centroid 3.0467 / 3.6822; centroid (10.5347, −38.1491); **offset from the crystal centre (+10.0729, −0.1482), |d| = 10.0740 mm**. Ours 38.96 mm² (**+0.23 %**), 7.383 × 6.100, offset (+10.08, −0.15). The 3D flat carried the hole too (body53, 703.92 mm², 2 wires). **F-16 confirmed.**

**R5 — bracelet links are pure rounded rectangles at half our wrap.** Manual centre link loop #0, exactly (every arc centre given):

```
ARC R 0.3000 c=(-13.5637, 19.6041) sweep 90.00 deg   LINE 7.1930
ARC R 0.3000 c=(-20.7567, 19.6041) sweep 90.00 deg   LINE 3.4467
ARC R 0.3000 c=(-20.7567, 16.1574) sweep 90.00 deg   LINE 7.1930
ARC R 0.3000 c=(-13.5637, 16.1574) sweep 90.00 deg   LINE 3.4467
                                  -> axis-aligned bbox 7.7930 x 4.0467
```

No large arc appears anywhere on a link: **R 2.8787 never shows up as a 2D radius**, only through the developed width.

| family | manual | ours | Δ |
|---|---|---|---|
| centre link (rows 2–14) | **13 identical**, 7.7930 × 4.0467, **A 31.459**, R 0.3 ×4 | LINK_C ×10, 8.400 × 7.544, A 63.23 (×6) | **A +101 %, H 1.759** |
| centre link, case end | **1** (#47) 7.7936 × 3.4309, A 24.331, one edge R 21.352 | 8.400 × 5.25, A 44.0 | +80.8 %, H 1.175 |
| side link | **28** (14/run × 2), **L 5.2950 constant**, **W 4.896 → 3.197** in ≈0.23 mm steps then 3.197 ×4 | LINK_S ×20, L 6.252–8.007, W 5.400 → 3.600 in 0.30 steps | +39…+72 % |
| side link, end rows | #45/#49 4.896 × 3.696 (18.02); #46/#50 5.457 × 2.753 (11.21, edges R 36.4/R 93.7) | — | unmatched |
| tabs | #4/#15 4.046 × 2.938 (8.885), R 0.3 + R 11.676 | — | unmatched |
| rows per run | **14** (7 links/side) | 10 (5 links/side) | +14 pieces |
| sheet row pitch | **7.9933 mm** uniform (first two intervals 6.489/6.511 at the case end); column x-spacing 7.95/8.02 | — | **layout only** — the piece is 4.047 tall, so the gap is 3.947 mm |
| bracelet film | **995.21 mm² over 44 pieces** | 1 235.76 over 30 | +24.2 % |

**Developed wrap on R 2.8787**: manual centre 4.047 → **80.55°**, widest manual side 4.896 → 97.45°, narrowest 3.197 → 63.63°; ours LINK_C 7.544 → **150.15°**, LINK_S 5.400 → 107.48°. The manual covers **roughly half** the arc we do on the centre links. **End inset:** manual centre link 7.7930 along the bracelet vs ours 8.4000 = **0.6070 = 2 × 0.3035**, exactly one **0.30 mm end inset per end** — so our centre links lost or double-counted it. Skill claims tested: **"4.7" CONFIRMED** as the side-link straight edge (4.6945/4.6964 on all 24 mid-rows, bbox L 5.295); **"5.1" not found** (the end rows are 4.896 and 5.457); **"pitch 6.8" matches neither** the sheet pitch 7.9933 nor the measured physical pitch 6.12 ± 0.10 (E2E-228235 F-03).

**R6 — crystal and caseback centre.** Manual crystal loop **#60** CIRCLE r **15.3620** (**Ø30.7240**), centre (0.4618, −38.0009), disc 741.388 mm², **net minus cyclops 702.515 mm²**; ours Ø30.7990, net 706.08 — **H 0.046, ΔA +0.51 % — ACCEPT**. Typed 3D construction value p0 = 30.8 and the 3D flat measured Ø30.91 (body53, 30.913 × 30.909), so the **0.08 mm step happened in the uncaptured 2D redraw**, inside cut tolerance. Manual caseback centre loop **#56** r **10.7240** (**Ø21.4480**), A 361.296 mm²; ours Ø21.4990 — **H 0.036, ΔA +0.48 % — ACCEPT**; typed 3D p86 = 21.5; 3D flat body49 361.961 mm², 21.576 × 21.579.

## 4. Corner-fillet census — all 273 arcs inside manual loops

| radius | count | where | mean sweep |
|---|---|---|---|
| **R 0.3000** | **206** | every link, both lug families, both flank pieces, the small tabs | 90.4° |
| R 0.3210 | 4 | one per lug-under piece (#35–#38) | 175.3° |
| **R 0.4000** | **3** | flank #1 ×2, flank #2 ×1 — **nowhere else** | 130.5° |
| R 1.3490 | 4 | cyclops corners (#54) | 43.5° |
| ≥ 2 mm | 56 | outline curvature + the R 2.8950 crown notch + the 6 case circles | — |

**R 0.3 is the rule on this watch: 206 of 217 sub-2 mm arcs (95 %).** R 0.4 appears 3 times, only on the two case-flank pieces.

## 5. Lug families — one template, cut four times

| | manual | ours |
|---|---|---|
| lug-top | **4 identical** loops #34/#51/#52/#53, **15.0145 × 4.5903, A 35.149–35.150** (spread 0.001 mm²), fill 0.510, R 0.3 only | 4 different: 34.12/35.28/35.41/36.53, L 14.704–15.240, W 3.743–3.885; H 0.746/0.839/0.875/0.943, ΔA −2.94…+3.93 % — **2 of 4 miss the H gate** |
| lug-under | **4 identical** loops #35–#38, **17.1633 × 4.3242, A 42.225**, fill 0.569, R 0.3 + R 0.321 | 4 different: 49.87/50.14/51.61/52.60; H 0.603–0.720 (all pass) but **ΔA +18.10…+24.56 % — all fail the 12 % gate** |
| lug outer wall / "horn" | **none** — the lug outer wall is an end of the flank sheet, never its own piece | none either (LUG_FLANK ×4 retracted mid-run, F-11) |
| lug inner / end wall | **none** | LUGWALL_12 + LUG_INNER ×3 — no counterpart |

**The manual idealises repeated families to one template; we build each instance from its own mesh** — 4 identical lug-tops, 4 identical lug-unders, 13 identical centre links, 4 identical narrowest side links. Our F-13/F-20 "side-aware constants, never mirror" is a deliberate departure, but it is what turns one lug-under delta into four separate 18–25 % misses.

## 6. Unmatched, compressed

**Manual, no accepted partner (52).** M59 bezel ring 289.99 (best BEZEL H 1.432); **M55 = the 1.000 mm scrap band** between the bezel bore and the rim outer, a 1.0 × 93 mm sliver, not a handleable part; M35–M38 lug-unders ×4 (42.23); M51/M52/M53 lug-tops ×3 (35.15); centre links 7.793 × 4.047 ×13 (31.46) + end centre link M47 (24.33); side links by area — M39/M40 25.84, M42/M44 25.03, M31/M33 23.81, M18/M20 22.59, M19/M21 21.37, M22/M30 20.15, M17/M23 18.93, M45/M49 18.02, M25/M29 17.71, M03/M05/M08/M10/M11/M13/M14/M16 ×8 16.85, M46/M50 11.21 (the curved slivers); tabs M04/M15 ×2 (8.885).

**Ours, no accepted partner (46).** BEZEL 376.63; FLANK_3C_6 94.96; LUGWALL_12 64.61 (18.776 × 3.619); LINK_C ×10 (43.89–63.23); LINK_S ×20 (28.34–38.64); LUG_UNDER ×4 (49.87–52.60); LUG_TOP ×3 (34.12–35.41); CROWN_BAND 31.08 (18.369 × 1.700); LUG_INNER_6B 22.95; CLASP_COVER_12 19.92 (8.361 × 2.400); LUG_INNER_12C 18.05; CROWN_CAP 17.36 (disc Ø4.701); LUG_INNER_12B 16.06. The seven `maintainer-confirmed-extra` pieces (LUGWALL_12, LUG_INNER ×3, CROWN_BAND, CROWN_CAP, CLASP_COVER_12) have **no manual counterpart at all** — the manual kit is case + bracelet only.

**Cross-family ambiguity.** The same matcher run *without* the class constraint accepts 17 pairs instead of 6, and **11 of the 17 are cross-family** — 8 pair a manual CENTRE link with one of our SIDE links (e.g. M12 7.793 × 4.047 A 31.46 ↔ LINK_S_12_4B 7.604 × 4.100 A 31.03 at **H 0.111, ΔA −1.35 %**). A real measurement, not matcher noise: **our LINK_S family is the size of the manual's CENTRE link**, and our LINK_C family is roughly twice it.

## 7. How the manual kit was made (record facts)

**Margin stage — uncaptured, reconstructed from the surviving tree.** 7 `Offset in Face` + 7 `Divide Face` pairs (ids 74–80), all pre-existing (id ≤ 169) at session 9d37's first snapshot: Body(66) **0.55**, Body(67) **0.65**, Body(68) **0.75**, Body(69–72) **0.85 ×4**. Each `Divide Face(N)` reuses the exact expression id/value of its sibling `Offset in Face(N)` (both id-74 features share `p171 = 0.55 mm`) — Divide Face carries no independent value, it **splits the face along the curve Offset-in-Face just produced**. Downstream: `Offset Region(81)` (p178 = 16.0 mm reach) → `Mirror Geometry(83)` (476 `nx_feature_modified` cascade events, the most-touched node of the session) → patterned instance bodies Body(122/123/125/127/128/130) at Y-pitch ≈6.3–6.8 mm from a Pattern/Instance step never captured as its own named feature. **The record cannot answer** why the margins are graduated, nor why they converged at 0.55–0.85 mm.

**Flatten stage — captured.** 18 `Flattening and Forming` create-events = **15 unique features + 3 duplicates** (185/187/193: the duplicate event's timestamp is **0.09 s** after the original, while its linked screenshots are **23–33 s** apart — capture duplicates or immediate edits; **the record cannot say which**, and no human re-runs a dialog in 0.09 s). The dialog was live-captured on F&F(189) and is uniform across all 15: type **Flattening**, Outer Boundary none, Constraint Group "Flattening with" **None**, Rip Edge none, Transformation Objects none, Distortion Map **None**. **Target plane for all 15 flats = z = 0.0000 mm**, measured on the last STEP export — flats land in place above their source and are then dragged aside. Fidelity ΔA: **0.003 %** (FLANK_9, flat 203.1532 vs 3D 203.1470), **0.002 %** (3-face patch, 25.9644 vs 25.965), **0.18 %** (LUG_UNDER candidate, 11.4293 vs 11.409). 6/15 identities high-confidence (CASEBACK centre 361.961 / 21.576 × 21.579; bezel ring 294.944 / 35.712 × 35.711, 2 wires; CRYSTAL+cyclops 703.922 / 30.913 × 30.909, 2 wires; FLANK_3 88.102 / 22.566 × 6.504; two link instances 18.125 and 9.389); **9/15 unresolved** — the Flattening dialog's Source-Face pick is never logged as typed data, and several source parents (Body(125/127/128/130)) are leaf nodes with no ancestry. Only **4–5 of the ~36 bracelet-link bodies were individually flattened**: one representative per size class, not every copy.

**Layout stage — captured.** All 17 new `Move Object`s carry `expressions: []` (Motion Dynamic, Specify Orientation checked, Associative on, Move Original) — mouse drags with no typed distance, against 45 pre-existing Move Objects that each carry one typed scalar (0.05–42.5 mm / −0.5 to 1.5°). `Move Object(197)` is a **group move**: a shared child of Flattening 189/191/193/195, batch-aligning 4 flats at once.

**2D stage — start captured, rest not.** Exactly **one sketch**, SKETCH_005 (feature id 204), type "On Plane", coincident with the global Datum CS(0), view Top. **Project Curve**: Associative **OFF**, Output Curve Type **Original**, Tolerance **0.010 mm**, pick mode Single Curve, ≥13 objects (running count only — the dialog never closed on camera), 46 window-title events over ~122 s. `nx_sketch_entered` then reports **geometry_count 65, first 20 = 1 Line + 19 Spline** — the raw projection is spline-dominated while the delivered DXF has **zero** splines, so the idealisation happened in the uncaptured window. A **save hang** followed: Ctrl+S 18:30:14 UTC, stuck "Saving 50 %", a ~3.2 s "Save Failed" window, recovery by NX close/reactivate/reopen, **zero filesystem evidence of any backup**. Also uncaptured: the fillet pass, the replication of the link representatives into the 44 bracelet pieces, and the RV3–RV7 saves (5 RV3 lines 21:45–22:15 local, 1 RV5 at 22:44).

**Export.** `Watch_STL_to_DXF_RV7.log`: Unigraphics **NX2206.9140 → AutoCAD 2004** (2D Exchange / UGTODXF), source part `…\Desktop\STL TO DXF SESSION RECORD 2\Watch_STL_to_DXF_RV7.prt`; **input 195 Line + 261 Arc + 6 Circle = 462**; output the same 462 plus **6 translator Layout objects** = 468; Sun Aug 30 22:50:25 2026 local, CPU 0 m 1 s. The DXF is **AC1018**, `$INSUNITS 4` (mm), layer table `0`/`1`/`Defpoints` with every entity on layer **"1"**, **61 closed loops / 0 open at 0.06 mm**, **no SPLINE, POLYLINE or TEXT** — and, as in the Daytona kit, **no labels at all**.

## 8. Findings against our own pipeline

- **F-A — our r2 DXF is fully polygonised**: 8 237 chords, 0 non-zero bulges, min segment 0.0801 mm, against `dxf-contract.md`'s exact-bulge-arc promise and the ground truth's 195 LINE / 261 ARC / 6 CIRCLE. Writer or kit-builder defect; **flagged as a separate fix task, not fixed in this patch**.
- **F-C — independence caveat**: 43 of our 52 pieces are marked `nx-record` / `nx-record-recovered`, i.e. built to this same NX record. Near-exact agreement on CRYSTAL (H 0.046), the cyclops (+0.23 %) and CASEBACK_CENTER (H 0.036) is **expected, not evidence of independent pipeline accuracy**. The informative results are the disagreements (bezel, links, lug-unders) and the extras.
