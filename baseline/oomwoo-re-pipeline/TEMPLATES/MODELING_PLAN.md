# MODELING PLAN — <OOM-Xnn part name>
<!-- Produced by re-planner into <part>/MODELING_PLAN.md in the repo.
     Ratified by Muhammed on the part's GitHub issue together with the intake card.
     The re-drafter executes it feature by feature and MAY NOT deviate from it —
     a mismatch with reality is a STOP-and-report on the PR thread, never a silent fix.
     ANTI-LEGO (RE_SPEC §6): largest-sketch-first, few profiles, symmetry/patterns,
     facet-chasing forbidden. -->

## 1. Strategy summary (3–6 lines)
The part in one sentence; the dominant silhouette and which ONE sketch captures it;
main symmetry (revolve axis / mirror / polar pattern); what is boolean-ed onto/out of it.

## 2. FEATURE BUDGET
**N ops before fillets** (most vacuum-robot parts ≤ ~12). F00 (datum) and the
fillet/chamfer pass sit outside the budget — the budget counts geometry-creating ops. Exceeding N without a manager-approved raise on the
PR thread = automatic REVISE.

## 3. Ordered feature list
| F## | Operation | On datum/plane | Driving dims (source) | Acceptance criterion |
|---|---|---|---|---|
| F00 | DATUM: align mesh per intake card §5 → write `alignment.json` | primary flat → XY @ Z=0, clocking feature → +X/+Z, origin at named feature intersection | plane RANSAC tol ≈ scan noise; axis fit from normals (never bbox) | submitted views show axes triad on aligned mesh; residual plane fit ≤ noise; manager APPROVED before F01 |
| F01 | e.g. sketch+extrude: dominant silhouette | XY @ Z=0 | ENV-1 62.4 (caliper), profile from scan section Z=3 | silhouette overlays scan section within band; single solid |
| F02 | e.g. revolve: hub | axis +Z | Ø34.2 (caliper F02), profile r–z from scan | Ø re-measured 34.2±0.15 on STEP |
| … | | | | |
| Fnn | fillets/chamfers (last) | edges named | radii from sections | no failed fillet, still one valid solid |

Rules for the table:
- Every op is one of: sketch-on-plane / extrude / revolve / loft / sweep / boolean /
  fillet-chamfer / shell / pattern (pattern = one op regardless of instance count).
- Every driving dim carries its SOURCE tag (caliper / scan / photo-inferred).
- Every acceptance criterion must be checkable on the feature's view set (or a
  demanded section) — "looks right" is not a criterion.

## 4. Interior features
How each enumerated rib/boss/web from the intake card is produced (which F##), or an
explicit statement of why it is out of scope (occluded, ruled by Muhammed, etc.).

## 5. Known risks to the plan
Where the plan is most likely to meet reality-mismatch (occlusions, soft features,
uncertain counts), and what the drafter should report if it happens.
