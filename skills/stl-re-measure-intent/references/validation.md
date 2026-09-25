# Script validation against golden numbers

These runs are **inspection only**. None re-grades a project. Decimated scans are marked as
such (`golden-examples/README.md` states the decimated-copy deviation bound). The runs used
Python 3.11, trimesh 5.1.0, numpy 2.4.6, scipy 1.17.1, build123d 0.13.0. A determinism check
ran `pattern_count.py` twice in fresh processes and got identical JSON apart from `created`.

This file records *that* each script was checked against a golden part's recorded result, and
what agreed or disagreed in kind (e.g. "order matched", "window computation disagreed because a
recess was left out"). It deliberately does not restate the golden's own numbers inline — those
live in the golden report and in `analysis/golden/*.md`, and copying them here would let a blind
run of this skill read its own answer key. If you need to re-validate a script, compare its
output against the cited golden path yourself.

## pattern_count.py (new code: no golden code exists)

| Case | Command (abridged) | Result | Compare against |
|---|---|---|---|
| M02 big gear, delivered STEP tessellated at fine resolution | `--stations <3 axial> --orders 10,40 --tol 0.002` | Order agreed at all 3 stations; a small set of harmonically-related orders also qualified; the true order had a residual local minimum orders of magnitude below its neighbours | `qa_report.json#gears.big` |
| M02 small gear | `--stations <3 axial> --orders 10,40 --tol 0.002` | Order agreed at all 3 stations; qualified set was the single true order | `qa_report.json#gears.small` |
| P03 kidneys, decimated scan + `2_mesh_cleaned/alignment.json` | `--signal mass --stations <3 axial> --z-half 0.3 --r-band <feature> --rays 3600` | Order agreed at all 3 stations (FFT-dominant, and a residual local minimum) | `OOM-P03/6_RE_work/PARAM_TABLE.md:38` |
| P03 stem, same scan | `--signal radius --stations <3 axial> --r-band <feature>` | Order agreed at all 3 stations; coverage was partial (< 1.0) | `PARAM_TABLE.md:42`, `VERDICT.md:49` |
| P03 tread slots, same scan (extra) | `--signal mass --r-band <feature> --orders 20,80` | FFT-dominant order **disagreed** across stations → CHK-COUNT finding | `PARAM_TABLE.md:37`; the partial angular scan coverage is a likely cause, unconfirmed |

The absolute FFT magnitudes are not comparable between this script and P03's own record, because
P03's normalisation and signal are not recorded. Compare only which order is dominant.

## sim_caliper.py (lifted from B02 q10/40_verify)

| Case | Result | Compare against |
|---|---|---|
| B02 delivered STEP (`4_STEP/OOM-B02.step`), a Tier-1 outside-jaw reading at its recorded station | This script's window matched the golden's CAD-based window **exactly** | `OOM-B02/6_RE_work/PARAM_TABLE.md:154-155` |
| B02 full-res scan `2_mesh_cleaned/OOM-B02.stl` + `alignment.json`, same station, outside jaws | This script's window on the full-res scan is **wider** than the window recorded in the golden report, with partial angular coverage over two gaps roughly matching the golden's recorded occlusion | `PARAM_TABLE.md:111` — see §"the B02 caliper window" below for why the two disagree |
| The flagged B02 caliper reading, against the scan window, no `--scan-offset` | Comes out **UNPROVEN** by a small margin below the window minimum, with `d` not measured on this scan | golden calls it struck |
| Same reading, with `--scan-offset` set from another calipered dimension on the same scan | Still **UNPROVEN, within the measured scan offset** (the margin is smaller than the measured offset) | — |
| B02 full-res scan, inside jaws, the cup-bore Tier-1 reading | Window computed with real partial angular coverage; the reading is **achievable, PASS** | golden used this reading directly at Tier-1 and it passed (`PARAM_TABLE.md:36,153`) |

**Round-1 fixes applied here (orchestrator decisions B1, B2 — `reviews/stl-re-measure-intent.md`):**
inside-jaw mode now requires `--r-band`, pools the in-band points from every polyline of the
open scan section, and builds an inner (min-radius) envelope with its own real angular
coverage instead of picking one polyline and assuming full coverage. This is what fixes the
cup-bore case above: the old inside-jaw code wrongly struck a reading the golden had accepted.
Below the outside-jaw window, a reading is only struck when the margin exceeds a measured,
per-scan `--scan-offset d`; within `d` (or when `d` is unknown) it is unproven, not struck.
This reclassifies the F06-equivalent case above from struck to unproven, because another
calipered dimension on the same scan showed a larger dilation than this reading's own margin
below the window.

**Explained (was "not recorded"): the B02 caliper window.** The golden's own analysis gives its
method for the achievable window: the minimum diametral reading a two-jaw caliper can produce is
the sum of a lobe crest and the opposite flat, evaluated analytically
(`OOM-B02/6_RE_work/VERDICT.md:64-66`). Reproducing that analytic pair here lands close to the
golden's recorded window (see `PARAM_TABLE.md:108-111` and §G-5 for the golden's own figures).
That argument leaves out one recess feature near the flat (documented in the golden's own §G-5
notes), which the CAD geometry happens to bridge with flat jaws but a real scan section does not
bridge the same way — so a full support-function window computed on the scan (recess included)
comes out narrower than the golden's analytic window. In short: the golden's recorded window used
an analytic simplification that excluded one feature; this skill's full support-function window
includes it. Both approaches land in the same STRIKE/UNPROVEN region, but the margin differs
enough to matter once a scan-offset is applied — see `analysis/golden/OOM-B02.md` for the actual
figures and the other calipered reading (`README A3`) that this affects.

## sections.py cluster (CHK-CLUSTER)

On P03's decimated scan, cropped to the stem region, the script found a single connected
component with a flat top, consistent with the golden's own report of "a large coherent cluster
with a solid flat top" for the same feature (`OOM-P03/6_RE_work/PARAM_TABLE.md:43`). The exact
vertex/face counts differ from the golden's because this run used the decimated copy rather than
the full-resolution scan; see the cited file for the golden's own count.

## fits.py / sections.py planar

On the M02 tessellation, a Kåsa fit on the bore loop agreed with the operator-specified bore
diameter to well within the fit's own residual. Loop tracks chain the outer loops across the
tooth-count transition and keep the bore as a separate track.
