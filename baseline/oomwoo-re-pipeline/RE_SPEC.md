# RE_SPEC v4 — OOMWOO Sourced-Part Reverse Engineering Line
<!-- v4 ratified 2026-08-02 from V4_NOTES.md (first-run feedback, OOM-E03/E05).
     Deltas vs v3: fixed 300k relay + automated succession + manager-tier rule (§12),
     per-feature fresh drafter (§5), submission-comment cap (§5/§8), issue stays open
     until merge (§8), tracker cells = status+links (§8), environment parity at BEGIN
     (§10), out-of-order features with stated dependency (§5), pre-v3 deliveries
     grandfathered (§9), one session per clone (§10). -->


> Single source of truth for the production line. Per-part facts live in `TRACKER.md`
> (same folder, and in the repo — §8). Methodology lives in the skills
> (`stl2step-build123d`, `cad-section`) and the `re-*` agent definitions — this file sets
> project-level decisions, data authority, PASS bands, the feature-gated review loop, and
> the GitHub protocol. Supersedes v2 (`RE_SPEC_v2_SUPERSEDED.md`, kept for history).

**Drive root:** `H:\My Drive\111 UP UP UP\REMAKE AI - DIY\OOMWOO_CAD\01_SOURCED_reverse-engineered\`
**Repo:** private GitHub repo `oomwoo-re` (§8) — cloned on LOCAL disk on every machine, never on Drive-streamed storage.

## 0. PURPOSE & LESSONS

Convert scans of the 20 sourced OOMWOO components into clean, design-intent parametric
STEP solids + documentation. Standing session: scans arrive over time; each is processed
with "process OOM-Xnn".

**v1→v2 lessons (still in force):** scanner noise floor ~0.5–0.8 mm → calipers are the
dimensional authority; only the verifier's independent registration counts; interior
structure must be enumerated at intake; tool bake-off is CLOSED — build123d won.

**v2→v3 lessons (why this version exists):**
1. **Lego-slop geometry.** Drafters produced polygon-like patchwork — dozens of tiny
   extrusions where the honest model is 3–4 sketches + booleans (OOM-W01 attempt 1:
   5,485 faces vs the 734-face reference part). Design intent was lost because nobody
   planned the modeling approach up front and nobody reviewed until the end.
2. **Review came too late.** QA gated only the finished part; by then a bad modeling
   strategy is baked in. v3 moves review to FEATURE granularity: the manager (highest
   available model) rules on every feature as it is built, and independent QA still
   gates the finished part. Both layers are mandatory.

**Priority is QUALITY over token cost.** Never optimize for fewer agent turns.

## 1. WORKSPACES & PER-PART DATA CONTRACT

### 1a. Drive part folders (scans in, deliverables out — unchanged owners)

Each part keeps its existing `OOM-Xnn_<name>\` folder on Drive:

| Subfolder | Owner | Contents |
|---|---|---|
| `1_scan_raw_STL\` | Muhammed | raw scan STL(s) — never modified, never meshed in place |
| `2_mesh_cleaned\` | pipeline | decimated/cleaned working mesh + `alignment.json` (datum transform) |
| `3_NX_PRT\` | Muhammed | manual NX rebuilds — pipeline never touches |
| `4_STEP\` | pipeline | **deliverable** `OOM-Xnn.step` — synced from the repo after merge (§8) |
| `5_reference\` | Muhammed + pipeline | photos (`OOM-Xnn_photo_01.jpg`…), `MEASUREMENTS.md` (caliper sheet), datasheets/links |
| `6_RE_work\` | pipeline | intake-phase scratch (mesh analysis scripts, intake views) — build code now lives in the repo |
| `7_docs\` | pipeline | **deliverables**: final view set + `README.md` — synced from the repo after merge (§8) |

Photo guidance (more photos = better intake): overall view, each functional interface
close-up, any label/model number, and — when possible — a photo of the caliper ON the
feature showing the reading (self-documenting measurement).

### 1b. GitHub repo (the build & review workspace — §8 for the protocol)

```
oomwoo-re/
  _PIPELINE/            spec (this file), templates, tools, TRACKER.md, SETUP.md, machines.toml
  OOM-Xnn/              one folder per part:
    cad/                build123d source, one file per part, committed per feature
    views/f<NN>/        rendered views for feature NN (committed so PR comments render them)
    scan/               small scan metadata ONLY (trim.json, alignment.json) — never meshes
    OOM-Xnn.step        the deliverable solid (re-exported every feature)
    MODELING_PLAN.md    re-planner output, ratified on the part's issue
    VERDICT.md          re-qa-verifier output (final gate)
    README.md           per-part delivery document (replaces the v2 PDF)
