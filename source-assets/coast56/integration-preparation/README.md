# Coast56 bounded integration preparation

Preparation is complete; actual renderer build/verification is **not run**. The target `project/assets/coast56/` and `scenes/candidate56-coast/Game56Coast.tscn` do not exist yet. Python compilation and both Godot4.5.1 `--headless --check-only` entries pass. Parsing never loads/instantiates a world or saves a MultiMesh.

## Exact save scope

The prepared native inheritance template is1453bytes and inherits `Game55Observation.tscn`. It overrides only:

1. `World/Terrain/Ground_-4_-4/Model/Ground_-4_-4.mesh` with one independent two-surface ArrayMesh
2. `World/Terrain/Ground_-4_-4/Collision/Shape.shape` with one independent ConcavePolygonShape3D
3. Four existing MultiMesh properties, affecting only29Ytranslation slots:3rock,1bush,14pine in oak_-4_-4_CoastalPines36b,11pine in poplar_-4_-4_CoastalPines36b

The other15roots, including all3pines in nominal_-4_-5 groups, keep complete original buffers. Validation covers all684instances/8208floats in the six actual source groups, not just the44roots. There is no PackedScene.pack call, no100MB world copy, no root script/scene/environment/material override change, and no default promotion or54work. Existing resources with identical content may be reused after exact readback; nonmatching existing outputs stop the builder instead of being overwritten.

Persistent outputs, when the explicit builder is later run, are only6independent resources in `res://assets/coast56/`, the tiny inherited `Game56Coast.tscn`, and its build report. All source/default inputs stay SHA-frozen. The exact template is `Game56Coast.tscn.template`; `static-multimesh-authority.json` is extracted from the saved53TSCN with its complete source SHA and complete buffer floats.

## Why two surfaces preserve the source

Surface0 keeps all original9423packed vertices and all original GPU fields; only its indices change to render the2665untouched triangles. Exactly1583original vertices become unreferenced in this surface. Surface1 renders the533authorized candidate triangles, with uncompressed float32positions and original colors/material. No scene node is added. `surface-triangle-map.json` maps all3198original faces to their exact surface/face location and explicitly lists the unused surface0vertex indices.

All surface0fields read back exactly against the saved native arrays, including attributes of unused vertices. Every actual surface1position and original color reads back exactly against the source candidate. Edited-face normals/tangents undergo the engine's native encoding, whose normal delta is reported separately; the whole built resource must survive native save/readback with identical canonical data. No out-of-scope field gets a tolerance. Both surfaces' actual active materials must equal the original active material.

The original source text stores no LOD or shadow mesh. Runtime gates independently require one source surface, empty LOD data and null mesh.shadow_mesh; either being present stops preparation's builder for explicit handling. Both result surfaces likewise require no stale LOD/shadow data. Actual drawn faces must map exactly to the3198source faces, and actual collider discrepancy cannot exceed the inherited original exact component error. Mesh.get_faces is used only for checking the existing runtime's derived cache, never as source authority.

A new MeshInstance dynamic property `surface_material_override/1` is the only extra node property masked besides the authorized mesh assignment. It must independently be exactly null, and both get_active_material calls must equal the original material. Every other node property, order, owner, actual group, persistent connection, child scene path, script and unrelated resource is compared.

## Execution entry points

From the Aether directory:

- Parse only (safe default): `python source-assets/coast56/integration-preparation/run_coast56.py --parse-only`
- Explicit GL resource build and saved readback: `python source-assets/coast56/integration-preparation/run_coast56.py --build-renderer`
- Separate fresh-process GL strict readback, live support/cache/physics and eight images: `python source-assets/coast56/integration-preparation/run_coast56.py --verify-renderer`

The last two have **not** been executed. They require an actual DISPLAY and refuse a headless save/verification fallback. No implicit parse→render escalation exists. The wrapper pins absolute tools-feiting/userdata data/cache/config paths, copies executed scripts to evidence, records source hashes, phase reports, PID, exit/signal, errors and child maxRSS, and terminates only its own child process group on timeout/interruption.

The builder instantiates55outside the SceneTree, obtains actual GLMultiMesh buffers and checks them against the static TSCN authority before any resource save. It never invokes world._ready. It then saves only independent resources, frees the original, reloads the tiny inherited56and strictly compares the native graph. The verifier repeats the strict checks in a new process, freeing its original baseline before loading56; only after successful strict saved readback does it enter56into the tree.

## Bounded live gate and images

All44actual GLroots must equal their expected saved-buffer world positions. Each needs raw current mesh and collider support, a real physics ray to the intended terrain body, unchanged runtime placement bookkeeping and consistent world.ground_height. The loaded `world.chunks[(-4,-4)]` must be the actual56mesh, and its runtime terrain cache must equal that mesh's current derived triangles exactly. The existing runtime intentionally calls Mesh.get_faces, which uses0.1mm snapping; the separate execution comparison uses a fixed1mm arithmetic/cache bound and reports exact deltas. This is not a preservation tolerance for any source array or saved resource.

Exactly8actual images are prepared:1131front/side/back;1347front/side/back; a low shore view; a north-neighbor boundary view. Reference front poses come from unchanged existing navigation; side/back rotate at that same point. Local cameras are labeled diagnostic observations in the same saved world. Weather time is held at0.35seconds as in survey47. Every capture checks actual camera collision clearance and records camera/FOV/weather/world-instance/image SHA. This is a local review set, not61-view/full-flight verification; original-opening regression images and final artistic acceptance remain separate.

## Resource budget

Existing55flight measured1,807,516KiB peakRSS (about1.72GiB). Allow roughly1.8–2.2GiB for a single56real-renderer stage plus50–150MB for transient canonical snapshots/arrays; run stages sequentially without another heavy world job. This is an estimate, not a new measured renderer result. The wrapper records actual stage peakRSS. The1453byte scene and6resources are expected below1–2MB combined, subject to actual native serialization. Parse-only runs measured about110–115MB, which says nothing about live-world memory.

## Readback limitations to retain

A parse pass only proves syntax and API binding; the future renderer may still expose a native serialization, inherited-property or physics-cache issue. Any such issue must stop with preserved evidence, not be hidden by weakening fields or loading old terrain GLBs. Complete object-footprint support, real user-input flight, GPU hardware acceptance and21-reference visual acceptance remain untested by this prepared gate.
