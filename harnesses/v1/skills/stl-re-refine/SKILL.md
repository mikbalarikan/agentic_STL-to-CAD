---
name: stl-re-refine
description: Staged deviation refine loop for scan-to-CAD. Starting from a feature tree with the datum and the base body, it repeatedly measures signed scan<->CAD deviation, splits red regions into clusters, fits scripted hypotheses (cylinder hole/boss, stepped revolve, prism with draft, offset pocket, lathe cut, plane cut), really builds each candidate, and keeps a feature only if it lowers the objective and fixes its own cluster. Use after stl-re-build has a base tree, or when verify reports unexplained clusters.
---

# stl-re-refine (harness v1)

You do not write geometry. `scripts/loop.py` proposes, builds and measures features. You
**start** it with a good base, **answer** decision cards when you run it with `--arbiter agent`,
and **review** what it accepted. Every number here is a builder self-check, not QA
(CHK-INDEP): verify runs afterwards in a fresh context.

## 1. Start from a base tree

Write `build/base_tree.json` with `stl-re-build`. It holds:
- the datum frame (from `intake/alignment.json`);
- the dominant silhouette as one or two nodes: a sketch-extrude of the outline, or a revolve of
  the main turned profile.

Do not add holes, ports or pockets yourself. The loop finds them, and it measures them on the
scan.

Examples:
- `examples/od_h22/base_tree.json`: flange outline + core revolve.
- `examples/drm_screw/base_tree.json`: pentagon prism.

## 2. Run the loop

```
python3 <skill>/scripts/loop.py --tree build/base_tree.json --params measure/params.json \
    --scan input/scan.stl --alignment intake/alignment.json --band <regime p95 band> --out refine/
```

Defaults: 150k scan samples, at most 25 rounds, and `--arbiter auto`.

Each round:
1. Pick the largest red cluster.
2. Build and measure its hypotheses. Each one carries its own variants: through or blind,
   draft ±, bridged into the host.
3. Accept the best candidate only if all of these hold:
   - J falls;
   - the candidate fixes ≥ 50 % of its own cluster;
   - the gain is ≥ 30 % of what fixing that cluster could give.
4. Try to merge sibling clusters into one repeated node (pattern).

A cluster that fails 3 times becomes an **open point**. A cluster that is mostly a short,
small-radius arc becomes a **blend candidate**: a fillet for the finishing stage, never a body.

## 3. Decision cards

When the two best candidates are of different kinds and within 1 % in J, the loop writes
`refine/cards/NNN.json`.
- With `--arbiter auto` it takes the lower J and records `answered_by: auto`.
- With `--arbiter agent` it stops. Then:
  1. Read the card: `python3 scripts/cards.py list refine/`.
  2. Answer it: `python3 scripts/cards.py answer refine/cards/NNN.json <i> --by <you> --why "..."`.
  3. Paste the printed line into `DECISIONS.md`.
  4. Re-run the same command. The loop is deterministic and applies the answer.

The guided mode (M4) shows the same cards to the user.

## 4. Review before verify

- `refine/refine_log.json`: per round, every candidate with its J, the share of its cluster it
  fixed, or why it was rejected; then the open points and the blend candidates.
- `refine/feature_tree.json`: base + accepted nodes.
- `refine/params_refine.json`: every measured value with `source: scan` and its estimator.

Check what the loop added:
- Each accepted node must be a real design feature. If one reads like a patch (an odd skew
  axis, many small instances, a chain at the segment limit), remove it from the tree and list
  its cluster as an open point.
- Move the measured params into `measure/params.json` (keep `source`, `estimator` and
  `evidence`). Rename them to design names (`R03_r` → `tube_bore_r`). Round them within noise
  only.
- Fillets: turn the blend candidates into `fillet` nodes at the end of the tree. Use
  `stl-re-build` and measure the radii with `stl-re-measure-intent`.
- Then build with `stl-re-build` and hand over to `stl-re-verify`.

## Limits (M2)

- The loop adds features. It does not yet re-fit the size of a feature that is already in the
  tree. A wrong base dimension shows up as a thin cluster on that face.
- Repeated features inside ONE cluster (two ports joined by a rib) are added in separate
  rounds, not as one pattern.
- No sweeps, helices, freeform skins or sheet metal.
