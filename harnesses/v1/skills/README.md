# v1 skills (in development)

| Skill | State |
|---|---|
| `stl-re-build` | **New in M1.** Feature-tree builder: `treexpr.py`, `sketch2d.py`, `features.py`, `build_tree.py`. The export and validation scripts are copied unchanged from v0 `stl-re-rebuild-build123d`. Replaces v0's hand-written `model.py`. |
| `stl-re-refine` | **New in M2.** Staged deviation loop: `devmap.py`, `classify.py`, `loop.py`, `cards.py`, `compare.py`. Results and open points: `../README.md` "M2 result". |
| `stl-re-orchestrate`, `stl-re-intake-datum`, `stl-re-measure-intent`, `stl-re-verify`, `stl-re-deliver` | Copied from v0 at M1 as the base for v1. Changed so far: `stl-re-verify/scripts/observability.py` + `deviation_gate.py` (M2 `sky` observability, default; `--obs-method cone` = v0). Their `SKILL.md` text is still v0 text and still points at `stl-re-rebuild-build123d`. They are rewritten (slimmed, wired to `stl-re-build` and the refine loop) in M2–M3. |

v1 is not installable yet: `HARNESS.json#skills` stays empty until M3, so
`tools/harness.py install v1` refuses.
