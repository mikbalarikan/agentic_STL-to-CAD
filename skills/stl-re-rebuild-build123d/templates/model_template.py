#!/usr/bin/env python3
"""model_template.py - minimal params-driven build123d skeleton for build/model.py.

Copy to <run>/build/model.py and replace the FEATURES section with the ordered
features of build/MODELING_PLAN.md. Every pattern below is lifted from a golden build:

  P["name"]            parameters only from measure/params.json (run-contract.md section 4);
                       no geometry literal except documented clearances  (SYNTHESIS D6)
  revolve_rz()         revolve a closed (r,z) profile about Z             (D2; DRM build_snap.py:23-28,
                                                                           OD build_pump.py:80-128,
                                                                           P03 rebuild_OOM-P03.py:56-79)
  one instance +       one tool solid, placed at measured (possibly unequal)
  placements           angles                                              (D4, C10; DRM build_snap.py:62-69)
  cut tools            separate solids, fused, subtracted once             (D5; P03 rebuild_OOM-P03.py:138-146)
  hex AF               RegularPolygon(AF/sqrt(3), 6, major_radius=True)    (P03 rebuild_OOM-P03.py:82-86)
  FilletLog            try/log/fallback, target vs used radius             (D7, CHK-FILLET)
  export_frames()      datum STEP + scan STEP + CAD STL + export_check     (D12, D14)

Run:  python model.py --params ../measure/params.json --alignment ../intake/alignment.json \
                      --out . --part <part>
Tiny self-contained example:  python model_template.py --example
Exit codes: 0 ok, 2 export aborted (invalid solid etc.).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

from build123d import (Align, Axis, Cylinder, Face, GeomType, Part, Pos, RegularPolygon, Rot,
                       Vector, Wire, extrude, revolve)

HERE = Path(__file__).resolve().parent


def find_scripts(explicit: Path | None) -> Path:
    """Locate stl-re-rebuild-build123d/scripts (flag, env, sibling folder, ~/.claude/skills)."""
    cands = [explicit, Path(os.environ["STL_RE_REBUILD_SCRIPTS"]) if "STL_RE_REBUILD_SCRIPTS" in os.environ else None,
             HERE.parent / "scripts", Path.home() / ".claude/skills/stl-re-rebuild-build123d/scripts"]
    for c in cands:
        if c is not None and (c / "export_frames.py").is_file():
            return c
    raise SystemExit("cannot find stl-re-rebuild-build123d/scripts; pass --scripts")


class Params:
    """Read-only view of measure/params.json. Records which params the model used, so the
    build log can list unused params (a param nobody uses is a plan/measure mismatch)."""

    def __init__(self, path: Path) -> None:
        d = json.loads(path.read_text(encoding="utf-8"))
        self.raw: dict[str, dict[str, Any]] = d["params"]
        for k, v in self.raw.items():
            if "value" not in v or "source" not in v:
                raise SystemExit(f"param {k}: needs value and source (run-contract.md section 4)")
        self.used: set[str] = set()

    def __getitem__(self, key: str) -> Any:
        self.used.add(key)
        return self.raw[key]["value"]

    def group(self, prefix: str) -> list[Any]:
        """Values of prefix_1, prefix_2, ... in numeric order (e.g. measured hole angles)."""
        keys = sorted((k for k in self.raw if k.startswith(prefix + "_") and k[len(prefix) + 1:].isdigit()),
                      key=lambda k: int(k[len(prefix) + 1:]))
        return [self[k] for k in keys]

    def unused(self) -> list[str]:
        return sorted(set(self.raw) - self.used)


def revolve_rz(pts: list[tuple[float, float]]) -> Part:
    """Revolve a closed (r, z) polygon (drawn in the XZ half-plane, r >= 0) 360 deg about Z."""
    face = Face(Wire.make_polygon([Vector(r, 0, z) for r, z in pts], close=True))
    return revolve(face, Axis.Z, 360)


def build(P: Params, flog: Any) -> Part:
    # ---------------------------------------------------------------- FEATURES
    # F01 revolve: flange + hub, bore included in the profile (one (r,z) sketch).
    rb = P["bore_dia"] / 2
    body = revolve_rz([
        (rb, 0.0), (P["flange_od"] / 2, 0.0), (P["flange_od"] / 2, P["flange_t"]),
        (P["hub_od"] / 2, P["flange_t"]), (P["hub_od"] / 2, P["hub_top_z"]), (rb, P["hub_top_z"]),
    ])
    flog.log(f"F01 revolve (r,z) profile: faces={len(body.faces())}")

    # F02 hex socket from the top: across-flats -> circumradius via major_radius.
    hex_depth = P["hex_depth"]
    hex_tool = Pos(0, 0, P["hub_top_z"] - hex_depth) * extrude(
        RegularPolygon(P["hex_af"] / math.sqrt(3), 6, major_radius=True, rotation=P["hex_phase_deg"]),
        amount=hex_depth + 1.0)  # +1.0: tool overshoots the top face (documented clearance)
    # F03 bolt holes: ONE tool, placed at the measured (unequal) angles on the PCD.
    hole = Pos(P["hole_pcd"] / 2, 0, -1.0) * Cylinder(P["hole_dia"] / 2, P["flange_t"] + 2.0,
                                                      align=(Align.CENTER, Align.CENTER, Align.MIN))
    tools = hex_tool
    for th in P.group("hole_theta"):
        tools = tools + Rot(0, 0, th) * hole
    body = body - tools
    flog.log(f"F02/F03 cut tools subtracted once: {len(P.group('hole_theta'))} holes + hex")

    # F04 local chamfer on the bore bottom edge (edge survives later ops; could be last).
    body = flog.apply(body, "F04 bore bottom chamfer",
                      lambda s: [e for e in s.edges().filter_by(GeomType.CIRCLE)
                                 if abs(e.center().Z) < 1e-3 and abs(e.radius - rb) < 1e-3],
                      radii=[P["bore_chamfer"]], op="chamfer", param="bore_chamfer")
    # F05 hub/flange fillet LAST, with a declared fallback list (target first).
    r_f = P["hub_fillet"]
    body = flog.apply(body, "F05 hub-flange fillet",
                      lambda s: [e for e in s.edges().filter_by(GeomType.CIRCLE)
                                 if abs(e.center().Z - P["flange_t"]) < 1e-3
                                 and abs(e.radius - P["hub_od"] / 2) < 1e-3],
                      radii=[r_f, r_f * 0.5], param="hub_fillet",
                      why_fallback="plan: half radius allowed if the full one fails; declare it")
    return body.clean()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="params-driven build123d model (stl-re-rebuild-build123d template)")
    ap.add_argument("--params", type=Path)
    ap.add_argument("--alignment", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--part", default="part")
    ap.add_argument("--scripts", type=Path, help="stl-re-rebuild-build123d/scripts folder")
    ap.add_argument("--example", action="store_true", help="run on templates/example_*.json into /tmp")
    a = ap.parse_args(argv)
    if a.example:
        a.params = a.params or HERE / "example_params.json"
        a.alignment = a.alignment or HERE / "example_alignment.json"
        a.out = a.out or Path("/tmp/stl_re_template_example")
        a.part = "example_bushing"
    if not (a.params and a.alignment and a.out):
        ap.error("--params, --alignment and --out are required (or --example)")
    sys.path.insert(0, str(find_scripts(a.scripts)))
    from export_frames import ExportAbort, export_frames
    from fillet_log import FilletLog

    import build123d

    P = Params(a.params)
    flog = FilletLog()
    flog.log(f"build123d {build123d.__version__}  params={a.params}")  # version drift is real
    body = build(P, flog)
    if P.unused():
        flog.log(f"UNUSED params (plan/measure mismatch?): {P.unused()}")
    a.out.mkdir(parents=True, exist_ok=True)
    flog.write(a.out / "fillets.json", a.out / "build_log.txt", inputs=[a.params, Path(__file__)])
    try:
        chk = export_frames(body, a.alignment, a.out, a.part, fillets_json=a.out / "fillets.json",
                            model_py=Path(__file__).resolve())
    except ExportAbort as ex:
        print(f"ABORT: {ex}", file=sys.stderr)
        return 2
    s = chk["datum"]
    print(json.dumps({"solids": s["solids"], "valid": s["valid"], "closed": s["closed"], "faces": s["faces"],
                      "volume_mm3": s["volume_mm3"], "fillets": flog.summary(),
                      "scan_bbox": chk["scan"]["bbox"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
