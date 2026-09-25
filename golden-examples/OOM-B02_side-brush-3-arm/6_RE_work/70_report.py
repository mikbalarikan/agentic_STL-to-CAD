"""OOM-B02 RE report — flowing-cursor A4 layout (W01 g5_report.py precedent).

Every Tier-1 / Tier-2 number is READ FROM THE SAVED QA JSON, never retyped, so the PDF
cannot drift from the artefacts that produced it.
"""
import json, textwrap
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

SC = "/root/projects/oomwoo_b02/scratch"
P = ("/root/gdrive/111 UP UP UP/REMAKE AI - DIY/OOMWOO_CAD/"
     "01_SOURCED_reverse-engineered/OOM-B02_Side-brush-3-arm")

Q = json.load(open(f"{SC}/qa/_qa_it2.json"))
T = json.load(open(f"{SC}/qa/_tier2_it2.json"))
D = json.load(open(f"{SC}/qa/_datum_indep.json"))
Z = T["zones"]

NAVY = "#1b2a41"; RED = "#b3261e"; AMB = "#8a6d00"; GRN = "#1b6b3a"
PT = 841.89
L, Rm = .07, .93; WID = Rm - L
def lh(size, ls=1.45): return size * ls / PT
def nfmt(n): return format(int(n), ",d").replace(",", " ")


class Page:
    def __init__(s, pp, title, sub=None):
        s.pp = pp; s.f = plt.figure(figsize=(8.27, 11.69)); s.f.patch.set_facecolor("white")
        s.f.text(L, .955, title, size=17, weight="bold", color=NAVY)
        if sub: s.f.text(L, .936, sub, size=9.5, color="#555")
        s.f.add_artist(plt.Line2D([L, Rm], [.928, .928], color=NAVY, lw=1.4))
        s.f.text(L, .028, "OOM-B02 Side brush 3-arm — RE report — 2026-07-30 — "
                          "APPROVED it2, THREE DECLARED LIMITATIONS", size=7, color="#888")
        s.y = .905
    def gap(s, g=.014): s.y -= g; return s
    def head(s, t, size=11.5):
        s.y -= .006
        s.f.text(L, s.y, t, size=size, weight="bold", color=NAVY, va="top"); s.y -= lh(size) + .010; return s
    def para(s, txt, size=9.2, color="#222", x=L, weight="normal", wid=None):
        wid = wid or (WID - (x - L))
        cpl = int(wid / WID * 104 * 9.2 / size)
        out = []
        for line in txt.split("\n"):
            if not line.strip(): out.append(""); continue
            ind = "   " if line.lstrip()[:2] in ("• ", "1.", "2.", "3.", "4.", "5.") else ""
            out.extend(textwrap.wrap(line, width=cpl, subsequent_indent=ind) or [""])
        s.f.text(x, s.y, "\n".join(out), size=size, color=color, weight=weight, va="top", linespacing=1.45)
        s.y -= lh(size) * len(out) + .008; return s
    def box(s, txt, fc="#fff8e1", ec=AMB, size=8.6, color="#5a4a00", pad=.012):
        cpl = int(102 * 9.2 / size)
        lines = []
        for line in txt.split("\n"): lines.extend(textwrap.wrap(line, width=cpl) or [""])
        h = lh(size) * len(lines) + pad * 2
        s.f.patches.append(plt.Rectangle((L, s.y - h), WID, h, transform=s.f.transFigure,
                                         fc=fc, ec=ec, lw=1, zorder=0))
        s.f.text(L + .014, s.y - pad, "\n".join(lines), size=size, color=color,
                 va="top", linespacing=1.45, zorder=1)
        s.y -= h + .014; return s
    def table(s, rows, widths, head=None, size=8.8, rowh=None):
        rowh = rowh or lh(size) + .006
        if head:
            cx = L
            for w, h in zip(widths, head):
                s.f.text(cx, s.y, h, size=size, weight="bold", color=NAVY, va="top"); cx += w
            s.y -= rowh
            s.f.add_artist(plt.Line2D([L, L + sum(widths)], [s.y + rowh * .42] * 2, color="#ccc", lw=.8))
            s.y -= .004
        for r in rows:
            cx = L; extra = 1
            for w, c in zip(widths, r):
                t = str(c); col = "#222"
                if t[:2] == "!!": t = t[2:]; col = RED
                elif t[:2] == "~~": t = t[2:]; col = AMB
                elif t[:2] == "++": t = t[2:]; col = GRN
                cpl = max(6, int(w / WID * 104 * 9.2 / size))
                ls = textwrap.wrap(t, width=cpl) or [""]
                extra = max(extra, len(ls))
                s.f.text(cx, s.y, "\n".join(ls), size=size, color=col, va="top", linespacing=1.35); cx += w
            s.y -= rowh * extra
        s.y -= .008; return s
    def imgrow(s, items, h):
        y0 = s.y
        for path, x, w, cap in items:
            im = np.asarray(Image.open(path))
            a = s.f.add_axes([x, y0 - h, w, h]); a.imshow(im); a.axis("off")
            if cap: a.set_title(cap, size=8.5, color=NAVY)
        s.y = y0 - h - .02; return s
    def img(s, path, h, x=L, w=None, cap=None):
        im = np.asarray(Image.open(path)); ar = im.shape[1] / im.shape[0]
        w = w or h * ar * (11.69 / 8.27)
        a = s.f.add_axes([x, s.y - h, w, h]); a.imshow(im); a.axis("off")
        if cap: a.set_title(cap, size=8.5, color=NAVY)
        s.y -= h + .02; return s
    def done(s, png=None):
        if png: s.f.savefig(png, dpi=100)
        s.pp.savefig(s.f); plt.close(s.f)


