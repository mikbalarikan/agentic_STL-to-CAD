# OOM-B02 — ASSUMPTIONS LEDGER for "proceed with assumptions" (2026-07-29)

Muhammed directed the line to proceed without a caliper session. Every assumption below is
load-bearing on the final verdict and is reproduced verbatim in VERDICT.md and the report.

| # | Assumption | Basis | If wrong |
|---|---|---|---|
| A1 | **F01 hex AF = 7.358** (scan area-fit, rms 0.037, ~2/3 of the hexagon scanned). NOT intent-snapped to 7.0/7.5. | no caliper reading exists in any photo | the drive fit is wrong; one reading forces a re-run. Highest risk on the part. |
| A2 | **F06 (D-05, 24.84) is STRUCK from Tier-1** — it is not achievable as a two-jaw diametral reading on a 3-lobed skirt (no antipodal flat-flat pair; min achievable 25.99 on the scan). `SKIRT_R_FLAT` reverts to **scan authority 12.55** (it1 used 12.420 and re-measured 25.487, Δ+0.647 OUT OF BAND). | geometry proof in PARAM_TABLE §G-1 | if 24.84 was a real skirt dim measured some other way, the flat radius is 0.13 mm large. |
| A3 | **D-06 (25.79) likewise not used** — also below the achievable window (25.99). Unassigned, as are D-09/D-10/D-12. | same geometry argument | — |
| A4 | Tier-1 is gated on the **6 surviving photo-transcribed dims** (F02, F03, F05, F10, F11 + X01 soft). **17 of 24 dims are ABSENT, not passed.** The verdict states this. | partial sheet | verdict is weaker than a full Tier-1 pass; it is labelled as such. |
| A5 | **Absolute scale UNVERIFIED** — ENV-1/2/3 empty, RE_SPEC §2 envelope check impossible. No global scale applied (the 0.4–1.6% disagreement is not uniform). | RE_SPEC §2 | whole part could be off by a uniform factor. |
| A6 | **Hex pocket Tier-2 is masked over the 124° scan gap** — distance to a hole edge is not a surface deviation. Only the scanned ~2/3 of the hexagon is gated. | intake occlusion map | — |
| A7 | **SAF-1 internal boss is an interior/occluded bucket** — reported with numbers, NOT gated at 0.8 mm. It sits inside the cup, reachable only through the opening; the scan cannot resolve its moulded edge softness. RE_SPEC §4 permits interior buckets to be reported not gated. | RE_SPEC §4 | the key's internal half is less controlled than the hole/nub. |
| A8 | **SAF-1 hole is held as the key datum** (Q5 fallback, Muhammed's stated fallback). Nub + recess gated at 0.8; hole bottom photo-inferred, not gated. | Q5 fallback | — |
| A9 | Central bore interior, tuft-socket interior, SAF-1 hole bottom = **photo-inferred, not gated** (100% occluded). Screw NOT modelled (COTS), masked out of the gate reference. | intake §4, R2 | — |
| A10 | Bristles (r > 38.5) **not modelled, excluded from both gates**, soft band ±3 mm. Tuft modelled at the anchor (r = 38.20), not the tips. | R4 / Muhammed's brief | — |
| A11 | Arm path **planar in r-z**, 3-arm mean; tangential drift 0.97–2.20 mm treated as free-state deformation and left as a reported Tier-2 residual. | Q4 ruling | arm flank residual is expected, not chased. |
| A12 | **Blender is not installed** on this machine. Documentation renders are produced with a purpose-written z-buffer rasteriser (the W01 precedent), geometry = the delivered STEP. | environment | renders are diagrammatic, not Cycles studio images. |
| A13 | The `re-*` agents and `cad-qa-gate` / `stl2step-build123d` skills named in SESSION_PROMPT are **not installed** here. QA is re-derived from the raw scan with independently written code, but by the same context that built the part — it is **not** an organisationally independent verifier. | environment | the gate is weaker than the RE_SPEC intends; stated in the verdict. |
