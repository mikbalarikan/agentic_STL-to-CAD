# Case: `deviation_gate.py` reproduces the OD-H12 golden deviation stats bit-for-bit

## Skill
`stl-re-verify`

## Input (repo paths)
- `golden-examples/OD-H12_delonghi-dedica-pump/0_input/OD-H12-Pump.stl` (full-res scan)
- `golden-examples/OD-H12_delonghi-dedica-pump/report/alignment_T1.json`
- `golden-examples/OD-H12_delonghi-dedica-pump/OD-H12-Pump_datum.stl`
- Golden reference: `golden-examples/OD-H12_delonghi-dedica-pump/report/deviation_gate.json`

## Command or procedure
```
python3 skills/stl-re-verify/scripts/deviation_gate.py \
  --scan golden-examples/OD-H12_delonghi-dedica-pump/0_input/OD-H12-Pump.stl \
  --scan-kind full \
  --align golden-examples/OD-H12_delonghi-dedica-pump/report/alignment_T1.json \
  --cad golden-examples/OD-H12_delonghi-dedica-pump/OD-H12-Pump_datum.stl \
  --regime <regime.json with bands p95_mm:0.30, max_mm:0.80> \
  --out <run>/qa/deviation.json
```
(`deviation_gate.py --help`: required `--scan`, `--scan-kind {full,decimated}`, `--cad`,
`--regime` (required — see case 03); optional `--align`, `--registration`, zone/mask/sampling
flags.)

## Expected outcome
Cited from `analysis/golden/OD-H12.md` §7/§9 and `reviews/stl-re-verify.md` "What I ran": scan→CAD
p95 **0.4478 mm**, max **2.4934 mm** (Band NOT MET vs the 0.30/0.80 regime — this is the exact
"Band NOT MET" case in SYNTHESIS §0.1); unobservable CAD fraction **25.65%**. The review's own
standard is "max absolute difference to `report/deviation_gate.json` over every statistic and
all 8 region blocks: **0**" — i.e. exact match to the recorded golden value, not a tolerance
band.

## Baseline behaviour (cited)
The baseline skill's deviation gate is "blocking" with no per-region attribution and no
observability split (`analysis/baseline/stl2step-skills.md` §7 "Deviation gate", and §5.6/§6.11:
"the gate is 'blocking'... the skills define no verdict for a missed band... give no method to
classify or exclude unscanned regions"). A baseline-only agent computing this same scan→CAD
distance would report a single p95/max pass-fail with no unobservable-fraction context, and
because the OD golden's own delivery treated this as a validity PASS despite the miss
(`analysis/SYNTHESIS.md` §0.1: "Validity PASS. Band NOT MET"), the baseline gate's binary framing
would either force an unwarranted FAIL or (per its own precedent) simply not represent the miss
at all.

## Last observed result
**Run this session** (2026-09-25): `scan_to_cad n 493060 rms 0.2174 p50 0.1012 p95 0.4478 p99
0.6745 max 2.4934`; `cad_to_scan n 300000 ... p95 3.4303 max 9.0269`; `cad_to_scan_observable n
14870 ... p95 0.5671 max 8.6481`; `unobservable CAD fraction 25.65%`. This matches the review's
own reproduction exactly ("scan→CAD n 493,060, p95 0.4478, max 2.4934... Max absolute difference
to `report/deviation_gate.json` over every statistic and all 8 region blocks: 0") and the
post-fix re-verification ("all match `report/deviation_gate.json` with zero difference in every
statistic"). **PASS.**
