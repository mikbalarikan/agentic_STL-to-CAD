# Baseline audit — OOMWOO RE pipeline (agents + `_PIPELINE/`)

Scope: `baseline/agents/{re-planner,re-drafter,re-qa-verifier}.md` and
`baseline/oomwoo-re-pipeline/` (snapshot of `oomwoo-re/_PIPELINE/` @ 20c09cd, per
`baseline/README.md`). Every claim cites `path:line`. Numbers are reproduced verbatim
from the cited file; none are derived here.

Path shorthands used below: `AG/` = `baseline/agents/`, `PL/` = `baseline/oomwoo-re-pipeline/`,
`GE/` = `golden-examples/`.

---

## 1. Inventory

| File | Lines | What it is |
|---|---|---|
| `AG/re-planner.md` | 68 | Agent brief (header says "v3", `AG/re-planner.md:3`): intake card, caliper request + caliper guide, modeling plan + feature budget |
| `AG/re-drafter.md` | 68 | Agent brief (header "v4", `AG/re-drafter.md:3`): one plan feature per PR submission, build123d only, F00 datum first |
| `AG/re-qa-verifier.md` | 50 | Agent brief (header "v3", `AG/re-qa-verifier.md:3`): datum audit, validity, Tier-0/1/2, visual, VERDICT.md |
| `PL/RE_SPEC.md` | 472 | Spec v4 (ratified 2026-08-02, `PL/RE_SPEC.md:2`): data authority §2, datums §3, PASS bands §4, roles/loop §5, anti-Lego §6, view tooling §7, GitHub §8, DoD §9, ops §10, standing session §11, context relay §12 |
| `PL/CHANGES_V3.md` | 174 | v2→v3 upgrade report + datum addendum §6b |
| `PL/CHANGES_V4.md` | 28 | v3→v4 change table (13 items) |
| `PL/V4_NOTES.md` | 97 | Rationale for v4 (first v3 production run, OOM-E03/E05) |
| `PL/SESSION_PROMPT.md` | 106 | Manager (orchestrator) prompt, v4 |
| `PL/TEMPLATES/INTAKE_CARD.md` | 41 | Intake card template, §1–§8 |
| `PL/TEMPLATES/MEASUREMENTS.md` | 38 | Caliper sheet template (§A envelope, §B functional w/ Datum ref, §C extras) |
| `PL/TEMPLATES/MODELING_PLAN.md` | 40 | Plan template: strategy, FEATURE BUDGET, ordered F## table, interior mapping, risks |
| `PL/TRACKER.md` | 33 | Parts tracker, 21 part rows (`PL/TRACKER.md:12-33`) |
| `PL/tools/render_views.py` | 604 | Headless STEP/STL/.py renderer (std views, section, wireframe, closeup, overlay, `--datum`) |

Referenced but NOT in the snapshot: `SETUP.md`, `machines.toml`, `tools/sync_to_drive.py`
(`PL/CHANGES_V3.md:30-31,39`; left out per `baseline/README.md`), skills `cad-qa-gate` and
`cad-section` (`PL/SESSION_PROMPT.md:17,100-101`; `baseline/skills/` holds only
`stl2step-build123d`, `stl2step-freecad`, `stl2dxf-facet-film`), and the W01 Tier-0 script
`6_RE_work/surftypes.py` (`PL/TRACKER.md:32`).

---

## 2. Pipeline as specified

### 2.1 Roles

| Role | Nature | Source |
|---|---|---|
| Manager | The orchestrator session itself, highest model tier; never models; views every submission's images; sole approver/merger | `PL/RE_SPEC.md:187-188,230-236,402-407`; `PL/SESSION_PROMPT.md:3-9` |
| re-planner | Intake + modeling strategy (replaces re-mesh-analyst) | `PL/RE_SPEC.md:190-211`; `AG/re-planner.md:9-68` |
| re-drafter | Executes plan, build123d only, one feature at a time; fresh drafter per feature (v4) | `PL/RE_SPEC.md:213-228`; `AG/re-drafter.md:9-68` |
| re-qa-verifier | Independent final gate; trusts nothing from drafter | `PL/RE_SPEC.md:238-245`; `AG/re-qa-verifier.md:9-50` |
| Muhammed (human) | Calipers dims, confirms functional reading + plan, comments GO | `PL/RE_SPEC.md:298-300,381-383` |

### 2.2 Stages and hand-off artefacts

