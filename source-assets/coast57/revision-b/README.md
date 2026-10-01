# Coast57B: explicit broad shore sections and real object feet

Status, 2026-10-01: the independent editable source and fresh source/prop readbacks pass697 checks, and all eight CPU source renders completed and were actually inspected. B replaces A's abrupt back wall with a broader slope and readable low shoulder; the original gray shore band and broad facets remain. This is a reviewable source candidate, not57 world integration or world/reference acceptance. All frozen57A source files and images still match `../freeze-manifest57a.json`.

## Profile and expanded footprint

B remains entirely in Ground_-5_-5. Its engineering envelope is X[-3440,-3090], Z[-3816,-3430]:30m farther inland and56m farther north than A. Actual native screening found no intersecting independent building/road/island mesh bounds or saved Path3D route hulls. East/north tile edges remain18m/24m beyond the envelope and all four native boundary vertex/attribute values are exact. Existing1.201mm/2.220mm north/east seam differences are retained as baseline, not claimed repaired.

The expansion adds19 roots to the screen, giving60:51 pines,7 rocks and2 bushes in4 groups. It increases the native movable control span at Z=-3680 from about137m to217m, and at Z=-3620 from106m to162m. The underlying source remains8264 vertices and2870 triangles. B changes1942 stored vertices only inY and759 triangles;2111 triangles retain all original GPU attributes, including the1912 crossing/exterior triangles. OriginalXZ, indices, colors, field absence and open topology are preserved. Collision corners map to the same actual native vertices; the original local mesh/collider discrepancy is not enlarged.

`section-controls.json` records explicit cross-section knots at actual source vertex Z values: actual source waterline, shifted bay waterline atY0; shore foot8m inland atY4; unequal shoulder32–46m inland atY7–9; and original native height at a back-slope anchor generally128–188m from the old waterline, limited by the protected inland edge. Linear section intervals distribute the main landward rise. The northern end closes over148m instead of the previous narrow fade. It still needs actual visual review; numerical slope/foot checks do not establish natural landform.

## Physical placement and visibility

The actual pine trunk base ring and actual rock/bush lower surface triangles come from the saved native MultiMesh.mesh resources. Full foot polygons are intersected with each overlapping native terrain triangle. Plane-difference extrema are evaluated at every intersection vertex, with complete footprint coverage checked. This is continuous piecewise-planar foot contact, beyond the previous root-point samples.

Forty placements are affected;20 keep their native buffers and original foot conditions. The affected feet have no positive gap after a2mm rounding pad, and actual fresh Blender poses also meet the1mm evaluation bound. Original native buffer values are stored and read back byte-for-byte. Blender's displayed rotation decomposition has maximum component difference2.980232238769531e-7; it is separate from the exact native buffers, and the actual displayed pose is tested for foot contact. This bound does not relax terrain or native placement preservation.

Original shore-height guards remain:pine3m, bush1.5m, rock0.5m, evaluated on the actual supporting terrain triangle. Additional seating uses actual model dimensions: for trees, burial is limited to half the first nonzero model layer; for rocks/bushes, extra seating is limited to one third of the model's height above its origin and total burial to half its full height. These are preparation checks, not visual acceptance. B also retains at least95% of the original above-terrain mesh area for affected pines and75% for affected rocks/bushes, plus95%/two-thirds of original top clearance respectively.

Seven bounded XZ changes are individually declared in `placement-scope57b.json`. All rotation/scale components remain exact:

| Source instance | ΔX, ΔZ (m) | Distance (m) | Extra seating (m) |
|---|---:|---:|---:|
| rock_-5_-5[4] | +2, -4 | 4.472 | 0.812 |
| rock_-5_-5[7] | -8, +28 | 29.120 | 1.245 |
| oak_-5_-5_CoastalPines36b[6] | +2, +16 | 16.125 | 0.182 |
| oak_-5_-5_CoastalPines36b[33] | 0, -2 | 2.000 | 0.101 |
| oak_-5_-5_CoastalPines36b[37] | -8, -14 | 16.125 | 0.187 |
| oak_-5_-5_CoastalPines36b[44] | +10, 0 | 10.000 | 0.238 |
| poplar_-5_-5_CoastalPines36b[4] | 0, +12 | 12.000 | 0.185 |

The final relocated footprints were checked against all final neighboring feet, not only old root positions. Minimum conservative radial foot clearance is4.758m. Complete original/candidate12-float buffers, positions, supporting triangles, seating depths and recorded moves are in `scatter-replacements-seated.json`; the unseated root-only calculation remains separately in `scatter-replacements.json`.

