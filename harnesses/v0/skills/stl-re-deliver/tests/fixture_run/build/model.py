"""Fixture model: plate with a through bore, driven by ../measure/params.json.

Writes fixture_part_datum.step (datum frame) and fixture_part.step (scan frame = inverse of
intake/alignment.json#matrix_4x4) next to this file. Deterministic.
"""
import json
from pathlib import Path

import numpy as np
from build123d import Box, Cylinder, Location, export_step
from OCP.gp import gp_Trsf

HERE = Path(__file__).resolve().parent
P = {k: v["value"] for k, v in json.loads((HERE / "../measure/params.json").read_text())["params"].items()}
T = np.array(json.loads((HERE / "../intake/alignment.json").read_text())["matrix_4x4"], dtype=float)

part = Box(P["plate_x"], P["plate_y"], P["plate_t"]) - Cylinder(P["bore_d"] / 2, P["plate_t"])
export_step(part, str(HERE / "fixture_part_datum.step"))

inv = np.linalg.inv(T)
u, _, vt = np.linalg.svd(inv[:3, :3])  # re-orthonormalise before OCP (OD-H12 export_final.py:17-22)
inv[:3, :3] = u @ vt
trsf = gp_Trsf()
trsf.SetValues(*inv[0], *inv[1], *inv[2])
scan_frame = part.moved(Location(trsf))
export_step(scan_frame, str(HERE / "fixture_part.step"))
print("volume", round(part.volume, 6))
