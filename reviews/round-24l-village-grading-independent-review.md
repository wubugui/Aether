# 24l independent actual-geometry review — reject combined terrain and paving

The actual 24l graded headland preserves the checked original boundary and underside, but its combination with the actual 24j paving is **not accepted**. Independent GLB geometry checks found a 0.75 m terrain/paver penetration and confirmed the reported 15 cm overlapping pavers. These are actual artifact findings, not inferred GPU ray errors.

## Rejecting evidence

**Bay terrain/paver penetration:** world XZ **(-2224.3179219903564, -1872.8434267137125)** has an actual exported limestone cap at **9.75 m**, with actual new terrain at **10.500003 m**: **0.750003 m above the cap**. The overlapping terrain/cap triangle intersection has area 0.0125659 m². The corresponding design cap belongs to `bay worn stair paver 9.750 -3401 -2783 component 0`; 9.90 m and 10.05 m pavers also cover this point, while no foundation cap covers it within 0.1 mm. This flags paving outside its supporting graded bands; it does not establish that the intended bedding-based grading field itself is wrong.

**Foreground overlapping pavers:** at the runtime counterexample XZ **(-2257.72192382813, -1750.06359863281)**, both `foreground worn stair paver 10.500 -3185 -2823 component 0` and the corresponding **10.650** solid cover the point. Their projected overlap is **0.115773 m²**, and the point is **12.8 cm inside both boundaries**. Actual GLB triangle decoding confirms lower top 10.5 m, upper bottom 10.5500002 m, and upper top 10.6499996 m. This supports the runtime 10.65 m hit and rules out a mere rounding-at-the-boundary explanation. See `round-24l-independent-paving-overlap-counterexample.json` for actual triangle coordinates.

## Completed actual-geometry checks

- Current 24l BLEND and GLB SHA-256 values match the separately reopened native gate. Original GLB identity is also recorded.
- All **134 core upper boundary vertices** remain present at their exact exported coordinates. Independent boundary graph reconstruction finds components of 134 vertices plus eleven groups of 5 rock-shoulder boundary vertices; all 189 vertices are preserved.
- All **2,937 original non-upward exported triangles** remain with exactly the same vertex coordinates and material names. This covers the original bottom/side geometry, including rock geometry, under an exact triangle comparison.
- Every actual horizontal upward paving cap triangle was checked against actual upward terrain triangles by planar intersection and linear plane-height extrema: **7,233 foreground cap triangles / 29,272 overlaps**, and **5,009 bay cap triangles / 22,890 overlaps**. Foreground has no terrain penetration and minimum clearance **47.9984 mm**. Bay fails as described above. The reported 7.92783 m² sum counts full intersection cells having an extreme above 1 mm; it is not an exact penetrated-area measurement.

## Deliberate limit

The nine real foundation assets were identified from the frozen 24l validation inputs, but their complete original/new terrain-region comparison was **not completed** after these sufficient rejecting counterexamples. Prior native success proves closed meshes, not a correct mutual arrangement. The earlier 24i/24j route findings concerned foundation-derived profiles, and do not certify the visible upper envelope of overlapping pavers. This review does not substitute for GPU, full walking, or visual acceptance.

Fix the actual paver/band inconsistency and then repeat only the affected artifact/clearance checks before completing the remaining foundation and visual reviews. No production or generated assets were modified by this reviewer. Full metrics and identities are in the adjacent JSON; independent audit scripts are `audit_24l_actual.py`, `audit_24l_overlap_counterexample.py`, and `finish_24l_review.py`.
