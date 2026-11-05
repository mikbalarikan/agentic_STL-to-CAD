# v1 skills

Install them with `python3 tools/harness.py install v1 [--dest DIR]`. The entry skill is
`stl-re-orchestrate`.

| Skill | Stage | What changed vs v0 |
|---|---|---|
| `stl-re-orchestrate` | entry, state machine | **Rewritten.** The stage order is intake → measure → refine → build → verify → deliver, with a review step between refine and build. `init_run.py` knows the v1 skills, stage exits and carry-forward (feature trees, not `model.py`). New `run_metrics.py` writes `run_metrics.json`. |
| `stl-re-intake-datum` | intake + datum | Unchanged from v0. |
| `stl-re-measure-intent` | measure | Unchanged from v0, apart from one boundary line. |
| `stl-re-refine` | refine (new) | Staged deviation loop: `devmap.py`, `classify.py`, `loop.py`, `refine_ops.py` (refit, slot merge, add-before-cut placement), `cards.py`, `compare.py`. |
| `stl-re-build` | build (new) | The JSON feature tree replaces v0's hand-written `model.py`: `treexpr.py`, `sketch2d.py`, `features.py`, `build_tree.py`, plus v0's export/validation scripts unchanged. |
| `stl-re-verify` | verify (fresh context) | `observability.py` gets the `sky` method (the default; `--obs-method cone` = v0). The patchwork census reads `feature_tree.json`. |
| `stl-re-deliver` | deliver | Design-source aware (`_common.design_sources`). A feature tree is rebuilt with `build_tree.py` in the repro check. The manifest and README name the tree. v0 `model.py` runs still work, and the fixture tests are unchanged. |

The intake, measure, verify and deliver `SKILL.md` texts keep v0's evidence citations. They
are longer than the new skills; slimming them is listed in the v2 backlog
(`../README.md`).
