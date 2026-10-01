# DECISIONS — dreame_brush_core

Human decisions that gate this run. One entry per decision; never edit an old entry,
append a new one. Format: `- <date> | <who> | <decision id> | <decision> | <evidence path>`

Decision ids: REGIME (band regime chosen at intake), MEASUREMENTS (calipers supplied /
proceed scan-only), PART-CLASS (unsupported class: proceed or stop), ACCEPT-BAND
(BAND_NOT_MET accepted for delivery), HALT (reason and options), INDEP (verify could not
run in a fresh context), OTHER.

- 2026-09-30 | owner (Ikbal), chat instruction | REGIME | baseline-skill, material_class plastic (p95 <= 0.30 / max <= 0.80 mm, baseline/skills/stl2step-build123d/SKILL.md:87). Owner wrote "p95 plastik parça toleransı kullan"; the regime's max band is kept as declared, not dropped | intake/regime.json
- 2026-09-30 | agent (delegated: owner supplied only the STL and asked for a finished delivery) | MEASUREMENTS | scan-only: no calipers or photos supplied. Carried limitations: "Tier-1 not run" and "absolute scale not caliper-verified", re-run trigger = caliper sheet (intake/MEASUREMENTS.md) filled | intake/MEASUREMENTS.md
- 2026-09-30 | agent (delegated, see above) | OTHER | inspection-only, no full-res scan: the supplied file is named "..._decimated_20MB.stl" (391,998 faces) and no full-resolution export was supplied. Graded as inspection-only: verdict at most APPROVED_WITH_LIMITATIONS, re-run trigger "full-res scan available" | input/INPUT_HASHES.json
- 2026-09-30 | agent | PART-CLASS | brush-roll core with twisted (helical) constant profile + drive hub; bristles are a soft feature: not modelled, excluded from the gate as a declared zone (precedent B02 INTAKE_CARD R4) | intake/INTAKE_CARD.md
- 2026-10-01 | agent (orchestrator) | OTHER | it1 verdict REVISE (verify, errors []): CHK-ENUM missed slot undercut foot. Superseded with --route measure (iteration 2 of 3); intake/datum unchanged (the frame was not at fault); feature 2 of INTAKE_CARD §5 now reads "4 T-slots: 1.24 neck to r 6.0, flared foot to the floor" | _it1_SUPERSEDED/qa/VERDICT.md
- 2026-10-01 | agent (delegated) | OTHER | slot-occupant occlusion declared before re-grading: in 8-40 mm z-windows per slot the slot floor is hidden under a ragged surface at r 6-7.2 (lodged hair/bristle/debris), while the floor that is visible matches. Verify may use a named mask "slot occupants" (scan points inside the slot void that are not wall/floor, and CAD slot walls/floor/foot that the occupant hides), reporting the unmasked numbers next to it | _it1_SUPERSEDED/qa/overlays/slot_floor_profile_qa.png
- 2026-10-01 | agent (delegated) | OTHER | local recess beside the slot-1 entry at the hub (z 0..2.5) is NOT modelled and NOT masked: asymmetric (1 of 4 entries), no photo to tell a feature from damage; it stays in the gate as a named local miss | measure/figures/m14_hub_recess.png
- 2026-10-01 | agent | OTHER | correction: the it1-REVISE entry said INTAKE_CARD §5 'now reads' T-slot; the card was not edited in place — the correction is the appended §10 addendum | intake/INTAKE_CARD.md
- 2026-10-01 | owner (Ikbal), chat answer | ACCEPT-BAND | accept scan_to_cad and cad_to_scan_observable (and zone) band misses for delivery, gate 830ff7000088 | decisions/accept_band_it2.md
- 2026-10-01 | owner (Ikbal), chat: "to know what max volume occupied I need to also add the brush wires as single body only fitted" | OTHER | add-on deliverable: core + fitted bristle envelope (0.2/99.8 % percentile fins per tuft row, tuft holes filled as roots) fused into ONE solid, plus the envelope alone; the verified core and its gate are unchanged; the envelope is checked separately (containment, soft band +-3 mm) | bristle/out/volumes.json
- 2026-10-01 | agent | OTHER | bristle add-on moved from bristle/ to addons/bristles/ (path references updated in its scripts and check files); independent containment check PASS on the soft band | addons/bristles/qa/BRISTLE_CHECK.md
