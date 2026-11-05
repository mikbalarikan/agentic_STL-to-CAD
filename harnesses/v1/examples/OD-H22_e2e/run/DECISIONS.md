# DECISIONS — OD-H22_3-way-valve

Human decisions that gate this run. One entry per decision; never edit an old entry,
append a new one. Format: `- <date> | <who> | <decision id> | <decision> | <evidence path>`

Decision ids: REGIME (band regime chosen at intake), MEASUREMENTS (calipers supplied /
proceed scan-only), PART-CLASS (unsupported class: proceed or stop), ACCEPT-BAND
(BAND_NOT_MET accepted for delivery), HALT (reason and options), INDEP (verify could not
run in a fresh context), OTHER.

- 2026-11-05 | Ikbal (owner, OD-H22 run 2026-09-25) | MEASUREMENTS | No calipers; proceed scan-only (decision carried over from the v0 OD-H22 run, same scan sha256 4ebbb8c4...). Limitations: "Tier-1 not run", "absolute scale not caliper-verified"; re-run trigger: any caliper reading. | harnesses/v0/examples/OD-H22_3-way-valve/run/DECISIONS.md
- 2026-11-05 | Ikbal (owner, decision card 2026-09-25 10:54) | REGIME | baseline-skill, plastic: p95 <= 0.30 / max <= 0.80 mm (carried over from the v0 OD-H22 run; declared before any v1 gate number). | intake/regime.json
- 2026-11-05 | orchestrator (agent) | OTHER | v1 end-to-end check: intake/ and measure/ are the v0 OD-H22 artefacts (stages unchanged in v1, same scan); intake/work.stl regenerated with v1 intake.py stats, aligned_work.stl = work.stl x alignment.json#matrix_4x4. | intake/intake.json
- 2026-11-05 | orchestrator (agent) | OTHER | Refine review: all 14 accepted nodes kept (ports, tray pocket, tube/port bores, two slot-prism clip blocks, rib, clip-slot cut, ear holes; no patch-like node). 7 low-gain clusters stay open points; 8 blend candidates are not modelled as fillets in this run (declared limitation). refine/feature_tree.json -> build/feature_tree.json, refine/params_refine.json -> measure/params_refine.json. | refine/refine_log.json
- 2026-11-05 | orchestrator (agent) | OTHER | Correction to the refine-review entry above: refine_log.json lists 4 blend candidates, not 8. | refine/refine_log.json
