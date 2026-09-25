# CHANGES_V3 — v2 → v3 upgrade report (2026-08-01)

Implemented per the ratified V3 work order (`V3_UPGRADE_PROMPT.md`). No part was
processed, modeled, or intaken in the upgrade session. **Status: awaiting ratification.**

## 1. Why v3 (the two failures)

1. **Lego-slop geometry** — drafters produced polygon-like patchwork (OOM-W01 attempt 1:
   5,485 faces vs the 734-face reference) because nobody planned the modeling approach
   and nobody reviewed until the end.
2. **Review came too late** — QA gated only the finished part; a bad modeling strategy
   was already baked in.

v3 answer: a ratified MODELING PLAN before any geometry, manager review at FEATURE
granularity throughout the build, and the whole conversation auditable on GitHub.
Priority is quality over token cost.

## 2. File-by-file changes

### Spec & prompts (Drive `_PIPELINE\`, to become the repo `_PIPELINE/`)

| File | Change | Rationale |
|---|---|---|
| `RE_SPEC.md` | **Rewritten as v3.** New: §1b repo workspace/layout, §5 roles + feature-gated loop (re-planner / re-drafter / manager-as-orchestrator / re-qa-verifier, FEATURE BUDGET, circuit breakers), §6 ANTI-LEGO doctrine incl. standing Tier-0 surface-quality check, §7 `render_views.py`, §8 GitHub protocol, §9 README.md-based deliverables. Kept verbatim in substance: data hierarchy §2, datums §3, Tier-1/Tier-2 bands §4, ops rules §10, honesty rules. v2 preserved as `RE_SPEC_v2_SUPERSEDED.md`. | Work order §3–§4. Tier-0 was already born on OOM-W01; it is now line-wide because it is the numeric teeth of the anti-Lego doctrine (W01 proved Tier-2 deviation cannot detect patchwork — attempt 1 sat ON the scan and was garbage CAD). |
| `SESSION_PROMPT.md` | **Rewritten as v3 production prompt**: manager-run feature-gated loop, GitHub protocol, ONE live drafter per part continued via SendMessage, manager views every submission's images, standing "process OOM-Xnn" behavior. v2 preserved as `SESSION_PROMPT_v2_SUPERSEDED.md`. | Work order §3.1/§5.2. |
| `TRACKER.md` | **New** — the parts tracker moved out of RE_SPEC §7, v2 rows migrated verbatim. Updated in each PR's merge commit once the repo exists. Status flow now `BUILD (feature F<NN>/<budget>)` instead of `REBUILD (N/3)`. | Work order §3.4: tracker lives in the repo and updates atomically with delivery. |
| `TEMPLATES\MODELING_PLAN.md` | **New template**: strategy summary, FEATURE BUDGET, ordered feature table (op / datum / driving dims with source / acceptance criterion), interior-feature mapping, plan risks. | The plan is the v3 keystone artifact — it is what the drafter executes and the manager enforces. |
| `TEMPLATES\INTAKE_CARD.md` | §6 now summarizes strategy and points to the MODELING PLAN. Otherwise unchanged. | Keep-and-extend per work order §1. |
| `TEMPLATES\MEASUREMENTS.md` | **Unchanged.** | Caliper workflow is keep-as-is (§4 of the work order). |
| `SETUP.md` | **New** — env setup for Windows + Linux VPS (python ≥3.11, pip deps, gh, git identity, LFS, local-clone rule, machines.toml). | Work order §3.5. |
| `machines.toml` | **New** — machine paths keyed by hostname (`mery` filled in; `vps-placeholder` to be renamed at VPS setup). Tools never hardcode paths. | Work order §3.5. |

### Tools (`_PIPELINE\tools\`)