```

The repo clone lives on LOCAL disk on both machines (Windows: `C:\src\oomwoo-re`;
VPS: `/root/repos/oomwoo-re`). **Scan transport: Google Drive, on both machines**
(Windows `H:` / VPS `/root/gdrive` — `drive_root` in machines.toml). Raw scans and
photos are read from Drive and copied to local `scratch` before any mesh op; meshes
are NEVER committed to the repo (`.gitignore` enforces this). The repo carries code,
configs, views, STEP, and docs — PR reviewers see the mesh through committed VIEW
images, and both machines see the identical mesh through Drive. Derived working
copies (decimation/trim) are reproducible from `scan/trim.json`.

## 2. DATA AUTHORITY HIERARCHY (unchanged v2 core rule)

Three data sources per part, with explicit precedence on conflict:

1. **CALIPERS** (`5_reference\MEASUREMENTS.md`) — authoritative for every DIMENSION they
   cover: envelopes, ODs/IDs, bore diameters, hole pitches, wall thicknesses, shaft flats.
   Instrument uncertainty ±0.05 mm ≪ scan noise. A caliper value is used DIRECTLY as the
   CAD parameter (after standard-size snap if within ±0.1 mm of a standard).
2. **STL scan** — authoritative for FORM & TOPOLOGY: feature positions, profiles, blends,
   anything a caliper can't reach. Also the whole-surface gate reference.
3. **PHOTOS** — authoritative for INTENT: what the part is, functional vs cosmetic
   surfaces, expected symmetry/revolve axes, real feature vs scan artifact.

**Global scale correction:** if the three caliper envelope dims disagree with the STL
envelope by a consistent factor (scanner calibration error), apply ONE uniform scale to
the mesh before any modeling, and log it in `alignment.json` + the param table.
Non-uniform disagreement = flag at intake, do not proceed silently.

## 3. DATUM & REFERENCING PROCEDURE (v3.1 — replaces the v2 carryover)

### 3.1 Order of operations
Scale/units verification (§2: caliper envelope vs mesh envelope, uniform-scale rule)
ALWAYS precedes datum work. Never datum an unverified-scale mesh.

### 3.2 The DOF ladder (all 6 DOF accounted, none twice)
1. **Primary datum LEVELS** the part — kills 3 DOF (2 rotations + 1 translation):
   the chosen surface becomes XY, part sits on Z=0.
2. **Secondary datum CLOCKS** it — kills 1 rotation: the chosen feature aligns to
   +X (or +Z for axis-primary parts).
3. **Origin PINS it** — kills the last 2 translations: (0,0,0) is a NAMED feature
   intersection (e.g. "bore axis ∩ base plane", "symmetry planes ∩ seat").

### 3.3 Selection rules
- Functional/mating surface beats largest surface. Prefer the **CHASSIS-MATING
  interface as primary** so every part's frame is assembly-meaningful — a future
  robot assembly (step-registry) consumes these frames directly.
- Allowed secondary sources: bore/cylinder axis (fit from surface NORMALS — eigen
  method; bbox-center axes are FORBIDDEN), a second plane, or a fitted symmetry
  plane when the part has no usable bore/second flat.
- Each of the three datums is named in the intake card §5 WITH a functional WHY.

### 3.4 Fit-quality duty (blocking)
Plane fits by RANSAC at tol ≈ scan noise (0.05–0.1 mm). The drafter reports fit
residuals (RMS + max) with the F00 submission and STOPs-and-reports if residuals
exceed scan noise — never force a datum onto a bad region (warp, wear, artifact).

### 3.5 The F00 gate
Datum execution is **feature F00** — the first gated feature of every part, manager-
approved from `--datum` views (§7) before any sketch is drawn. F00 sits OUTSIDE the
feature budget. **HARD RULE: any change to `alignment.json` after F00 approval
invalidates ALL downstream features** — the plan resets to F01, the manager re-approves
F00, and git history is the audit trail of the re-datum.

### 3.6 Mirrored / multi-piece sets
Model ONE hand in its own datum frame; the mirrored instance is DEFINED by mirroring
about a NAMED datum plane, stated in the modeling plan and the part README.

### 3.7 alignment.json schema v2 (the ops contract)
Row-major 4×4 under `matrix_4x4` (raw-scan → datum frame) stays mandatory; consumers
tolerate the added keys. New required keys:
```json
{
  "matrix_4x4": [[...],[...],[...],[...]],
  "scale_factor": 1.0,
  "scan_noise_mm": 0.08,
  "primary":   {"type": "plane", "mesh_region_desc": "chassis seat, 3 pads",
                "fit_rms_mm": 0.05, "fit_max_mm": 0.11},
  "secondary": {"type": "bore_axis", "mesh_region_desc": "eyelet-A bore",
                "fit_rms_mm": 0.04, "fit_max_mm": 0.09},
  "origin":    {"definition": "eyelet-A bore axis ∩ chassis seat plane"}
}
```
`scale_factor` is 1.0 when no §2 correction was applied.

### 3.8 Intent snapping (unchanged from v2)
- Units mm; caliper values → standard sizes within ±0.1 mm; scan-derived dims →
  round within scan noise; symmetry/concentricity enforced. Every measured→snapped
  pair logged in the param table with its SOURCE column (caliper/scan/photo-inferred).
- Fillets last, from sections; micro-blends omitted unless functional.
- Worn/damaged regions: rebuild NOMINAL intent, exclude from gate, note restoration.

## 4. PASS BANDS (blocking — final gate, unchanged numbers)

**Tier 1 — caliper dims (the tight gate, immune to scan noise):**
- Every dimension listed in `MEASUREMENTS.md`, re-measured on the FINAL STEP by the
  verifier (never echoed from params): **|CAD − caliper| ≤ 0.15 mm**. Per-dim, blocking.

**Tier 2 — scan skin (form gate, ratified 2026-07-26 scan-adjusted bands):**
- Independent best-fit ICP registration + normal-based outer-skin mask (the verifier's
  M02 protocol is the reference): **p95 ≤ 1.6 mm, max ≤ 4.0 mm**.
- Functional interfaces named in the intake card and NOT caliper-covered: **max ≤ 0.8 mm**.
- Interior/occluded buckets reported with numbers, not gated.
- Intent-snap and caliper-driven deviations from the scan are CORRECT (report, don't chase).

**Feature review (§5) does NOT replace this gate — both layers are mandatory.**

**Honesty rule:** a region that can't hit its band (occlusion, wear, scanner noise) is
HALTed with the measured gap and options (waive with justification / restoration zone /
freeform patch) — never silently loosened, never a faked APPROVED.

## 5. ROLES & THE FEATURE-GATED LOOP (the v3 core)

Four roles. The manager is the orchestrator session itself — the highest available model
— not a subagent. Handoffs stay lean: paths + numbers only.

### re-planner (intake AND modeling strategy — replaces re-mesh-analyst)
Views the part photos AND a rendered set of STL screenshots (iso/front/top/right + any
needed closeups, from `render_views.py`), analyzes the mesh (units, bbox, watertightness,
symmetry/revolve axes, interior ribs/bosses — enumerate them), then outputs three things:
1. **INTAKE CARD** (existing template).
2. **MEASUREMENT REQUEST** (existing caliper template) **+ CALIPER GUIDE images
   (mandatory)**: 2–4 annotated scan views where EVERY requested dim is drawn on the
   geometry (extent arrows/leaders at the true measurement locations). Conventions:
   **RED = Tier-1 blocking dims, BLUE = second tier** (legend in the corner); each
   label = the MEASUREMENTS.md row ID + jaw placement ("inside jaws", "depth rod",
   "jaws on this plateau") + the scan-predicted value in parentheses — so a gross
   misread (wrong feature, wrong jaws) is caught at the bench, not at the Tier-1
   gate; a scale bar on every view. Dims NOT measurable from outside get an explicit
   callout box stating what is needed instead (e.g. "underside photo WITH a ruler in
   frame"). Files: `<part>/views/intake/caliper_guide_*.png`, committed, and posted
   on the part's issue (absolute `?raw=true` URLs) so the guide opens on a phone at
   the bench.
3. **MODELING PLAN** (`MODELING_PLAN.md`): an ordered feature list — for each step the
   operation (sketch-on-plane / extrude / revolve / loft / sweep / boolean /
   fillet-chamfer / shell / pattern), the datum/plane it builds on, the scan/caliper dims
   that drive it, and its acceptance criterion. The plan declares a **FEATURE BUDGET**
   (expected op count; most vacuum-robot parts ≤ ~12 ops before fillets).

### re-drafter (executes the plan — replaces re-modeler)
Executes the MODELING PLAN in **build123d ONLY** (no FreeCAD, no Blender), ONE feature at
a time, **starting at F00 (datum, §3)**: perform the alignment per intake card §5, write
`alignment.json` (schema v2, §3.7), submit the `--datum` view set, and WAIT — no sketch
before F00 is APPROVED. After each feature: commit the code, generate the standard view set (§7), push,
post a submission comment on the part's PR — **≤ ~3,000 characters**: feature #, op,
one-line what, param deltas, acceptance evidence (numbers), image links; full analysis
goes in COMMITTED files, never the comment (run-1 comments grew to 14k chars and burned
the manager's context) — then **WAIT** for the manager verdict before the next feature.
The drafter never self-approves, never merges, and never deviates from the plan — if the
plan doesn't fit reality, it STOPS and reports on the PR thread.
**One drafter per FEATURE (v4):** agent transcripts are not retained across features, so
every feature gets a FRESH drafter briefed from the plan + the PR thread + the committed
code — the thread IS the memory, by design. **Out-of-order execution is allowed** when
the manager states the dependency in a ruling on the PR (run-1 precedent: F12 before
F04); plan order is the default, not law.

### MANAGER (= the orchestrator session, highest available model)
Reviews every feature submission **by viewing the images with its own eyes**. May demand
extra views (section at a named plane, wireframe, closeup, different rotation) before
ruling. Verdicts are posted on the PR thread:
- **APPROVED** → drafter proceeds to the next feature.
- **REVISE** → specific, actionable instruction (what is wrong, which dim/photo says so).
Only the manager approves submissions or merges PRs. The manager never models.

### re-qa-verifier (independent final gate — unchanged doctrine)
After the LAST feature: **DATUM AUDIT first** (independently re-fit the primary +
secondary datums on the RAW scan with its own code, rebuild the transform, compare vs
`alignment.json` — angular error ≤ 0.3°, origin offset ≤ 0.15 mm, reported in VERDICT.md
every time; audit FAIL ⇒ the deviation numbers are meaningless ⇒ REVISE at F00, not at
the failing dims). Then: own registration/ICP, two-way deviation vs scan (Tier-2 bands),
re-measure every calipered dim on the STEP (Tier-1 ±0.15 mm), photo plausibility. Writes
`VERDICT.md` into the part folder in the repo. Trusts nothing the drafter reported.

### Circuit breakers (blocking)
- **Per-feature:** 3 REVISE verdicts on the same feature → HALT to Muhammed with the
  images and options.
- **Per-part:** 3 full-loop iterations (post-QA REVISE cycles) → HALT, unchanged from v2.
- **Plan mismatch:** drafter stops and reports; manager decides — send back to
  re-planner for a re-plan, or approve a FEATURE BUDGET raise with written justification
  on the PR thread. A silent budget overrun = automatic REVISE.

## 6. ANTI-LEGO DOCTRINE (blocking rules)

1. **Largest-sketch-first:** capture the dominant silhouette in ONE sketch, not stripes.
2. **Few profiles:** prefer revolve/extrude/boolean of FEW profiles; use symmetry
   (mirror, polar/linear patterns) instead of repeating geometry.
3. **Facet-chasing is FORBIDDEN:** never approximate a smooth face with stacked prisms,
   `Polyline` section stacks, or `ruled` lofts of scan slices. Analytic primitives or
   fitted `Spline` profiles only (the OOM-W01 attempt-2 rule, now line-wide).
4. **FEATURE BUDGET is enforced:** more ops than planned → HALT to the manager
   (re-plan or justified budget raise). Silent overrun = automatic REVISE.
5. **Tier-0 surface-quality check** (from OOM-W01, now standing, checked by QA and
   spot-checked by the manager mid-build): face count consistent with the plan
   (reference-class parts ≈ hundreds, not thousands), dominant area on analytic
   surfaces (planes/cylinders/cones/tori/revolutions), zero ruled-loft patchwork.
   Deviation-to-scan can NEVER excuse patchwork: a re-tiled scan skin scores well on
   Tier-2 and is still garbage CAD.

## 7. VIEW TOOLING (`_PIPELINE/tools/render_views.py` — replaces Blender)

One cross-platform, headless, pure-Python script renders every image in the pipeline:

- **Input:** a STEP, STL, or build123d `.py` file (convention: script exposes `result`).
- **Standard set:** `iso`, `front`, `top`, `right` — neutral background, consistent
  scale/edge styling, one part per frame.
- **On-demand (manager may demand any of these before ruling):**
  `--section <X|Y|Z> <offset>` (cut view), `--wireframe`, `--closeup x0,y0,z0,x1,y1,z1`
  (bbox zoom), `--dir dx,dy,dz` (arbitrary rotation), `--overlay <scan.stl>`
  (scan-vs-CAD comparison, with `--align alignment.json`).
- **`--datum` (the mandatory F00 view set):** iso + 3 orthos of the ALIGNED mesh with
  an RGB axes triad (X red, Y green, Z blue) and an origin marker at (0,0,0).
- Implementation: OCP tessellation (STEP) / trimesh (STL) + numpy z-buffer shading +
  true BRep feature edges, matplotlib output. No GUI, works headless on Windows & Linux.
- `blender_doc_render.py` is RETIRED. Blender is no longer a pipeline dependency.

Usage per feature: drafter renders the standard set into `<part>/views/f<NN>/`, commits
the PNGs, and links them in the PR comment with absolute blob URLs + `?raw=true` (§8 —
relative links do not render in PR comments).

## 8. GITHUB PROTOCOL (the communication workspace)

Prereq: `gh auth status` passes on the machine doing the pushing.

- **Repo:** private `oomwoo-re` on Muhammed's GitHub account. Clone on LOCAL disk only.
- **Issue per part = the work order.** Body: intake card, modeling plan, measurement
  checklist. **EXTERNAL GATE:** Muhammed confirms calipers + plan by commenting on the
  issue. No rebuild starts before that comment.
  **The issue stays OPEN until the part's PR merges** (close it in/with the merge, e.g.
  "Closes #n" in the PR body). Run-1 mistake: issue #3 was closed while measurements
  were still awaited on it — pending human asks must always live on an OPEN issue.
- **Branch per part:** `part/OOM-Xnn`.
- **One commit per feature.** Message format:
  `OOM-W02 F03: revolve hub profile (Ø34.2 caliper)`.
- **PR per part.** The PR thread is the complete manager↔drafter review conversation —
  every submission and every verdict is a PR comment, auditable from GitHub end to end.
- **Images in PRs:** view PNGs are committed under `<part>/views/f<NN>/` and referenced
  in PR comments with absolute blob URLs + `?raw=true`
  (`https://github.com/<owner>/oomwoo-re/blob/<branch>/<path>.png?raw=true`) — GitHub
  does not render relative links inside comments (verified on the demo PR).
