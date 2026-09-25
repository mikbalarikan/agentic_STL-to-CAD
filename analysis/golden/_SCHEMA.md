# Golden-example extraction schema (fixed)

Every `analysis/golden/<project>.md` uses exactly these sections, in this
order. Every claim cites a path relative to the repo root (optionally
`:line` or `#json.key`). Write "not recorded" rather than guessing.

```
# <project> — evidence extraction

## 0. Record inventory
Which files carry method evidence (one line each), and which are pure outputs.

## 1. Part class and geometry type
Part, function, material/process if known, geometry class (prismatic / turned /
gear / freeform / thin-wall / mixed), size envelope, symmetry.

## 2. Stages actually run, in order
Numbered list: stage → artefact produced → path.

## 3. Datum / alignment method
How the scan was put into a design frame: method, primary/secondary/tertiary
datums, numbers (residuals, angles, offsets), and the file that records it.

## 4. Measurement methods
Sections, fits (plane/cylinder/circle/sphere), histograms, caliper inputs,
photos. For each: tool/function, what was measured, numeric result.

## 5. Design-intent rounding
Table: feature | measured | chosen | rule used (round to 0.5, standard size,
symmetry, mating part…) | source path.

## 6. Feature tree
Ordered build123d feature list as actually built (base → features → fillets),
with parameter names.

## 7. Gates run, with actual numbers
Table: gate | threshold (and where the threshold came from) | measured |
PASS/FAIL | source path. Include deviation (p50/p95/max, signed/unsigned,
which scan: full-res or decimated), watertight/validity, volume, visual, etc.

## 8. Iterations
Per iteration: what failed, root cause, what fixed it, evidence path.

## 9. Declared limitations and assumptions
Verbatim-ish with path. Include anything that missed a band and how it was
explained.

## 10. Deviations from the baseline skill
Where the project did something the v0 doctrine (`baseline/`) does not say,
or contradicts it; did it help? cite both sides.

## 11. Reusable code
Table: file:function | what it does | generality (reusable as-is / needs
generalising / project-specific) | determinism concerns.

## 12. Lessons
Candidate rules for the new skills, each tagged with evidence path(s) and
whether it came from a success, a failure, or a limitation.

## Questions
Conflicts or missing evidence (no guessing).
```
