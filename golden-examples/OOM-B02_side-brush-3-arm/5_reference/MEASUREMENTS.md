# MEASUREMENTS — OOM-B02_Side-brush-3-arm

<!-- Pre-filled by the RE line at intake 2026-07-29 (re-mesh-analyst request, §8 of
     6_RE_work/INTAKE_CARD.md). Muhammed fills the "Caliper (mm)" column.
     Rules: record the value AS READ (no rounding — snapping is the modeller's job and every
     snap is logged). Measure critical dims twice; if the two reads differ by >0.05 mm, record
     both. Soft/flexible features (bristles): marked "soft" — wider band. Unreachable: write
     N/A, never guess. "Scan says" is FYI only — do NOT copy it into the caliper column. -->

Instrument: Mitutoyo digital caliper ±0.02 mm (per photos) — state if different (depth rod, pin gauges, mic)
Date measured: 2026-07-29 (the readings visible in the photos); **no dedicated caliper session was run**

Tier-1 band: |CAD − caliper| ≤ 0.15 mm on every dim below except those marked **soft**.

> ## ⚠ STATUS — PARTIAL SHEET, PROCEED-WITHOUT DIRECTED
>
> **2026-07-30, Muhammed: "I confirm all assumptions, go ahead, do not be blocked."**
> The line proceeded to REBUILD without a caliper session, on that direction. Recorded per the
> RE_SPEC §4 honesty rule so the verdict cannot be read as stronger than it is:
>
> 1. **§D photo-transcribed attributions are CONFIRMED** by that direction and are promoted into the
>    caliper column below, tagged `photo-transcribed (attribution confirmed 2026-07-30)`. They are real
>    instrument readings, but the jaw placement was inferred by the line from the photo, and screen
>    parallax is not the instrument's ±0.02 mm — treat their effective uncertainty as **±0.1 mm**, not ±0.02.
> 2. **Tier-1 is PARTIAL: 7 of 24 dims carry a value.** The other 17 are **ABSENT, not passed** — the
>    verifier gates the 7 and reports the rest as ungated. Any final verdict must say so.
> 3. **ENV-1/2/3 are empty → the RE_SPEC §2 envelope scale check could not be run. Absolute scale is
>    UNVERIFIED.** Partial corroboration only: four mid-size dims sit 0.4–1.6 % under the scan
>    (ratios 0.984 / 0.996 / 0.991 / 0.989). That disagreement is **not uniform enough to justify a global
>    scale correction**, so per RE_SPEC §2 none is applied and it is flagged here instead. The confirmed
>    caliper values are used directly as CAD parameters, which absorbs the discrepancy locally.
> 4. **F01 (hex AF) has NO reading of any kind** — no photo captures it. The CAD takes the scan fit
>    **7.358** (rms 0.037 over the ~2/3 of the hexagon that was scanned) and is **NOT intent-snapped** to
>    7.0 or 7.5. This is the largest single risk on the part: it is the drive interface, and an internal
>    pocket on a dilating scan can read either way. **Re-measure hook: one caliper reading on F01 changes
>    the part's fit and should trigger a re-run.**
> 5. **D-09 (1.32), D-10 (4.63), D-12 (30.56) stay UNASSIGNED.** The line never asserted a feature for
>    them, so there was nothing to confirm; they are not used as parameters.

## A. Envelope (mandatory — drives the unit check & global scale correction)

| ID | Feature | Where to place the jaws | Caliper (mm) | Scan says | Notes |
|---|---|---|---|---|---|
| ENV-1 (M1) | **Overall Ø over bristle tips — SOFT, ±3 mm** | Brush on the table cup-side UP, bristles falling naturally (orientation of `IMG_20260729_181846.jpg`). Outside jaws, largest tip-to-tip distance between two arms' tuft ends. Record WHICH two arms. | | ~108 tip-to-tip (≈124.9 swept Ø) | soft — not Tier-1 blocking |
| ENV-2 (M2) | **Overall Ø over the RIGID plastic arm ends** | Same orientation. Outside jaws on the **white plastic collar where the filaments emerge** (`IMG_20260729_182035.jpg`), two arms. Do not touch filaments. | | ~66 across two arms (≈76.4 rigid Ø) | |
| ENV-3 (M3) | **Overall height, rim face → highest plastic** | Stand the brush on a flat table **cup-rim-face DOWN** (rim annulus flat on the glass). Depth rod / height gauge from table to the highest point of **white plastic** arm; ignore filaments. | | 17.6 | |

## B. Functional dimensions (analyst-requested, priority order)

