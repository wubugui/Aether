# K import v1: selected-mesh export and isolated native roundtrip preparation

Status: **source-only, not natively parsed/exported/imported**. The accepted source
is unchanged: `recovery-01/authored_envelope58k.blend`, 136,389 bytes,
SHA256 `16eeb67dce6e89f05562b67f869c77dd7882942585241a2648ae46ff48012bee`.
This package prepares the next narrow transfer test. It does not promote K into
Game61, replace the four cloud roots, or claim world/composition/weather acceptance.
No engine process, export, image, Git operation, CLOUD_RESUME edit, or Slack action
was performed while preparing this package.

## Frame decision from the actual source and original Godot basis

The accepted fresh-source/contact reports are in
`cloud-evidence/cloudbank58k-recovery01-20261002T075038Z-4xi10wm2/outputs`.
The scene's native identity stores anchor `(3958, 0, 3667)`, u direction
`(0.685364723205566, 0, 0.728199958801270)`, and v direction
`(0.728199958801270, 0, -0.685364723205566)`. The original D frame and
`common58d.source_coordinates/world_coordinates` give the same conversion.
The four original root bases/positions were read from `native-intake58.json`;
they differ from this shared source frame and are recorded in
`basis-provenance58k.json`. Applying a root inverse now would be premature.

- Preserve the source object's identity matrix and origin `(0,0,0)`
- Export with Blender's standard Y-up map `(x,y,z) → (x,z,-y)`; its determinant is +1
- This yields **Godot world-axis-aligned coordinates relative to the source anchor**
- Do not add the anchor or any of the four roots' inverse transforms
- Do not recenter, rotate, scale, rebuild, triangulate, smooth, weld or modify the mesh
- Keep the six editable Empty controls, semantics and embedded recipe exclusively
  in the unchanged `.blend`; only the one selected shell enters the GLB

Pure reconstruction from the accepted report's effective controls reproduces the
actual saved native fingerprint exactly. This allows an advance bounds expectation;
it does not substitute for the future fresh Blender readback:

- Blender min `(-233.44503784179688,-165.92005920410156,606.328857421875)`
- Blender max `(226.94137573242188,183.78085327148438,851.9830932617188)`
- Godot relative min `(-233.44503784179688,606.328857421875,-183.78085327148438)`
- Godot relative max `(226.94137573242188,851.9830932617188,165.92005920410156)`

## Exact future trial

From the Aether repository root, **only after the parent's scheduling decision**:

```sh
PYTHONDONTWRITEBYTECODE=1 python source-assets/cloud-bank58/revision-k/import-v1/run_import58k.py --run-approved-import
```

Without that flag the runner prints preparation status and creates nothing.
A persistent exclusive attempt marker is written before admission. A concurrent
invocation or restart after an interrupted attempt cannot re-export in place.
The first failure, its temporary project and all outputs are retained. Diagnose
and prepare a separate version instead of deleting a failed attempt marker.

Four serial native stages, maximum requested durations **30/30/20/20 seconds**:

1. Official Blender 4.5.14 opens the exact accepted source with autoexec disabled.
   It checks complete native identity, source dependencies, original cameras,
   settings and saved-array fingerprint, then exports one selected GLB. No save
   operator or render exists in this script
2. Official Godot 4.5.1 editor imports the copied GLB in a new `/tmp` minimal
   project. Only that temporary project's `.godot` and `.import` sidecars are used
3. A separate Godot resource-only process reads actual imported arrays/material,
   verifies identity node transforms, and saves a native PackedScene with embedded
   duplicate mesh/material resources. No geometry/material values change
4. Another fresh Godot process loads the saved native scene. Actual arrays,
   materials, transforms and AABB must exactly equal stage 3

The total admission/work/finalization budget is 120 seconds; deadline overruns
fail the result. The supervised children are pinned to two CPUs with thread limits
of two. The supervisor forces BLAS to one thread **before importing NumPy**, checks
that it is single-threaded before using `preexec_fn`, and remains on the same CPU2
set. Wrapper-plus-child observed RSS and conservative actual peak sums are limited
to 1.5 GiB. GLB size is capped at 250,000 bytes before a bounded read; native scene
size is capped at 500,000 bytes. Every child exit comes from wait4, including killed
children. Logs, PIDs, stage reports, input hashes, immutable intermediate hashes,
final terminal report and a temporary-project manifest are retained.

`bounded_support58k.py` is derived from the previously audited
`coast61-nearbay-orbit/continuous-v6/wrapper_support.py`. The accompanying diff
shows only the RSS checks, single-thread precondition and inclusion of SIGALRM in
the existing signal-safe child-ownership path. No native execution is hidden in
imports or the source-only default.

