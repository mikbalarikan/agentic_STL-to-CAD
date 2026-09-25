# Baseline-skill blind replay (agent report, saved by orchestrator)

## B02 (baseline_run/)
- Datum: skill's "largest facet" picked a 3.4 mm² arm flank; agent replaced with area-weighted normal histogram + RANSAC seat annulus (129 mm², rms 0.013). Axis from hub normals 0.60° from seat normal. Clock: key pin at +X; arms 60.05/179.56/-61.14 snapped 60/180/300.
- 12 features; 1 valid solid, 75 faces, 5492.6 mm³.
- Arm section chosen 5.8×3.3 from scan PCA (5.7–6.2 × 3.3–3.5) — contradicts confirmed calipers D-02 5.33 / D-01 4.07. Hex depth: caliper D-11 3.44 won (3.45). Hex A/F 7.4 (photo ~7.32?). Counterbore top z -8.0 assumed.
- Gate (baseline band p95≤0.3/max≤0.8), agent's own KD-tree gate (full closest_point OOM at 15 GB):
  - scan→CAD all (bristles) rms 7.66 p95 22.5 max 29.5
  - scan→CAD rigid only rms 0.239 p95 0.517 max 1.223
  - CAD→scan all rms 0.417 p95 0.895 max 2.894
  - CAD→scan observable rms 0.290 p95 0.637 max 1.629
  - FAIL. By arm p95: 60° 0.51, 180° 0.49, 300° 0.75.
- Agent verdict: valid design-intent solid, not releasable; owner should recheck D-01/D-02.
- Skill gaps: datum recipe fails on scans; axis eigen formula wrong; networkx dep undocumented; gate OOM; no caliper-vs-scan policy; no guidance on non-part scan content/unobservable; no deformed-instance or twisted swept-arm guidance.

## DRM screw (baseline_run/)
- Datum: largest flat RANSAC 33.6 mm² rms 0.007; opposite face parallel 0.61°, 5.107 apart. Bore axis tilt 0.51°; pentagon centre vs bore 0.04 → snapped concentric. Clock: one flat normal on +X (-2.69°).
- 8 features; 1 valid solid, 36 faces, 267.35 mm³.
- Params: boss Ø8.1×0.45; pentagon apothem 4.50; draft 4.5°; chamfer 30°; height 5.1; lower bore Ø3.9 + double-D 3.3 at 52.5°; lip Ø2.2 z2.6–4.0; upper bore Ø4.1; rounds R0.5 / R0.3.
- Gate (inspection only): scan→CAD rms 0.0620 p95 0.1445 max 0.2573; CAD→scan rms 0.0560 p95 0.1322 max 0.2322. PASS plastic and (barely) machined.
- Limitations: units unverified; 52.5° kept measured; boss notch not modelled. Gaps: no debris guidance; no draft-vs-exact rule; same eigen/networkx issues.
- Harness blocked the agent from writing REPORT.md; this file is the saved text.