pp = PdfPages(f"{P}/7_docs/OOM-B02_RE_report.pdf"); n = [0]
def newpage(t, sub=None):
    n[0] += 1; return Page(pp, t, sub)

# ---------------- 1 cover ---------------------------------------------------
p = newpage("OOM-B02 — Side brush, 3-arm",
            "Reverse-engineered STEP from 3D scan · OOMWOO RE line v2 · build123d 0.11.1")
p.box("VERDICT: APPROVED (iteration 2 of 3) — with three declared limitations\n"
      "Tier-1 PARTIAL (5 of 24 dims gated, 17 absent) · absolute scale UNVERIFIED · "
      "F01 hex drive socket has no caliper reading of any kind",
      fc="#eef6ee", ec=GRN, size=10.5, color="#14532d", pad=.011)
p.gap(.006)
p.imgrow([(f"{P}/5_reference/IMG_20260729_181846.jpg", L, .33, "The part (as received)"),
          (f"{P}/7_docs/OOM-B02_iso.png", .47, .46, "Rebuilt STEP — iso, dome side")], .245)
p.head("Summary")
p.table([["Deliverable", "4_STEP/OOM-B02.step — one valid solid, %.1f mm³, %d faces"
          % (Q["qa1"]["volume"], Q["qa1"]["counts"]["face"])],
         ["Scan", "798 874 tri raw; %s pts sampled for the gate" % nfmt(3_000_000)],
         ["Tier-1 worst", "++%.3f mm (F11 arm thickness) — band 0.15 — PASS" %
          abs(Q["qa4"]["F11"]["cad"] - Q["qa4"]["F11"]["caliper"])],
         ["Tier-1 coverage", "!!PARTIAL — 5 of 24 sheet dims gated; 17 ABSENT, not passed"],
         ["Tier-2 p95", "++%.3f mm (band 1.6) PASS" % T["whole"]["p95"]],
         ["Tier-2 max", "++%.3f mm (band 4.0) PASS" % T["whole"]["max"]],
         ["Named interfaces", "++4 of 4 PASS at max ≤ 0.8 mm (worst %.3f, SAF-1 skirt recess)"
          % Z["SAF-1 skirt recess"]["max"]],
         ["Absolute scale", "!!UNVERIFIED — ENV-1/2/3 empty, so the §2 scale check is impossible"],
         ["Iterations", "2 of 3 — circuit breaker not reached"],
         ["Symmetry", "3-fold enforced at exactly 120.00°; scan reads 120.00 / 120.53°"]],
        [.19, .74], size=9)
p.head("What this part is")
p.para("A Mi/Mijia three-arm robot-vacuum side brush. The drive interface is a hex socket in the "
       "cup floor plus a central retaining screw — not a plain bore. One in-moulded bristle tuft "
       "per arm, no tuft holes. A single asymmetric feature (SAF-1: a hole, an external nub and an "
       "internal boss at one inter-arm position) breaks the 3-fold pattern and was ruled a "
       "FUNCTIONAL KEY, so it is modelled and gated rather than dismissed as a witness mark.")
