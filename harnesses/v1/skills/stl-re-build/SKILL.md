---
name: stl-re-build
description: Build a scan-to-CAD part as a JSON feature tree with build123d. The agent writes build/feature_tree.json (data, not code); one tested builder makes the STEP, checks every feature (validity, solid count, volume-delta sign), rolls back failures and logs fillets. Use once measure/params.json exists, or when a verdict or the refine loop changes a feature.
---

# stl-re-build (harness v1)

You write **data**. `scripts/build_tree.py` turns it into geometry. Do not write a
`model.py`. If the tree cannot express a feature, stop and report which op is missing.

Schema and every op: `references/feature-tree.md`. Worked example:
`examples/od_h22/feature_tree.json`.

## Steps

1. **Read the inputs:**
   - `measure/params.json`: every value has a `source`;
   - the intake card's feature list;
   - `intake/alignment.json`.

   If a dimension you need is missing from `params.json`, send it back to measure. Do not
   invent it.
2. **Write `build/feature_tree.json`:**
   - the dominant silhouette first (one revolve or one sketch-extrude);
   - then the added bodies;
   - then the cuts;
   - fillets last. A fillet that must come earlier gets `local: true` and a `why`.

   Map every intake feature to a node, or list it under `"out_of_scope"` with a reason.
   Repeated features are one node with `repeat` over the measured per-instance lists.
3. **Build:**
   ```
   python3 <skill>/scripts/build_tree.py --tree build/feature_tree.json \
       --params measure/params.json --alignment intake/alignment.json --out build --part <part>
   ```
4. **Read the build result** from the summary printed on stdout, then `build/tree_log.json`:
   - A FAILED node names its error and has been rolled back. Fix that node only, then rebuild.
   - `unused_params` means the tree and the measurements disagree.
   - `literals` lists numbers that should be params or documented constants.
   - Fillets: `python3 <skill>/scripts/fillet_log.py summarize build/fillets.json`. Exit 2
     means a fillet was reduced or not applied. Fix it, or declare it for verify and deliver.
5. **Exit criteria:**
   - `tree_log.json#status == "OK"`;
   - `export_check.json` shows one valid closed solid in both frames.

   Every check here is a builder self-check, not QA. Verify runs in a fresh context
   (CHK-INDEP).

## Rules kept from v0

- No ruled lofts and no stacks of per-station extrusions. Fit one designed profile per region.
- Select edges by geometry (`edges` predicates), never by index.
- Place repeated features at their measured angles. Force symmetry only when the measured
  scatter is within noise.
- Sheet metal, freeform skins and multi-body deliverables have no supported strategy yet:
  HALT and ask.

## Tests

- `python3 tests/test_features.py`: library unit tests.
- `python3 tests/test_od_h22.py`: OD-H22 tree equals v0 `model.py`.