| # | Stage | Actor | Hand-off artefact(s) | Where specified |
|---|---|---|---|---|
| 0 | BEGIN: environment parity check (agents, skills, python deps, `gh`, `machines.toml`) — any missing → HALT | Manager | queue status report | `PL/RE_SPEC.md:364-373`; `PL/SESSION_PROMPT.md:98-106` |
| 1 | INTAKE: copy STL to local scratch, decimate if > ~15 MB, view photos + rendered STL views, trimesh analysis, enumerate interior | re-planner | **INTAKE CARD** (§1 identity, §2 scan health, §3 functional zones, §4 interior, §5 datum plan, §6 strategy, §7 risks, §8 measurement request) | `AG/re-planner.md:19-39`; `PL/TEMPLATES/INTAKE_CARD.md:5-41`; `PL/RE_SPEC.md:190-194` |
| 1b | Caliper request | re-planner | **MEASUREMENTS.md** pre-filled (ID/Feature/Type/Datum ref/Why; caliper column blank); 8–15 dims, 3 envelope first | `AG/re-planner.md:39-42`; `PL/TEMPLATES/INTAKE_CARD.md:38-41`; `PL/TEMPLATES/MEASUREMENTS.md:1-38` |
| 1c | Caliper guide | re-planner | **caliper_guide_*.png** 2–4 annotated views, RED=Tier-1 blocking / BLUE=second tier, row ID + jaw placement + scan-predicted value, scale bar; self-reviewed | `AG/re-planner.md:43-51`; `PL/RE_SPEC.md:195-206` |
| 1d | Modeling plan | re-planner | **MODELING_PLAN.md**: ordered F## (op / datum / driving dims w/ source / acceptance criterion) + **FEATURE BUDGET** | `AG/re-planner.md:52-57`; `PL/TEMPLATES/MODELING_PLAN.md:1-40`; `PL/RE_SPEC.md:207-211` |
| 1e | Manager anti-Lego sanity check of plan | Manager | — | `PL/SESSION_PROMPT.md:42-43` |
| 2 | WORK ORDER: GitHub issue per part (intake + plan + checklist + guide images); stays OPEN until PR merges | Manager | GitHub issue | `PL/RE_SPEC.md:298-303`; `PL/SESSION_PROMPT.md:44-47` |
| 3 | EXTERNAL GATE (blocking): human calipers dims, confirms reading + plan, comments GO | Human | filled MEASUREMENTS.md + GO comment | `PL/RE_SPEC.md:381-383`; `PL/SESSION_PROMPT.md:48-50` |
| 4a | F00 DATUM: align per intake §5, RANSAC plane, axis from normals, write `alignment.json` schema v2, `--datum` views; STOP if residuals > scan noise | re-drafter → Manager | `alignment.json` (v2), `views/f00/` datum set, PR submission | `AG/re-drafter.md:20-29`; `PL/RE_SPEC.md:126-157,215-217`; `PL/SESSION_PROMPT.md:52-57` |
| 4b | FEATURE LOOP per F##: build → render std views → one commit → push → submission comment ≤ ~3,000 chars → WAIT → APPROVED/REVISE | fresh re-drafter per feature; Manager rules | **per-feature commit** `OOM-Xnn F<NN>: <op> (<dims>)`, `views/f<NN>/`, re-exported STEP, **PR submission comment**, PR verdict comment | `AG/re-drafter.md:31-54`; `PL/RE_SPEC.md:217-236,304-312`; `PL/SESSION_PROMPT.md:58-67` |
| 5 | QA GATE: datum audit → validity → Tier-0 → Tier-1 → Tier-2 (both directions) → visual vs photos | re-qa-verifier | **VERDICT.md** (APPROVED/REVISE, routed findings) | `AG/re-qa-verifier.md:15-50`; `PL/RE_SPEC.md:238-245`; `PL/SESSION_PROMPT.md:68-72` |
| 6 | DELIVER: drafter writes part README.md (numbers from VERDICT.md), manager checks, merge (tracker in merge commit), `sync_to_drive.py` | re-drafter + Manager | README.md, `views/final/`, tracker row | `AG/re-drafter.md:60-64`; `PL/RE_SPEC.md:313-336`; `PL/SESSION_PROMPT.md:73-75` |
| — | CONTEXT RELAY at 300k tokens: HANDOVER comment, tracker `RELAY→ at F<NN>`, successor resumes from NEXT ACTION | Manager | HANDOVER PR comment | `PL/RE_SPEC.md:396-472`; `PL/SESSION_PROMPT.md:81-90` |

QA tiers (as named): Datum audit (step 0), Validity (1), Tier 0 surface quality (2),
Tier 1 calipers (3), Tier 2 scan skin (4), Visual (5) — `AG/re-qa-verifier.md:15-43`.

---

## 3. Gates and thresholds

Every numeric gate/threshold found in the group. "Applies to" names the artefact the
number is checked on.