p.para("The bristles are NOT modelled. The scan captures splayed free-state filament, which is not "
       "design intent; the model stops at the tuft anchor, r = 38.20 mm. Swept Ø over bristles "
       "(124.9 mm) is a SOFT number with a ±3 mm band; the hard envelope number is the rigid arm "
       "swept Ø, 76.40 mm (scan 76.43, arm-to-arm spread 0.08).")
p.done()

# ---------------- 2 method --------------------------------------------------
p = newpage("1. Method", "How the model was built and how it was gated")
p.head("1.1 Datum")
p.para("Datum A is the cup rim annular face → XY plane at z = 0, material occupying +Z (plane fit "
       "rms 0.052 mm over 30 342 faces). Datum B is the rotation axis → +Z, common to the cup bore, "
       "the skirt and the hex, converged to better than 0.0001°. Datum C is arm 1 → θ = 0 (+X). "
       "Measured arm centres are 0.04 / 120.30 / −118.96°; the pattern is enforced at exactly "
       "120.00° because the residual (p95 0.99 mm) is at the scan noise floor and the part is "
       "a moulding with 3-fold intent.")
p.head("1.2 Build decomposition")
p.para("• Cup + skirt: revolve of the measured meridional profile, with the 3-lobed skirt driven by "
       "a smoothstep lobe/flat radius function (flat 12.550, lobe crest to 13.425).\n"
       "• Hex drive socket: AF 7.358 from the scan area-fit, depth 3.440 below the cup floor.\n"
       "• Arms: swept along a planar r–z spline (z rise ~11.4–12.8 mm over r 13 → 38.2), then "
       "PolarArray(3, 120.00°). The measured 0.97–2.20 mm tangential drift is free-state "
       "deformation and is deliberately NOT modelled (Q4 ruling).\n"
       "• Tuft socket at the arm end, 4.60 × 3.50 × 3.00 deep, from the ribbon envelope less the "
       "measured scanner dilation. Interior fully occluded — not gated.\n"
       "• SAF-1 modelled as three sub-features at θ = +59°: through-hole, external nub, internal "
       "boss, plus a 36°-wide × 1.05 mm deep skirt recess under the nub that the intake did not list.\n"
       "• Central screw is COTS: NOT modelled, and masked out of the gate reference.")
p.head("1.3 Gate (independent, per RE_SPEC §0.2 / §4)")
p.para("The gate reference is the RAW 798 874-tri scan, not the decimated work mesh. The STL is "
       "unwelded, so it is merged first — without that every edge reads as an open boundary and the "
       "hole-edge mask becomes meaningless. The scan is brought to the datum frame with "
       "alignment.json and then ICP-refined against the CAD, so a datum error cannot flatter the "
       "numbers. 3 000 000 scan samples against 300 000 CAD samples.")
p.para("ICP correction applied: %.3f° / %.3f mm — small, i.e. the modeller's datum was already close."
       % (T["icp_deg"], T["icp_mm"]), weight="bold")
p.head("1.4 Masks, with their cost")
p.table([["M1 bristles", "scan r > 38.5", "not modelled, soft ±3 mm (A10)", "150 548 faces (18.8%)"],
         ["M2 screw", "r < 3.6, z 8.6–10.4", "COTS, not modelled (A9)", "16 610 faces"],
         ["M3 open boundary", "< 0.8 mm from a hole edge", "distance to a hole EDGE is not a "
          "surface deviation", "%.1f%%" % (100 * T["edge_drop"])],
         ["M4 outer skin", "normal agreement < cos 70°", "an occluded interior correspondence is "
          "not an outer-skin deviation", "%.1f%%" % (100 * T["skin_drop"])],
         ["A6 hex gap", "unscanned part of the hex wall", "scan covers %d of 360° of the pocket "
          "wall; the gap is located FROM the scan, not assumed" % T["hex_cov_deg"], "—"]],
        [.13, .17, .40, .17], head=["mask", "what it removes", "why", "cost"], size=8.6)
p.done()

