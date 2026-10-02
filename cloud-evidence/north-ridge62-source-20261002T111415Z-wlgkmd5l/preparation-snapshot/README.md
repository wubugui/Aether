# North ridge62: executable isolated source authoring pipeline

## Current boundary

This directory implements the actual editable Blender source builder, explicit embedded rebuild, independent fresh-reopen validator, and two one-shot bounded launch stages. Preparation and pure Python tests have run. **Blender and Godot have not run for build-v1; no north-ridge62.blend or new rendered PNG exists.** Parent scheduling is required before either native stage.

Frozen preparation remains unchanged: `preparation-v1/FINAL_SHA256.json` SHA256 `12d9f492d3ae1251d37f6b8b94e9e5877eb85dd96f723f97542a5c4885818702`. No shape revision was made. The 754,050m²/12-point footprint, 27 controller points, 15 named relief points, 1,246 per-tile Y overrides, 2,479 affected triangles and main peak745m remain identical. All167 instance support results remain pending;509 query slots and at least57,630 global slots are untouched. This pipeline has no world integration or scatter-edit action.

Original1131/1347 and current61's two corresponding fronts were actually viewed before coding. Their right-hand dominant articulated peak is absent from current61. The present candidate must still earn source-form acceptance, particularly its13 faces steeper than80° and rear silhouette. The retained92.1403m cloud-AABB spatial clearance does not resolve camera-ray cloud visibility. No cloud/weather or camera intervention is implemented here.

## Actual architecture

- `prepare_bindings62.py`: pure offline binding construction. One common controller over all source geometry, never four height/noise generators. Its default performs no writes; `--write` writes only bindings and its check
- `bindings62.json`: one4,326-position shared source surface and8,192 original triangles; exact original beforeXYZ, canonical Y, frozen candidateY, full float64 barycentric weights,72m collar, point/triangle/tile/source-resource mappings, original split-vertex attributes and packed buffers
- `rebuild62.py`: embedded explicit edit command. The editable27-vertex `R62_MASTER_CONTROL` plus15 named semantic height handles feed one `R62_MASTER_EVALUATED`; four terrain objects are deterministic subsets. Editing master relief vertexZ or handleZ works; editing both before one rebuild adds both differences. Exit Edit Mode on all ridge meshes before running the Text; active edit meshes are rejected to prevent stale data or unsafe mesh replacement. All six mesh objects must retain identity transforms; the intended edits are master relief vertices and semantic handle Z. Boundary/XZ edits reject because they require a separately reviewed binding. No autoload handler, driver, save, export or renderer is installed in the rebuild
- `native62.py`: actual bpy builder, immutable fresh read, and exactly one named image per render child. Each stage writes raw native geometry, controls, mappings, attributes, materials, camera matrices/FOV, actual normals and source text identities before validation. Failed raw/terminal evidence is retained
- `contract62.py`: independent frozen-source/mapping checks and actual native validator. Saved positions and original/candidate data use exact float32 bytes. Original Godot clockwise triangles are reversed to BlenderCCW after the right-handed axis map; native polygon and actual corner normals separately meet3e-5 geometry gates, and each face's three corner normals are byte-flat. Polygon and corner results are not wrongly required to be bit-identical
- `run_source62.py`: uses the existing unchanged `bounded_support58k.run_child` for actual PID, CPU affinity, wait4 status/RSS, timeout, kill and reap; uses existing `run_import58k.file_manifest` for original file guards. No replacement subprocess framework and no Godot invocation

Native original_world, original_local, canonical_base_y, collar, changed, source_vertex, source_triangle/tile, material_region attributes and27 weight groups remain editable. Rock/grass/snow are separate native material slots/face regions with editable Principled nodes. They are a neutral source material study, not replacement world materials or weather acceptance. No textured background, image plane, source image composite or whole-world mesh is created.

## Exact original vertex/index preservation

The independent `offline-mapping/` read is restricted to the four original ArrayMesh blocks in pinned53d and the already frozen survey/intake. It preserves6,144 /6,144 /6,058 /6,009 original attribute-vertex slots,6,144 indices per tile and2,048 triangles each. There are1,089 geometric positions in each tile, but welding these would discard distinct original color/normal slots. Only the shared authoring master is position-welded; the four derivatives retain original source slot/index identity.

