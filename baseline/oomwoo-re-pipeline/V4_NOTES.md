# V4 NOTES — feedback from the first V3 production run (OOM-E03/E05)

**STATUS: RATIFIED & IMPLEMENTED 2026-08-02** (OOM-E03 delivered; Muhammed ratified;
all items below executed — see `CHANGES_V4.md`). Kept as the rationale record.

## A. Confirmed keepers (validated in production — carry into V4 unchanged)

1. **CALIPER GUIDE as mandatory planner output** (RE_SPEC §7): annotated views,
   RED = blocking / BLUE = second tier, row-ID labels + jaw placement +
   scan-predicted value, scale bar, un-measurable callouts, posted on the issue
   with `?raw=true` URLs. Used successfully on E03 (guide commit on PR #4).
2. **Planner self-review of its own annotated images** — overlapping/clipped
   labels are a REVISE.
3. **Bench sanity rule in the MEASUREMENTS template** — reading wildly off the
   scan prediction → re-check the feature before recording.
4. **Feature-gated loop discipline** — the PR #4 thread shows the design working:
   clean SUBMISSION→VERDICT rhythm, per-verdict budget arithmetic ("2/11 used"),
   honest STOP-and-report twice (F00 datum, F12 comb ramp), and the manager's own
   flat-trim spec REFUTED by drafter evidence and superseded on the record —
   exactly the honesty the doctrine wants.

## B. Ratified V4 changes (decided by Muhammed, pending implementation)

1. **CONTEXT RELAY threshold → fixed 300k tokens** (was 40% plan / 50% mandatory
   of a 1M window). At 300k: handover at the next clean boundary, always. Rationale:
   run-1 quality was visibly fine at 300k and the relay cost is near zero, so relay
   early and often; never gamble on the 400–500k band again.
2. **Automatic handover → new session, no human in the loop.** Target flow: at
   300k the outgoing manager posts the HANDOVER comment, updates the tracker, then
   ITSELF initiates the successor with the one-line resume kickoff:
   - Windows: investigate spawning a fresh session programmatically
     (`claude -p`-style headless launch, or the app's session-management tools);
   - VPS: post the `resume OOM-Xnn` kickoff to the Slack channel — the bot IS the
     session spawner there, so automation is native.
   Fallback if spawning proves unreliable: today's manual one-line paste.
   Implementation must keep the §12 invariants: never mid-feature, verdicts stand,
   fresh drafter, no intake re-run.

## C. Problems found reviewing run-1 PRs/issues (proposed V4 fixes)

1. **Work-order issue closed mid-build.** Issue #3 is CLOSED while F05–F07 are
   officially "HELD on pin re-measures arriving on issue #3" — the human-gate
   channel was closed with asks still pending on it. V4 RULE: the part issue stays
   OPEN until the part's PR merges (merge commit closes it); pending-measurement
   asks live on an OPEN issue, always.
2. **Submission-comment bloat.** Submissions grew 6.7k → 8.9k → 14k chars
   (F01→F02→F03), duplicating what the commit and committed files already hold.
   V4 RULE: submission comment ≤ ~3k chars — feature ID, one-line what, param
   deltas, acceptance evidence (numbers), image links; full analysis goes in
   committed files. Protects thread readability AND the manager's context budget
   (14k-char comments are what pushes a session to relay faster).
3. **Tracker-cell bloat.** The E03 tracker cell is a multi-thousand-word state
   dump duplicating issue/PR content. V4 RULE: tracker cells are STATUS + feature
   counter + links (issue/PR/handover) — one or two lines. The PR thread is the
   memory; the tracker is the index.
4. **Per-feature drafter is the de-facto standard — formalize it.** Finished
   agent transcripts are not retained (observed: "Drafter #1 could not be resumed
   — transcript recycled. Spawning drafter #2 from the PR thread."). V4: drop the
   keep-one-drafter-alive-via-SendMessage assumption; standard = fresh drafter per
   feature, briefed from plan + PR thread + committed code (the thread IS the
   memory). This also removes the ~10-feature recycle rule (§12) as moot.
5. **Environment parity is a gate property.** Tracker notes intake ran
   "in-context, not organisationally independent" because `re-*` agents and the
   cad skills were not installed in that environment. V4 RULE: session BEGIN
   verifies agents + skills + tools exist on THIS machine; missing → HALT and
   report, never silently improvise in-context (independence of QA is part of the
   gate, not a nice-to-have).
6. **Out-of-order feature execution — codify what run 1 improvised.** F12 ran
   before F04–F07 (dependency: F03's verdict touched the comb underside). It was
   the right call; V4: allow out-of-order execution when the manager states the
   dependency in the ruling; plan order is default, not law.
7. **Deliverable-set drift between parts.** E05 (delivered under v2-era flow)
   shipped Blender renders + PDF; v3 parts ship render_views sets + README.
   V4: state explicitly that pre-v3 deliveries are grandfathered; do not
   retro-redo them (E05 open item stands: re-caliper F02 before tooling).
8. **Shared-clone races.** Two sessions in `C:\src\oomwoo-re` raced (vanished
   branch, files swept into a foreign commit). V4 RULE (already in memory, put in
   spec): ONE session per clone; concurrent pipeline edits via `git worktree`.

## B2. Added at ratification (Muhammed, 2026-08-02)

3. **Manager model-tier rule**: the manager session MUST run the highest model tier
   available (Fable-class); relay successors inherit this requirement — a relay must
   never silently demote the reviewer, because the tier gap over the Opus workers IS
   the review authority. Successor can't meet the tier → HALT, don't continue lower.
4. **Agents & skills moved into the repo** (`.claude/agents/`, `.claude/skills/`) so
   environment parity holds on every clone — the run-1 "not organisationally
   independent" failure becomes impossible on any machine with the repo.

## D. Open questions for the V4 ratification session

- 300k relay + max-2-parts concurrency: is 300k per session still right when two
  parts interleave in one manager context? (Each part's reviews consume ~half.)
- Auto-spawn mechanics on Windows: which launcher is reliable enough to trust
  unattended? (Prototype before writing it into the spec.)
- Should the caliper guide get its own tool (`annotate_views.py`) so label
  placement is deterministic instead of per-planner matplotlib code?