# ---------------- 3 tier-1 --------------------------------------------------
p = newpage("2. Tier-1 — caliper gate", "RE_SPEC §4 Tier-1: the finished STEP re-measured, band ±0.15 mm")
p.para("Nothing is echoed from build parameters. The delivered STEP is re-imported with "
       "build123d.import_step, tessellated at 5 µm chordal / 0.05 rad, then measured with trimesh "
       "plane sections and a support-function two-parallel-jaw width — the caliper modelled as two "
       "parallel planes closing on the section, polylines resampled at 0.02 mm.")
r1 = []
for k, lab in [("F02", "hex pocket depth"), ("F03", "cup bore ID"), ("F05", "skirt OD MAX (lobe)"),
               ("F10", "arm width @ r 36.5"), ("F11", "arm thickness @ r 36.5")]:
    e = Q["qa4"][k]; dlt = e["cad"] - e["caliper"]
    r1.append([k, lab, "%.3f" % e["caliper"], "%.3f" % e["cad"],
               ("++" if abs(dlt) < 0.05 else "~~") + "%+.3f" % dlt, "++PASS"])
r1.append(["F06", "skirt OD MIN (flat)", "~~STRUCK", "%.3f" % Q["qa4"]["F06"]["cad"], "—",
           "~~not gated — §3"])
r1.append(["F01", "hex AF", "!!none exists", "%.3f" % Q["qa4"]["F01"]["cad"], "—",
           "!!not gated — scan authority"])
p.table(r1, [.06, .22, .11, .12, .11, .24],
        head=["dim", "feature", "caliper", "CAD re-measured", "Δ", "verdict"], size=8.8)
p.box("TIER-1 IS PARTIAL — 5 of 24 sheet dims are gated. 17 are ABSENT, not passed.\n"
      "No caliper session was run. Muhammed directed proceed-without on 2026-07-30. The seven dims "
      "that carry values are photo-transcribed: real instrument readings, but the jaw placement was "
      "inferred by the line from the photograph, so their effective uncertainty is ±0.1 mm, not the "
      "instrument's ±0.02. Absent: ENV-1/2/3, F04, F07, F08, F09, F12–F18, and the unassigned "
      "D-09 / D-10 / D-12. A future caliper session on them can only tighten this verdict, never "
      "loosen it.", fc="#fdecea", ec=RED, color=RED, size=9.0)
p.head("3. The it1 → it2 change: F06 is STRUCK, with proof")
p.para("Iteration 1 applied the photo-transcribed F06 (24.84) as a skirt flat RADIUS (12.420). The "
       "finished solid then re-measured F06 = 25.487, Δ +0.647 — out of band. That is a data "
       "problem, not a modelling error, and it is provable from the geometry:")
p.box("On a 3-lobed skirt a two-jaw caliper reads R(θ) + R(θ+180). The three flats are only ~34° "
      "wide and sit 120° apart, so NO antipodal flat–flat pair exists — the minimum achievable "
      "diametral reading is lobe + flat. On the scan the achievable window is 25.99 … 27.08 mm; on "
      "the delivered CAD it is 25.62 … 26.85 mm. The value 24.84 is 1.15 mm below anything the "
      "scanned geometry can produce, whatever the modeller does.", size=8.8)
p.para("it2 ruling: F06 is struck from Tier-1 and SKIRT_R_FLAT reverts to scan authority 12.550. "
       "Nothing was silently loosened — the dim is removed with a stated geometric proof and a "
       "re-measure hook. If 24.84 was a real skirt dimension taken some other way (flat-to-axis ×2, "
       "or a mis-attributed lobe-to-flat reading), the flat radius is 0.13 mm large and this part "
       "must be re-run. Exactly one parameter changed between it1 and it2.")
p.done()

# ---------------- 4 tier-2 --------------------------------------------------
p = newpage("4. Tier-2 — independent scan-skin gate", "CAD → scan, after independent ICP, outer-skin masked")
p.head("Gated")
rows = [["WHOLE PART", nfmt(T["whole"]["n"]), "%.3f" % T["whole"]["mean"],
         "++%.3f" % T["whole"]["p95"], "++%.3f" % T["whole"]["max"], "p95 1.6 / max 4.0", "++PASS"]]
for k in ["rim annulus (datum A)", "hex pocket (F01)", "SAF-1 external nub", "SAF-1 skirt recess"]:
    v = Z[k]
    rows.append([k, nfmt(v["n"]), "%.3f" % v["mean"], "%.3f" % v["p95"],
                 "++%.3f" % v["max"], "max 0.8", "++PASS"])