All24,576 original indexed corners, after the original float32 world transform, match the survey float32 bytes exactly. The survey uses surface_get_arrays/index expansion, **not** Mesh.get_faces snapping. Original source-local coordinates are separately retained because float32 world translation rounds by up to0.000244140625m; subtracting origin would not recover them exactly. Original RGBA8 and normalized float32 colors are preserved in native authoring data and the embedded binding. UV/UV2 are absent in all four originals. Packed normals/tangents remain archived byte-exact but are not newly semantically decoded. Original material/shadow references are recorded, not replaced or followed.

Changing a compressed AABB during future Godot integration could requantize untouched positions. This source build is not that integration gate. Future integration must explicitly preserve unhit native channels, regenerate affected visual derivatives/collision consistently, and pass all167 foot constraints.

## Coordinates and view constraints

Godot→Blender: `(worldX+2560, -worldZ-4608, worldY)`; local originGodot `(-2560,0,-4608)`. The local→world float32 roundtrip is exact for all source candidate positions. Frozen candidateY SHA256 is `2eca5d39aedc03678f7d4611aa8aa497bb616ec9e7b5bade5da16db5284d13d5`; shared authored position SHA256 is `30b541d723bccaef3d5b7bae5f1569bfe65c9c67b256a451ddf33deb382f4a40`.

Reference source views preserve original inputs exactly:

-1131: eye(-2600,330,-2350), target(-2969,156,-3263), verticalFOV55
-1347: same eye, target(-3033,174,-3238), verticalFOV55
-Side diagnostic: eye(-3840,690,-4740), target(-2490,340,-4730), FOV55
-Back diagnostic: eye(-2460,790,-6060), target(-2510,350,-4660), FOV55

Actual camera matrices, lens and vertical field of view are checked on fresh reopen; stored labels alone are not accepted. All four outputs remain1179×664 at100%, square pixels. Fixed neutral CyclesCPU,2threads,8samples, no denoise. No adaptive resolution or repeated tuning loop. Side/back are diagnostics, not replacements for the fixed source reference views. No actual-world cloud occlusion or reference weather is present in this isolated file.

## One-shot native execution, only after scheduling

From Aether, safe default (no engine, blend or image):

    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-authoring/build-v1/run_source62.py

One source build + independent fresh-process reopen, **60s total wall including guards**,CPU2,1.5GiB conservative wrapper+childRSS:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-authoring/build-v1/run_source62.py --run-approved source

Only after that completed terminal passes, four named source images, **90s total wall including guards**,CPU2,1.5GiB, unchanged full resolution:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-authoring/build-v1/run_source62.py --run-approved views

Both stages atomically create exclusive admission files and retain completion files, even failures. No retry in place. Source only writes new `build-v1/north-ridge62.blend`; views never save it. There is no standalone unbounded wrapper option. Every native process runs fresh `--factory-startup --disable-autoexec -b -t2`. Official Blender4.5.14 binary SHA is pinned.

The whole existing source-assets, original blender/assets/ref trees, actual main project including .godot/cache/sidecars, and root project.godot are manifest-guarded before/after. Only this new blend and explicit admission/terminal files are excluded; all other original files/memberships must remain exact. Full-original guard changes, timeout/RSS, mapping/float32 error or logged engine error fail the stage, preserve the evidence, and stop. No parallel source edits should overlap this scheduled window.8s is reserved inside each total budget for final protection checks; the independent review measured the pure guard near5s. Failure is not permission to increase budget or reduce image size.

Raw+native terminal, actual process report, source SHA and wrapper gate must all agree. Fresh reopen requires whole raw native identity equality with the build capture except processPID/affinity. SourceSHA remains fixed throughout verify/views and finalization. Outputs live under a uniquely named new `cloud-evidence/north-ridge62-{source|views}-.../` directory.

## Static tests and limits

Normal and `python -O` authoring suites pass21 methods including six independent-review corruption cases. Offline mapping suites pass9 methods each. Tests reject frozenY changes, wrong winding, welded source attribute slots, originalindex/color/local/rawpayload changes, wrong tile/master association, shifted original cameras, changedmask falsification and boundary movement. AST compilation and preparation reconstruction pass; default launch preflight must pass against final freeze before scheduling.

No actual BlenderAPI readback, saved source, native normals/materials, render performance, four images, visual acceptance,167-foot result, Godotintegration, fullflight or hardwareGPU result is claimed by these pure tests. CompleteGOAL remains open.