| ID | Feature | Type | Why it matters | Where to place the jaws | Caliper (mm) | Scan says | Notes |
|---|---|---|---|---|---|---|---|
| F01 (M6) | **Hex drive socket across-flats (AF)** | AF | **Most important dim on the part** — takes all drive torque; scan sees only ~2/3 of the hexagon (124° gap), so this cannot be intent-snapped without you | Cup up. Knife-edge inside jaws into the hex pocket (`IMG_20260729_182250.jpg`, `IMG_20260729_181852.jpg`), square across **two opposite flats**, not corners. Three readings at 60° apart; give the smallest and the spread. | | **7.358** | do NOT snap to 7.0 without this |
| F02 (M7) | Hex pocket depth below cup floor | depth | Shaft engagement length | Depth rod on the **flat cup floor** (annulus around the hex), rod down to the hex pocket floor. `IMG_20260729_182142.jpg`. | **3.44** | 3.48 | photo-transcribed D-11 (attribution confirmed 2026-07-30), ±0.1 |
| F03 (M8) | Cup bore ID | ID | Spigot/pilot onto the motor hub | Inside jaws across the cup's inner cylindrical wall, ~1 mm above the rim face. `IMG_20260729_182203.jpg`. | **20.75** | 20.93 | photo-transcribed D-08 (attribution confirmed 2026-07-30), ±0.1 |
| F04 (M9) | Cup depth, rim face → cup floor | depth | Axial stack to the motor boss | Depth rod from the **rim face** (flat annular ring the caliper body rests on) down to the cup floor. | | 2.566 | |
| F05 (M4) | **Hub skirt OD — MAX (lobe)** | OD | Chassis pocket clearance; skirt is **3-lobed**, one number is ambiguous | Cup side up (`IMG_20260729_182142.jpg`). Outside jaws on the cylindrical skirt band ~1 mm above the rim (NOT the dome); rotate to find the **largest** reading. | **26.85** | 27.29 (R 13.55) | photo-transcribed D-03 (confirmed), corroborated by D-07 26.80. **Weakest of the promoted set**: 0.44 under the scan, and a max-lobe reading is the easiest to under-read if the operator did not hit the lobe crest. Modeller: hold 26.85, expect a positive scan residual here. |
| F06 (M5) | **Hub skirt OD — MIN (flat)** | OD | same | Same band, rotate to the **smallest** reading — the flat lands on an arm centreline. | **24.84** | 24.95 (R 12.56) | photo-transcribed D-05 (confirmed), ±0.1. A min reading is self-finding (rock the caliper) → more trustworthy than F05. |
| F07 (M10) | Hub total thickness, rim face → dome apex | height | Axial envelope under the chassis | Outside jaws: one jaw flat on the **cup rim annulus**, the other on the **highest point of the dome** near the screw. `IMG_20260729_182318.jpg`. | | 10.97 | |
| F08 (M11) | **Central screw bore Ø** — *needs the screw REMOVED* | ID | Axial retention; bore + boss are 100% occluded by the fitted screw | Unscrew the centre Phillips screw. Inside jaws / pin gauges in the through-hole at the hex-pocket floor. **Also report: screw thread Ø, thread length, head type (pan/csk), head Ø, drive size.** | | 2.70 at the mouth | **blocked on Q2 — may the screw come out?** |
| F09 (M12) | Dome-side counterbore Ø | ID | Screw head seating | Inside jaws in the circular recess around the screw head, dome side (`IMG_20260729_182318.jpg`, centre). Measure the **plastic bore**, not the screw head. | | 7.07 (×1.49 deep) | |
| F10 (M13) | Arm cross-section — **width** | width | Arm stiffness; drives the swept section | Photo station is the **outer half of the blade, at/near the tuft collar** (`IMG_20260729_182035.jpg`), not mid-arm. | **5.33** | 5.8–6.3 | photo-transcribed D-02 (confirmed), ±0.1. Scan reads **+0.5 oversize** here (dilation, R6). |
| F11 (M13b) | Arm cross-section — **thickness** | thickness | same | Same station as F10 (`IMG_20260729_182020.jpg`). | **4.07** | 3.8–4.5 | photo-transcribed D-01 (confirmed), ±0.1. Scan agrees within 0.1 here — **note the inconsistency with F10: dilation shows on the width but not the thickness.** Modeller: hold both at this station, take the taper toward the hub from the scan SHAPE, and let QA report the flank residual rather than blending the two offsets. |
| F12 (M14) | Arm section at the tuft collar — **width × thickness** | width/thickness | Sets the tuft socket and the collar step | Outside jaws immediately **before** the step where the filaments emerge (collar in `IMG_20260729_182035.jpg`): two numbers. | | 5.8–6.2 × 3.9–4.1 | |
| **F13 (M17a)** | **SAF-1 hole Ø** | ID | **Ruled a FUNCTIONAL KEY 2026-07-29 → now a gate zone, not a witness mark.** It gets modelled and gated. | The small dark hole through the skirt wall at the one inter-arm position, `IMG_20260729_182109.jpg` / `IMG_20260729_182231.jpg`. Inside jaws or pin gauges. Clear the debris/filament out of it first. | | Ø ≈ 2 | promoted from wall section |
| **F14 (M17b)** | **SAF-1 external nub — radial extent + width** | OD / width | Sets the key's engagement | Outside jaws from the opposite side of the skirt across the nub → gives (skirt OD + nub projection); also the nub's circumferential width. | | to R 15.07 (≈2.1 wide) | |
| **F15 (M17c)** | **SAF-1 clocking relative to the HEX flats** | angle/chord | **A key only works if its phase to the drive hex is held.** This is the dim that makes or breaks the key. | Hardest one: with the cup up, note the hex flat orientation, then the hole's angular position from the nearest hex flat normal. If an angle is impractical, give the **chord distance from the hole centre to the nearest hex corner** and say which corner. If neither is practical, write N/A and I will take the scan value (50.7° hex phase, hole at θ≈−71° from arm 1). | | hole −71° from arm 1; hex phase 50.7° from arm 1 | may be N/A |
| **F16 (M17d)** | **SAF-1 internal boss** — height above cup floor, and its footprint | height | The internal half of the key feature | Depth rod from the cup floor onto the raised boss on the cup floor at the same clocking; plus rough length × width of its footprint. | | 1.7 proud, r ≈ 5–9 | |
| **F17 (M11b)** | **Screw: thread Ø, thread length, head type/Ø, drive size** | OD/length | Q2 = YES, screw comes out → the fastener becomes a documented COTS item and the bore stops being a guess | With the screw out, measure the thread major Ø, the threaded length, head Ø, head height, and state pan vs countersunk and the drive (PH0/PH1). | | head OD ≈ 5.4–6.0 | Q2 answered YES |
| **F18 (M11c)** | **Bore depth / thread-engagement depth, screw removed** | depth | Was 100% occluded; now measurable | Depth rod down the central through-bore from the hex-pocket floor; note whether the bore is plain, tapered, or has a moulded thread/boss, and whether it breaks through to the dome counterbore. | | unresolvable while fitted | Q2 answered YES |