- **Merge rules (blocking):**
  1. Only the MANAGER approves submissions or merges PRs.
  2. A PR may merge to `main` only after re-qa-verifier writes APPROVED in `VERDICT.md`.
  3. The tracker (`_PIPELINE/TRACKER.md` in the repo) is updated in the merge commit.
     **Tracker cells are STATUS + feature counter + links (issue/PR/handover) — one or
     two lines, no state dumps.** The PR thread is the memory; the tracker is the index
     (run-1 cells grew into multi-thousand-word essays duplicating the PR).
  4. After merge, `tools/sync_to_drive.py` copies the deliverables (STEP, README.md,
     final views) from `main` to the Drive delivery folders (§1a). Drive paths come from
     `machines.toml` — the Linux VPS may skip the sync or rclone it.

## 9. PER-PART DELIVERABLES (Definition of Done)

1. `<part>/OOM-Xnn.step` in the repo — clean single valid solid (or the ruled solid
   count), Tier-0 clean.
2. `<part>/MODELING_PLAN.md` (as-ratified, with any approved budget raises),
   `<part>/VERDICT.md` (APPROVED), full PR review thread.
3. `<part>/README.md` — the per-part delivery document (replaces the v2 PDF): reference
   photo, method summary, parameter table with source tags (caliper / scan / inferred),
   caliper check table, deviation stats, restoration notes. Drafter authors it at
   delivery; manager checks it before merge.
