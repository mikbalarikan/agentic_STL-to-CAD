# M02-02-03 — watertight compound spur gear

## Primary deliverable

- `M02-02-03_WATERTIGHT_SOLID.step`

## Editable semantic source

- `model.py`
- `model_params.json`

The STEP is a neutral exact B-Rep. It does not preserve native SolidWorks feature history. The supplied Python source preserves the intended sketch/extrude/circular-pattern/boolean-cut construction.

## Governing dimensions

- Large gear: 30 teeth, outside diameter 19.05 mm, face width 3.00 mm
- Small gear: 17 teeth, outside diameter 11.20 mm, face width 6.95 mm
- Coaxial through bore: diameter 1.95 mm
- Axial layout: adjacent bands; overall modeled height 9.95 mm

## Assumptions

- Common nominal module: 0.6 mm
- Pressure angle: 20 degrees
- Supplied outside diameters truncate the nominal addendum tips
- Relative gear phase: 0 degrees
- No unmeasured hub projection, relief, chamfer, backlash, profile shift or root fillet was invented

## Claim boundary

Digital design-intent model constrained by operator measurements. Physical interchangeability and manufacturing release require mating-part or physical fit verification.
