# Coast56: one native low cape and short bay

Status, 2026-10-01: the independent editable source has been integrated into `res://scenes/candidate56-coast/Game56Coast.tscn`, inheriting Game55Observation. The actual GL builder and a separate fresh-process verifier both finished with exit 0, empty failures and `passed: true`. Saved-resource preservation, live root support, collision and runtime-cache checks passed; eight real world screenshots were captured. The reviewed low cape and short bay are visible, while the distant straight shore, materials, water and clouds still fall short of the references. This is a bounded coast improvement, not world visual acceptance or default promotion.

## The specific change

Only the river-mouth south coast within current `World/Terrain/Ground_-4_-4/Model/Ground_-4_-4` is changed. The world-space intake box is X[-3010,-2660], Z[-3040,-2760]. A wide low cape interrupts the straight coast in its northern half; a short bay retreats in its southern half. Actual saved-source sea-level contour samples extend46.19m seaward at Z-2980 and retreat23.16m at Z-2855. These coordinates are recorded design inferences from1131/1347 shore hierarchy, not geography measured from the images.

The source uses the current saved53west ArrayMesh/Shape authority, never the stale external terrain GLB. The current tile is an open heightfield. Its open boundaries remain open; no bottom or wall was added. The initial X-sliding draft folded one projected triangle and was rejected. The final version keeps every original XZ position and index exactly and changes Y using the actual original triangular height surface. It lowers the dry shoulder locally instead of retaining a uniformly steep wall.

## Reviewable artifacts

- `Ground_-4_-4_authority56.blend`: independently reconstructed zero-change current53 source
- `Ground_-4_-4_coast56.blend`: candidate plus hidden original-authority object; selected candidate `Ground_-4_-4_COAST56`
- `native-authority/authority.json`: complete originalpositions/normals/tangents/colors/indices plus direct Shape.faces; UV/custom/bone/weight fields are absent, not invented
- `native-authority/surface_0_arrays.bin`, `original_surfaces.bin`, `collider_faces.bin`: exact Godot Variant serialization of original unpacked arrays, stored compressed surface dictionaries, and collision vectors
- `zero-change-readback.json`: original `.blend` reopened in a fresh Blender process and read back
- `candidate-blend-readback.json`: actual candidate `.blend` reopened and read back, with all native attributes
- `candidate-native.json`: candidate arrays and collision replacement, one-to-one original/candidate vertex and triangle identity, changed vertex/triangle lists, protected face list
- `scatter-replacements.json`: all44 saved roots with exact before/after12-float buffers, source group anchors, original/candidate support triangles/heights and preserved placement offsets
- `verified-static56.json`:75 executable exact-data checks and actual saved-source coastline measurements
- `previews/`: five actual standalone Cycles CPU candidate views plus same-camera original sea-south and overhead images

The integrated Godot candidate lives outside this source folder, under `candidates/round40-exclusive-20260930/project/scenes/candidate56-coast/`; its six resources are in that project's `assets/coast56/`. The generated source and integrated resources preserve the existing terrain material identity and original vertex colors; Blender's preview shader is only a vertex-color display and does not replace the Godot material. Existing shallow-colored submerged vertices become visible on the new cape, producing the pale exposed shore band also visible in the actual world screenshots. Its appearance remains a separate material review item.

## Authority and exact preservation

Input: `res://scenes/candidate53d-west/Game53dWest.tscn`, SHA256 `6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18`, mesh `ArrayMesh_136tc`, collision `ConcavePolygonShape3D_e2dpk`. Game55Observation inherits this world. The external `assets/terrain/Ground_-4_-4.glb` has maxY18.506613; the current saved source has maxY107.849724. They are materially different. Do not reimport the old prefab as the source of truth.

Blender axis contract: native local(x,y,z) maps to Blender(x,-z,y). Triangle winding reverses for Blender display and reverses back on readback. Vertex and triangle order remain unchanged. Exact native normals/tangents are stored as explicit point attributes named `godot_normal`, `godot_tangent_xyz`, `godot_tangent_w`; `NativeColor` is a FLOAT_COLOR point attribute. They are read explicitly rather than replaced with Blender's derived display normals. Every original field round-trips byte-for-byte through a saved/reopened `.blend`.

