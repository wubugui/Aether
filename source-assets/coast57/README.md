# Coast57: broad shallow bay and unequal low shoulder

Status, 2026-10-01: Draft A is rejected for world integration. Its editable source and fresh readbacks pass84 exact-data/root-point checks, but eight actual source previews show an abrupt planar back wall, and actual native object-foot measurements confirm worsened floating/penetration. Preserve this source and its images as failed evidence. Any further shape work belongs in independent `revision-b`, not in these frozen files.

## Shape and bounded scope

The target is current `World/Terrain/Ground_-5_-5/Model/Ground_-5_-5`, in world X[-3440,-3120], Z[-3760,-3430]. This box first served as a survey envelope. The actual change excludes every triangle crossing its edge and freezes every original vertex shared with a protected triangle. A broad shallow inward bay peaks at about31.97m of X retreat at Z=-3630. Its lower shoulder widens toward the already lower southern shore, with a narrower northern transition back into the original high plateau. The northern74–79m and southern24–35m background terrain are retained outside the local transition. This is a reference-informed design inference, not geography measured from1131/1347.

The source keeps every original XZ position and index. It samples the original native heightfield with a lateral profile offset and changes only Y, then lowers the dry shoulder within a bounded falloff. A narrow rising shore foot joins a gentler low bench and the original back slope. No new cap, side wall, global terrain generation, camera movement or weather mask is involved. The original source is an open heightfield and stays open.

## Authority and lineage

Current saved53 native mesh `ArrayMesh_5ypxy` and collision `ConcavePolygonShape3D_iacqo` are authoritative. The source scene SHA256 is `6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18`. `export_saved57_authority.gd` reads only the target resources through SceneState, never instantiating the world. Mesh authority comes from actual `surface_get_arrays`, and collision authority from direct Shape.faces. All original stored surface dictionaries are also retained. The source has no LOD data or shadow_mesh, verified through the native API.

The current world lineage is56→55→53. This target block is unchanged through55 and56, which is why53 is its source authority. Any future integrated57 candidate must inherit `res://scenes/candidate56-coast/Game56Coast.tscn`, retaining both56's Ground_-4_-4 low cape/short bay and55's observation changes. Do not revert the whole world to53/55. `lineage.json` records this base and hashes the three scenes, default configuration and all six56 resources; the static verifier checks they remain byte-identical.

Original east/north seam differences are approximately2.220mm/1.201mm; west/south common-coordinate height differences are zero. All four target boundaries remain exact and the neighboring world files remain unchanged, preserving these baselines. This package does not claim to repair those existing seams.

## Artifacts

- `Ground_-5_-5_authority57.blend`: current native source reconstructed without geometry or attribute change
- `Ground_-5_-5_coast57.blend`: selected editable candidate `Ground_-5_-5_COAST57`, plus hidden original authority
- `native-authority/authority.json`, `surface_0_arrays.bin`, `original_surfaces.bin`, `collider_faces.bin`: direct native authority and exact Variant bytes
- `zero-change-readback.json`, `candidate-blend-readback.json`: actual saved files reopened in separate Blender processes; exact native attributes read from explicit stored point attributes
- `candidate-native.json`: full candidate arrays, shape replacement, changed/protected indices and identity vertex/triangle mappings
- `scatter-replacements.json`: all41 actual saved roots, complete original/candidate transform buffers, supporting triangles/heights and retained root offsets
- `static-design-checks.json`, `verified-static57.json`: shape metrics and executable preservation/support gates
- [Pre-edit intake](../../cloud-evidence/coast57-intake/REPORT.md) and [numerical map](../../cloud-evidence/coast57-intake/intake-map.png): source occupancy, coastline, cross-sections and adjacent boundaries
- `logs/authority-stage-report.json`, `logs/candidate-stage-report.json`: actual process exit, RSS, duration and invocation records
- `preview_coast57.py`, `previews/`, `logs/preview-stage-report.json`: five actual candidate views and three same-camera original views, all source-only CPU renders
- `diagnostics-foot57/actual-foot-support57.json`: actual native tree/rock feet transformed by the saved buffers and measured against original/candidate native terrain
- `draft-a-rejected/`: frozen first-candidate source/data/image snapshot and rejection note

Blender's native axis mapping is Godot(x,y,z)→Blender(x,-z,y), with winding reversed for display and reversed again on readback. Original normals, tangents, colors and source indices are explicit attributes, not replaced by Blender-derived display data. The preview shader displays original native vertex colors; it does not replace the existing Godot surface material `Meadow stone and shore.066` or the saved MeshInstance material override.

## Completed data gates

The source has8264 vertices,8610 indices and2870 triangles.1560 saved vertices change only Y, affecting583 triangles. Every GPU field on the2287 unchanged triangles remains bit-exact. All2087 box-crossing/exterior triangles, all XZ coordinates, indices, native colors and field absence remain exact. The original fields present are positions, normals, tangents, colors and indices; UV/custom/bone/weight fields are absent.