## Transfer gates

- Exactly 194 authored positions and 384 triangles remain the source authority
- Flat-face GLB export may split vertices by normal. The gate permits 194–1152
  render vertices; every one maps to a source position, every source point is used,
  and all 384 oriented triangles match bijectively. Vertex/triangle ordering may
  change; arbitrary duplication, missing triangles and reversed fronts fail
- Position maximum error ≤ 0.00001 m. Bounds are compared from actual arrays and
  also against Godot's native ArrayMesh AABB
- All three normals on each triangle remain equal within 1e-7. Outward normal
  component error ≤ 3e-5 in GLB and ≤ 2e-4 in Godot, allowing packed-normal
  quantization while rejecting smoothing. Godot reverses CCW glTF indices to its
  clockwise front-face convention; normals retain the same outward direction
- No UVs, colors, skinning, morphs, animations, cameras, lights, textures or external
  GLB buffer references. One material surface, plain opaque neutral PBR only
- GLB baseColorFactor remains linear RGBA; Godot albedo_color is checked after the
  documented linear-to-sRGB conversion. Roughness, metallic, double-sided/culling,
  alpha, zero emission, absence of shader/texture/mesh overrides are checked
- Import flags disable LOD generation, tangents, shadow meshes, mesh compression,
  light baking, animation and material extraction. Naming version is explicitly 2.
  The actual importer sidecar values must match after import
- The native roundtrip must contain embedded resources and no external dependency;
  fresh-process result PIDs must match the wrapper's observed child PIDs
- Every main-project file, including existing `.godot` and `.import` files, is
  hashed before and after. The approximately 2.56 GB hashing cost is included in
  the finite budget. Prepared dependencies/executables and accepted source also
  must remain unchanged. The main project is never an engine `--path`

Headless runs here establish **resource import and serialization only**. They do
not add the mesh to a viewport, use MultiMesh, render images, or claim hardware or
visual behavior. Godot 4.5.1's dummy mesh storage retains ArrayMesh surface buffers;
ArrayMesh itself retains its AABB/materials. Native success remains to be tested.

## Source-only checks and remaining limits

Normal and optimized Python each pass 17 test methods, including all 384 individual
triangle-winding corruptions, wrong axis/origin/mirror, missing/invalid indices,
nonfinite values, smooth/flipped normals, GLB bounds/dependency/schema corruption,
material/emission/color-space corruption, process completion failures and the
no-launch default. In-memory GLB bytes are test fixtures, never exported files.
An initial test fixture accidentally shared its material dict between mutation
cases; both failing logs are retained as `static-tests-failure01-*`. The fixture
now deep-copies its material. This was a test isolation error, not native evidence.

Independent source review checked API plausibility and uncovered several guards
that have now been tightened. GDScript has **not** been parsed by Godot; exporter,
importer, sidecar behavior, normal quantization, resource ownership, actual budgets
and fresh native reload are **not yet proven**. A native failure must remain a
failure; do not relax tolerances or silently change import settings to call it a pass.

Reproduce the non-native checks:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python source-assets/cloud-bank58/revision-k/import-v1/test_import58k.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -O source-assets/cloud-bank58/revision-k/import-v1/test_import58k.py
PYTHONDONTWRITEBYTECODE=1 python source-assets/cloud-bank58/revision-k/import-v1/check_preparation58k.py
```

## Primary implementation references

- Installed official Blender 4.5.14 `io_scene_gltf2/__init__.py` exporter properties
  and `blender/com/gltf2_blender_math.py` Y-up swizzle, both frozen by hash
- [Godot 4.5 import options](https://docs.godotengine.org/en/4.5/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html)
- [Godot 4.5.1 glTF implementation](https://raw.githubusercontent.com/godotengine/godot/4.5.1-stable/modules/gltf/gltf_document.cpp): index reversal and linear/sRGB material conversion
- [Godot 4.5.1 glTF editor importer](https://raw.githubusercontent.com/godotengine/godot/4.5.1-stable/modules/gltf/editor/editor_scene_importer_gltf.cpp): explicit naming-version compatibility behavior
- [Godot 4.5.1 dummy mesh storage](https://raw.githubusercontent.com/godotengine/godot/4.5.1-stable/servers/rendering/dummy/storage/mesh_storage.h) and [ArrayMesh implementation](https://raw.githubusercontent.com/godotengine/godot/4.5.1-stable/scene/resources/mesh.cpp): resource-array/AABB readback scope
