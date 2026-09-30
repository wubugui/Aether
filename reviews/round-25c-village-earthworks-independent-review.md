# 25c independent earthworks review — reject exposed slope geometry/art

**The fill hides the previous high smooth roadbed walls, but introduces near-vertical exposed terrain faces and conspicuous radial creases. Keep 25c as a rejected study, not a final or production asset.** The cap, main-house foundation and shoreline checks below pass; they do not override the slope and visual defects.

## Confirmed exposed slope counterexamples

The steepest qualifying actual core triangle is **88.0158°**, at centroid world XZ **(-2254.270833, -1747.735263)**, versus original slope ratio 0.506081 (about 26.8°). Its projected area is **0.02193586 m²**, shortest projected edge **0.563975 m**, and the whole triangle projection lies outside the paving footprint. Its centroid is **0.942929 m from the paving**. It is not a sub-millimeter degenerate face that can be dismissed by deleting small triangles.

| Actual world vertex X, Y, Z | Original 23g Y |
| --- | ---: |
| (-2256.0, 9.54705143, -1746.0) | 9.32237339 |
| (-2253.60102081, 10.89001465, -1748.39897919) | 10.06570940 |
| (-2253.21147919, 10.73998070, -1748.80680847) | 10.18724445 |

A bay counterexample reaches **87.8157°** at XZ **(-2236.040401, -1875.814321)**. Two of its vertices move horizontally only **0.0721169 m** while rising **1.486990 m**: world (-2236.15621948, 6.55302429, -1875.88206100) and (-2236.15621948, 8.04001427, -1875.95417786). Original heights were 6.55302215 and 6.58144318. Almost all its 0.01252865 m² projected area is outside paving. The adjacent JSON records the steepest ten actual triangles and original vertex heights for targeted constraint/subdivision diagnosis.

## Completed independent checks

- Actual 25c BLEND and GLB hashes match both build report and the passed reopened native gate.
- All **12,083 actual 24m cap triangles** were unioned by level/kind and checked against whole actual 25c terrain intersections. No penetration was found. Minimum clearance is **47.2098 mm foreground**, but only **2.2623 mm bay** at XZ (-2218.225736, -1857.576501), below the 8.55 m paver. This very small remaining margin is recorded rather than rounded up to a nominal 6 cm guarantee.
- Actual house foundation-base projections were derived from frozen GLB sandstone base faces (local upper Y <= 0.181 m), not copied from preparer exclusions. Over whole original/new core triangle intersections, all **nine main foundation bodies**, excluding forward doorstep projections, preserve old terrain height within **0.03861 mm** maximum discrepancy.
- The **forward doorstep parts are not unchanged**: their terrain rises approximately **0.12–0.40416 m**, with the largest change at `fore_workshop`, XZ (-2248.894623, -1744.806121). Thus “all nine foundation regions retain original height” is accurate only for the main bodies, not the complete base-plus-doorstep projection. This check does not by itself label intentional fill beneath doorstep slabs as a collision defect.
- All **134 original core boundary vertices** retain exact exported coordinates. All **2,937 original non-upward triangles** retain exact vertex geometry and material names. Original lower/side geometry is preserved.

The core-height comparison isolates the largest coordinate-connected actual core component from the eleven separate rock components, avoiding erroneous comparisons with buried rock-shoulder layers. Slope risk screening uses changed height > 1 cm, projected triangle area >= 0.01 m² and shortest projected edge >= 5 cm; it deliberately separates meaningful exposed faces from microscopic slivers. It is not a complete slope bound for every surface triangle.

## Actual GPU inspection

Run `village-paving-25c-20260908T140040Z-542f147b2e5043ea9e91bb591f0cb494` is terminal **passed**, with zero paving failures in all five sidecars. This reviewer directly viewed all five images: foreground, bay, doorway junction, upper street and night reference.

The former smooth elevated ribbon walls largely disappear, so the fill addresses its immediate visual target. However, the doorway close-up clearly reveals a long dark crease descending from the court edge and multiple sharp, radiating triangular faces across the fill. Foreground and upper-street views also show fan-like skinny terrain facets and abrupt patch transitions. The night overview still contains the village groups but is too distant to cancel these close-view defects. The measured near-vertical exposed triangles and the visible sharp creases support rejecting this earthworks revision for final visual use.

Next work should target height-field continuity and controlled slope subdivision at the recorded counterexamples. Do not remove these large-edge faces as if they were the earlier tiny degenerate triangle, and do not repeat the already passed cap/body-foundation/shoreline checks until relevant geometry changes. Full reference fidelity and full-width locomotion are not accepted by this report. No production or generated assets were modified by the reviewer.
