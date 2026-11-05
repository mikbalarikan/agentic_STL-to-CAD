"""Fixture model, iteration 1 (superseded). Datum frame only."""
import json
from pathlib import Path

from build123d import Box, Cylinder, export_step

HERE = Path(__file__).resolve().parent
P = {k: v["value"] for k, v in json.loads((HERE / "../measure/params.json").read_text())["params"].items()}
part = Box(P["plate_x"], P["plate_y"], P["plate_t"]) - Cylinder(P["bore_d"] / 2, P["plate_t"])
export_step(part, str(HERE / "fixture_part_datum.step"))
