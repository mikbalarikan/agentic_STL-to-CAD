#!/usr/bin/env python3
"""make_params.py - turn measure/figures/measurements.json into measure/params.json.

Every value comes from a measurements.json entry (never retyped). Rules follow
stl-re-measure-intent references/intent-rules.md: scan values are kept as measured
(keep-measured) or averaged over their own stations/sides (mean-of-n); nothing is snapped
(no calipers, so std-size-snap is not allowed); unscanned geometry is `assumed` with a note.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

RUN = Path(__file__).resolve().parents[1]
MJ = RUN / "measure" / "figures" / "measurements.json"
AL = RUN / "intake" / "alignment.json"
M = json.loads(MJ.read_text())["results"]
ALJ = json.loads(AL.read_text())
NOISE = float(ALJ["scan_noise_mm"]["value"])
EV = "measure/figures/measurements.json#"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


P: dict[str, dict] = {}


def v(key):
    return M[key]["value"]


def keep(name, key, crit=False, note=None, unit="mm", trig=None, idx=None, unc=None):
    e = M[key]
    val = e["value"] if idx is None else e["value"][idx]
    row = {"value": round(float(val), 3), "unit": unit, "measured": round(float(val), 3),
           "rule": "keep-measured", "source": "scan", "estimator": e["estimator"],
           "uncertainty_mm": round(float(unc if unc is not None else max(e.get("rms", NOISE), NOISE)), 3),
           "evidence": EV + key, "critical": crit}
    if note:
        row["note"] = note
    if trig:
        row["rerun_trigger"] = trig
    P[name] = row


def mean_n(name, reads, keys, crit=False, note=None, unit="mm", trig=None):
    reads = [round(float(r), 3) for r in reads]
    val = round(float(np.mean(reads)), 3)
    row = {"value": val, "unit": unit, "measured": reads, "rule": "mean-of-n", "source": "scan",
           "estimator": "mean of: " + "; ".join(keys),
           "uncertainty_mm": round(max(float(np.std(reads)), NOISE), 3),
           "evidence": ", ".join(EV + k.split(" ")[0] for k in keys), "critical": crit}
    if note:
        row["note"] = note
    if trig:
        row["rerun_trigger"] = trig
    P[name] = row


def assumed(name, value, note, unit="mm"):
    P[name] = {"value": value, "unit": unit, "measured": None, "rule": "assumed", "source": "assumed",
               "estimator": "not measurable on the scan", "uncertainty_mm": 0.3, "evidence": note.split(";")[0],
               "critical": False, "note": note}


TRIG = "any caliper reading of this dimension (scan-only run) should trigger a re-run"
# ---------------------------------------------------------------- body (clear cover)
bp = M["body_bottom_plane"]
n = np.array(bp["normal"])
P["bottom_z_at_x0"] = {"value": round(bp["coord_at_point"], 3), "unit": "mm", "measured": round(bp["coord_at_point"], 3),
                       "rule": "keep-measured", "source": "scan", "estimator": bp["estimator"] + "; z of the fitted plane at x=y=0",
                       "uncertainty_mm": round(max(bp["rms"], NOISE), 3), "evidence": EV + "body_bottom_plane", "critical": False,
                       "note": "one plane carries the whole bottom (cover, cap and nose cup); cross-checks "
                               f"z(x=-20)={v('body_bottom_z_at_x-20'):.3f}, z(x=-3)={v('body_bottom_z_at_x-3'):.3f}, "
                               f"nose {v('nose_bottom_z'):.3f}, cap {v('cap_bottom_z'):.3f}"}
slope = float(np.degrees(np.arctan2(-n[0], -n[2])))  # dz/dx = -(nx/nz); bottom falls toward +x
P["bottom_slope_deg"] = {"value": round(slope, 3), "unit": "deg", "measured": round(slope, 3), "rule": "keep-measured",
                         "source": "scan", "estimator": bp["estimator"] + "; atan(-nx/-nz) of the fitted normal",
                         "uncertainty_mm": round(max(bp["rms"], NOISE), 3), "evidence": EV + "body_bottom_plane", "critical": False,
                         "frame": "positive = bottom face drops (more negative z) toward +x",
                         "note": f"normal y component {n[1]:.4f} (roll {np.degrees(np.arcsin(n[1])):.2f} deg) not modelled"}
mean_n("body_y_pos", [v("body_y_pos"), v("body_y_pos_behind_tab"), v("body_y_pos_below_tab")],
       ["body_y_pos (x -20.8..-15.5)", "body_y_pos_behind_tab", "body_y_pos_below_tab"],
       note="three wall stations; spread is wall draft/bow of the moulding")
mean_n("body_y_neg", [v("body_y_neg"), v("body_y_neg_behind_tab"), v("body_y_neg_below_tab")],
       ["body_y_neg (x -20.8..-15.5)", "body_y_neg_behind_tab", "body_y_neg_below_tab"],
       note="three wall stations; spread is wall draft/bow of the moulding")
mean_n("body_front_x", [v("body_front_x"), v("body_front_x_neg")], ["body_front_x (+y strip)", "body_front_x_neg (-y strip)"],
       note="front face of the body box beside the nose cup (|y| 15.3..16.2)")
tr = [r["R"] for r in M["cover_top_edge_R"]["per_station"] + M["cover_top_edge_R_neg"]["per_station"]]
mean_n("cover_top_R", tr, ["cover_top_edge_R (+y, 5 stations)", "cover_top_edge_R_neg (-y, 5 stations)"],
       note="-y stations at x -12.5..-5 read low where a shallow dent runs along the edge (declared simplification)")
br = [r["R"] for r in M["cover_bot_edge_R"]["per_station"] + M["cover_bot_edge_R_neg"]["per_station"]]
mean_n("cover_bot_R", br, ["cover_bot_edge_R (+y, 6 stations)", "cover_bot_edge_R_neg (-y, 6 stations)"])
# ---------------------------------------------------------------- seam groove between clear cover and black cap
sg = M["seam_groove"]
mean_n("seam_x", [r["cu"] for r in sg["per_station"]], ["seam_groove centre x (4 stations y=+-5,+-10)"],
       note="x of the cover/cap parting line on the top face")
mean_n("seam_groove_R", [r["R"] for r in sg["per_station"]], ["seam_groove R (4 stations)"])
mean_n("seam_groove_zc", [r["cv"] for r in sg["per_station"]], ["seam_groove centre z (4 stations)"],
       note=f"groove floor = zc - R; independent p1 floor z {v('seam_groove_bottom_z'):.3f}")
# ---------------------------------------------------------------- rear cap (seam..x=0) and connector shelf (x=0..end)
mean_n("cap_y_pos", [v("cap_y_pos"), v("cap_y_pos_low")], ["cap_y_pos (z -1.9..-0.8)", "cap_y_pos_low (z -8.3..-7.0)"])
mean_n("cap_y_neg", [v("cap_y_neg"), v("cap_y_neg_low")], ["cap_y_neg (z -1.9..-0.8)", "cap_y_neg_low (z -8.3..-7.0)"])
mean_n("cap_top_R", [v("cap_top_edge_R"), v("cap_top_edge_R_neg")], ["cap_top_edge_R", "cap_top_edge_R_neg"])
keep("rear_wall_x", "rear_wall_x", note="datum origin plane (x=0 by construction); modelled at the measured value")
keep("shelf_end_x", "shelf_end_x", trig=TRIG, crit=True, note="overall length reference (nose tip to shelf end)")
keep("shelf_y_pos", "shelf_y_pos")
keep("shelf_y_neg", "shelf_y_neg")
keep("shelf_top_z", "shelf_top_z", note="black cap/shelf top sits slightly below the clear-cover top plateau (z=0)")
keep("shelf_bottom_z", "shelf_bottom_z")
mean_n("shelf_top_R", [v("shelf_top_edge_R"), v("shelf_top_edge_R_neg")], ["shelf_top_edge_R", "shelf_top_edge_R_neg"])
keep("pocket_ceiling_z", "pocket_ceiling_z", crit=True, trig=TRIG, note="connector pockets: mating faces for the harness plug")
keep("pocket_x_front", "pocket_x_front", crit=True, trig=TRIG)
keep("pocket_x_back", "pocket_x_back", crit=True, trig=TRIG)
keep("pocket_lip_z", "pocket_lip_front_z", note="bottom of the lip between the rear wall (x=0) and the pocket front wall")
for i, nm in enumerate(["pocketA_y0", "pocketA_y1", "pocketB_y0", "pocketB_y1", "pocketC_y0", "pocketC_y1"]):
    keep(nm, f"pocket_wall_{i}", crit=True, trig=TRIG)
# ---------------------------------------------------------------- side rails and tabs (mounting interface)
for tag in ("pos", "neg"):
    keep(f"rail_y_{tag}", f"rail_y_{tag}", crit=True, trig=TRIG, note="guide rail outer face (mounting interface)")
    keep(f"rail_x_start_{tag}", f"rail_x_start_{tag}")
    keep(f"tab_y_{tag}", f"tab_y_{tag}", crit=True, trig=TRIG, note="tab outer face (mounting interface)")
    keep(f"tab_x_start_{tag}", f"tab_x_start_{tag}", crit=True, trig=TRIG)
    keep(f"tab_x_end_{tag}", f"tab_x_end_{tag}")
mean_n("rail_top_z", [v("rail_top_z_pos"), v("rail_top_z_neg")], ["rail_top_z_pos", "rail_top_z_neg"])
mean_n("rail_rear_top_z", [v("rail_rear_top_z_pos"), v("rail_rear_top_z_neg")], ["rail_rear_top_z_pos", "rail_rear_top_z_neg"])
mean_n("rail_rear_x_start", [v("rail_rear_x_start_pos"), v("rail_rear_x_start_neg")], ["rail_rear_x_start_pos", "rail_rear_x_start_neg"])
mean_n("tab_top_z", [v("tab_top_z_pos"), v("tab_top_z_neg")], ["tab_top_z_pos", "tab_top_z_neg"], crit=True, trig=TRIG,
       note="tab thickness = tab_top_z - tab_bot_z; slides in the bumper slot")
mean_n("tab_bot_z", [v("tab_bot_z_pos"), v("tab_bot_z_neg")], ["tab_bot_z_pos", "tab_bot_z_neg"], crit=True, trig=TRIG)
# ---------------------------------------------------------------- wire slot (rear bottom centre)
keep("slot_y_pos", "slot_y_pos")
keep("slot_y_neg", "slot_y_neg")
keep("slot_x_end", "slot_x_end", note="slot end at the bottom face; the end wall is only partly scanned")
keep("slot_top_z", "slot_top_z", note="highest scanned slot-wall point; the slot roof is NOT in the scan (open boundary loop), "
                                      "the real slot may be taller (wire exit, photo_5)", unc=0.3)
# ---------------------------------------------------------------- bottom ramps (two wedges under the cover)
mean_n("ramp_x_start", [v("ramp_x_start_pos"), v("ramp_x_start_neg")], ["ramp_x_start_pos", "ramp_x_start_neg"],
       note="where the wedge leaves the bottom face (p1 x of vertices below z -9.28)")
mean_n("ramp_x_end", [v("ramp_x_end_pos"), v("ramp_x_end_neg")], ["ramp_x_end_pos", "ramp_x_end_neg"])
mean_n("ramp_peak_z", [v("ramp_peak_z_pos"), v("ramp_peak_z_neg")], ["ramp_peak_z_pos", "ramp_peak_z_neg"])
mean_n("ramp_y_in", [M["ramp_y_span_pos_x-16.0"]["value"][0], M["ramp_y_span_neg_x-16.0"]["value"][0]],
       ["ramp_y_span_pos_x-16.0 p1", "ramp_y_span_neg_x-16.0 p1"])
mean_n("ramp_y_out", [M["ramp_y_span_pos_x-16.0"]["value"][1], M["ramp_y_span_neg_x-16.0"]["value"][1]],
       ["ramp_y_span_pos_x-16.0 p99", "ramp_y_span_neg_x-16.0 p99"])
# ---------------------------------------------------------------- nose (lens cup with two recessed windows)
ns = M["nose_slope_plane"]
P["nose_plane_normal"] = {"value": [round(x, 5) for x in ns["normal"]], "unit": "mm", "measured": [round(x, 5) for x in ns["normal"]],
                          "rule": "keep-measured", "source": "scan", "estimator": ns["estimator"] + " (unit normal)",
                          "uncertainty_mm": round(max(ns["rms"], NOISE), 3), "evidence": EV + "nose_slope_plane", "critical": True,
                          "rerun_trigger": TRIG,
                          "note": f"frame + centre rib face of the lens; inclination {ns['angle_to_axes_deg']['z']:.2f} deg "
                                  "from the top plane (unit 'mm' = dimensionless direction cosines)"}
P["nose_plane_point"] = {"value": [round(x, 4) for x in ns["centroid"]], "unit": "mm", "measured": [round(x, 4) for x in ns["centroid"]],
                         "rule": "keep-measured", "source": "scan", "estimator": ns["estimator"] + " (centroid on the plane)",
                         "uncertainty_mm": round(max(ns["rms"], NOISE), 3), "evidence": EV + "nose_slope_plane", "critical": True,
                         "rerun_trigger": TRIG, "note": f"plane crosses y=z=0 at x={ns['coord_at_point']:.3f}"}
mean_n("nose_half_w", [v("nose_half_width_top_pos"), -v("nose_half_width_top_neg")], ["nose_half_width_top_pos", "nose_half_width_top_neg"])
cr = [r["R"] for r in M["nose_cup_R_pos"]["per_station"] + M["nose_cup_R_neg"]["per_station"]]
mean_n("nose_cup_R", cr, ["nose_cup_R_pos (8 stations)", "nose_cup_R_neg (8 stations)"],
       note="bottom-to-side round of the lens cup (outer envelope only; see-through hits excluded by the envelope binning)")
keep("nose_tip_R", "nose_tip_R", note="round between the lens front plane and the bottom")
keep("window_depth", "window_depth", note="both windows recessed below the frame/rib plane; clear plastic, partly scanned")
mean_n("window_y_in", [M["window_y_pos"]["value"][0], M["window_y_neg"]["value"][0]], ["window_y_pos p1", "window_y_neg p1"],
       note="window inner edge = centre-rib half width")
mean_n("window_y_out", [M["window_y_pos"]["value"][1], M["window_y_neg"]["value"][1]], ["window_y_pos p99", "window_y_neg p99"])
keep("window_s_lo", "window_s", idx=0, note="s measured in the nose plane from nose_plane_point, +s up the slope")
keep("window_s_hi", "window_s", idx=1)
assumed("window_corner_R", round(P["nose_cup_R"]["value"] - (P["nose_half_w"]["value"] - P["window_y_out"]["value"]), 3),
        "nose_cup_R - (nose_half_w - window_y_out); window outline assumed concentric with the cup round (constant side frame); "
        "confirm on a photo of the lens face")
assumed("nose_top_R", P["cover_top_R"]["value"],
        "same as cover_top_R; the cup's top edges run only 1.2 mm (x -22.4..-21.2) between the lens plane and the body, "
        "too short for a separate fit")
# ---------------------------------------------------------------- declared, not modelled
assumed("tab_blob_not_modelled", 0.0,
        "measure/figures/measurements.json#nub_top_z_pos; irregular 1.2 mm blob on the +Y tab at x -8.2..-7.1 (top z "
        f"{v('nub_top_z_pos'):.2f}); no flat top, not mirrored on -Y; treated as debris/scan artefact, not modelled "
        "(CHK-CLUSTER finding, open question to the owner)")

doc = {"schema": "stl-re/params.json@1", "tool": "make_params.py", "tool_version": "run-local@1",
       "inputs": {"measure/figures/measurements.json": sha(MJ), "intake/alignment.json": sha(AL),
                  "input/photos/photo_1.png": sha(RUN / "input/photos/photo_1.png"),
                  "input/photos/photo_5.png": sha(RUN / "input/photos/photo_5.png")},
       "seed": 0, "part": "cliff_bumper_sensor",
       "frame": ("datum frame of intake/alignment.json: z=0 on the top face (clear-cover plateau), material below (-z); "
                 "y=0 mid-plane of the two side walls; x=0 rear wall of the lower body, +x toward the connector shelf, "
                 "-x toward the lens nose; theta CCW about +Z from +X (no angles used except bottom_slope_deg)"),
       "scan_noise_mm": NOISE,
       "params": P,
       "struck": [],
       "simplifications": [
           {"name": "top face", "modelled_as": "plane z=0 (cover) and z=shelf_top_z (cap + shelf)",
            "deviation_cost": "cover plateau crown and cap crown: face residual -0.08..+0.05 mm (intake top-face map)"},
           {"name": "side walls", "modelled_as": "one plane per side at the mean of three stations",
            "deviation_cost": f"station spread {P['body_y_pos']['uncertainty_mm']:.3f} (+y) / {P['body_y_neg']['uncertainty_mm']:.3f} (-y) mm std"},
           {"name": "shallow dent along the -Y top edge (x -13..-5)", "modelled_as": "not modelled (plain round cover_top_R)",
            "deviation_cost": "up to ~0.5 mm locally (x=-10 section, y -13.9)"},
           {"name": "small vertical-edge and pocket-corner rounds", "modelled_as": "sharp",
            "deviation_cost": "<= R(1-1/sqrt2) ~ 0.15-0.2 mm for the observed R ~0.5-0.7 corners"},
           {"name": "bottom parting lip at the cover/cap seam", "modelled_as": "not modelled",
            "deviation_cost": "~0.3 mm bump over ~0.4 mm (y=15.5 section, x -1.2)"},
           {"name": "interior seen through the transparent lens windows", "modelled_as": "not modelled (envelope only)",
            "deviation_cost": "scan hits up to ~3.5 mm behind the window face (nose histogram)"},
           {"name": "slot roof", "modelled_as": "slot to the highest scanned wall point slot_top_z",
            "deviation_cost": "unknown (roof not scanned); CAD->scan only"},
       ],
       "checks": {
           "CHK-COUNT": {"ran": True, "result": "pass",
                         "note": "no rotational pattern on this part; linear instances (3 pockets, 2 windows, 2 tabs, 2 rails, "
                                 "2 ramps) each measured individually, no count parameter"},
           "CHK-ACHIEVABLE": {"ran": True, "result": "pass", "note": "no caliper or photo readings (scan-only run); nothing to strike"},
           "CHK-CLUSTER": {"ran": True, "result": "finding",
                           "note": "(1) +Y tab blob x -8.2..-7.1, 1 component, ~1.2 mm tall, no flat top, absent on -Y: not "
                                   "modelled, open question; (2) scan material behind the lens windows: explained as the "
                                   "interior seen through clear plastic (photo_2, photo_4 show transparent lens)"},
           "CHK-FRAME": {"ran": True, "result": "pass", "note": "all values measured on intake/aligned_work.stl in the frozen datum frame"},
       },
       "open_questions": [
           "Is the blob on the +Y tab (x -8.2..-7.1) a real latch/detent or debris? Not modelled.",
           "Slot roof height (wire exit) is not in the scan; modelled to the highest scanned wall point.",
           "Calipers on overall length, width over tabs, tab thickness and pocket sizes would verify scale (CHK-SCALE FLAG).",
       ]}
out = RUN / "measure" / "params.json"
out.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
print(f"{len(P)} params -> {out}")