| Gate / rule | Threshold (verbatim) | Applies to | Source |
|---|---|---|---|
| **Tier 1 — caliper dims** | \|CAD − caliper\| ≤ 0.15 mm, per dim, blocking | every dim in MEASUREMENTS.md, re-measured on FINAL STEP by verifier | `PL/RE_SPEC.md:168-170`; `AG/re-qa-verifier.md:28-30`; `PL/SESSION_PROMPT.md:32` |
| **Tier 2 — scan skin, whole part** | p95 ≤ 1.6 mm, max ≤ 4.0 mm | independent ICP + normal-based outer-skin mask | `PL/RE_SPEC.md:172-174` |
| **Tier 2 — named functional interfaces not caliper-covered** | max ≤ 0.8 mm | zones named in intake card §3 | `PL/RE_SPEC.md:175` |
| Tier 2 — interior/occluded | reported, not gated | interior buckets | `PL/RE_SPEC.md:176`; `AG/re-qa-verifier.md:34-35` |
| Tier 2 — reverse (scan→CAD) | reported (no separate band) | verifier | `AG/re-qa-verifier.md:33-34`; `PL/RE_SPEC.md:243` ("two-way") |
| Tier 2 — ICP convergence | unconverged ⇒ gate invalid (no numeric criterion) | verifier ICP | `AG/re-qa-verifier.md:37-38` |
| **Datum audit** | angular error ≤ 0.3°, origin offset ≤ 0.15 mm; FAIL ⇒ REVISE at F00 | verifier's own re-fit vs `alignment.json` | `PL/RE_SPEC.md:239-242`; `AG/re-qa-verifier.md:15-21`; `PL/SESSION_PROMPT.md:68-70` |
| Datum audit rationale | "0.3° ≈ 0.26 mm lateral over a 50 mm part" | — | `PL/CHANGES_V3.md:148-151` |
| **F00 datum fit quality** | plane RANSAC tol ≈ scan noise (0.05–0.1 mm); STOP if residuals (RMS + max) exceed scan noise | F00 submission | `PL/RE_SPEC.md:126-129`; `AG/re-drafter.md:22-27` |
| F00 approval | no sketch before F00 APPROVED; any later `alignment.json` change ⇒ plan resets to F01 | feature loop | `PL/RE_SPEC.md:131-136`; `AG/re-drafter.md:28-29` |
| **Tier 0 — surface quality (spec)** | face count consistent with plan ("reference-class parts ≈ hundreds, not thousands"), dominant area analytic, zero ruled-loft patchwork (qualitative) | final STEP; manager spot-checks mid-build | `PL/RE_SPEC.md:265-270`; `AG/re-qa-verifier.md:24-27` |
| Tier 0 — surface quality (W01 numeric form, TRACKER only) | ≤ ~600 faces, ≥60 % of area on analytic surfaces, zero ruled-loft faces | OOM-W01 | `PL/TRACKER.md:32` |
| Validity | single valid solid (or ruled count), positive volume, no shells/self-intersects (BOPAlgo) | final STEP | `AG/re-qa-verifier.md:22-23`; `PL/RE_SPEC.md:326-327` |
| **FEATURE BUDGET** | expected op count; "most vacuum-robot parts ≤ ~12 ops before fillets"; F00 and fillet/chamfer pass outside budget; pattern = one op | modeling plan | `PL/RE_SPEC.md:210-211`; `PL/TEMPLATES/MODELING_PLAN.md:13-16,29-30`; `AG/re-planner.md:56-57` |
| Budget overrun | silent overrun = automatic REVISE; raise needs written justification on PR | feature loop | `PL/RE_SPEC.md:251-253,263-264`; `AG/re-drafter.md:50-54` |
| Per-feature breaker | 3 REVISE on same feature → HALT to human | feature loop | `PL/RE_SPEC.md:248-249`; `PL/SESSION_PROMPT.md:64-65` |
| Per-part breaker | 3 full-loop iterations (post-QA REVISE cycles) → HALT | part | `PL/RE_SPEC.md:250`; `PL/SESSION_PROMPT.md:71-72` |
| Caliper instrument uncertainty | ±0.05 mm (spec) vs ±0.02 mm (template) — see §6 | calipers | `PL/RE_SPEC.md:91`; `PL/TEMPLATES/MEASUREMENTS.md:10` |
| Standard-size snap | caliper value snapped to standard if within ±0.1 mm | CAD params | `PL/RE_SPEC.md:92,160` |
| Scan-derived dims | "round within scan noise" | CAD params | `PL/RE_SPEC.md:160-161` |
| Scanner noise floor | ~0.5–0.8 mm | context | `PL/RE_SPEC.md:25` |
| Double-read rule | two reads differ by >0.05 mm → record both | MEASUREMENTS | `PL/TEMPLATES/MEASUREMENTS.md:6-7` |
| Global scale correction | consistent-factor disagreement of 3 envelope dims → ONE uniform scale; non-uniform → flag | mesh before datum | `PL/RE_SPEC.md:98-101,105-107` |
| Measurement request size | 8–15 dims (3 envelope first) | intake | `AG/re-planner.md:40`; `PL/TEMPLATES/INTAKE_CARD.md:39` |
| Caliper guide | 2–4 annotated views | intake | `AG/re-planner.md:43`; `PL/RE_SPEC.md:196` |
| Mesh decimation | > ~15 MB → decimated working copy; final QA vs raw scan | ops | `PL/RE_SPEC.md:347-348`; `AG/re-planner.md:20-21` |
| Submission comment | ≤ ~3,000 characters | PR comment | `AG/re-drafter.md:40`; `PL/RE_SPEC.md:218` |
| Context relay | 300k tokens, relay at next clean boundary | manager session | `PL/RE_SPEC.md:416-420`; `PL/SESSION_PROMPT.md:81-82` |
| Slack turn budget | hard-kill at 5400 s; end turns within ~60 min | VPS | `PL/RE_SPEC.md:451-455` |
| Concurrency | feature loop max 2 parts; intakes may fan out | manager | `PL/RE_SPEC.md:391-393`; `PL/SESSION_PROMPT.md:77-79` |
| Merge gate | merge only after VERDICT.md APPROVED; tracker updated in merge commit | PR | `PL/RE_SPEC.md:313-319` |
| render_views STL feature edges | dihedral 40.0°; tessellation deflection default 0.05 mm | renderer | `PL/tools/render_views.py:43,544` |