4. Final view set under `<part>/views/final/`.
5. Tracker row updated in the merge commit; deliverables synced to Drive
   (`4_STEP\`, `7_docs\`).

**Grandfathering:** parts delivered before v3 (e.g. OOM-E05: Blender renders + PDF
report) keep their original deliverable set — do NOT retro-redo them. Their open items
(e.g. E05's "re-caliper F02 before tooling") stand as tracker notes.

## 10. OPS RULES (hard-won, non-negotiable)

- H: is Google-Drive-streamed: COPY every STL to local scratch before ANY mesh op; write
  results back at the end. Never import a large mesh in a loop — measure once, cache
  (`_measured_cache.json` pattern; re-derive on file change, never trust a stale cache).
- Meshes > ~15 MB: decimate an aggressive working copy first; the final QA gate still
  runs against the raw scan (or a light decimation, logged).
- Workers return PATHS + NUMBERS only — no raw mesh/CAD data in chat.
- `alignment.json` contract: schema v2 per §3.7 — `matrix_4x4` (row-major raw-scan→datum)
  plus `scale_factor`, `scan_noise_mm`, `primary`/`secondary` fit records, and the named
  `origin` definition. Consumers tolerate additional keys.
- **Cross-platform (Windows local + Linux VPS):** all tools pure Python 3 + pathlib;
  no PowerShell-only or bash-only steps in the method; forward slashes in configs.
  Machine-specific paths (Drive delivery folder, scratch dir) live ONLY in
  `_PIPELINE/machines.toml`, keyed by hostname — never hardcoded in tools. Env setup for
  both OSes: `_PIPELINE/SETUP.md`.
- Tool choice RATIFIED: build123d (bake-off closed 2026-07-26 — do not revisit).
  FreeCAD is not used in v3 drafting at all.
- **ONE session per clone.** Two sessions sharing a clone raced in run 1 (vanished
  branch, files swept into a foreign commit). Concurrent pipeline/main edits while a
  part is in flight go through `git worktree add` (temp checkout → edit → push →
  remove), never through the active clone's checkout.
- **ENVIRONMENT PARITY at BEGIN (blocking).** Before accepting any "process"/"resume"
  order, the session verifies THIS machine has: the `re-*` agent files, the cad skills
  (`cad-qa-gate`, `stl2step-build123d`, `cad-section`), `render_views.py` importable
  deps, gh authed, and a machines.toml entry for this hostname. ANY missing → HALT and
  report; never improvise the roles in-context (run-1 intakes ran "not
  organisationally independent" when agents were absent — independence of QA is part
  of the gate, not a nice-to-have). **Where user-level agent copies exist (VPS,
  SETUP §1.8 exception): additionally `diff` them against the clone's
  `.claude/agents/` — any byte difference = HALT** (a stale v2 verifier once
  shadowed the v4 gate under the same name; staleness is a silent quality hole).

## 11. STANDING-SESSION PROTOCOL

"process OOM-Xnn" (scan + photos in the Drive folder) →
1. Tracker row → INTAKE. Spawn **re-planner** (feed it photos + STL view renders).
2. Open the part's **GitHub issue** with intake card + modeling plan + measurement
   checklist. Present to Muhammed.
3. **EXTERNAL GATE (blocking — WAIT):** Muhammed calipers the requested dims into
   `5_reference\MEASUREMENTS.md`, confirms/corrects the functional reading AND the
   modeling plan, comments GO on the issue.
4. Branch `part/OOM-Xnn`, open the PR, spawn **re-drafter** — the FEATURE LOOP (§5) runs:
   submit → manager views images → verdict → next feature. Budget and breakers enforced.
5. Last feature APPROVED → **re-qa-verifier** (independent, Tier-1 + Tier-2 + Tier-0 +
   photo plausibility) → `VERDICT.md`.
6. QA APPROVED → drafter authors `README.md` → manager checks it → merge (tracker row in
   the merge commit) → `sync_to_drive.py` → report DONE to Muhammed in ONE line.

Batch drops: intakes may fan out in parallel (one message, multiple re-planners); the
FEATURE LOOP runs max 2 parts concurrently (manager attention is the bottleneck, and
that is by design — quality over throughput). Never skip the external gate, the feature
gate, the QA gate, or the tracker update.

## 12. CONTEXT RELAY (session handover — long-context quality protection)

Long contexts degrade judgment quality before they hit any hard limit. GitHub is the
system of record precisely so that the manager session is DISPOSABLE — relaying to a
fresh session must cost almost nothing. Protocol:

**Model tier (v4, blocking).** The manager session MUST run the highest model tier
available to Muhammed (Fable-class as of 2026-08). Relay successors INHERIT this
requirement — a relay must never silently demote the reviewer, because the tier gap
over the Opus workers IS the review authority (§5). If a successor cannot run the
required tier (e.g. a bot with a fixed lower model), HALT and report instead of
continuing at a lower tier.
**Standing VPS waiver (Muhammed, 2026-08-02):** `vmi3467979` pins `opus` in its bot
settings — Fable is not reachable there. VPS sessions run as a DECLARED demotion,
logged per part on the tracker. Recorded consequence: with manager and workers both
Opus, the tier gap is gone on the VPS — verdict quality rests entirely on the two
independent process gates (personal feature review + re-qa-verifier). Reserve
tight-tolerance parts for desktop Fable sessions. Revisit if the bot's model becomes
configurable.

**Monitoring (v4: fixed threshold).** The manager checks its context usage at every
gate boundary (feature verdict posted, intake presented, QA verdict in). At
**300k tokens**: relay at the next clean boundary, always — no discretionary band
(run 1 showed quality intact at 300k and relays are near-free, so relay early rather
than gamble at 400–500k). NEVER hand over mid-feature.

**Handover (outgoing session).**
1. Reach a clean boundary: current feature's verdict posted on the PR, all repo state
   committed AND pushed, tracker current.
2. Post a **HANDOVER comment** on each in-flight part's PR — standard block:
   part ID; feature counter `F<NN>/<budget>` + REVISE count; last verdict + one-line
   rationale; NEXT ACTION (specific: "await drafter F07 submission", "rule on F05
   rev 2 — check the rib thickness in a Y-section"); open questions / warnings;
   links (issue, MODELING_PLAN, latest views folder).
3. Update the tracker cell: `RELAY→ at F<NN>`.
4. **Initiate the successor (v4: automatic where the platform allows).**
   - **VPS/Slack:** succession is native — the outgoing session's final reply in the
     thread states the exact one-line kickoff; Muhammed (or any automation) sends
     `@claude-code /root/repos/oomwoo-re: resume OOM-Xnn` as a NEW channel message,
     which spawns a fresh bot session. If the bot can post messages that trigger
     itself, it MAY send the kickoff directly — verify once, then rely on it.
   - **Windows/desktop:** report ONE line with the exact `resume OOM-Xnn` command for
     a fresh session (automated spawn is an open V4 prototype — see V4_NOTES §D; do
     not fake automation that isn't verified).
   Either way the outgoing session then STOPS — no further reviews after handover.

**Resume (incoming session).** On "resume OOM-Xnn": read RE_SPEC + tracker + the
part's issue + MODELING_PLAN.md + the PR thread FROM the last HANDOVER comment down
(+ VERDICT.md if present). Then:
- **Posted verdicts STAND.** Never re-review approved features — re-litigating the
  record burns the new context and second-guesses a reviewer with identical authority.
- Spawn a FRESH drafter with the lean brief: plan, current feature, cad file path,
  last verdict text. The committed code + plan IS the drafter's state.
- Never re-run intake for a resumed part. Continue the loop from NEXT ACTION.

**Slack turn budget (blocking on VPS).** The Slack bot hard-kills any turn at 5400 s.
Never race it: end every turn at a clean checkpoint (verdict posted + pushed) within
~60 min, replying with the state header + "send `continue` to proceed". A killed turn
loses all unpushed work; a cleanly ended turn loses nothing and resumes on your next
one-word message. One feature cycle per turn is the safe default.

**Relay deferral.** After a HANDOVER, the outgoing session does NO further work — it
answers any message with the resume instruction only. Exception: Muhammed may
explicitly defer the relay ("go ahead"); that is a ONE-boundary deferral, documented
on the PR, and the relay fires at the very next clean boundary regardless.

**Crash resume (no HANDOVER comment).** A session that dies mid-turn (API error,
kill) leaves no handover — same procedure, different anchor: `git pull`, read the
tracker cell + issue + MODELING_PLAN + the ENTIRE PR thread; the resume point is
the first feature with no posted verdict; everything pushed/posted STANDS, anything
only claimed in the dead session's chat does NOT exist. Never redo pushed work,
never trust unpushed work.

**Drafter hygiene — superseded in v4.** Drafters are fresh PER FEATURE (§5), so
drafter-context accumulation no longer exists; no recycle rule is needed. The relay
protocol applies identically on Slack/VPS sessions — the resume command is the same
one-liner kickoff.
