# build123d idioms that the golden builds used

These notes were tested against **build123d 0.13.0** in this repo's environment. Every idiom
cites the golden file it comes from. `P[...]` means a value from `measure/params.json`.

## 1. Hex (or any regular polygon) from across-flats

```python
RegularPolygon(radius=P["hex_af"] / math.sqrt(3), side_count=6, major_radius=True,
               rotation=P["hex_phase_deg"])
```

- For a hexagon, the circumradius is AF/√3. For an n-gon it is `AF / (2*cos(pi/n))`. DRM's
  pentagon used `apothem / cos(36°)` (`golden-examples/dreame_brush-caps/report/source/build_screw.py:22-25`).
- `major_radius=True` means that `radius` is the circumradius. P03 used this for the hex boss
  and the stem (`golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/rebuild_OOM-P03.py:82-94`).
  With `major_radius=False`, `radius` is the apothem instead: this is the classic
  off-by-cos(30°) error.
- Clock the polygon with `rotation`, using a param measured in the frozen datum frame
  (CHK-FRAME). B02 built the hex from explicit vertices at `HEX_PHASE_DEG + 30 + 60k`
  (`build_OOM-B02.py:163-166`). Both forms work. Write down which vertex or flat the phase
  refers to.
- Rounded polygon corners: `fillet(sketch.vertices(), r)` inside the `BuildSketch`
  (B02 `HEX_CORNER_R`, `build_OOM-B02.py:171`). Route it through a logged 2D fillet, because
  P03's `sector_tool` corner fillet skipped silently on failure
  (`rebuild_OOM-P03.py:118-122`).

## 2. Revolve from a param dict

```python
def revolve_rz(pts):                       # closed (r, z) polygon in the XZ half-plane, r >= 0
    face = Face(Wire.make_polygon([Vector(r, 0, z) for r, z in pts], close=True))
    return revolve(face, Axis.Z, 360)
body = revolve_rz([(rb, z0), (ro, z0), (ro, z1), ...])      # every r, z is a P[...] expression
```

- Algebra form: DRM snap (`build_snap.py:23-28`). Builder form: OD
  (`BuildSketch(Plane.XZ)` + `Polyline` + `make_face` + `revolve(axis=Axis.Z)`,
  `build_pump.py:80-128`) and P03 (`rebuild_OOM-P03.py:56-79`).
- A `Polyline` **of profile vertices** is correct. The anti-patchwork rule forbids
  polylines **of raw scan slices**, not straight profile edges
  (`baseline/oomwoo-re-pipeline/RE_SPEC.md:260-262`).
- For curved meridians, use `ThreePointArc` / `CenterArc` for arcs and `Spline` through
  **fitted** points (B02 groove and dome, `build_OOM-B02.py:140-157`).
- Keep every profile vertex a param expression. OD's profile carried three bare radii
  (3.05, 2.95, 2.6), which is a D6 violation to avoid (`analysis/golden/OD-H12.md` §6).
- If the result has volume ≤ 0, the profile orientation is reversed. P03 mirrored the body
  as a safety net (`rebuild_OOM-P03.py:78-79`). `validate_step.py` fails on volume ≤ 0
  either way.
- **Revolve over a span** (legs, hooks): `revolve(Rot(0, 0, -half) * face, Axis.Z, 2*half)`,
  then place it at the measured angles (DRM snap F04, `build_snap.py:50-64`).

## 3. One instance + placements (measured angles)

```python
for th in P.group("leg_theta"):            # measured, possibly unequal
    body = body + Rot(0, 0, th) * leg
```

- DRM used explicit `Rot` loops because its angles are unequal (legs at 60°, 150° and −60°;
  `build_snap.py:63-64`; `README.md:50`).
- M02 fused rotated copies of one tooth in a loop (`model.py:57-64`). B02 used
  `Rotation(0,0,120k)` (`build_OOM-B02.py:279-280`).
- `PolarLocations` is fine for equal pitch, but it has to wrap the **objects**, not the
  `BuildSketch` context. W01 attempt 2 wrapped the context, so its grooves were never
  replicated (`baseline/oomwoo-re-pipeline/TRACKER.md:32`). After any pattern, check the
  instance count, for example by counting the faces or volumes it added.

## 4. Polar sector (annular slot, window, boss segment)

- P03 `sector_tool(r_in, r_out, ang0, half, z_bot, z_top, corner_r)` built its sector from
  `CenterArc` + `Line` + `make_face` and extruded it. It keeps **true arcs**
  (`rebuild_OOM-P03.py:104-124`). Prefer this form.
- B02 `polar_sector` sampled each arc with a 24-point `Polyline`, which facets the arc into
  planes (`build_OOM-B02.py:222-234`; `analysis/golden/OOM-B02.md` §11). Avoid that for
  visible faces.

## 5. Hull + inward offset pocket (OD flange)

