# Golden examples

Successful STL→CAD reverse-engineering projects used as **input** for
distilling the skills in this repo. Each folder is the project's working record
imported as-is (intake, measurements, build scripts, QA reports, verdicts,
renders, final STEP). Do not edit them — they are evidence, not templates.

| Project | Part | Toolchain | Outcome | Record depth |
|---|---|---|---|---|
| [`M02-02-03_watertight-design-intent`](M02-02-03_watertight-design-intent/) | Compound spur gear 30T/17T | build123d (`model.py`) | Independent QA **PASS** | full: spec, params, QA + reproducibility reports |
| [`OOM-B02_side-brush-3-arm`](OOM-B02_side-brush-3-arm/) | Robot-vacuum side brush, 3 arms | build123d + trimesh; NX | **APPROVED** it2/3, 3 declared limitations | full: intake, calipers, params, QA scripts, verdict, iteration 1 kept |
| [`OOM-P03_mop-pad-bracket`](OOM-P03_mop-pad-bracket/) | Mop pad bracket | build123d + trimesh; NX | **APPROVED** it2/3 (it1 REVISE) | full: intake, calipers, params, sections, PDF report |
| [`dreame_brush-caps`](dreame_brush-caps/) | Brush screw cap + snap cap | trimesh + build123d; NX | Delivered: screw p95 0.085 PASS, snap p95 0.157 | full: source, gates, alignment, deviation maps |
| [`OOM-E01_battery-2P4S-6800`](OOM-E01_battery-2P4S-6800/) | Battery pack 2P4S | NX only | stub | **none** — see its README |

## What was left out (and why)

Each project has a `MANIFEST.json` listing **every** source file with bytes +
sha256; excluded entries carry a `reason`. Originals stay on Google Drive at
`source_path`.

- `1_scan_raw_STL/` — raw scanner project/cache (vendor formats, ~1.7 GB total).
- `*.prt` — Siemens NX native parts (binary, need NX); the STEP export is the
  portable record.
- Scan STLs > 50 MB — replaced by `*_scan_decimated.stl` (950k triangles,
  quadric decimation). The decimation provenance (original sha256, triangle
  counts, bbox, decimated→original deviation p50/p95/max) is in the excluded
  entry's `decimated_copy`. Measured max deviation ≤ 0.028 mm — fine for
  inspection, **but official deviation gates must re-run against the original
  full-resolution scan.**
