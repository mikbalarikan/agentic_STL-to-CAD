# brush_CAD-REVISED: cleanup to one watertight solid

**Deliverable:** `brush_CAD-REVISED_single_solid.stp` (AP214, mm, 1 body)
**Input:** `brush_CAD-REVISED_stp_1.stp` (NX2206 export, sha256 `59ce4480…c325`)
**Output sha256:** `aa4fb1058d5f96a30fb6da5484bb27c3a93556dfbbb263aeb7e5900e87fbb6f5`

## What was wrong in the input

| Item | Found |
|---|---|
| Bodies | 6 separate solids: the core ("Body (5)") and 5 identical ribs (2185.96 mm³ each) |
| Core | `BREP_WITH_VOIDS`: the outer shell (270 faces) enclosed a large inner void shell (156 faces, 22,152 mm³). The core was only a ~0.2 mm skin (4,922 mm³ of material inside a 27,075 mm³ envelope). There were also 5 zero-volume sliver void shells at the petal tips (z 4.25–6.27). |
| Ribs vs core | The 5 ribs form an exact 5-fold pattern, but its axis is tilted 0.046° from the core axis (direction (0.000709, −0.000379, 1), 2.4 µm offset). Each rib root sits in a twisted channel of the stem with alternating gap and interference of up to ±0.15 mm. Booleans fail on this near-coincident contact, and a plain union would leave hairline crevices. |

## What was done

1. **Filled the core.** Rebuilt it from its outer shell only, which drops the inner void and the 5 sliver voids. The exterior is unchanged.
2. **Re-registered the ribs** with a rigid rotation of 0.046° that puts their pattern axis on the core axis. The rib end faces now sit exactly on the core planes z = 4.5 (floor) and z = 168.6 (pocket floor). Maximum displacement is 0.133 mm, at the blade extremities. The rib shapes themselves are untouched.
3. **Filled the 5 rib channels** so each rib root is embedded rather than resting on the channel walls:
   - Between z 4.25 and 168.61, each channel is filled below a chord across its mouth, plus 0.3 mm into the walls. The fill is swept with the stem's measured twist of 1.10229°/mm; the stem is an exact twisted extrusion, with sections matching within 0.01 mm.
   - At the base petals (z 4.38–6.3), each fill is a prism capped exactly at R 7.6222, the rib's own outer face.
   - This closes the ≤0.15 mm crevices between ribs and channels.
4. **Fused in z-sections** (−1…40, 40…80, 80…120, 120…150, 150…180). Every fill and rib step was volume-checked against an independent 2D-section calculation. The sections were then joined along their flat interfaces.

## Validation of the delivered file (re-read from STEP)

| Check | Result |
|---|---|
| Solids / shells | 1 / 1 closed shell, no voids |
| Faces | 604 |
| Free boundary edges | 0 (watertight) |
| BRepCheck | valid |
| Bounding box (mm) | x −16.866…16.910, y −16.741…17.032, z −0.012…175.914 (input: −16.84…16.91, −16.76…17.03, −0.01…175.92) |
| Volume | ≈ 38,048 mm³ (sum of the verified sections) |
| Deviation vs core + re-registered ribs | median 0.002 mm, p99 0.023 mm, max 0.15 mm (at channel mouths where crevices were bridged) |
| Deviation vs original input (includes the rib re-registration) | p99 0.116 mm, max 0.18 mm |

Other small effects: the channel fill ends 0.01 mm above the rib tops (z 168.61), which leaves a 0.01 mm film on the rib top faces and next to the pocket floor. This was needed for a robust boolean, because the coplanar version failed.

Unchanged: the base ring and recess, petals, hexagon, star stem outer surface, top rim, pocket and cones.

`brush_sections_before_after.png` shows sections at z = 2, 5.5, 85 and 168.45. Red is the new solid, blue the original ribs, and grey dotted the original core with its inner void.

## Not carried over

The PMI, saved views and colours in the original NX file. The output contains geometry only.

## Reproduction

`src/` contains the OpenCascade 7.7 (`cadquery-ocp==7.7.2`) scripts and the 2D fill profiles that were used:
- `align.py`: rib re-registration
- `k2d.py`, `kbase2db.py`, `kbase3d.py`, `kbrot.py`, `kloft.py`: the fill solids
- `seq.py`, `seq2.py`, `base3.py`: the section fusing
- `join.py`, `finalize.py`: assembly and checks

These are working scripts, not a packaged tool.
