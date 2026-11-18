# Real run: OD-H21 DeLonghi anti-drip valve (2026-09-28)

The second real run of the v1 skills (branch `claude/stl-reverse-engineering-lt6n05`), on a part with no golden
record. Ikbal supplied a scan and two catalogue photos, with no calipers. Records are copied under `OD-H21/`:
`DECISIONS.md`, `BUILDER_REPORT.md`, the it2 `VERDICT.md` and `gate.json`, `VERDICT_it1.md`, the delivered
`README.md`, `accept_band.md` and the it2 CAD→scan heatmap (`overlay.png`). The STEP files are in the
delivery zip.

## Inputs and decisions
- Scan: 600,142 faces, one body, not watertight (7 open loops), about 47 × 34 × 61 mm, mean edge 0.152 mm.
  It is a **closed shell of an assembly**: the scanner bridged every internal passage, so only shallow bore mouths are open.
- Regime: baseline-skill plastic, p95 ≤ 0.30 / max ≤ 0.80 mm. The owner's words were "p95 plastik parça toleransı
  kullan", now recorded as a shorthand in the root `CLAUDE.md`.
- No calipers, so Tier-1 did not run. The photos carry no scale reference.
- `scan_resolution = full` was inferred by the agent from the face count and edge length, the same scanner family
  as OD-H22. The owner has not confirmed it; it is a limitation with a trigger.
- Orchestrator decision: model the visible geometry only. Bores stop at the observed scanner bridge, and no internal
  passages or valve internals are invented.

## Result
- **Build:** one valid closed solid in both frames, 146 faces, all analytic, 103 params (all from the scan).
  Each sub-part (nozzle, nut, bands, body, cap part, outlet, barb) is revolved about its own measured axis:
  the assembly is tilted (nozzle about 1.4°, cap part about 3.4°). The O-ring is fused, and the G1/8-like
  thread (pitch 0.908 ≈ 28 TPI) is built as a plain cylinder.
- **it1:** independent verify returned `REVISE` (gate `dd052135f7c2`). There were three geometric findings:
  - the nozzle latch window was under-cut;
  - the ring window spans were too long or too deep;
  - the skirt slits were over-cut.

  Routed with `supersede --route geometry`.
- **it2:** the same verifier re-ran with the same protocol (CHK-LIKE4LIKE pass) and returned `BAND_NOT_MET`
  (gate `a7a0a18a5df9`). ICP delta was 0.046° / 0.0125 mm; the datum audit was 0.018° / 0.007 mm.
  - scan→CAD masked: p95 0.175 / max 0.799. This passes, but only with the M1 bore mask; the unmasked max is 1.085.
  - CAD→scan observable: p95 0.255 / max 3.120, which misses. The cause is the unscanned nozzle bore floor, which
    the ray test counts as observable. Zones I1 (latch edge) and I5 (ring windows) miss by scanner bridge membranes.
  - The verifier found no rebuild target left.
- **Delivery:** Ikbal answered "del'ver" after seeing the heatmap, which was recorded as `ACCEPT-BAND` citing
  `a7a0a18a5df9`.
  - The repro check was reproducible.
  - The README and MANIFEST were rendered.
  - The zip `OD-H21_antidrip-valve_RE_BAND_NOT_MET_2026-09-28.zip` is 19 MiB.

## Skill defects found (status on this branch)

| # | Where | Defect | Status |
|---|---|---|---|
| 1 | `stl-re-verify/scripts/observability.py:84`, `deviation_gate.py:338`, `verdict.py:64` | Open-mouthed bores, windows and slits count as observable (OD-H22 #3 again). The observable split runs on unmasked distances, so a declared mask can never reach the gated CAD→scan term. **Main driver of the band miss for the second run in a row.** | open |
| 2 | `stl-re-verify/scripts/observability.py:61` | `chunk=2000` rays is not exposed on the CLI. The run needed a wrapper with chunk 64 (1.8 GB peak) on a 518k-triangle CAD STL | open |
| 3 | `stl-re-verify/scripts/datum_audit.py:183-185` | The circle is fitted after projection onto the primary plane. For a tilted axis this gives the mid-station centre, not axis ∩ plane (0.37 mm apart here) | open |
| 4 | `stl-re-intake-datum/scripts/align.py:358-367` | The axis-primary crop is radial only (no axial window), so one cylinder cannot be isolated on a stacked turned part | open |
| 5 | `align.py:404,465` | The STOP checks have no tie margin (OD-H22 #4 still open) | open |
| 6 | `stl-re-measure-intent/scripts/{sections,fits,pattern_count}.py` | Every tool assumes features coaxial with Z. Tilted sub-parts and radial ports needed a run-local library | open |
| 7 | `stl-re-rebuild-build123d/SKILL.md:185` | Rounds drawn as arcs inside revolve profiles are invisible to CHK-FILLET (`fillets.json` stays empty) | open |
| 8 | `stl-re-measure-intent/scripts/param_table.py:26` | No dimensionless unit (slopes, ratios) | open |
| 9 | CLI (`datum_fit.py`, `align.py`, `fits.py`) | A vector argument with a leading minus must be written `--arg=-0.4,...` (OD-H22 D5 still open) | open |
| 10 | `stl-re-intake-datum/SKILL.md` Step 5 | CHK-ENUM has no residual-driven pass. Three real features (outlet→ring web, two skirt slits, second latch cut-back) surfaced only in the self-check | open |
| 11 | `stl-re-deliver/scripts/make_manifest.py` roles | `decisions/*.md` (the ACCEPT-BAND evidence) and a root `BUILDER_REPORT.md` are `unclassified` | open |
| 12 | `stl-re-deliver/scripts/package_zip.py` | `*.npz` QA arrays (2 × 18.6 MB) were shipped, so the zip was 55.5 MiB, above the 30 MiB chat upload limit, and could not be sent | fixed: `*.npz` is regenerable, `--max-zip-mb 29` refuses an oversize zip, and the fix is documented in `delivery-package.md` and `CLAUDE.md` |

The builder's and verifier's full notes are in `OD-H21/BUILDER_REPORT.md` §6 and `OD-H21/VERDICT.md`.
