# Case: `pattern_count.py` reproduces M02 gear tooth counts (30 / 17)

## Skill
`stl-re-measure-intent`

## Input (repo paths)
- `golden-examples/M02-02-03_watertight-design-intent/M02-02-03_WATERTIGHT_SOLID.step`
  (re-tessellated to STL at 0.01 mm / 0.1 rad, matching the golden QA's own re-tessellation,
  `analysis/golden/M02-02-03.md` §4)

## Command or procedure
```
python3 skills/stl-re-measure-intent/scripts/pattern_count.py \
  --mesh <m02.stl> --signal radius --stations 0.5,1.5,2.5 --orders 10,40 --tol 0.002 \
  --out <run>/measure/m02_big.json
python3 skills/stl-re-measure-intent/scripts/pattern_count.py \
  --mesh <m02.stl> --signal radius --stations 3.5,6.5,9.5 --orders 10,40 --tol 0.002 \
  --out <run>/measure/m02_small.json
```
(`pattern_count.py --help`: required `--mesh`, `--stations` (>=3, CHK-COUNT), `--out`;
`--signal {radius,inner,mass}` default `radius`; `--orders lo,hi` default `2,60` (see MINOR
finding m1 in `reviews/stl-re-measure-intent.md` — default should be `3,60`); `--tol` sets the
max-abs-radial-residual qualification threshold, "M02 hard-coded orders 10-40 and 0.002 mm"
per the script's own provenance header.)

## Expected outcome
Exact match to the recorded golden values (`analysis/golden/M02-02-03.md` §4,
`G/qa_report.json#gears.*.station_details`): big gear **30** teeth (qualified orders
{10,15,30}, residual at 30 = 7.77e-06 mm), small gear **17** teeth (qualified {17}, residual
6.08e-06 mm). Crest-peak counts (31 / 16) are documented as wrong and diagnostic-only
(`G/VERDICT.md:25`) — CHK-COUNT must select the FFT/rotational-order count, not the peak count.

## Baseline behaviour (cited)
No baseline skill or golden project script for this method is in the repo
(`analysis/golden/M02-02-03.md` §11, Questions 8; `pattern_count.py`'s own provenance header:
"NEW CODE - no golden source code exists for this method"). The only prior practice was the M02
QA's own crest-peak picking, which the golden record itself calls wrong for both gears (31 vs 30,
16 vs 17) and labels diagnostic-only. A pattern-count method that used crest peaks instead of
rotational-order qualification would reproduce the golden's own historical mistake.

## Last observed result
**Run this session** (2026-09-25): big gear stations 0.5/1.5/2.5 all gave
`FFT-dominant=30 selected-maximal=30`, `COUNT = 30`, `CHK-COUNT pass`, with diagnostic peak
counts [32, 32, 32] (disagreeing with 30, as expected — the script itself notes "peaks are
diagnostic only (M02 31/16)"). Small gear stations 3.5/6.5/9.5 all gave
`FFT-dominant=17 selected-maximal=17`, `COUNT = 17`, `CHK-COUNT pass`, peaks [18,18,18]. This
matches the review's own reproduction (`reviews/stl-re-measure-intent.md` "What I ran": "30 at
z 0.5/1.5/2.5 ... and 17 at z 3.5/6.5/9.5"). **PASS.**
