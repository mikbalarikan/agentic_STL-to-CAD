# CHANGES v3 → v4 (ratified & implemented 2026-08-02)

Source: `V4_NOTES.md` (first-run feedback, OOM-E03 + OOM-E05). Spec is now
`RE_SPEC.md` v4; session prompt rewritten. Rationale for every item lives in
V4_NOTES.md — this is the what/where.

| # | Change | Where |
|---|---|---|
| 1 | Context relay: fixed **300k token** threshold (no 40/50% band), relay at next clean boundary, never mid-feature | RE_SPEC §12, SESSION_PROMPT |
| 2 | **Manager tier rule**: manager = highest model tier (Fable-class); relay successors inherit; can't meet tier → HALT | RE_SPEC §12, SESSION_PROMPT |
| 3 | Relay succession: Slack/VPS states the one-line kickoff (native spawn); desktop reports the `resume` command (auto-spawn = open prototype); outgoing session STOPS after handover | RE_SPEC §12 |
| 4 | **Fresh drafter per feature** (transcripts not retained; PR thread is the memory); keep-alive-via-SendMessage removed; §12 drafter-recycle rule superseded | RE_SPEC §5 §12, SESSION_PROMPT, `.claude/agents/re-drafter.md` |
| 5 | **Submission comments ≤ ~3k chars** (feature #, op, param deltas, acceptance numbers, image links; analysis in committed files) | RE_SPEC §5, re-drafter agent, SESSION_PROMPT |
| 6 | **Part issue stays OPEN until PR merge** ("Closes #n" in PR body); pending human asks always on an open issue | RE_SPEC §8, SESSION_PROMPT |
| 7 | **Tracker cells = status + feature counter + links** (1–2 lines, no state dumps) | RE_SPEC §8 |
| 8 | **Environment parity check at BEGIN** (agents, skills, python deps, gh, machines.toml hostname — any missing → HALT, never improvise roles in-context) | RE_SPEC §10, SESSION_PROMPT BEGIN |
| 9 | **Agents & skills ship in the repo**: `.claude/agents/re-*.md` + `.claude/skills/{cad-qa-gate,stl2step-build123d,cad-section}` — parity on every clone; user-level copies removed on MERY | repo `.claude/`, SETUP §1.8 |
| 10 | **Out-of-order features** allowed with manager-stated dependency (run-1 F12 precedent); plan order is default | RE_SPEC §5, SESSION_PROMPT |
| 11 | **Pre-v3 deliveries grandfathered** (E05 keeps Blender/PDF set; open items stand as tracker notes) | RE_SPEC §9 |
| 12 | **One session per clone**; concurrent main edits via `git worktree` | RE_SPEC §10 |
| 13 | Consistency fix: §7 now says absolute `?raw=true` image URLs (was "relative", contradicting §8) | RE_SPEC §7 |

Not changed (deliberately): all v2/v3 measured gates (Tier-1 ±0.15, Tier-2 1.6/4.0,
Tier-0, datum audit ≤0.3°/≤0.15), the anti-Lego doctrine, feature budget mechanics,
the caliper guide standard, GitHub protocol structure, build123d ratification.

Open (V4_NOTES §D): Windows auto-spawn prototype; 300k-with-2-parts question;
optional `annotate_views.py` for deterministic caliper-guide labels.
