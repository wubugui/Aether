# 26b independent sloped-paving review

**Retain the continuous slope-lane improvement as a bounded pass.** The repeated scalloped contour steps disappear and the actual five views show connected lanes, level doorway aprons and shared courts. Overall reference-art fidelity and full character traversal are not accepted by this review. A thin bedding-cap intersection with terrain remains explicitly recorded.

## Actual inclined top surfaces and clearance

The review reads actual 26b GLB geometry and includes **inclined as well as horizontal top faces**. Design data is used only to identify declared top-vertex roles: every actual vertex of a top candidate must be within 0.1 mm of a declared top vertex. Plane heights and intersection extrema come from the actual exported vertices. No broad normal-angle cutoff hides steep anomalous top microfaces.

This identifies **12,157 upward top faces, including 10,639 inclined faces**. Full projected triangle intersections with actual 26b terrain give:

| Surface/group | Worst actual result |
| --- | --- |
| Foreground true stone top | **31.409224 mm minimum clearance** |
| Bay true stone top | **23.840572 mm minimum clearance** |
| Foreground bedding cap, including thin anomalous faces | Terrain exceeds cap by **0.961332 mm** |
| Bay bedding/stone top combined | **12.838210 mm minimum clearance** |

The foreground bedding overlap is at world XZ **(-2236.54780354, -1760.94030619)**. It is **foundation/bedding cap**, not the stone walking top: bedding Y 14.61852813, terrain Y 14.61948946. The relevant intersection projects to **0.0000391951 m²**, with minimum caliper width **0.118905 mm**. Actual stone top in that vicinity remains above the terrain. The JSON preserves the actual triangle, intersection polygon and dimensions.

Consequently **do not carry forward 25f's 47.96 mm all-cap clearance or claim a nominal 6 cm gap across the entire actual export**. The stone top is clear, but an exact zero-intersection claim for all bedding caps would be false.

The initial raw “4 cm penetration” at XZ (-2250.0, -1760.45912170) is retained in the JSON with corrected classification. It is a slightly tilted stone thickness sidewall, containing Y 12.679938 and 12.579939 vertices at XZ separated by only about 7.6 micrometers. Its actual same-XZ upper envelope is 10 cm above the reported side point. Intended ground burial of this lower sidewall is not stone-top penetration. Actual normal and upper-envelope evidence are recorded, rather than merely discarding the face by a normal threshold.

## Support, interfaces and slope

- No paver/paver overlap with more than **5 mm height mismatch** was found at intersection area above 0.000001 m².
- For **9,278 support intersections** retaining more than 0.0001 m² after 1 mm inward erosion, actual stone-top to bedding-top separation is **11.9966–12.0026 mm**, matching the intended 12 mm relationship. The 10 cm-thick stones therefore overlap their support volume in these resolved regions rather than floating above it.
- Remaining unsupported projection fragments vanish under a 1 mm inward buffer. Raw extreme support gaps on microscopic/edge intersections remain in the JSON; they are not described as a uniform 12 mm gap everywhere.
- All **27 transverse samples across nine doorway interfaces** lie at the authored entry level or approximately 12 mm below it where the exposed joint reaches bedding (maximum absolute difference 12.003 mm).
- For actual paver top triangles with projected area >= 0.001 m² and minimum projected altitude >= 5 mm, maximum slope is **22.992° foreground / 22.990° bay**. These are relatively steep but continuous hillside lanes. This is geometric evidence, not proof that every intended character/controller traverses every route correctly. Abnormal thin top faces are retained in the raw results, not presented as ordinary road grades.

## Foundation, shore and identity

Whole original/new core triangle intersections beneath the nine actual main house bodies preserve original terrain within **0.023052 mm**. Forward doorstep projections still contain under-slab fill, so the unchanged-height claim excludes those doorstep extensions.

All **134 original core shoreline vertices** retain exact coordinates, and all **2,937 original non-upward triangles** retain exact geometry/material identities. Actual headland BLEND/GLB hashes match the passed reopened gate; actual paving BLEND/GLB hashes match the passed gate with **469 + 453 = 922** editable source parts. Frozen GPU geometry matches these independently audited assets.

## Five current GPU views

Run `village-paving-26b-20260908T143321Z-441bad8ec7bd4024b195dca93cc8bd82` is terminal **passed**. All five sidecars match the run and report zero paving failures. This reviewer directly viewed foreground, bay, door junction, upper street and night reference.

Continuous paving reads more coherently than the prior scalloped steps, including in the doorway close-up. The large exposed spike faces and long black radial crease do not visibly recur. Some short exposed roadbed edges, irregular ground facets and broad original rock faces remain; the distant night view still has the unresolved regular water-glint and overall composition/art differences. These images establish a bounded regression improvement, not final reference-art acceptance.

Keep the improvement and the recorded edge limitations. No further repeat of this geometry suite is warranted without relevant changes. No production assets or generators were modified by this reviewer. The adjacent JSON includes raw-sidewall evidence, corrected true-top measurements, native/frozen-input identities, protection checks and image hashes.
