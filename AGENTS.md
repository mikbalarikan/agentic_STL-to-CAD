# Agent instructions for this repo

This repo holds several versions of an STL→CAD (STEP) reverse-engineering harness under
`harnesses/<id>/`. See `harnesses/README.md` for the list.

## Picking a version

- When the user says "use v0" / "v0 kullan", "use v1" / "v1 kullan", and so on, install that
  version's skills before starting the job:
  `python3 tools/harness.py install <id> --dest <your agent's skills dir>`.
  - For Claude Code the default `--dest` is `~/.claude/skills`. Use a project-local skills
    directory if the user wants the install isolated.
  - Then follow that version's entry skill (`HARNESS.json#entry_skill`).
- If the user names no version, ask which one. Do not guess.
- Check what is installed: `python3 tools/harness.py which --dest <dir>`.
- Never mix skills from two versions in one skills directory.

## Working on the harnesses

- `v0` and `v1` are frozen (tags `harness-v0`, `harness-v1`). Do not change their behaviour. Put new
  ideas in a new version folder (`harnesses/v2/`, ...) with its own `HARNESS.json`.
- Shared evidence (`golden-examples/`, `baseline/`) is read-only.
- Run a version's checks with `python3 tools/harness.py doctor <id>` and
  `python3 tools/harness.py selftest <id>`.