Note on provenance: CHANGES_V3 states Tier-1/Tier-2 numbers were carried over from v2
unchanged (`PL/CHANGES_V3.md:67-68`) and the Tier-2 bands were "ratified 2026-07-26
scan-adjusted" (`PL/RE_SPEC.md:172`); CHANGES_V4 confirms no measured gate changed in v4
(`PL/CHANGES_V4.md:23-25`).

---

## 4. Evolution v2 → v3 → v4

### v1→v2 (inherited lessons, `PL/RE_SPEC.md:25-27`)
Scanner noise ~0.5–0.8 mm ⇒ calipers are dimensional authority; only the verifier's
independent registration counts; interior must be enumerated at intake (a prior run
missed radial ribs, `AG/re-planner.md:31-32`); build123d won the bake-off.

### v2 → v3 (2026-08-01, `PL/CHANGES_V3.md`)

| Change | Motivating failure | Source |
|---|---|---|
| Ratified MODELING PLAN + FEATURE BUDGET before any geometry; re-planner replaces re-mesh-analyst | OOM-W01 attempt 1 "Lego-slop": 5,485 faces vs 734-face reference; nobody planned the approach | `PL/CHANGES_V3.md:6-16,59`; `PL/RE_SPEC.md:29-33` |
| Feature-granularity manager review; re-drafter replaces re-modeler (build→render→commit→PR→WAIT) | "Review came too late" — QA gated only the finished part | `PL/CHANGES_V3.md:11-12,60`; `PL/RE_SPEC.md:34-37` |
| Anti-Lego doctrine §6 + line-wide Tier-0 surface-quality check | W01 proved Tier-2 cannot detect patchwork (attempt 1 sat on the scan and was garbage CAD); cause `Polyline` sections + `loft(ruled=True)` | `PL/CHANGES_V3.md:24`; `PL/TRACKER.md:32` |
| Verifier: reverse-direction Tier-2, ICP-convergence honesty, own renders, VERDICT.md in repo | W01: missing material hides from forward-only; ICP hit its cap | `PL/CHANGES_V3.md:61` |
| `render_views.py` replaces Blender; re-doc-artist + re-report-writer retired; PDF → README.md | Blender Windows-only / install-fragile, bypassed on B02/E03/W01 | `PL/CHANGES_V3.md:37-38,62-63` |
| GitHub protocol (issue/branch/PR per part, one commit per feature), TRACKER split out | auditability; atomic tracker update | `PL/CHANGES_V3.md:14-15,26` |
| **§6b Datum addendum**: DOF ladder, functional-beats-largest, normals not bbox, RANSAC fit duty, F00 gate, alignment.json schema v2, `--datum` views, QA datum audit ≤0.3°/≤0.15 mm, MEASUREMENTS "Datum ref" column | (Datum upgrade work order; no single failure named — schema-v2 had "not yet been produced by a real F00 run") | `PL/CHANGES_V3.md:119-166` |

### v3 → v4 (2026-08-02, `PL/CHANGES_V4.md`, rationale `PL/V4_NOTES.md`)

| Change | Motivating failure / evidence | Source |
|---|---|---|
| Fixed 300k-token relay (was 40 % / 50 % of 1M) | run-1 quality fine at 300k; relay near-free | `PL/V4_NOTES.md:24-27`; `PL/CHANGES_V4.md:9` |
| Automated succession; manager tier rule (highest tier, successors inherit) | tier gap over Opus workers IS review authority | `PL/V4_NOTES.md:28-37,82-85`; `PL/CHANGES_V4.md:10-11` |
| Part issue stays OPEN until merge | issue #3 closed while F05–F07 held on pin re-measures | `PL/V4_NOTES.md:41-45`; `PL/CHANGES_V4.md:14` |
| Submission comment ≤ ~3k chars | comments grew 6.7k → 8.9k → 14k (F01→F03) | `PL/V4_NOTES.md:46-51`; `PL/CHANGES_V4.md:13` |
| Tracker cells = status + counter + links | E03 cell became multi-thousand-word dump | `PL/V4_NOTES.md:52-55`; `PL/CHANGES_V4.md:15` |
| Fresh drafter per feature | "Drafter #1 could not be resumed — transcript recycled" | `PL/V4_NOTES.md:56-61`; `PL/CHANGES_V4.md:12` |
| Environment parity at BEGIN; agents/skills shipped in repo | intakes ran "in-context, not organisationally independent" (B02/E03/E05) | `PL/V4_NOTES.md:62-66,86-88`; `PL/CHANGES_V4.md:16-17` |
| Out-of-order features with stated dependency | E03 F12 ran before F04–F07 | `PL/V4_NOTES.md:68-71`; `PL/CHANGES_V4.md:18` |
| Pre-v3 deliveries grandfathered | E05 shipped Blender+PDF | `PL/V4_NOTES.md:72-75`; `PL/CHANGES_V4.md:19` |
| One session per clone / `git worktree` | two sessions raced (vanished branch, foreign commit) | `PL/V4_NOTES.md:76-78`; `PL/CHANGES_V4.md:20` |
| §7 absolute `?raw=true` image URLs | spec self-contradiction (relative vs absolute) | `PL/CHANGES_V4.md:21` |
| (post-v4, "v4.1") VPS declared-demotion waiver; user-level agent `diff` check | VPS pins `opus`; stale v2 verifier shadowed v4 gate | `PL/RE_SPEC.md:408-414,369-373`; `PL/TRACKER.md:30` |