## C. Wall thicknesses

| ID | Feature | Where to place the jaws | Caliper (mm) | Scan says | Notes |
|---|---|---|---|---|---|
| W01 (M15a) | Skirt wall thickness at a **lobe** (between two arms) | Outside jaws straddling the skirt wall at the rim: one jaw on the outer skirt, one inside the cup bore. | | 3.09 | |
| W02 (M15b) | Skirt wall thickness at a **flat** (on an arm centreline) | Same, repeated at a flat. | | 2.10 | |
| W03 (M16) | Cup floor + dome stack *(optional)* | M10 − M9 − (dome apex → hex-pocket floor). Awkward — skip and note it if so. | | ≈4.9 | optional |

<!-- M17 (SAF-1) was promoted out of this section into B (F13–F16) when Q1 was ruled
     "functional key" on 2026-07-29 — a key is a functional interface, so it is gated, not optional. -->

## C2. RULINGS — Muhammed, 2026-07-29 (CLOSED)

| # | Question | Ruling | Consequence for the rebuild |
|---|---|---|---|
| **Q1** | SAF-1 (hole + nub + internal boss at θ≈−71°): witness or key? | **FUNCTIONAL KEY** | SAF-1 **is modelled** as a single-instance feature breaking the 3-fold pattern. It becomes a named functional interface → per RE_SPEC §4 it is gated at **Tier-2 max ≤ 0.8 mm** where not caliper-covered. Dims promoted to **F13–F16**. Its **phase relative to the hex** (F15) now matters. |
| **Q2** | May the centre screw be removed? | **YES** | Screw comes out → **F08** (bore Ø), **F17** (fastener spec), **F18** (bore depth / thread engagement) become measurable instead of photo-inferred. Screw stays a COTS item, excluded from `OOM-B02.step` and masked out of the Tier-2 gate reference (r < 3.6, Z +8.6…+10.4). |
| **Q3** | Functional reading: cup toward the motor, dome to the floor, hex takes the torque, rim annulus is the axial seat. | **CONFIRMED** | Datum plan stands as intake proposed: rim annulus → XY at Z=0 (plane fit rms 0.052), rotation axis → +Z, arm 1 → +X. |
| **Q4** | Model the arm path planar in r–z, tangential drift = free-state deformation? | **YES** | Arm swept along a planar r–z spline (z rise ~11.4–12.8 mm over r 13→38.2), then `PolarArray(3, 120.00°)`. The 0.97–2.20 mm tangential drift is **not** modelled; expect it to show as a reported Tier-2 deviation on the arm flanks — correct per RE_SPEC §3, not to be chased. |