Actual rendered triangles were clipped against the native terrain to measure above-ground surface area and top clearance. These are actual geometry quantities, not a solid-volume or self-occlusion estimate. The native rock/bush meshes do not satisfy a simple convex-volume assumption, so no invented solid-volume percentage is reported.

| Affected object | Extra seat / original above-origin height | Maximum burial / full height | Above-terrain area, original→B | Area retained vs original | Top above root terrain, original→B |
|---|---:|---:|---:|---:|---:|
| bush[1] | 5.6% | 20.4% | 92.4%→81.1% | 87.7% | 3.677→3.470m |
| rock[3] | 6.4% | 25.5% | 87.3%→76.8% | 88.0% | 5.121→4.794m |
| rock[4] | 12.2% | 30.1% | 87.3%→67.0% | 76.7% | 6.656→5.845m |
| rock[6] | 22.4% | 38.2% | 84.2%→65.2% | 77.5% | 4.158→3.226m |
| rock[7] | 20.7% | 36.8% | 87.9%→66.0% | 75.0% | 6.024→4.780m |

The first B placement seated rocks4/7 too deeply, retaining only58%/61% of original above-terrain area. That source and evidence are retained in `rejected-placement-01/`. The initial3m root guard failure and the initially too-narrow placement-search result remain in `failed-probes/` and logs. No gate was silently turned into a pass; the final placement changes and continuous foot/visibility checks address those failures.

## Saved source and verification

- `Ground_-5_-5_coast57b.blend`: editable candidate terrain, hidden original authority and60 actual original plus60 candidate native props, preserving their original mesh/color data and exact native buffer metadata
- `candidate-native.json`: exact full candidate terrain arrays/collision data and identity source mappings
- `candidate-blend-readback.json`, `candidate-props-readback.json`: fresh-process saved source readbacks
- `verified-saved57b.json`:697 passed checks covering native geometry/attributes, all120 stored prop buffers, actual display feet, final relocated-neighbor clearance, existing project hashes and every frozen57A file
- `diagnostics-foot57b/continuous-foot-support57b.json`, `visible-geometry57b.json`: full contact and actual above-terrain area/height evidence
- `intake/`: full775-node/700-external-resource coordinate screen of the expanded envelope
- `logs/source-v3-stage-report.json`: final build/fresh terrain/fresh props/static check, all exit0. Blender peaks256812/267152/250544KiB, static verification161888KiB; total about2.01s
- `previews/`, `logs/preview-stage-report.json`: five candidate and three original same-camera900×700 source views with all60 actual props; exit0,125.46s,819164KiB peak RSS,2CPU threads. All fixed source-input hashes remained unchanged

The placed Blender props are reference geometry for editing, contact measurement and source rendering. Their vertices/indices/normals/colors and native transform-buffer metadata were read back exactly. Future native integration keeps the existing original prop meshes and materials, including any fields not needed by this preview reconstruction, and changes only the declared transform buffers. Do not overwrite native prop mesh resources with the preview reconstructions.

`read_props57b.py` makes both source collections evaluable before reading matrices; hidden original collection world matrices were lazy in the first diagnostic, while their stored native buffers remained exact. Both phases now read back and pass.

## Integration boundary and remaining work

Any later integrated candidate must inherit saved `Game56Coast`, preserving56's Ground_-4_-4 result and55 observation changes. This package's target is still the unchanged saved53 `ArrayMesh_5ypxy`/`ConcavePolygonShape3D_iacqo`, with source SHA `6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18`. `lineage.json` and the verifier preserve the existing scene/default and six56 resource hashes.

Source-view findings: `candidate_sea_south`, `candidate_low_shore` and their same-camera originals show the high rise spread across a wider slope, with a visible low shore bench. The overhead/north views show the inward bay and changing shoulder width. The60 real props are visibly seated in these source views, consistent with the continuous foot tests. The gray shoreline strip remains from original colors; no new hard white band appeared. Broad simple facets are still evident. The land-back view exposes the isolated tile's original open perimeter because neighboring blocks are absent; it does not show a new world crack or a repaired seam. No new paint hides geometry.

World integration, saved Godot renderer readback, runtime scatter/terrain caches, native collisions, fixed1131/1347 views, neighboring terrain/harbor regression, actual flight, hardwareGPU and all-reference acceptance remain undone. No default, native world,54, protected cliff source, CLOUD_RESUME or Git operation is changed by this source work.
