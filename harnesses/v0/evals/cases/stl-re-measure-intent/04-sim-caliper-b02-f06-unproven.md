# Case: `sim_caliper.py` classifies B02 F06 as UNPROVEN, not struck or passed

## Skill
`stl-re-measure-intent`

## Input (repo paths)
- `golden-examples/OOM-B02_side-brush-3-arm/2_mesh_cleaned/OOM-B02.stl` (full-res scan)
- `golden-examples/OOM-B02_side-brush-3-arm/2_mesh_cleaned/alignment.json`
- Golden reference: `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/PARAM_TABLE.md:108-121`
  (F06 = 24.84, golden window 25.99…27.08, "1.15 mm below", declared struck in the golden run);
  `golden-examples/OOM-B02_side-brush-3-arm/5_reference/MEASUREMENTS.md:61` and
  `6_RE_work/PARAM_TABLE.md:41` (F10 arm-width scan dilation, caliper 5.33 vs scan mean 5.89,
  the source of the `--scan-offset` value below)

## Command or procedure
```
python3 harnesses/v0/skills/stl-re-measure-intent/scripts/sim_caliper.py \
  --mesh <OOM-B02.stl> --alignment <alignment.json> \
  --z 1.0 --mode outside --r-band 12,14 --reading 24.84 --reading-unc 0.1 --scan-offset 0.56 \
  --out <run>/measure/f06.json
```
(`sim_caliper.py --help`: `--scan-offset d`, "measured per-scan dilation, mm (largest scan-minus-
caliper gap among the OTHER calipered dims of this same scan, e.g. B02 F10: scan 5.89 - caliper
5.33 = 0.56, MEASUREMENTS.md:61 / PARAM_TABLE.md:41). Not a threshold, and never invented.")

## Expected outcome
Cited from `harnesses/v0/reviews/stl-re-measure-intent.md`, BLOCKER B2: F06's margin below the achievable
window (0.148 mm on this reproduction) is smaller than the measured scan dilation on this same
scan (0.56 mm, from F10). The finding states this makes "F06 is still struck" **not proven** by
the golden's own evidence. Expected classification is **UNPROVEN ("within measured scan
dilation")**, distinct from both STRIKE and a clean PASS — this is a qualitative three-state
outcome (STRIKE / UNPROVEN / use), not a numeric tolerance.

## Baseline behaviour (cited)
Before the fix, the strike rule was `reading < window_min − u` with no allowance for scan
dilation at all (`SKILL.md:164-167`, `references/intent-rules.md:128-133` pre-fix). Applied to
F06 that rule gives a clean STRIKE, matching the golden's own historical treatment of F06
("still struck", `SKILL.md:291` pre-fix) — but the review showed that same rigid rule would also
have struck F10 (5.33 mm caliper vs a 5.8–6.3 mm scan window, a golden-**accepted** Tier-1 PASS,
`PARAM_TABLE.md:40,157`), so the un-fixed rule cannot distinguish a real miss from ordinary scan
dilation.

## Last observed result
**Run this session** (2026-09-25), on the post-fix script: window **24.988 .. 27.246** (jaws @
59.00° / 143.35°), coverage 0.878, reading 24.840 ± 0.1, `--scan-offset 0.56` →
**"UNPROVEN: below the window but within the measured scan dilation offset; do not build to it,
do not strike it — ask for a jaw-placement photo or re-measure."** This matches
`harnesses/v0/reviews/stl-re-measure-intent.md` "Fixes applied (round 1)", B2: "F06 (24.84) on the B02
full-res scan is now UNPROVEN both with no offset and with the measured F10 offset (0.56 mm)...
since its margin (0.148 mm) never exceeds an available offset." **PASS.**