```python
with BuildSketch(Plane.XY.offset(z1)):
    Circle(r_hub); Locations((x, 0), (-x, 0)); Circle(r_lobe)   # inside Locations
    make_hull()
    offset(amount=-P["pocket_rim"], kind=Kind.INTERSECTION, mode=Mode.REPLACE)
    Circle(P["r_body"], mode=Mode.SUBTRACT)                        # keep bosses/hub solid
extrude(amount=pocket_depth, mode=Mode.SUBTRACT)
```

Source: `golden-examples/OD-H12_delonghi-dedica-pump/report/src/build_pump.py:181-202`.
`make_hull()` gives the lozenge outline, and `offset(kind=INTERSECTION)` keeps sharp
outline corners on the rim.

## 6. Tangent-coincident booleans: offset the tool

When a cut tool's face would coincide with or be tangent to a body face (e.g. a lobed
outline cutter whose crest equals the revolved radius), hold the tool **0.02 mm** clear.
B02's comment says "tangent faces make the OCC boolean fail"
(`build_OOM-B02.py:182-185`).

- This is a heuristic (n=1: B02). Treat 0.02 as a parameter. Log it and declare it in the
  plan.
- Through-cuts should overshoot both faces (e.g. `+1.0`, as in P03/OD/DRM tools). The
  overshoot is a documented clearance, not geometry.

## 7. Edge selection pitfalls

| Pitfall | Do this instead | Evidence |
|---|---|---|
| Selecting by list index (`edges()[3]`) | Filter by type + position + radius: `[e for e in s.edges().filter_by(GeomType.CIRCLE) if abs(e.center().Z - z) < 1e-3 and abs(e.radius - r) < 1e-3]` | DRM every fillet (`build_screw.py:55-97`) |
| Selecting on a stale shape (before a boolean) | Pass a *selector function* to `FilletLog.apply`, which runs it on the current shape | booleans rebuild edges |
| Box filters that catch neighbours | Add a radius/type filter, or exclude a known feature: P03 skipped the socket rim with `center().length > SOCKET_SQ` | `rebuild_OOM-P03.py:150-152` |
| Position/lambda filters that break when a param changes | Derive every filter bound from the same params the geometry uses; assert `n_edges` equals the plan's expectation | OD `build_pump.py:241,265` flagged fragile (`analysis/golden/OD-H12.md` §11) |
| Empty selection silently skipped | `FilletLog` logs `NO_EDGES` | P03 `if top_edges:` (`rebuild_OOM-P03.py:153`) |
| `.clean()` merges coplanar faces and changes edges | Select after `.clean()`, or fillet before it and re-check | DRM calls `clean()` once at the end (`build_screw.py:100`) |
| Seam edges of full cylinders appear as extra LINE edges | Filter by `GeomType` and by position | general OCC behaviour |

## 8. Other golden idioms

- **Tilted-cylinder dimple**, tilt = atan(depth slope) (DRM F05, `build_screw.py:60-71`).
- **Cone-frustum drafted pocket** via `Cone(r_bot, r_top, h)` (DRM F05 cups,
  `build_snap.py:66-69`).
- **Rounded-rect sheet frame**: `RectangleRounded` ring extruded, plus notches (OD
  `build_pump.py:147-178`).
- **Loft through fitted sections**: `RectangleRounded(w, t, r)` on planes normal to a
  measured r–z path, then `loft(sections)` (non-ruled; B02 `build_OOM-B02.py:255-268`).
  Never use `ruled=True` on scan slices (W01).
- **Envelope intersection**: prism `&` cylinder for turned corners (DRM F02); `&` a
  cylinder for a radial trim (B02 `:283`).

## 9. Version drift (build123d / OCP)

| Symptom | Cause | Fix used in this skill |
|---|---|---|
| `TypeError: 'bool' object is not callable` on `shape.is_valid()` | `is_valid` is a **property** in 0.13 and a method in older releases | `v = getattr(s, "is_valid"); v() if callable(v) else v`; P03 had the same shim (`rebuild_OOM-P03.py:161-162`) |
| `ImportError: TopTools_IndexedMapOfShape` / `TopTools_IndexedDataMapOfShapeListOfShape` / `TopTools_ListOfShape` | Renamed in newer OCP (B02 `q01_solid.py` used the old names) | Dedupe `TopExp_Explorer` results by `hash()` (as build123d does); `BOPAlgo_CheckerSI.AddArgument` |
| `AttributeError: TopoDS has no attribute Face_s` | Static downcasts renamed `Face_s` → `Face` | `getattr(TopoDS, "Face_s", None) or TopoDS.Face` |
| `Bnd_Box.Get()` fails to convert | Return type not bound in newer OCP | `CornerMin()` / `CornerMax()` |
| gp_Trsf rejects a rotation | Float inverse of T is only near-orthonormal | SVD re-orthonormalise (`export_frames.py`; OD `export_final.py:19`) |

The rows marked with an OCP rename were found while testing this skill's scripts on
build123d 0.13.0. Record `build123d.__version__` in `build_log.txt`.