| File | Change | Rationale |
|---|---|---|
| `render_views.py` | **New, replaces Blender.** Pure-Python headless renderer: STEP (OCP tessellation + true BRep edges), STL (trimesh + dihedral edges), build123d `.py` (exec, `result` convention). Standard iso/front/top/right; on-demand `--section X|Y|Z off`, `--wireframe` (with per-view silhouettes), `--closeup bbox`, `--dir dx,dy,dz`, `--overlay scan.stl --align alignment.json`. numpy z-buffer + lambert shading, scale bar + view label on every frame, cad-section no-clip rule on sections. | One consistent image pipeline for intake, feature review, QA, and final docs, working identically on Windows and the VPS. Blender was a Windows-only, install-fragile dependency that most parts ended up bypassing anyway (z-buffer precedent on B02/E03/W01). |
| `blender_doc_render.py` | **DELETED** after the replacement passed its smoke test. | Work order §3.3. |
| `sync_to_drive.py` | **New** — copies merged deliverables (STEP → `4_STEP\`, README/VERDICT → `7_docs\`, `views/final/*` → `7_docs\views\`) from the repo `main` clone to the Drive part folders; refuses to run off-main; no-ops where `sync_enabled = false` (VPS). `--dry-run` supported. | Work order §3.4: Drive stays the delivery shelf, repo is the workshop. |

**Smoke tests run (TESTED):**
- `render_views.py` on `OOM-E05.step`: 4 standard views + 4 wireframes + section Z=−3 — all images viewed, part legible, edges crisp, nothing clipped.
- On `OOM-E05.stl` (scan): iso, front, custom `--dir`, `--closeup` — viewed.
- Overlay `OOM-E05.step` + scan + real `alignment.json` (`matrix_4x4`) — viewed; scan registers on CAD correctly (orange over gray, cable tail visible).
- build123d `.py` input (stepped disc + bore) — viewed, correct.
- `sync_to_drive.py --dry-run` against a fake repo tree: hostname resolution, Drive-folder glob (`OOM-E05*` matched), copy plan, missing-file skip — all correct; nothing written to Drive.

**UNTESTED (no silent assumption of success):**
- `render_views.py` on Linux (pure-Python/Agg so expected fine — verify via SETUP.md §4 at VPS setup).
- `sync_to_drive.py` real (non-dry) copy and the on-main refusal path against a real git clone.
- Git LFS routing for >50 MB scans (no repo yet).
- The whole GitHub protocol end-to-end (issue → branch → per-feature commits → PR review thread → merge) — **blocked: `gh` is not installed on this machine** (see §5).
- `effort: high` agent frontmatter is documented as supported; behavior not directly observable in this session.

### Agents (`~\.claude\agents\`)

| Agent | Change | Rationale |
|---|---|---|
| `re-planner` | **New (replaces `re-mesh-analyst`, deleted).** opus, effort high. Intake AND modeling strategy: photos + rendered STL views + trimesh analysis → INTAKE CARD + MEASUREMENT REQUEST + MODELING PLAN with FEATURE BUDGET (≤ ~12 ops before fillets typical). Anti-Lego plan doctrine embedded. | Failure #1: nobody planned the modeling approach. Now a dedicated strategist does, and the plan is ratified before any geometry exists. |
| `re-drafter` | **New (replaces `re-modeler`, deleted).** build123d ONLY, ONE feature at a time: build → render views → commit → push → PR submission comment → WAIT for manager verdict. Never self-approves, never merges, never deviates; plan mismatch = stop-and-report. One drafter lives per part across all features. Authors the part README.md at delivery. | Failure #2: review must interleave with building. The drafter's loop makes unreviewed progress impossible. |
| `re-qa-verifier` | **Revised (kept).** Same independent doctrine; added: Tier-0 surface-quality audit, reverse-direction Tier-2 reporting (W01 lesson: missing material hides from forward-only), ICP-convergence honesty (W01 lesson: gate untrusted when ICP hits its cap), renders its own views via `render_views.py`, writes `VERDICT.md` into the repo part folder. | Feature review never replaces the independent gate — both are mandatory. |
| `re-doc-artist` | **RETIRED (deleted).** | Final images come from `render_views.py` (same script the whole line uses). |
| `re-report-writer` | **RETIRED (deleted).** | The per-part PDF is replaced by `<part>/README.md` in the repo — versioned, reviewable on the PR, no MiKTeX dependency. Drafter authors it; manager checks it before merge. |

### Unchanged from v2 (deliberately)

- Data-fusion hierarchy (calipers ±0.15 blocking > STL form > photo intent) and both
  measured gates (Tier-1 ±0.15; Tier-2 p95 1.6 / max 4.0 / named-interface 0.8).
- Measurement-request workflow and caliper sheet template; external caliper gate.
- Uniform scale-correction rule; local-scratch rule; lean handoffs; honesty rules.
- build123d ratified (bake-off closed); per-part circuit breaker 3 full loops.

## 3. New blocking rules introduced (summary)

1. MODELING PLAN + FEATURE BUDGET ratified on the issue before any geometry.
2. Per-feature manager review: drafter waits on every feature; verdicts on the PR.
3. Anti-Lego doctrine (RE_SPEC §6) incl. Tier-0 surface quality, line-wide.
4. Per-feature circuit breaker: 3 REVISEs on one feature → HALT to Muhammed.
5. Silent budget overrun = automatic REVISE; raises need written justification.
6. Only the manager approves/merges; merge only after QA APPROVED; tracker updated in
   the merge commit; deliverables synced to Drive from main.

## 4. Repo skeleton (ready to push once the repo exists)

`_PIPELINE/` as it now stands on Drive (spec, session prompt, templates ×3, tools ×2,
TRACKER.md, SETUP.md, machines.toml, this file) + per-part folders created as parts
enter the line. Proposed `.gitattributes`: `OOM-*/scan/*.stl filter=lfs diff=lfs merge=lfs -text`.

## 5. BLOCKED ITEMS — need Muhammed

1. **`gh` CLI is not installed on MERY** (`gh` not found in PATH or standard installs).
   The work-order prereq `gh auth status` cannot pass. Needed once:
   `winget install GitHub.cli`, then `gh auth login` (interactive — your GitHub
   account). I did not install software or handle credentials without you.
2. **Repo creation approval** (external action, per the work order): private repo
   `oomwoo-re` on your GitHub account — confirm the name or give another.
3. After 1+2, the remaining §5 step runs: push the `_PIPELINE` skeleton, open the demo
   issue + demo PR on a dummy branch showing the submission/verdict comment format with
   inline images, then hand you the links for ratification.

## 6. First-run instructions (after ratification + repo exists)

### Windows (MERY)
1. `SETUP.md` §1–2 (deps already present: python 3.13.13, build123d 0.10.0,
   trimesh 4.12.2, matplotlib 3.11.0, OCP ok; missing only gh).
2. Clone to `C:\src\oomwoo-re` (machines.toml already points there).
3. Start a session with the new `SESSION_PROMPT.md`; say `process OOM-W02` (or any
   part with scan + photos). The line will: render intake views → re-planner → GitHub
   issue → WAIT for your calipers + plan GO on the issue → feature loop on the PR →
   QA → merge → sync to Drive.

### Linux VPS
1. `SETUP.md` §1 + §3; rename `[vps-placeholder]` in `machines.toml` to the real
   hostname (commit that).
2. Working scans come from the repo (`<part>/scan/`), so no Drive mount is needed;
   `sync_enabled = false` — final Drive sync stays on the Windows box.
3. Same session prompt, same flow; verify the SETUP.md §4 render smoke test first.

## 6b. ADDENDUM — DATUM & REFERENCING UPGRADE (2026-08-01, same day)

Executed per `DATUM_UPGRADE_PROMPT.md` (A–H) before the repo push:

- **A — RE_SPEC §3 rewritten** as the full DATUM & REFERENCING procedure: scale check
  always precedes datum work; DOF ladder (primary levels 3 DOF / secondary clocks 1 /
  origin pins 2 — all 6 accounted, none twice); selection rules (functional beats
  largest, chassis-mating interface preferred as primary for assembly-meaningful
  frames, axis fits from normals — bbox centers forbidden); RANSAC fit-quality duty at
  tol ≈ scan noise with STOP on excess residuals; the F00 gate (datum = first
  manager-approved feature, outside the budget; **alignment.json change after F00
  approval = plan reset to F01**); mirrored sets = one hand + a named mirror plane.
  Intent snapping kept as §3.8.
- **B — alignment.json schema v2** (§3.7): `matrix_4x4` (unchanged, mandatory) +
  `scale_factor`, `scan_noise_mm`, `primary`/`secondary` fit records (type, region,
  RMS/max residuals), named `origin` definition. Consumers tolerate extra keys —
  `render_views.py --align` reads only `matrix_4x4`, so v1 files still render
  (TESTED with OOM-E05's v1 alignment.json); QA tooling written per-part consumes v2.
- **C — `render_views.py --datum` mode**: iso + front/top/right of the ALIGNED mesh
  with RGB axes triad (X red / Y green / Z blue) + origin crosshair marker; `--align`
  now applies to the INPUT when no `--overlay` is given. **TESTED** on OOM-E05's scan
  + its real alignment.json — triad lands on the datum (face plane Z=0, axis on Z),
  images viewed.
- **D — re-drafter**: F00 duties added (align per intake card §5, write schema-v2
  alignment.json, submit `--datum` views + residuals, WAIT; STOP on residuals > scan
  noise or missing datum feature; post-approval alignment change = plan reset).
- **E — re-qa-verifier**: DATUM AUDIT as gate step 0 — independent re-fit of primary +
  secondary on the RAW scan, own transform, compare vs alignment.json; angular error
  and origin offset reported in every VERDICT.md; **PASS ≤ 0.3° / ≤ 0.15 mm**; FAIL ⇒
  REVISE routed at F00 (deviation numbers meaningless). Thresholds kept at the work
  order's values: 0.3° ≈ 0.26 mm lateral over a 50 mm part — tightening below that
  approaches the scan-noise floor and would produce false REVISEs; revisit only with
  measured audit history.
- **F — re-planner**: datum plan duty synced with intake card §5 (three named datums
  with functional WHY, chassis-mating primary preference, mirrored-set convention,
  flag no-good-datum parts at intake).
- **G — MEASUREMENTS template**: "Datum ref" column added to §B so every requested dim
  is datum-referenced ("base plane → top of boss", "Ø about datum axis"); envelope
  dims unchanged.
- **H — SESSION_PROMPT** updated (loop starts at F00, manager verifies the triad on
  the `--datum` views; QA gate begins with the datum audit). SETUP.md needed no change
  (no tool install/interface steps affected).
- Template groundwork done earlier in another session and built upon, not redone:
  MODELING_PLAN F00 row + budget note, INTAKE_CARD §5 expansion.

**UNTESTED (addendum):** the QA datum-audit code itself is written per-part by the
verifier (no shared script yet — candidate for a future `tools/datum_audit.py`);
schema-v2 alignment.json has not yet been produced by a real F00 run.

## 7. Rollback

v2 files are intact: `RE_SPEC_v2_SUPERSEDED.md`, `SESSION_PROMPT_v2_SUPERSEDED.md`,
and byte-identical copies of all five deleted v2 agent definitions in
`_PIPELINE\_v2_SUPERSEDED_agents\` (the originals lived on C:\ with no version
history, so they were preserved here before deletion). `blender_doc_render.py` is
recoverable from Google Drive version history if ever needed.