Editable source candidate:9423vertices,9594indices,3198triangles remain.1426 stored vertices move only inY;533triangles change. Every field of the other2665triangles remains bit-exact, including positions/normals/tangents/colors. All2509triangles crossing/outside the intake box are frozen, as are all four tile borders. Original/candidate welded topology has1669points,138boundary edges,0nonmanifold edges and0degenerate triangles. IdenticalXZ triangles provide a direct no-new-projected-intersection/winding proof. Original/candidate collider has the same welded topology and no folded faces.

The saved Godot mesh uses two surfaces to preserve the untouched native GPU data exactly. Surface0 keeps all9423 original vertices and attribute bytes, but its index list draws only2665 untouched triangles;1583 original vertices are now unreferenced there. Surface1 draws the533 changed triangles using1599 expanded vertices. The explicit mapping is `integration-preparation/surface-triangle-map.json`. Both active materials equal the original active material; the extra `surface_material_override/1` property is verified to be only a null default slot. Original LOD indices and `shadow_mesh` are absent, so no stale alternate mesh draws the replaced faces. Height/collision checks use each surface's actual indices, excluding unreferenced old vertices. Changed-surface native normal encoding has a measured maximum component delta of0.0000832463992992416; this is reported only for the newly encoded changed surface, not used to relax any untouched-field or saved-resource equality check.

Collision replacement is direct and conservative: corners whose corresponding native vertex moves receive that new native position; every other original Shape.faces corner is preserved byte-for-byte. Maximum local native-mesh/collider difference is0.00006103515625m both before and after, inherited on untouched corners. No tolerance was enlarged and no Mesh.get_faces-derived snap was used as native authority.

44saved roots cover38pines,4rocks,2bushes across6groups.29change only theirYbuffer component and15remain byte-identical. XZ/rotation/scale stay unchanged for all44; none requires horizontal relocation. Three pines belong to groups named_-4_-5 but actually lie in this tile and are included. The renderer read all6 source MultiMesh buffers and checked all684 instances/8208 floats against the saved-TSCN static authority, allowing only the29 declared Y slots. Only4 groups need replacement resources. All44 actual runtime roots passed current mesh, shape, physics and world-height support checks; complete tree/rock/bush base footprints are not covered by these root-point tests.

## Protection and completed integration gates

The north river-mouth and tile perimeter are frozen. Neighbors Ground_-5_-4, Ground_-3_-4, Ground_-4_-5 and Ground_-4_-3 are not modified. The intake box has no intersecting independent building/road/island mesh AABBs; nearest harbor_stair_3 lies52.73m outside, keeper_house_42 lies54.66m outside. Underlying world SHA remains byte-identical, proving no saved world assembly change. The protected cliff source and rejected54payload are unrelated and untouched.

The integrated scene is1453bytes and overrides only the target MeshInstance mesh, Collision/Shape shape, and4 MultiMesh resources containing the29 Y changes. Its six resources total352442bytes. No full100MB scene was repacked. Scene SHA256 is `5c0cd84b860c409b647d970f123187e89b2e01099e159a43aff372d40ddbe8c5`.

Evidence:

- [Builder report](../../cloud-evidence/coast56-build-20261001T101413Z-imsxu343/build-report56.json) and its [process report](../../cloud-evidence/coast56-build-20261001T101413Z-imsxu343/wrapper-report.json): exit0, no errors/failures; independent resource save/readback and strict inherited scene graph checks passed
- [Fresh verifier report](../../cloud-evidence/coast56-verify-20261001T101445Z-xvmw5o3r/verify-report56.json) and its [process report](../../cloud-evidence/coast56-verify-20261001T101445Z-xvmw5o3r/wrapper-report.json): exit0, no errors/failures; strict saved readback and live support/cache/collision checks passed
- The source scene, default configuration and recorded native scripts retained their input hashes. Unrelated saved node/resource properties, effective node graph, material identity, transforms, owner/groups, collision flags and unmodified scatter components passed the strict comparison. The dynamic null second-surface material slot is checked explicitly, not broadly ignored
- The44 live physics ray heights equal the raw shape-triangle heights in the report. Maximum `world.ground_height` versus raw mesh height difference is0.000232696533203125m. The0.001m live evaluation bound accounts for float evaluation and the existing derived `Mesh.get_faces` cache; native preservation remains exact. Mesh/shape maximum local component difference remains the inherited0.00006103515625m
- Runtime `prop_transforms` uses the actual saved replacement transforms, and `terrain_samples[-4,-4].triangles` exactly matches the current56 derived mesh faces. The verifier confirmed3198 drawn triangles rather than including old unindexed vertices
- Eight1179×664 PNGs were captured from one actual world instance:1131 and1347 front/side/back, `local_low_cape`, and `adjacent_north_boundary`. The six reference views use the saved observation positions; the two local views are diagnostic. Weather was held at0.35 for repeatable capture without a saved weather change. The parent reviewer viewed all eight and confirmed the physical low cape/short bay, while recording the remaining distant straight shore and material/water/cloud gaps

