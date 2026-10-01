# Cirque54v2 actual world shape diagnostic

Ready for the parent-controlled graphical slot:

`python source-assets/lake-cirque54/v2/world-diagnostic/run_world_diagnostic.py`

The actual five-view source run `cloud-evidence/cirque54v2-source-preview-20261001T084921Z-8w68fr6m` completed clean 0. All five images have been reviewed: the lower, wider side shoulder reads better, while longitudinal hard snow bands and large gray faces remain. This permits a limited two-view world diagnostic only, not visual acceptance or integration.

## Exact visual edit

Load frozen saved53west SHA `6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18`. Its cirque Model contains exactly one leaf, `massif_cirque_wall`. Replace that native node's original 692-triangle ArrayMesh with the new 862-triangle `remodeled_cirque_body`; retain the existing node, transform, owner, visibility, layers, shadow setting and material bindings. Add only three temporary snow leaves: `snow_gully_a` 360 triangles, `snow_gully_b` 284 and `upper_snow_basin` 48. Total visible authored source is 1554 triangles. The old visible root mesh is no longer assigned to any node. There is no old-root overlay.

Saved53 has no extra cirque leaves to remove. All west leaves stay intact, including its four additions `ridge_shoulders`, `snow_cap`, `snow_gully`, `shore_rock_apron`, and the original west root. No rejected 53/54 source parts are loaded.

The replaced body itself contains the original 432 whole wet/cross-water faces and 19 whole protected dry faces. Actual runtime raw surface arrays/indices are checked against the original saved GPU positions and colors, oriented triangle by oriented triangle. Neither `Mesh.get_faces` nor a tolerance replaces this exact gate. Every new rendered world vertex must match the frozen source float32 coordinate exactly.

The readonly native encoding probe found that ArrayMesh stores colors with RGBA8 precision. All 1353 original preserved face vertices keep exact original RGBA; the other 1233 body vertices and new snow vertices acquire at most 0.003920 channel quantization. `native-mesh-encoding.json` pins the actual Godot encoded-color hash for each component, independently generated without a scene or MultiMesh access. Runtime colors must match this encoding exactly, while wet/protected faces independently remain exact to the old native scene. Source Blender/payload/proofs are unchanged.

## Intentional diagnostic limits and gates

The old collision shapes and all saved53west scatter buffers/transforms remain unchanged, so visible modified dry slopes may temporarily disagree with support or vegetation. No physical integration claim is allowed. No Game54 or asset is saved. Runtime digests protect all scene collision shapes, all vegetation instances, west geometry/materials, and every other MeshInstance's geometry/bindings. Frozen source/scene/default SHAs are checked before and after.

Only the original1128 and1129 cameras are used. Weather is frozen at0.35 with live same-world reflection and depth. Two PNGs are visibly labeled UNINTEGRATED. No new camera hides remaining gray faces.

The wrapper records both raw streams, phase brackets, source snapshots, input hashes, native replacement/protection reports, actual child exit and strict wrapper exit. Any ERROR/SCRIPTERROR/leak, unexpected warning, missing image or failed gate causes wrapper failure even when Godot returns0. Only the known unsupported VSync warning is retained as allowed. Prior failed54v1 lifecycle reports stay untouched. The root-reference cleanup v4 passed its actual same-source control with no errors; see `LIFECYCLE_REVIEW.md` for its precise scope and the new entry reference-lifetime review. This new world run still must independently pass the same strict log gate.

Preflight: Godot check-only and Python compilation passed. The isolated native mesh replacement probe (no full scene, physics, MultiMesh or GUI) passed all four raw-position/native-color checks and all432wet plus19protected oriented raw geometry/RGBA checks. The actual graphical world still must repeat these gates.
