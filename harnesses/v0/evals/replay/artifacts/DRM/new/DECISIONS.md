# DECISIONS — drm_screw_cap

Human decisions that gate this run. One entry per decision; never edit an old entry,
append a new one. Format: `- <date> | <who> | <decision id> | <decision> | <evidence path>`

Decision ids: REGIME (band regime chosen at intake), MEASUREMENTS (calipers supplied /
proceed scan-only), PART-CLASS (unsupported class: proceed or stop), ACCEPT-BAND
(BAND_NOT_MET accepted for delivery), HALT (reason and options), INDEP (verify could not
run in a fresh context), OTHER.

- 2026-09-25 | owner (standing decision, relayed by caller) | REGIME | baseline-skill, consumer plastic: p95 ≤ 0.30 / max ≤ 0.80 mm (scan→CAD and observable CAD→scan) | intake/regime.json
- 2026-09-25 | owner (standing decision, relayed by caller) | MEASUREMENTS | proceed scan-only: no calipers and no photos exist; limitations "Tier-1 not run" and "absolute scale not caliper-verified" carried to the verdict | input/BRIEF (DRM/input/BRIEF.md), intake/MEASUREMENTS.md
- 2026-09-25 | owner (standing decision, relayed by caller) | OTHER | input scan.stl is a DECIMATED copy (≤0.028 mm from the original); every gate is INSPECTION ONLY, not an official grade | input/INPUT_HASHES.json#scan_resolution
- 2026-09-25 | owner (standing decision, relayed by caller) | OTHER | no human acceptance exists for this run: a BAND_NOT_MET cannot be delivered; there is no human reviewer | this file
- 2026-09-25 | owner | PART-CLASS | single-solid STEP requested (BRIEF.md); rigid moulded plastic prism/revolve part = supported class | DRM/input/BRIEF.md
- 2026-09-25 | agent (builder) | INDEP | verify run in the SAME agent context that built the model (no subagent tool available in this session); verify uses only the stl-re-verify scripts and does not import model.py/params.json; CHK-INDEP = finding | qa/review.json
- 2026-09-25 | agent | HALT | verify verdict HALT: only blocker is the decimated scan (INSPECTION ONLY); all inspection bands pass (s2c p95 0.078/max 0.309, observable c2s p95 0.066/max 0.277 vs 0.30/0.80). Options: (a) supply full-res scan and re-run stl-re-verify unchanged; (b) owner accepts inspection-only delivery (not covered by the contract); (c) stop. No deliver/ created. | qa/gate.json, qa/VERDICT.md