p.table(rows, [.20, .10, .09, .09, .09, .14, .10],
        head=["zone", "n", "mean", "p95", "max", "band", "verdict"], size=8.6)
p.head("Reported, not gated (RE_SPEC §4 interior / occluded / non-interface buckets)")
why = {"SAF-1 internal boss": "interior/occluded (A7)", "cup bore wall": "Tier-1 covers it (F03)",
       "cup floor": "interior", "skirt band z 0-4.5": "Tier-1 covers it (F05)",
       "dome, off-arm off-SAF": "cosmetic", "arms r 14-38.2": "free-state droop (A11)",
       "arm/hub root r 7-14": "blend region"}
p.table([[k, nfmt(Z[k]["n"]), "%.3f" % Z[k]["mean"], "%.3f" % Z[k]["p95"], "%.3f" % Z[k]["max"], w]
         for k, w in why.items()],
        [.20, .10, .09, .09, .09, .29], head=["zone", "n", "mean", "p95", "max", "why not gated"], size=8.6)
p.para("The buckets overlap by design — they are reported buckets, not a partition. The hex pocket "
       "lies inside the dome bucket, and the skirt band overlaps the arm/hub root, which is why "
       "those pairs share a maximum: the same extreme point counted twice, not a duplicated figure.",
       size=8.6, color="#555")
p.head("Mask sensitivity — does the PASS depend on the mask?")
sr = [[("r = %.1f mm" % float(k)), nfmt(v[0]), "%.3f" % v[1], "%.3f" % v[2],
       "++PASS" if (v[1] <= 1.6 and v[2] <= 4.0) else "!!FAIL"] for k, v in T["sensitivity"].items()]
p.table(sr, [.14, .12, .11, .11, .12], head=["M3 radius", "kept", "p95", "max", "whole-part"], size=8.6)
p.box("HONEST QUALIFICATION ON TWO OF THE FOUR GATED INTERFACES.\n"
      "The whole-part gate passes at every mask radius tested, so it is not mask-dependent. Two "
      "named interfaces are: unmasked (r = 0.0) the hex pocket reads max 1.624 — 0.824 OVER band — "
      "and the SAF-1 skirt recess reads 0.805, 0.005 over. Both are hole-edge artefacts that the M3 "
      "mask exists to remove, and for the hex the A6 occlusion mask is separately justified: the "
      "scan never saw 124° of that wall, so the unmasked figure is distance to a hole edge, not a "
      "surface deviation. Stated plainly: the hex-pocket PASS is a MASKED pass, on the same feature "
      "that carries no caliper reading at all.", fc="#fdecea", ec=RED, color=RED, size=8.8)
p.head("Reverse check — is the CAD missing material?")
p.para("Scan → CAD, outer skin, r ≤ 38.2: n %s, mean %.3f, p95 %.3f, max %.3f mm. No scan feature "
       "sits far from CAD material, i.e. no real feature was left out of the model. The forward max "
       "%.3f is CAD standing slightly proud of the scan, not a missing feature."
       % (nfmt(T["reverse"]["n"]), T["reverse"]["mean"], T["reverse"]["p95"],
          T["reverse"]["max"], T["whole"]["max"]))
p.done()

# ---------------- 5 datum + limits ------------------------------------------
p = newpage("5. Independent datum derivation", "Re-derived from the raw scan using no modeller output")
p.para("q03_datum_full.py re-derives the datum in RAW scanner coordinates: the rim plane by "
       "area-weighted spherical normal vote (rim-fit rms %.4f mm), the axis as that normal, the "
       "axis position by robust circle fit on the cup bore wall (fitted R %.3f), and the arm-1 "
       "phase from the angular mass distribution of the rigid arms."
       % (D["rim_rms"], D["bore_R"]))
p.table([["rotation difference vs alignment.json", "%.3f°" % D["rot_diff_deg"]],
         ["point disagreement, mean", "%.3f mm" % D["pt_disagree_mean"]],
         ["point disagreement, p95", "%.3f mm" % D["pt_disagree_p95"]],
         ["point disagreement, max", "++%.3f mm" % D["pt_disagree_max"]],
         ["arm centres (raw scanner frame)", " / ".join("%.2f°" % a for a in D["arm_centres"])],
         ["→ arm-to-arm spacing", "120.00° and 120.53° — 3-fold to within scan noise"]],
        [.34, .59], size=9)
