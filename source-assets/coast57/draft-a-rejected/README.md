# Coast57: broad shallow bay and unequal low shoulder

Status, 2026-10-01: the independent editable source, native replacement data and fresh Blender readbacks are complete. Static preservation/support checks pass. Same-camera source previews are prepared but have not yet been rendered; the shared render window is being coordinated. No57 world integration or visual acceptance is claimed.

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
- `preview_coast57.py`: same-camera source comparison script, prepared only at this status

Blender's native axis mapping is Godot(x,y,z)→Blender(x,-z,y), with winding reversed for display and reversed again on readback. Original normals, tangents, colors and source indices are explicit attributes, not replaced by Blender-derived display data. The preview shader displays original native vertex colors; it does not replace the existing Godot surface material `Meadow stone and shore.066` or the saved MeshInstance material override.

## Completed data gates

The source has8264 vertices,8610 indices and2870 triangles.1560 saved vertices change only Y, affecting583 triangles. Every GPU field on the2287 unchanged triangles remains bit-exact. All2087 box-crossing/exterior triangles, all XZ coordinates, indices, native colors and field absence remain exact. The original fields present are positions, normals, tangents, colors and indices; UV/custom/bone/weight fields are absent.

Original and candidate both have1505 welded positions,138 open boundary edges, zero nonmanifold edges, zero degenerate3D/XZ faces and identical projected winding. Maximum local mesh/shape component difference remains the inherited0.00006103515625m. Only collision corners corresponding to moved original native vertices change; every other original shape corner is byte-identical. Maximum local lowering is70.7325668m on the former steep high shore transition; this substantial local cut needs source and world visual review.

All775 saved MultiMesh nodes and700 external binary resources were screened by actual transformed coordinates during intake. The41 roots in scope are36 pines and5 rocks in3 groups.23 need only their Y buffer component adjusted;18 remain byte-identical. Every XZ, rotation and scale component stays exact. All41 candidate roots have actual native-triangle support; minimum terrain support is3.106584m and maximum Y adjustment is62.616874m. Original root offsets are preserved to float32 translation precision. Some source placements remain on steep slopes, so this is root-point support, not complete tree/rock-base contact acceptance.

The box intersects no independent building/road/island MeshInstance AABB in the saved native survey. All three saved Path3D route control hulls, including road widths, are outside. Actual buildings, harbor assets, neighboring terrain,56 resources, default entry and native scripts are not edited by this source package.

The actual zero-change source build and fresh readback preserve all native float32/int32 fields byte-for-byte. The candidate saved `.blend` then reopened in a fresh process matches the planned candidate arrays exactly. `candidate-blend-readback.json` also reports differences from original authority, which are expected for the changed fields; `verified-static57.json` separately asserts exact agreement with the planned candidate.

## Execution and open gates

Official Godot4.5.1 target-only export: exit0,7.03s,406644KiB peak RSS. Official Blender4.5.14LTS, background mode and2threads: zero-change build exit0 at253140KiB, fresh authority readback exit0 at262972KiB, candidate build exit0 at254948KiB, fresh candidate readback exit0 at266240KiB. The candidate build/fresh readback/static check sequence completed in about1.85s. No source-stage engine or Blender failure occurred; process logs are retained.

Remaining: inspect same-camera original/candidate source renders, inspect full object-base support and shoreline/underwater continuity, and decide whether the shape warrants an independent inherited56 world integration. Future integration requires exact saved native resources, fresh-process renderer readback, actual runtime caches/collision/support, fixed1131/1347 plus local source-targeted views, adjacent-tile and short-flight regression. Materials, water, cloud layers, snow range, islands and all21-reference world acceptance remain separate open work.

This source package does not edit56 history, the protected cliff Blender file,54, CLOUD_RESUME, any world scene or default, and performs no Git operation.