This README update rechecked the actual scene, six resource and eight image SHA256 values against those reports; all matched. The renderer was `llvmpipe (LLVM 19.1.7, 256 bits)`, not a hardware GPU. Measured peak RSS was924712KiB for the builder and1648684KiB for the verifier; elapsed times were31.85s and198.35s respectively. `visual_acceptance`, `hardware_gpu_acceptance` and `real_flight_tested` remain false as reported.

## Still open

- Same-state original55/candidate56 world-image comparison, dedicated bay-landward/near-water traversal, and a continuous inspection of Y0/wet-bed continuity
- Complete object-base support and visible penetration checks for the44 assets, plus neighboring harbor/stair/house support regression
- Unaffected opening/1125/1332/1342 image regression, a short real flight through this coast and adjacent tile boundary, and hardware-GPU behavior
- Distant coast shape, snow range, islands, materials, water, clouds and full21-reference acceptance; the eight bounded screenshots do not close these gates

Next morphology investigation: the straight coast across the river in `Ground_-5_-5`, rather than another equal-sized cape beside56. The earlier fixed1131 ray at pixel(520,360) hits this block at world(-3282.93,12.93,-3612.21), identifying the visible straight middle-distance section. A provisional interior survey box X[-3440,-3120], Z[-3760,-3430] could contain one broad shallow recess, an unequal lower shore bench, and a short retained rocky nose; variation should follow1131/1347 shore hierarchy instead of a repeating wave. This is a design hypothesis, not image-measured geography or an approved edit envelope. First read the current saved native mesh/shape and screen all actual-world scatter roots, building/road bounds and river-mouth clearance in that box. Freeze the four tile borders, river channel,56 result and all other blocks; retain the same exact preservation and independent source/readback gates before proposing dimensions or applying a new change.

## Reproduction and limits

`export_saved56_authority.gd` reads only target resources through SceneState, never instantiates the world. `blender_authority56.py` creates the reversible source; `read_blender56.py` performs saved-file readbacks; `design56.py` creates the bounded candidate/data; `blender_candidate56.py` saves it; `verify_static56.py` checks final saved data. `preview_coast56.py` adds temporary sea/light/cameras to a loaded source and renders CPU previews without saving them into the source.

All Blender processes used official4.5.14LTS, background mode, two threads. The five previews are source-asset form studies, not Godot screenshots. North/back views expose the isolated tile's original open boundary because adjacent tiles are intentionally absent in a source preview. The archived `candidate_low_shore-orthographic-diagnostic.png` had rays starting below the diagnostic sea plane in the bottom of the frame; the final perspective low-shore view corrects that preview-camera artifact. No game/reference camera was changed.

The first SceneState exporter used a path without its leading `./` and failed the target assertion; its logs remain. The corrected bounded export returnedclean0. The rejected horizontal-displacement draft and failure are retained in `draft-a-x-displacement-rejected/`.

`integration-preparation/run_coast56.py` provides separate parse, actual-renderer build and fresh-verifier entry points; its [README](integration-preparation/README.md) describes the implementation and its preparation-time estimates. The completed reports above supersede that preparation status and estimated resource sizes/RSS. Actual integration saved only the independent56 scene/resources; the verifier entered the inherited world and captured the eight views. Default promotion, full-world/reference acceptance, hardware-GPU and flight acceptance remain undone. This documentation update performed no engine run and changed only this README.
