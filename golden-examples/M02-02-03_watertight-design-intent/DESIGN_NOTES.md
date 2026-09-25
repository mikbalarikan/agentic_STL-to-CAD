# M02-02-03 corrected design-intent rebuild

## Authority

The operator-supplied tooth counts, outside diameters, face widths and bore diameter govern this revision. They invalidate the earlier 27-tooth / 21.75 mm candidate.

## Semantic feature chain

1. Large involute tooth sketch
2. Straight extrude, 3.00 mm
3. Circular pattern, 30 instances
4. Small involute tooth sketch
5. Straight extrude, 6.95 mm
6. Circular pattern, 17 instances
7. Coaxial core union
8. Through-bore cut, diameter 1.95 mm

## Explicit assumptions

- Millimetres are measurement-verified by the operator.
- The two toothed bands are adjacent: large gear Z=0..3.00 mm; small gear Z=3.00..9.95 mm.
- A common nominal module of 0.6 mm and a 20 degree pressure angle are used. Supplied outside diameters govern the actual tip radii, so the tips are truncated relative to nominal full addendum.
- Relative angular phase is 0 degrees because no phase datum was supplied.
- No extra hub projection, relief, chamfer, backlash, profile shift or root fillet is invented.

## Claim boundary

This is design-intent CAD constrained by the supplied measurements. STEP is a neutral exact B-Rep; it cannot preserve native SolidWorks feature history. Editable semantic construction is supplied in `model.py`. Physical interchangeability and manufacturing release remain outside the digital claim.
