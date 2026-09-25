# Baseline (v0) — the skills and agent briefs being replaced

Snapshot of the reverse-engineering doctrine as it stood on 2026-09-25. The
new skills in this repo are written **from scratch**. These files are the
starting point to measure against and mine for rules. Do not edit them.

| Path | Origin | What it is |
|---|---|---|
| `skills/stl2step-build123d/` | `~/.claude/skills` | STL→STEP with trimesh + build123d (used for Dreame caps, OD-H12 pump) |
| `skills/stl2step-freecad/` | `~/.claude/skills` | Same method, headless FreeCAD toolchain |
| `skills/stl2dxf-facet-film/` | `~/.claude/skills` | Scan → developable film-kit DXF (watch covers); richest reference set |
| `agents/re-planner.md` | `~/.claude/agents` | OOMWOO RE v3: intake card, caliper request, modeling plan + feature budget |
| `agents/re-drafter.md` | `~/.claude/agents` | OOMWOO RE v4: one plan feature per PR in build123d |
| `agents/re-qa-verifier.md` | `~/.claude/agents` | OOMWOO RE v3: independent re-measure, Tier-0/1/2 gate, verdict |
| `oomwoo-re-pipeline/` | github.com/mikbalarikan/oomwoo-re `_PIPELINE/` @ 20c09cd | RE_SPEC (tolerance bands §4), v3/v4 change logs, session prompt, templates, part TRACKER (includes failures, e.g. OOM-M02 blend STOP), view renderer |

Left out: machine config/setup notes, superseded v2 files, `__pycache__`.