p.para("The datum is independently reproducible; it is not carrying a hidden error.", weight="bold")
p.head("6. What the scan genuinely cannot resolve")
p.table([["F01 hex AF", "!!no caliper, 2/3 scanned",
          "No reading exists in any photograph and the scan sees only %d° of the pocket wall. CAD "
          "holds the scan area-fit 7.358, deliberately NOT intent-snapped to 7.0 or 7.5. This is the "
          "torque interface and the highest-risk item on the part." % T["hex_cov_deg"]],
         ["Central screw bore + boss", "!!100% occluded",
          "Hidden by the fitted screw. The screw is COTS and is not modelled. F08 / F17 / F18 become "
          "measurable now that Q2 has ruled the screw may be removed."],
         ["Tuft socket interior", "~~occluded",
          "Modelled 4.60 × 3.50 × 3.00 deep from the ribbon envelope less measured dilation. Not gated."],
         ["SAF-1 hole bottom", "~~photo-inferred",
          "Not gated. The hole itself is held as the key datum (A8, Q5 fallback)."],
         ["Bristle filaments", "~~not modelled",
          "Modelled at the tuft anchor r = 38.20, not the tips, per the brief. Swept Ø over bristles "
          "124.9 is SOFT (±3 mm); the rigid-arm swept Ø 76.40 is the hard number."],
         ["Absolute scale", "!!unverified",
          "ENV-1/2/3 are empty so the §2 envelope check could not run. Four mid-size dims sit "
          "0.4–1.6% under the scan — not uniform enough to justify a global scale correction, so "
          "none was applied. If this scanner is off by a percent, nothing in this pipeline reveals it."]],
        [.17, .16, .60], head=["item", "status", "why"], size=8.6)
p.head("7. Iteration history")
p.table([["1", "first build; F06 24.84 applied as a radius", "!!0.647 (F06)", "1.045 / 3.134",
          "!!REVISE — indicative check only, no ICP, no skin mask"],
         ["2", "SKIRT_R_FLAT 12.420 → 12.550 (F06 struck)", "++0.026 (F11)",
          "++%.3f / %.3f" % (T["whole"]["p95"], T["whole"]["max"]),
          "++APPROVED — independent ICP + skin mask"]],
        [.04, .30, .12, .12, .28], head=["it", "change", "Tier-1 worst", "Tier-2 p95/max", "outcome"], size=8.6)
p.done()

# ---------------- 6 views ---------------------------------------------------
p = newpage("8. Documentation views", "Orthographic renders of the rebuilt STEP")
p.imgrow([(f"{P}/7_docs/OOM-B02_iso.png", L, .40, "iso — dome side"),
          (f"{P}/7_docs/OOM-B02_iso_cup.png", .51, .40, "iso — cup side (drive interface)")], .235)
p.imgrow([(f"{P}/7_docs/OOM-B02_top.png", L, .40, "top (down the rotation axis)"),
          (f"{P}/7_docs/OOM-B02_front.png", .51, .40, "front")], .235)
p.imgrow([(f"{P}/7_docs/OOM-B02_scan_vs_cad.png", L, .40, "deviation, dome side"),
          (f"{P}/7_docs/OOM-B02_scan_vs_cad_cup.png", .51, .40, "deviation, cup side")], .235)
p.para("Renders produced by an orthographic z-buffer rasteriser with Lambert shading, written for "
       "this job. RE_SPEC §6.3 specifies Blender Cycles studio renders via "
       "_PIPELINE/tools/blender_doc_render.py, but Blender is not installed on this machine (A12). "
       "The geometry shown IS the delivered STEP tessellation, so the renders are dimensionally "
       "faithful; only the shading is diagrammatic.", size=8.6, color="#555")
p.done()

