# Benchmark (planned, not built yet)

Goal: compare harness versions (`harnesses/v0`, `v1`, ...) and LLMs on the same parts, with
no human in the loop, so that a harness change or a model change shows up as a number.

## Shape (to be built after v1)

- **Cases:** parts with a scan and a trusted reference.
  - From `golden-examples/`: DRM screw and snap, B02, P03, M02, OD-H12.
  - The v0 worked run, OD-H22.
  - The NX projects whose scans fit the size budget (`nx-re-intake` branch).

  Each case states its regime, calipers (if any), photos, and the scripted answers to the
  human gates.
- **Matrix:** harness × model × agent CLI. Each run uses a fresh run folder and a fresh
  skills directory (`tools/harness.py install <id> --dest <run>/skills`).
- **Oracle user:** human gates and decision cards are answered by a script from the case
  file, the same way every time. Guided-mode cases count the cards the script had to answer.
- **Grader:** the benchmark's own grader, never the harness's verify. It runs an independent
  ICP and a two-way deviation against the full-resolution scan, plus a STEP validity check
  (one closed solid), plus face and feature census against the reference where one exists.
- **Recorded by the runner:** tokens, cost, wall time, tool calls, crashes and timeouts.
- **Recorded by the harness:** `run_metrics.json` (v1+).
- **Report:** one table per case and a summary per harness × model. The scores are
  deviation, validity, verdict honesty (does the harness's verdict agree with the grader),
  tokens and time.