## D. Photo-transcribed candidates — CONFIRM THE ATTRIBUTION OR STRIKE IT

<!-- Readings are legible in the caliper photos and are treated as REAL READINGS; but the
     FEATURE each one belongs to is the line's inference from the jaw position in the frame.
     Confirm (tick), correct, or strike. A confirmed row can be promoted into the matching
     A/B/C row so you do not have to re-measure it. An unconfirmed row is NOT used. -->

| ID | Photo | Reading (mm) | Line's inferred feature | Maps to | Confirm? |
|---|---|---|---|---|---|
| D-01 | `IMG_20260729_182020.jpg` | **4.07** | arm thickness near the tuft collar | F11 / F12 | ☐ |
| D-02 | `IMG_20260729_182035.jpg` | **5.33** | arm width at the collar / mid-arm | F10 / F12 | ☐ |
| D-03 | `IMG_20260729_182048.jpg` | **26.85** | hub OD across the skirt, dome side | F05 | ☐ |
| D-04 | `IMG_20260729_182109.jpg` | **10.85** | fanned bristle-ribbon width at the tip (**soft**) | — (soft) | ☐ |
| D-05 | `IMG_20260729_182128.jpg` | **24.84** | hub skirt OD at a **flat** (min) | F06 | ☐ |
| D-06 | `IMG_20260729_182142.jpg` | **25.79** | hub skirt OD, intermediate clocking | F05/F06 | ☐ |
| D-07 | `IMG_20260729_182203.jpg` | **26.80** | hub skirt OD at a **lobe** (max) | F05 | ☐ |
| D-08 | `IMG_20260729_182215.jpg` | **20.75** | cup bore ID | F03 | ☐ |
| D-09 | `IMG_20260729_182231.jpg` | **1.32** | thin wall / rim step — attribution unclear | ? | ☐ |
| D-10 | `IMG_20260729_182250.jpg` | **4.63** | inside the cup centre — hex-related, attribution unclear | ? | ☐ |
| D-11 | `IMG_20260729_182301.jpg` | **3.44** | hex pocket depth below the cup floor | F02 | ☐ |
| D-12 | `IMG_20260729_182318.jpg` | **30.56** | span across the dome side incl. arm roots — attribution unclear | ? | ☐ |

Cross-check: D-03/D-07 (26.85/26.80) vs scan lobe 27.29 → −0.45; D-05 (24.84) vs scan flat 24.95 → −0.11;
D-08 (20.75) vs scan bore 20.93 → −0.18; D-11 (3.44) vs scan hex depth 3.48 → −0.04. Consistent small
negative offsets = the scanner dilation noted in the intake card (R6), not a scale error.
**No hex AF reading exists in any photo — F01 must be measured.**

## E. Extra dims measured on your own initiative

| ID | Feature | Caliper (mm) | Notes |
|---|---|---|---|
| X01 | Fanned bristle-ribbon width at the tuft tip — **SOFT** | **10.85** | photo-transcribed D-04 (confirmed). Free-state fan, no manufacturing meaning; **not modelled, not gated.** Recorded only as evidence the ribbon is a flat bundle. |

## F. Open questions

Q1–Q4 are CLOSED — see §C2. Remaining, **non-blocking** (answer in chat or here; if unanswered the
line takes the stated fallback):

| # | Question | Fallback if unanswered |
|---|---|---|
| **Q5** | Q1 was ruled "functional key" — **what does SAF-1 key into?** The chassis pocket, the motor hub, or a tufting/assembly jig? And is the **hole** the working feature, the **external nub**, or the **internal boss**? This decides which of the three is held tight and which is incidental. | Model all three as scanned; hold the **hole** as the key datum (smallest, most repeatable), gate the nub and boss at Tier-2 only. |
| **Q6** | Tracker: the OOM-B02 row was previously named *Side-brush-2arm-curved-Qrevo*. Is the 2-arm Qrevo brush a **separate part** that now needs its own row, or was the row simply mislabelled? | Treat as mislabelled; no new row created. |
