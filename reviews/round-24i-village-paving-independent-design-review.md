# 24i independent paving design review — rejected for two pinched contours

Scope: independent read-only inspection of the final `captures/village_paving_design_24i/paving.json`. All 1,521 solid caps were reconstructed from their triangle indices; no preparer or root profile-audit functions were imported. This report is design geometry evidence, not Blender, GPU, collision, visual, or full walking acceptance.

**Blocking defect:** two bay solids share a boundary vertex of degree four at world XZ **(-2219.105, -1858.989)**:

- `bay terrace bedding 8.550 3 component 0`, area 13.8094015 m², vertex 38.
- `bay worn stair paver 8.550 -3375 -2779 component 0`, area 0.059342 m², vertex 0. Another solid has the same name but is not defective.

Their caps have correct area, valid planar unions, and boundary-edge sets matching triangle incidence. However, inner and outer contour branches meet at one vertex. Extruding the recorded shared vertex and boundary edges gives four side faces incident on its vertical edge, so the closed-solid manifold condition fails. All other 1,519 solids passed the cap topology checks. Parent reports that its separately reopened native Blender artifact confirms exactly these two four-face vertical edges; that native inspection was not performed by this reviewer.

The paving profile changes are successful within the requested bounded audit. Independently calculated segment/boundary crossing parameters for all **27 route profiles** (nine centers and both ±0.6 m offsets) found **no step above 18 cm and no depression at least 15 cm deep and under 24 cm long**. All **27 entrance transverse points** matched their authored threshold level. Entrance points use lateral offsets -0.6/0/+0.6 m and are 20 mm inside the apron to exclude boundary quantization ambiguity. The 12 mm bedding/grout recess is excluded from the design stair metric.

Historical counterexamples now have these cap-derived design levels:

| World XZ | Current level | Levels within 10 cm |
| --- | ---: | --- |
| (-2251.58, -1750.84), old deep pit | 10.95 m | 10.80–10.95 m |
| (-2247.4, -1870.672734), old 6 cm groove | 6.75 m | 6.75 m |
| (-2235.170884, -1878.4), bay_upper -0.6 m | 8.25 m | 8.25 m |
| (-2219.636357, -1859.016522), bay_workshop -0.6 m | 8.55 m | 8.55 m |

**Disposition:** reject 24i as a completed closed-solid deliverable. Make a narrowly targeted fix for the shared contour point, then verify the resulting actual Blender solids and localized terrain grading before visual/GPU acceptance. No additional broad audit of the already failed 24i version is warranted. The adjacent JSON records all exact profiles, entrance samples, and defect coordinates; `reviews/audit_24i_independent.py` records the independent method. Production and generated assets were not modified by this review.
