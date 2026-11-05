# feature_tree.json (schema `feature_tree@v1`)

The model is data. `scripts/build_tree.py` builds it, checks every node and rolls back a node
that fails. Worked example: `examples/od_h22/feature_tree.json`. It is the OD-H22 valve and
equals v0's 297-line `model.py` to 0.000000 mm³.

## Top level

| Key | Meaning |
|---|---|
| `constants` | `{NAME: {value, why}}`: documented clearances only (cut overshoot, bury depth). A constant without a `why` fails lint. |
| `let` | Derived values, evaluated in order: `{"k": "tan(radians(a))"}`. |
| `profiles` | Named 2D profiles that nodes reuse with `{"ref": name, ...overrides}`. |
| `params` | Optional inline params (tests). Normally params come from `--params measure/params.json`. |
| `nodes` | The ordered feature list. |

## Values

A number is a literal. A string is an expression over these names:
- params
- `constants`
- `let` bindings
- `repeat` variables

Allowed functions: `sin cos tan asin acos atan atan2 radians degrees sind cosd tand sqrt hypot
abs min max len range sign round sum`. Expressions may also use `pi`, `x if c else y`,
comparisons, and indexing (`port_t0[i]`). Nothing else parses: no attributes, no imports, no
lambdas.

Any literal other than 0, 1, 2, 3, 4, -1, 0.5, 90, 180, 270 or 360 is reported in
`tree_log.json#literals`. Every dimension must come from a param, and every clearance from a
constant.

## Node

```json
{"id": "F07", "name": "...", "op": "revolve", "combine": "add",
 "let": {...}, "repeat": {"i": [0, 1]}, "let_each": {...},
 "frame": {...} | "frame_each": {...}, "place": [{"rot": [0,0,"th"]}, {"pos": [x,y,z]}],
 "post": [{"op": "fillet", "edges": {...}, "r": "..."}], "mirror": ["YZ"],
 "assert": ["len(slot_w) == slot_count"], "expect": {"solids": 1, "dv": "+"},
 "local": true, "why": "...", "on_fail": "stop" | "continue", "skip": false}
```

- **`combine`**: `new` (first body), `add` (default), `cut` or `intersect`.
- **`repeat`**: zips equal-length lists, giving one instance per element. The instance tools
  are unioned and combined with the body once. An empty list is an error.
- **Frames:**
  - `frame` (one for all instances) or `frame_each` (re-evaluated per instance) places the
    local tool.
  - A plane is `"XY"|"XZ"|"YZ"`, or `{"plane": "XY", "offset": d}`, or
    `{"origin", "x_dir", "z_dir"}`.
  - `place` rotates and translates in local coordinates before the frame is applied.
- **`post`**: fillets and chamfers on the tool in its local frame, before it is placed (for
  example a box's axial edges).
- **`mirror`**: unions the tool with its mirror about a global plane.
- **Checks after every node:**
  - the result is valid;
  - the solid count is `expect.solids` (default 1);
  - the volume delta has the right sign: add > 0, cut < 0, intersect ≤ 0, fillet ≠ 0.

  A failure rolls the body back. With `on_fail: stop` (the default) the build stops at that
  node and exits 2.

## Ops

| Op | Fields |
|---|---|
| `extrude` | `sketch: {plane, profile}`, then `amount` or `z0` + `z1` (offsets along the plane normal), plus `both`, `draft_deg` |
| `revolve` | `profile` in (u = radius, v = height), revolved about local Z; `angle` (default 360) |
| `box` | `size`, `at`, `align`: `center` (default) or `min` or `[ax, ay, az]` |
| `cylinder` | `r`, `h`, `at` (base centre), `align` (default: base at `at`) |
| `cone` | `r1`, `r2`, `h`, `at` |
| `loft` | `sections: [{plane, profile}]`. Non-ruled only: `ruled: true` is refused (anti-patchwork rule). |
| `group` | `parts: [primitive, ...]`, unioned in the same frame. Each part may have its own `repeat` and `place`. |
| `fillet`, `chamfer` | Body op: `edges` selector, `r`, `fallbacks`, `param`. Logged in v0 `fillets.json` format (CHK-FILLET). |
| `mirror_body` | `plane` |

Fillets come last. A fillet node placed before a later add or cut node needs `"local": true`
and a `why`, or lint fails.

## Profiles (`scripts/sketch2d.py`)

```json
{"items": [{"type": "circle", "c": [0, 0], "r": "plate_R"},
           {"type": "chain", "repeat": {"xh": "ear_hole_x"}, "let_each": {...},
            "pts": [[0, "y0"], ["s*tx", "ty"], ["s*tx", "-ty"], [0, "-y0"]],
            "arcs": {"1": {"center": ["s*X", 0]}}}],
 "fillet_vertices": {"r": "outline_blend_R", "select": "concave"},
 "offset": "-rim_wall_t"}
```

**Item types:**
- `circle {c, r}`
- `rect {c, w, h, angle, r}`
- `slot {c, length, width, angle}`
- `ngon {c, r, n, angle}`
- `polygon {pts}`
- `chain {pts, arcs}`

Items combine in order with `mode`: `add`, `sub` or `intersect`.

**Chain arcs.** Segment `i` runs from `pts[i]` to `pts[i+1]`. An arc always passes exactly
through both end points. The spec only picks its side and size:
- `{center}`: the centre is projected onto the chord bisector. Gives the minor arc unless
  `major: true`. A half circle also needs `side`.
- `{r, side}`
- `{mid}`
- `{sagitta}`

**Post-processing**, applied in this order:
1. `fillet_vertices`: `select` is `concave`, `convex`, `all`, or `near` (with `pts`). Concave
   and convex corners are found with a disc-area test, so tangent joints are never filleted.
2. `offset`: negative is inward. Arcs are kept, so concave blends grow by the offset.

## Edge selectors

All the given predicates must hold. They are evaluated on the current shape, never by list
index:
- `geom`: line, circle, ellipse or bspline
- `parallel`, `perpendicular`
- `z` (with `z_tol`): start, end and centre all lie at that z
- `near` (with `tol`): a list of `[x,y]` or `[x,y,z]` points
- `radius` (with `r_tol`)
- `in_box`

## Outputs (`--out`)

| File | Contents |
|---|---|
| `tree_log.json` | per node: `status`, `dv`, `volume`, `solids`, `faces`, `valid`, `seconds`, `error`; plus `unused_params`, `literals`, `sketch_fillets` |
| `fillets.json` | fillet and chamfer log (CHK-FILLET format) |
| `build_log.txt` | text build log |
| STEP and STL files | v0 `export_frames`: `<part>_datum.step`, `<part>.step` (scan frame), `<part>_cad.stl` |
| `export_check.json` | v0 `export_frames` export check |

`--until <id>` stops after one node, for staged builds and the M2 loop.
