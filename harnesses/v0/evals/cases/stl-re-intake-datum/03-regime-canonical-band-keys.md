# Case: `intake.py regime` writes canonical flat band keys

## Skill
`stl-re-intake-datum`

## Input (repo paths)
None (this subcommand needs no scan; it declares the QA band regime, run-contract §12). Cited
evidence: `harnesses/v0/skills/stl-re-orchestrate/references/run-contract.md` §12 "Band keys (canonical)";
`baseline/oomwoo-re-pipeline/RE_SPEC.md:170-175`; `baseline/skills/stl2step-build123d/SKILL.md:87`.

## Command or procedure
```
python3 harnesses/v0/skills/stl-re-intake-datum/scripts/intake.py regime --name RE_SPEC --out-dir <run>/intake
python3 harnesses/v0/skills/stl-re-intake-datum/scripts/intake.py regime --name baseline-skill --class plastic --out-dir <run>/intake
```
`intake.py regime --help`: `--name {RE_SPEC,baseline-skill,project-spec}`, `--source SOURCE`,
`--bands BANDS` (JSON string), `--class {plastic,machined}` (required for baseline-skill when
`--bands` is omitted), `--why WHY`, `--out-dir OUT_DIR` (required).

## Expected outcome
Cited from the review's fix record (`harnesses/v0/reviews/stl-re-intake-datum.md` "Fixes applied", item V1):
`intake/regime.json#bands` must always be one flat object with exactly the four canonical keys
`{p95_mm, max_mm, tier1_abs_mm, interface_max_mm}` (`null` when the regime does not gate that
band) — any other key name is rejected. RE_SPEC fills all four
(1.6 / 4.0 / 0.15 / 0.8 mm, `RE_SPEC.md:170-175`, unchanged values); baseline-skill fills only
`p95_mm`/`max_mm` for the chosen material class and records the class as
`regime.json#material_class` (`plastic|machined`), never nested inside `bands`. This is an
exact-match check against the recorded values, not a tolerance band.

## Baseline behaviour (cited)
Before this fix, intake wrote `RE_SPEC` bands under different key names
(`tier2_p95_mm`/`tier2_max_mm`/`tier1_abs_mm`/`interface_max_mm`) while `stl-re-verify` read
`p95`/`max`/`tier1_abs`/`interface_max`, so every band silently resolved to `None` and the gate
"failed open" (BLOCKER V1 in `harnesses/v0/reviews/stl-re-verify.md`): an `APPROVED` verdict was reachable on
an OD-scale band miss (p95 0.448, max 2.49) with zero band fails recorded. The baseline skill
itself (`analysis/baseline/stl2step-skills.md` §5.6/§6.11) offers only "blocking PASS" bands per
material class with no cross-skill key contract at all.

## Last observed result
**Run this session** (2026-09-25): `intake.py regime --name RE_SPEC` produced
`bands: {"p95_mm": 1.6, "max_mm": 4.0, "tier1_abs_mm": 0.15, "interface_max_mm": 0.8}`.
`intake.py regime --name baseline-skill --class plastic` produced
`bands: {"p95_mm": 0.3, "max_mm": 0.8, "tier1_abs_mm": null, "interface_max_mm": null}`,
`material_class: "plastic"`. Both match the canonical shape exactly. **PASS.**
