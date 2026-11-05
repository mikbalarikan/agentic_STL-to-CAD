# DECISIONS — OOM-B02

Human decisions that gate this run. One entry per decision; never edit an old entry,
append a new one. Format: `- <date> | <who> | <decision id> | <decision> | <evidence path>`

Decision ids: REGIME (band regime chosen at intake), MEASUREMENTS (calipers supplied /
proceed scan-only), PART-CLASS (unsupported class: proceed or stop), ACCEPT-BAND
(BAND_NOT_MET accepted for delivery), HALT (reason and options), INDEP (verify could not
run in a fresh context), OTHER.

- 2026-09-25 | owner (standing decision, relayed by orchestrating agent) | REGIME | RE_SPEC: Tier-1 <=0.15 per calipered dim, Tier-2 p95<=1.6/max<=4.0, named interfaces <=0.8 | input/BRIEF.md; task brief
- 2026-09-25 | owner (BRIEF.md) | MEASUREMENTS | No caliper session. Photo-legible readings D-01..D-12 only (8 confirmed incl. 1 soft, 4 unassigned); scan-authority for everything else; +-0.1 mm effective on caliper-photo | input/MEASUREMENTS.md, input/BRIEF.md
- 2026-09-25 | owner (standing decision) | OTHER | Agent may accept its own verdict for REPORTING purposes only; no human acceptance (ACCEPT-BAND or APPROVED sign-off) exists for this run | task brief
- 2026-09-25 | owner (standing decision) | OTHER | Time-box: max 2 loops (tighter than the skill's 3) | task brief
- 2026-09-25 | orchestrating agent | INDEP | verify run by the SAME agent that built the model (no subagent/fresh-context tool available in this session); verify uses the skill's own QA scripts + separately written QA inputs; CHK-INDEP=finding | qa/review.json
- 2026-09-25 | orchestrating agent (owner standing decisions) | OTHER | it2 verdict BAND_NOT_MET (tier1 D-05 +0.174; Z-KEY interface max 1.167/1.606 > 0.8). Owner loop budget (2) used. Agent accepts the verdict for REPORTING only; NO human ACCEPT-BAND exists, so deliver/ is NOT created (CHK-PUBLISH) | qa/gate.json