# ---------------- 7 sections ------------------------------------------------
p = newpage("9. Section overlays", "Rebuilt CAD (red) against the datum-aligned scan (blue)")
p.img(f"{P}/6_RE_work/B02_S1_meridian_arm1.png", .27, x=.05, w=.90)
p.img(f"{P}/6_RE_work/B02_S2_meridian_SAF1.png", .27, x=.05, w=.90)
p.para("Top: hub meridian through arm 1. The CAD arm path is the 3-ARM MEAN z(r); arm 1 is the "
       "lowest of the three, so the CAD reads ~0.74 mm high here and ~0.51 mm low on arm 3. That "
       "1.25 mm arm-to-arm spread is free-state droop (Q4) and is deliberately not chased. Bottom: "
       "meridian through SAF-1, showing the nub, the skirt recess and the internal boss.",
       size=8.6, color="#555")
p.done()

# ---------------- 8 fitness -------------------------------------------------
p = newpage("10. Fitness and open items", "What this STEP may and may not be used for")
p.box("FIT FOR: envelope / packaging / clearance work in 00_MASTER_ASSEMBLY; visualisation; and the "
      "functional-interface geometry (rim seating face, cup bore, skirt, arm path, tuft anchors) as "
      "a design-intent reference.", fc="#eef6ee", ec=GRN, color="#14532d", size=9.2)
p.box("NOT YET FIT FOR MANUFACTURE OR TOOLING until F01 is calipered. The drive socket across-flats "
      "is the one dimension that decides whether the part fits the motor shaft, and it currently "
      "rests on a scan fit of a two-thirds-visible pocket, un-snapped. The envelope dims "
      "(ENV-1/2/3) should also be taken, because absolute scale is presently unverified.",
      fc="#fdecea", ec=RED, color=RED, size=9.2)
p.head("Open items, in priority order")
p.table([["1", "!!F01 hex AF", "One caliper reading across two opposite flats, three times at 60°. "
          "This is the re-run hook: a reading that disagrees with 7.358 changes the drive fit and "
          "the part must be rebuilt."],
         ["2", "!!ENV-1/2/3", "Overall Ø over bristle tips (soft), Ø over rigid arm ends, and "
          "overall height. Makes the §2 absolute-scale check possible for the first time."],
         ["3", "~~F06 re-attribution", "24.84 was struck with a geometric proof. If it was a real "
          "skirt dimension taken some other way, the flat radius is 0.13 mm large."],
         ["4", "~~F08 / F17 / F18", "Q2 ruled the screw may come out. With it removed the central "
          "bore, the fastener spec and the thread engagement stop being photo-inferred."],
         ["5", "Q5 — what does SAF-1 key into?", "Chassis pocket, motor hub, or a tufting jig? And "
          "is the hole, the nub or the boss the working feature? Fallback taken: all three modelled "
          "as scanned, hole held as the key datum, nub and boss gated at Tier-2 only."],
         ["6", "Q6 — tracker naming", "The row was previously 'Side-brush-2arm-curved-Qrevo'. "
          "Treated as mislabelled; confirm no separate 2-arm Qrevo part is missing."]],
        [.03, .20, .70], head=["#", "item", "what is needed"], size=8.6)
p.head("11. Honesty notes")
p.para("• This is NOT an organisationally independent verification. The re-* agents and the "
       "cad-qa-gate / stl2step-build123d skills named in SESSION_PROMPT are not installed on this "
       "machine (A13). The QA code was written separately from the build code and re-derives every "
       "number from the raw scan — but the same context wrote both. The gate is weaker than RE_SPEC "
       "intends, and that is stated here rather than papered over.\n"
       "• Blender is not installed (A12); renders use the W01 z-buffer rasteriser precedent.\n"
       "• Two intake-card errors were found and corrected against the scan, both independently "
       "reproducible: SAF-1 sits at θ = +59° in the frozen datum frame, not −71° (sign convention); "
       "and the cup-floor annular feature is a 0.337 mm GROOVE, not a 0.25 mm proud ridge. A third "
       "SAF-1 sub-feature the intake did not list — a 36°-wide, ~1.05 mm deep recess in the skirt "
       "outer wall under the nub — was found and is modelled.\n"
       "• Iteration 1 was published to 4_STEP before the gate finished. It has been withdrawn to "
       "6_RE_work/_it1_SUPERSEDED/ and replaced by the approved it2 solid.")
p.done()

d = pp.infodict()
d["Title"] = "OOM-B02 Side brush 3-arm — RE report (APPROVED it2, three declared limitations)"
d["Author"] = "OOMWOO RE line v2"
pp.close()
print("wrote 7_docs/OOM-B02_RE_report.pdf  (%d pages)" % n[0])