Original and candidate both have1505 welded positions,138 open boundary edges, zero nonmanifold edges, zero degenerate3D/XZ faces and identical projected winding. Maximum local mesh/shape component difference remains the inherited0.00006103515625m. Only collision corners corresponding to moved original native vertices change; every other original shape corner is byte-identical. Maximum local lowering is70.7325668m on the former steep high shore transition; this substantial local cut needs source and world visual review.

All775 saved MultiMesh nodes and700 external binary resources were screened by actual transformed coordinates during intake. The41 roots in scope are36 pines and5 rocks in3 groups.23 need only their Y buffer component adjusted;18 remain byte-identical. Every XZ, rotation and scale component stays exact. All41 candidate roots have actual native-triangle support; minimum terrain support is3.106584m and maximum Y adjustment is62.616874m. Original root offsets are preserved to float32 translation precision. Some source placements remain on steep slopes, so this is root-point support, not complete tree/rock-base contact acceptance.

The box intersects no independent building/road/island MeshInstance AABB in the saved native survey. All three saved Path3D route control hulls, including road widths, are outside. Actual buildings, harbor assets, neighboring terrain,56 resources, default entry and native scripts are not edited by this source package.

The actual zero-change source build and fresh readback preserve all native float32/int32 fields byte-for-byte. The candidate saved `.blend` then reopened in a fresh process matches the planned candidate arrays exactly. `candidate-blend-readback.json` also reports differences from original authority, which are expected for the changed fields; `verified-static57.json` separately asserts exact agreement with the planned candidate.

## Execution and open gates

Official Godot4.5.1 target-only export: exit0,7.03s,406644KiB peak RSS. Official Blender4.5.14LTS, background mode and2threads: zero-change build exit0 at253140KiB, fresh authority readback exit0 at262972KiB, candidate build exit0 at254948KiB, fresh candidate readback exit0 at266240KiB. The candidate build/fresh readback/static check sequence completed in about1.85s. No source-stage engine or Blender failure occurred; process logs are retained.

The CPU2 source preview run completed exit0 in126.57s at813028KiB peak RSS, with five candidate angles and three original same-camera views. All recorded source input hashes remained unchanged. All eight images were actually inspected; the parent reviewer also inspected the main before/after and low/overhead comparisons. The inward bay is visible, but `candidate_sea_south` and `candidate_low_shore` show a more abrupt high planar back wall, not a natural broad slope transition. The original gray shore strip remains; these images do not show a new exposed hard white band like56. Original material/color data were not repainted.

Actual foot diagnostics, exported through target-only SceneState without a world instance, confirm why41 passing roots are insufficient. All36 pine trunks have a six-vertex native base ring at localY=0; all5 rocks were measured on actual lower mesh triangles clipped at their original root plane. Of41 placements,7 have maximum sampled foot air gap increase greater than0.1m:2 rocks and5 pines. Six have penetration increase greater than0.1m. The thresholds describe evidence and do not replace acceptance gates.

- `rock_-5_-5[7]`: maximum sampled lower-surface air gap0.146→4.560m, burial1.541→2.668m; its candidate sample at world(-3265.7915,33.5648,-3676.3171) lies above actual terrain triangle1862 atY29.0051
- `rock_-5_-5[6]`: air gap0.338→1.469m; its lower-surface sample at(-3161.3938,26.7973,-3562.6309) lies above triangle2244 atY25.3279
- `poplar_-5_-5_CoastalPines36b[4]`: actual trunk-base air gap0.122→0.436m, with comparable0.436m high-side penetration

All41 original/candidate placements, exact sampled foot coordinates, triangle IDs and gap/penetration values are in `diagnostics-foot57/actual-foot-support57.json`. This discrete surface sampling demonstrates failures; it does not claim continuous contact or rigid-body stability. Original rocks intentionally embed some lower body, so original and candidate depths are both retained. The native prop geometry export exited0 in7.01s at384640KiB peak RSS.

Remaining: use explicit broad cross-section control points to distribute the rise from low shoulder to74–79m platform, preserving unequal width and meaningful slope changes. First assess whether the current box fits that transition; if it does not, only read-survey the smallest inland expansion and its occupants before proposing a new envelope. Re-evaluate actual feet. A few documented within-box XZ relocations may be proposed if geometry alone cannot provide appropriate support, but the current preservation gates must not be silently weakened. Future accepted source work still needs saved native resources, fresh renderer readback, runtime caches/collision/support, fixed1131/1347 plus local views, adjacent-tile and short-flight regression. Materials, water, clouds, snow range, islands and all21-reference world acceptance remain open.

This source package does not edit56 history, the protected cliff Blender file,54, CLOUD_RESUME, any world scene or default, and performs no Git operation.