Confirmed keepers from run 1 (`PL/V4_NOTES.md:8-21`): caliper guide, planner
self-review of annotated images, bench sanity rule, feature-gated loop (honest
STOP-and-report at F00 and F12 on E03).

---

## 5. TRACKER failure analysis

**Discrepancy first:** the brief says TRACKER includes "OOM-M02 blend STOP". The snapshot
does not: OOM-M02 is at **INTAKE** (scan-only waiver, intake started 2026-08-03) with no
build, no STOP and no mention of blends (`PL/TRACKER.md:29`; `grep -i blend` in
`PL/TRACKER.md` returns nothing). The M02 blend STOP must be sourced elsewhere (possibly
the live repo after 20c09cd); it cannot be analysed from this baseline.

| Part / event | Status as recorded | Root cause (as recorded) | Check that would have caught it (named) |
|---|---|---|---|
| **OOM-W01 attempt 1** — WITHDRAWN, HALTED 3/3 | 5,485 faces (4,753 B-spline + 583 cones), 0.204 faces/mm², 12× reference density; Tier-2 max 5.042 vs 4.0; Tier-1 never run; pivot bore Ø6.0 a guess | `Polyline` cross-sections + `loft(..., ruled=True)` = scan re-tiled into BRep (`PL/TRACKER.md:32`) | **Tier-0 SURFACE QUALITY** (`PL/RE_SPEC.md:265-270`) + anti-Lego rule 3 (`PL/RE_SPEC.md:260-262`) + plan review (`AG/re-planner.md:61-64`) |
| **OOM-W01 attempt 2 it2** — REVISE (2/3) | Tier-0 PASS (177 faces, 100 % analytic); **Tier-2 FAIL** p95 6.356 / max 10.980; motor barrel max 2.037 vs 0.8; reverse p95 4.877 / max 9.203 | Too coarse: flat two-level housing prism, plain lug cut, smoothed wheel disc; ICP hit 50-iteration cap at 3.645°/0.973 mm; tread crest read the fender overhang; motor length from harness; `PolarLocations` wrapping bug; disconnected pivot boss (`PL/TRACKER.md:32`) | **Tier-2 reverse direction** (`AG/re-qa-verifier.md:33-34`); **ICP-convergence honesty** (`AG/re-qa-verifier.md:37-38`); **Validity single solid** for the floating parts (`AG/re-qa-verifier.md:22-23`); photo check. Note also Tier-1 ABSENT and scale UNVERIFIED — **external caliper gate** (`PL/RE_SPEC.md:381-383`) was waived. Scan (assembled) ≠ photos (disassembled) — no named check covers this. |
| **OOM-B02 it1** — REVISE | Tier-1 F06 Δ +0.647 out of ±0.15 | photo-transcribed F06 24.84 applied as skirt flat radius; not achievable as two-jaw diametral reading on 3-lobed skirt (`PL/TRACKER.md:13`; `GE/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:58-74`) | **Tier-1** caught it; earlier catch = **caliper guide** jaw placement + scan-predicted value (`PL/RE_SPEC.md:197-202`) |
| OOM-B02 — it1 published early | it1 STEP published to `4_STEP\` before gate finished; withdrawn | process error (`PL/TRACKER.md:13`) | **Merge rule 2** (merge only after VERDICT APPROVED) + Drive sync only from main (`PL/RE_SPEC.md:315,320-322`) |
| OOM-B02 — verdict number drift | first VERDICT draft quoted an intermediate Tier-2 run; deltas ≤0.02 mm | (`PL/TRACKER.md:13`) | "Numbers come from VERDICT.md … never from memory" (`AG/re-drafter.md:63-64`) — only partially; no named check re-reads JSON |
| OOM-B02 — qualified pass | hex pocket passes only with M3/A6 masks (unmasked max 1.624); intake errors (SAF-1 θ sign, groove vs ridge, missed recess) | (`PL/TRACKER.md:13`) | Tier-2 functional band 0.8 (`PL/RE_SPEC.md:175`) — mask policy not specified; intake review has no named check |
| **OOM-P03 it1** — REVISE | missing central hexagonal drive stem (scan "occlusion spike" was real); alignment.json 1.651 mm off at it1 | intake misread real geometry as artifact (`PL/TRACKER.md:31`; `GE/OOM-P03_mop-pad-bracket/6_RE_work/VERDICT.md:8,41,49-50`) | **Tier-2 max ≤ 4.0** caught it (4907 pts > 4.0 mm); earlier = **Visual vs photos** (`AG/re-qa-verifier.md:39-43`) and photo authority for "real feature vs artifact" (`PL/RE_SPEC.md:95-96`); datum drift = **Datum audit** |
| OOM-B01 it1 finding reversed | "it1 hub finding reversed (mask artifact)" (`PL/TRACKER.md:12`) | mask artifact in QA | Tier-2 mask protocol (no named check for mask validity) |
| OOM-E03 QA cycle 1 — REVISE | F01-bridge/F04 integration miss, shroud-arm roof drop, ENV-2 nose arc; 1 feature-REVISE; budget 11→16 | (`PL/TRACKER.md:16`) | Feature review missed integration; **independent QA** caught it — evidence both layers are needed (`PL/RE_SPEC.md:179`) |
| OOM-E03 — F08 pitch conflict | caliper 48.70 vs scan 49.914 (Δ1.23) SUSPECT under-reach; Tier-1 deferred | (`PL/TRACKER.md:16`) | **Bench sanity rule** / caliper-guide scan-predicted value (`PL/TEMPLATES/MEASUREMENTS.md:12-16`) |
| OOM-E05 — F03 struck | 12.19 was overall height, not neck; intake's ~5 % flange under-read flag disproved (p92/AABB artifact) | (`PL/TRACKER.md:17`) | caliper guide jaw placement; §2 caliper authority |
| OOM-P02 intake — manager REVISE | row-ID/feature-ID collision (F01–F12 → M01–M12); F03 decomposition; label overlap; gate answer forced RE-DATUM (seat plane, not cover face) | (`PL/TRACKER.md:30`) | planner self-review of guide (`AG/re-planner.md:49-51`); functional-beats-largest datum rule (`PL/RE_SPEC.md:118-120`) |
| "Not organisationally independent" (B02, E03, E05) | QA re-derived by same context | agents/skills not installed (`PL/TRACKER.md:13,17`) | **Environment parity check** (`PL/RE_SPEC.md:364-373`) — added in v4 for exactly this |

---

## 6. Gaps and internal contradictions

1. **Caliper uncertainty**: RE_SPEC says ±0.05 mm (`PL/RE_SPEC.md:91`); MEASUREMENTS template says ±0.02 mm (`PL/TEMPLATES/MEASUREMENTS.md:10`); practice treated photo-transcribed readings as ±0.1 mm (`PL/TRACKER.md:13`). No rule for photo-transcribed values.
2. **Scan noise vs RANSAC tol**: noise floor "~0.5–0.8 mm" (`PL/RE_SPEC.md:25`) vs RANSAC "tol ≈ scan noise (0.05–0.1 mm)" (`PL/RE_SPEC.md:127`). Two different "scan noise" magnitudes in one spec.
3. **Tier-0 has no numbers in the spec or agents** (`PL/RE_SPEC.md:265-270`; `AG/re-qa-verifier.md:24-27`); the only numeric form (≤ ~600 faces, ≥60 % analytic) lives in a TRACKER cell for W01 (`PL/TRACKER.md:32`). The verifier checks "face count vs the ratified FEATURE BUDGET's expectation" but the MODELING_PLAN template has no expected-face-count field (`PL/TEMPLATES/MODELING_PLAN.md:13-16`).
4. **Stale role names in templates**: INTAKE_CARD and MEASUREMENTS say "re-mesh-analyst" (`PL/TEMPLATES/INTAKE_CARD.md:2`; `PL/TEMPLATES/MEASUREMENTS.md:3`), retired in v3 (`PL/RE_SPEC.md:190`). INTAKE_CARD path `<PART>\6_RE_work\INTAKE_CARD.md` (`PL/TEMPLATES/INTAKE_CARD.md:2`) vs repo layout, which has no INTAKE_CARD location (`PL/RE_SPEC.md:64-74`; P02 put it at `OOM-P02/INTAKE_CARD.md`, `PL/TRACKER.md:30`).
5. **Section mis-reference**: re-planner cites caliper guide as "RE_SPEC §7" (`AG/re-planner.md:43`), as does V4_NOTES (`PL/V4_NOTES.md:10`); the guide is specified in §5 (`PL/RE_SPEC.md:195-206`); §7 is view tooling.
6. **Version drift**: re-planner and re-qa-verifier headers say v3, drafter v4 (`AG/re-planner.md:3`; `AG/re-qa-verifier.md:3`; `AG/re-drafter.md:3`); SESSION_PROMPT still says "In v3 the iteration header…" (`PL/SESSION_PROMPT.md:18-19`); TRACKER cites "RE_SPEC v4.1" (`PL/TRACKER.md:30`) but the file header says v4 (`PL/RE_SPEC.md:1`). TRACKER header still says "RE_SPEC v3 §8" (`PL/TRACKER.md:3`).
7. **Waivers are unspecified**: B02, E05, W01, M02, P03 all ran with calipers waived/partial (`PL/TRACKER.md:13,17,29,31,32`), but the spec's external gate is "blocking — never start a build on an empty caliper column" (`PL/SESSION_PROMPT.md:48-50`; `PL/RE_SPEC.md:381-383`). "Scan authority" rows that are not Tier-1 gated (P02 M05–M12, P03 8 dims) have no status in §4, which says "every dimension listed in MEASUREMENTS.md" (`PL/RE_SPEC.md:169`).
8. **Tier-2 mask policy undefined**: spec requires "normal-based outer-skin mask" (`PL/RE_SPEC.md:174`) but not boundary/COTS/soft masks; B02's pass on the hex pocket depends on M3/A6 masks (`PL/TRACKER.md:13`).
9. **ICP convergence has no criterion** (`AG/re-qa-verifier.md:37-38`) — W01 hit a 50-iteration cap (`PL/TRACKER.md:32`).
10. **Reverse direction** is mandatory in the verifier (`AG/re-qa-verifier.md:33-34`) but §4 bands do not say whether reverse is gated or advisory (`PL/RE_SPEC.md:172-177`); E05 treated it as advisory (`PL/TRACKER.md:17`).
11. **Measurement-request size**: 8–15 dims (`AG/re-planner.md:40`) vs B02's 24-dim sheet (`PL/TRACKER.md:13`).
12. **Multi-body parts**: validity rule is "single valid solid (or the ruled solid count)" (`AG/re-qa-verifier.md:22`) — P02's two-body ruling needed per-body Tier-0/1/2 (`PL/TRACKER.md:30`); not in spec.
13. **Budget overrun response** is stated both as "HALT to the manager" (`PL/RE_SPEC.md:263-264`) and "automatic REVISE" when silent (`PL/TEMPLATES/MODELING_PLAN.md:15-16`) — consistent only if read as "declared → HALT, silent → REVISE"; contingency pre-authorisation (P02 "8 base + 3 named contingencies", `PL/TRACKER.md:30`) is not in the template.
14. **Datum audit tooling** is written per part — "no shared script yet — candidate for a future `tools/datum_audit.py`" (`PL/CHANGES_V3.md:164-166`). Tier-0 script `surftypes.py` also not shipped.
15. **Manager is not a file**: the most important reviewer (`PL/RE_SPEC.md:230-236`) has no agent brief; its checklist is spread across SESSION_PROMPT. Manager-review acceptance is visual only (no numeric gate per feature besides the plan row).
16. **Heavy process coupling**: GitHub, Drive, Slack, `machines.toml`, model-tier rules (`PL/RE_SPEC.md:293-322,396-472`) are org-specific and not transferable to a generic skill.

---

## 7. Spot-check vs golden (B02, P03)

Both parts were delivered **before v3 existed** (B02 2026-07-30, P03 2026-07-29 —
`PL/TRACKER.md:13,31`; v3 dated 2026-08-01, `PL/CHANGES_V3.md:1`). They ran the **v2**
flow (re-mesh-analyst → re-modeler → independent QA, iterations N/3), not the v3/v4
feature-gated loop.

| Pipeline claim | B02 record | P03 record |
|---|---|---|
| Intake card (template §1–§8) | Present, all 8 sections; "Produced by `re-mesh-analyst`" (`GE/OOM-B02_side-brush-3-arm/6_RE_work/INTAKE_CARD.md:3,11-231`) | Present, §1–§8; re-mesh-analyst (`GE/OOM-P03_mop-pad-bracket/6_RE_work/INTAKE_CARD.md:3-4,6-113`) |
| Measurement request / sheet | Present; PARTIAL, "no dedicated caliper session" (`GE/OOM-B02_side-brush-3-arm/5_reference/MEASUREMENTS.md:3-4,11,15-25`) | Present; readings transcribed from photos, scan-authority fallback (`GE/OOM-P03_mop-pad-bracket/5_reference/MEASUREMENTS.md:10-14`) |
| Caliper guide images (`caliper_guide_*.png`) | **Absent** (no such file) | **Absent** |
| MODELING_PLAN + FEATURE BUDGET | **Absent**; only a per-region strategy table in intake §6 (`GE/OOM-B02_side-brush-3-arm/6_RE_work/INTAKE_CARD.md:131-146`) | **Absent**; intake §6 only (`GE/OOM-P03_mop-pad-bracket/6_RE_work/INTAKE_CARD.md:85`) |
| F00 / per-feature PRs / views/f<NN>/ | **Absent** — single build script, it1/it2 (`GE/OOM-B02_side-brush-3-arm/6_RE_work/build_OOM-B02.py`, `_it1_SUPERSEDED/`) | **Absent** — `rebuild_OOM-P03.py` |
| alignment.json schema v2 | Not v2: `scale_correction` not `scale_factor`, no `scan_noise_mm`/`primary`/`secondary` records; "written_by re-modeler" (`GE/OOM-B02_side-brush-3-arm/2_mesh_cleaned/alignment.json:3,32`) | Not v2: keys part/description/units/matrix_4x4/axis_source/notes/refinement (`GE/OOM-P03_mop-pad-bracket/2_mesh_cleaned/alignment.json`) |
| Datum audit ≤0.3° / ≤0.15 mm | Independent datum re-derivation present; 0.429° / 0.451 mm max point disagreement, marked PASS with band "—" (`GE/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:18,153-163`; `qa/_datum_indep.json`) — **would FAIL the later v3 audit band** | 0.154° / 0.600 mm vs refined alignment, judged "adequate for renders" (`GE/OOM-P03_mop-pad-bracket/6_RE_work/VERDICT.md:50,56`) — **origin offset would FAIL the v3 ≤0.15 mm band** |
| Validity | 1 solid / 1 closed shell / 185 faces (`GE/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:6`) | 1 solid, BRepCheck valid, 500 faces (`GE/OOM-P03_mop-pad-bracket/6_RE_work/VERDICT.md:13`) |
| Tier-0 surface audit | **No Tier-0 section** (face count only) | **No Tier-0 section** (face count only) |
| Tier-1 ±0.15 | Present, worst 0.026; 5 of 24 gated (`GE/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:15,22,44-50`) | Present, worst 0.00, 7 dims (`GE/OOM-P03_mop-pad-bracket/6_RE_work/VERDICT.md:16-27`) |
| Tier-2 p95 1.6 / max 4.0 + 0.8 interfaces | Present, own ICP (0.698°/0.188 mm) + skin mask; p95 0.740 / max 2.524; 4 interfaces ≤0.8 (`GE/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:16-17,80-82,105-111`) | Present, own trimmed ICP (30 iters) + skin mask; p95 0.971 / max 2.949; functional zones reported but not banded at 0.8 (`GE/OOM-P03_mop-pad-bracket/6_RE_work/VERDICT.md:7,31-42`) |
| Tier-2 reverse direction | Present: p95 0.659 / max 1.290 (`GE/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:147-151`) | **Absent** |
| Visual vs photos | Present (honesty notes, intake errors corrected) | Present, "Gate 4 — Photo plausibility" (`GE/OOM-P03_mop-pad-bracket/6_RE_work/VERDICT.md:44-46`) |
| Iteration breaker N/3 | it2 of 3 (`GE/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:5,180-184`) | it2/3 (`GE/OOM-P03_mop-pad-bracket/6_RE_work/VERDICT.md:3`) |
| Organisational independence | Explicitly NOT independent (`GE/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:189-193`) | Claims independent QA (`GE/OOM-P03_mop-pad-bracket/6_RE_work/VERDICT.md:5`); TRACKER does not flag it |
| Deliverable | STEP + PDF report (v2 set), not README.md | STEP + PDF report (v2 set) |

**Conclusion**: the golden records evidence the v2 core — intake card, measurement
sheet, Tier-1 ±0.15, Tier-2 1.6/4.0 (+0.8), independent ICP, photo check, 3-iteration
breaker. They do **not** evidence any v3/v4 addition (modeling plan, feature budget,
F00, per-feature review, caliper guide, Tier-0 audit, schema-v2 alignment, datum audit
band). The v3/v4 machinery is supported only by TRACKER/V4_NOTES narrative for E03/P02,
which are not in `golden-examples/`. Both golden datum re-checks exceed the later
0.15 mm origin band yet produced APPROVED parts — evidence the band may be tighter than
needed (cf. rationale `PL/CHANGES_V3.md:148-151`), or that the comparison metrics
differ (point disagreement vs origin offset).

---

## 8. Reusable code and templates worth lifting

| Item | Why | Caveats |
|---|---|---|
| `PL/tools/render_views.py` — `load_model` (STEP/STL/.py) (`:170-178`), `_tessellate_shape` OCP tessellation + true BRep edges (`:100-149`), `load_align_matrix` with `matrix_4x4` validation (`:181-189`), numpy z-buffer `rasterize` (`:231`), `render_section` with no-clip margins (`:458-488`), `clip_model` closeup with compacted verts (`:491-516`), `render_datum_view` RGB triad + origin (`:378`) | Headless, dependency-light (numpy/matplotlib/trimesh/OCP), one image path for intake, review, QA and docs | `--overlay` renders iso only and returns early (`:583-590`); `--datum` ignores `--views` (`:570-574`); STL feature edges dropped entirely above 60000 (`:162`); sections are mesh-plane cuts of the tessellation, not BRep sections |
| `PL/TEMPLATES/MEASUREMENTS.md` | Envelope-first, Datum-ref column, record-as-read, double-read >0.05 mm, soft/N/A rules, bench sanity vs scan prediction | Fix ±0.02 vs ±0.05 conflict; add "photo-transcribed" and "scan-authority (ungated)" statuses seen in golden sheets |
| `PL/TEMPLATES/INTAKE_CARD.md` | 8 sections match both golden intakes; mandatory interior enumeration; 3-datum plan with functional WHY | Drop re-mesh-analyst naming |
| `PL/TEMPLATES/MODELING_PLAN.md` | Op vocabulary, source-tagged driving dims, per-feature acceptance criterion, budget rules | Add expected face count / analytic share for Tier-0; contingency ops |
| alignment.json schema v2 (`PL/RE_SPEC.md:142-157`) | Makes datum fit quality auditable | Unproven — neither golden record uses it |
| DOF ladder + datum selection rules (`PL/RE_SPEC.md:109-124`) | Clear, tool-agnostic | — |
| Anti-Lego doctrine (`PL/RE_SPEC.md:255-270`) + W01 evidence (`PL/TRACKER.md:32`) | Strongest failure-backed rule in the set | Needs numeric Tier-0 threshold in the skill |
| Verifier gate order (`AG/re-qa-verifier.md:15-43`) | Datum → validity → Tier-0 → Tier-1 → Tier-2 both ways → visual; "intent-snap deviations are correct" | Specify masks and ICP convergence |
| Golden QA scripts referenced for comparison (not baseline, for other auditors): `GE/OOM-B02_side-brush-3-arm/6_RE_work/qa/q03_datum_full.py`, `q10_solid_tess_tier1.py`, `q20_tier2.py` | Concrete implementations of datum audit / Tier-1 / Tier-2 that the baseline lacks | Owned by golden-extraction agents |
