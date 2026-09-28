# Real run: OD-S01 steam valve assembly (2026-09-28)

This is the second run of the v1 skills on a part with no golden record. Ikbal sent a scan and 5
catalogue photos and asked for "p95 plastik parça toleransı". The records are copied under `OD-S01/`:
DECISIONS, the it2 VERDICT and gate, the it1 VERDICT and gate under `it1/`, the README, INTAKE_CARD,
MODELING_PLAN, PARAM_TABLE and one QA overlay. The run folder was in the session scratchpad. It was
delivered as one zip; see "Delivery" below.

## Inputs and decisions
- Scan: 499,756 faces, one body, not watertight (22 open loops), 48.0 × 47.5 × 54.7 mm, mean edge
  0.206 mm. The owner confirmed it is the full-res original (question card).
- Regime: `baseline-skill` plastic, p95 ≤ 0.30 / max ≤ 0.80 mm, from the owner's instruction.
- No calipers (question card: scan-only), so Tier-1 did not run.
- The part is an assembly: a cap with a splined spindle and a 3-fold cam ring, the valve body, a
  top clip port, 2 side ports, a hose barb, and a microswitch with blades. It is delivered as one
  fused solid.

## Result
- Datum: primary = cap disc outer face (rms 0.034); axis = upper column (Kåsa, rms 0.045 < circle
  noise 0.048); clock = microswitch face → +X. CHK-TILT is a finding: the span is short, and a
  two-feature fit was not resolvable.
- It1 (builder self-checks v0..v9, not QA): p95 went from 1.67 to 0.49. The biggest win was
  understanding the lower skirt as a 3-fold cam ring (3 posts + 3 trapezoid teeth), using an
  unwrapped r(θ,z) map.
- **QA it1 (independent agent): REVISE.** scan→CAD p95 0.520 / max 2.270; observable CAD→scan
  0.800 / 3.129. The causes were concrete: port blocks about 1 mm short of the visible end wall, 2
  features missing from intake (a bump under the switch, a column lug), stepped instead of sloped
  shoulder, the barb rib, the top-bore floor, and an invented wedge at the holder.
- It2 (`supersede --route datum`, intake re-run identical): all the named items were re-measured
  and rebuilt. 351 faces, 100 % analytic, 3/3 fillets OK.
- **QA it2 (a new independent agent): BAND_NOT_MET.** scan→CAD p95 0.449 / max 1.940; observable
  CAD→scan 0.761 / 2.890; only the barb zone passes. The max 1.94 is an **it2 regression**: the
  new port junction box fills a sloped wall by the neck. A QA probe (not a gate) says that even
  with every cluster over 0.8 mm perfect, the result stays around p95 0.34 / max 1.09. The rest is
  spread-out 0.3–0.8 mm error in the cam ring, collar and top-port outline. On top of that, the
  scan cannot resolve the spline count.
- The owner accepted (ACCEPT-BAND, gate `19f6d742b0ae`). Deliver produced the README, MANIFEST and
  a reproducible repro.json (2 fresh processes).
- Delivery: `OD-S01_steam-valve_RE_BAND_NOT_MET_2026-09-28.zip`, 72 MiB. The raw scan and the
  regenerable work meshes are excluded but listed. The app's file upload limit is 30 MiB, so the
  one zip was sent as 3 byte-split parts plus its `.sha256`. This is now in the delivery-package
  reference.

## Lessons for the skills
- On an assembly with many small moulded features, builder time goes into *understanding* the
  geometry. Unwrapped r(θ,z) maps and scan-vs-CAD section overlays found the cam ring, the drafted
  plates and the port windows faster than feature-by-feature fits did.
- A distance map from the builder's self-check (datum frame, no ICP) predicted the QA p95 within
  about 0.03–0.04 mm on both iterations: 0.49 vs 0.52, and 0.41 vs 0.45.
- A "hidden inside the column" assumption about a connector was wrong. QA saw the end wall. List
  what is claimed to be invisible, and check it against the scan before building.

## Skill defects found (status on this branch)

| # | Where | Defect | Status |
|---|---|---|---|
| 1 | `stl-re-verify/scripts/deviation_gate.py` | Only the top 12 over-band clusters go into gate.json (26–31 existed), so CHK-CLUSTER cannot see the rest | open |
| 2 | `stl-re-verify/scripts/overlay.py` | No `--registration` option, so the overlays are drawn in the builder frame and not the graded post-ICP frame | open |
| 3 | `stl-re-verify` zones | A `functional_interface` zone is silently ungated when the regime has no interface band (baseline-skill) | open |
| 4 | `stl-re-verify/scripts/verdict.py render` | No iteration comparison; the it1/it2 table appended by hand is dropped on re-render | open |
| 5 | `stl-re-measure-intent/scripts/param_table.py` | Nested list values (polygons, sector lists) are rejected. They have to be split into numbered keys (`name_1..n`) and read with `P.group()`; this is not documented in param-table-schema.md | open (doc) |
| 6 | `stl-re-intake-datum/scripts/align.py` | `noise_secondary` needs a circle-noise JSON measured on the *aligned* mesh, which only exists after a first align pass. A fresh re-run needs 2 passes; this is not documented | open (doc) |
| 7 | `stl-re-orchestrate/scripts/init_run.py status` | Reports "scan-only needs a MEASUREMENTS decision" even when `DECISIONS.md` has one | open |
| 8 | `stl-re-deliver/scripts/make_manifest.py` | `decisions/accept_band.md` gets role `unclassified` | open |
| 9 | `stl-re-deliver` | A zip over 30 MiB cannot be sent with SendUserFile | fixed in docs: `references/delivery-package.md` "Sending a large zip" (byte-split parts + sha256) |
| 10 | `stl-re-measure-intent/scripts/pattern_count.py` | On a partial arc (a D-flat and key interrupt the spline), the FFT order is unstable (24/25). The partial-arc least-squares fit also cannot separate 23–25 | open (finding) |
