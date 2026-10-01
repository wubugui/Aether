# Small native D source: build and fresh readback

This item saves the already checked 325 vertex / 646 triangle fold junction as
one editable native Blender mesh. It adds 32 editable design POLY curves and
two valley POLY curves, all unbeveled and excluded from rendering. Mesh vertex
groups preserve each upper crease/valley row, all three side rings and every
vertex role. The mesh is the authoring master; the curves are guides and do not
automatically deform it. Twelve small E folds remain guide-only.

No geometry regeneration, remesh, smoothing, subdivision, decimation, union,
flat cap or four-root expansion occurs. Existing frozen D JSON and C remain
unchanged. Only float32 storage conversion is permitted, with exact ordered
stored vertex and face comparison in the new Blender process.

## Files and expected product

- `build58d.py`: save `fold58d.blend` once, with native compression
- `verify58d.py`: open that exact SHA in a separate process and inspect it
- `common58d.py`: frozen input identity, coordinate conversion, camera settings
- `preview-settings58d.json`: one exact-reference front and four full-shape views
- `run_native58d.py`: coordinated build/readback, total 60 seconds, two threads,
  1.5 GiB observed and actual child peak RSS gates

The file contains one 325/646 mesh, 34 short curves, five cameras, one sun, one
neutral untextured material and one short editing note. No images, external
libraries, old world, duplicated JSON arrays or other source assets are packed.
Estimated compressed size is 0.15–0.6 MiB, not a measured promise. The actual
size is reported after saving. More than 1 MiB stops before fresh readback for
parent review; the saved source is preserved without removing editing data.
Publication uses ordinary Git only after the parent verifies the binary path.

Run only after explicit scheduling and publication-path approval:

```sh
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python3 -B \
  source-assets/cloud-bank58/revision-d/native-01/run_native58d.py \
  --run-approved-native-build
```

The wrapper checks the official Blender 4.5.14 binary SHA, refuses to overwrite
a saved candidate and creates a unique `cloud-evidence/cloudbank58d-native-*`
directory. It writes a running/false report first. Inputs are bound by SHA under
`inputs/`; it does not copy old reports over the current process report or make
large duplicate snapshots. Child exits, final report SHA and `wrapper.exit-code`
establish the terminal result. Failures and partial source files are retained.

## Strict native checks

- Exact expected float32 source coordinates, ordered oriented faces, identity
  object matrix, world origin and input SHA; flat shading and no modifiers
- Actual stored mesh: closed orientable genus-zero single shell, positive
  volume, no loose/pinched/degenerate/duplicate elements, all actual triangle
  candidates including adjacent faces checked for improper intersections
- Original valley 25 m stations plus endpoints, lanes −20/0/+20 m, unchanged
  floor bands and first-solid-interval minimum 160 m
- Every curve knot, width/junction metadata, one 3D POLY spline, zero bevel and
  extrusion; every upper/side/role mesh group index and weight exactly retained
- Main mesh effectively visible through its collection and view layer; guide
  objects and guide collection effectively excluded from rendering
- Exactly the intended object inventory and one Principled/Output material
  connection, no image/environment texture nodes, images or external libraries
- Reference-front camera basis, position, near/far and projection compared with
  the recorded 1216 values; all five matrices exact against pre-save values
- Four orthographic views frame every actual mesh vertex with at least 7% margin
- All 293 frozen C files, all frozen static D files and current inputs unchanged

These gates establish stored native identity and sampled geometry only. They
do not establish continuous valley-band clearance, ship flight or cloud style.

## Prepared preview cameras, not a rendering step

The exact 1216 front uses 836×471 and pixel aspect 942/941, preserving the saved
projection at reduced resolution. Its underside may fall outside the original
camera; that is measured, not corrected by moving the reference camera. Back,
side, underside and top use 836×586, square pixels and full actual-vertex framing.

The material is a single neutral Principled shader; no ID colors, reference
image, height-color law or texture. Fixed world strength 0.7 and sun energy 2.5
match the earlier neutral source lighting strengths. CPU Cycles, eight samples,
denoising off are prepared; no script here calls rendering. This is an isolated
shape inspection setup, not matched final cloud lighting or a world screenshot.

Publish this native/readback item with current progress before beginning the
separately scheduled five-image inspection. D cloud shape has no visual pass.
