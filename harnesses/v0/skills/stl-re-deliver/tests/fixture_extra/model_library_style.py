"""Fixture model, LIBRARY-USE variant (review D5): calls `export_frames()` the way
stl-re-rebuild-build123d/scripts/export_frames.py documents under "LIBRARY USE" --

    from export_frames import export_frames
    export_frames(body, Path("intake/alignment.json"), Path("build"), "part", ...)

with paths relative to the RUN ROOT, not to build/. This only works when the caller's cwd is
the run root and stl-re-rebuild-build123d/scripts is on sys.path -- exactly what
scripts/repro_check.py's default `--cwd run` now sets up (see repro_check.py `rebuild_once`).
Produces the same geometry as model.py so a fresh rebuild with this script is still
reproducible against the delivered STEP.
"""
import json
from pathlib import Path

from build123d import Box, Cylinder
from export_frames import export_frames  # resolves via PYTHONPATH (repro_check.py --cwd run sets it)

P = {k: v["value"] for k, v in json.loads(Path("measure/params.json").read_text())["params"].items()}
part = Box(P["plate_x"], P["plate_y"], P["plate_t"]) - Cylinder(P["bore_d"] / 2, P["plate_t"])
export_frames(part.clean(), Path("intake/alignment.json"), Path("build"), "fixture_part")
print("volume", round(part.volume, 6))
