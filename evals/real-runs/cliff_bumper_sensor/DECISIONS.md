# DECISIONS — cliff_bumper_sensor

Human decisions that gate this run. One entry per decision; never edit an old entry,
append a new one. Format: `- <date> | <who> | <decision id> | <decision> | <evidence path>`

Decision ids: REGIME (band regime chosen at intake), MEASUREMENTS (calipers supplied /
proceed scan-only), PART-CLASS (unsupported class: proceed or stop), ACCEPT-BAND
(BAND_NOT_MET accepted for delivery), HALT (reason and options), INDEP (verify could not
run in a fresh context), OTHER.

- 2026-09-30 | Ikbal (owner, session message) | REGIME | baseline-skill, material_class plastic: p95 <= 0.30 / max <= 0.80 mm (baseline/skills/stl2step-build123d/SKILL.md:87). User wrote "p95 plastik parça toleransı kullan". Declared before any gate numbers exist. | session message; intake/regime.json
- 2026-09-30 | Ikbal (owner, session message) | MEASUREMENTS | No calipers supplied (STL + 5 photos only); proceed scan-only, same as OD-H22 precedent. Limitations carried to verdict: "Tier-1 not run" and "absolute scale not caliper-verified", re-run trigger: any caliper reading. Photos are feature-identification only (no scale reference). | session message; input/INPUT_HASHES.json
- 2026-09-30 | Ikbal (owner, decision card) | OTHER | scan_resolution confirmed full-res ("Full-res original"): original scanner export, 499,218 faces, mean edge 0.13 mm. | input/INPUT_HASHES.json#scan_resolution
- 2026-09-30 | Ikbal (owner, decision card) | ACCEPT-BAND | Accept and deliver: accepts scan_to_cad:masked, cad_to_scan_observable, zone:Z-LENS and zone:Z-POCKET band misses, gate 78728df9af7e (created 2026-09-30T15:48:31+00:00); causes are lens transparency, a detached scan fragment and unscanned slot/pocket corners, not modelled geometry. | decisions/accept_band.md
