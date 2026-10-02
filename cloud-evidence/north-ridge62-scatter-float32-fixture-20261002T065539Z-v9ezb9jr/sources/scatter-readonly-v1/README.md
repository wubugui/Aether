# Saved MultiMesh intake: source-only preparation

No Godot, Blender, world, renderer, scene instantiation, resource save or project
mutation has run for this revision. The prior collector, plan, dependency guard,
old input manifests and all previous evidence are unchanged. This directory is a
new independently testable preparation. Its future parse and collection must be
coordinated separately; Python/source checks do not prove GDScript parses.

## Scope and facts established without an engine

The design X[-3048,-2040], Z[-5160,-3770] and 40 m buffered query
X[-3088,-2000], Z[-5200,-3730] remain fixed. Neither is an approved edit footprint.

The pinned successful prior collection is
`cloud-evidence/north-ridge62-collect-20261002T053100Z-3mmbw0ol/native-intake.json`:
1,215,201 bytes, SHA256
`5d6e5719b9b5f22397338ab508324ec180afd5a1d54554dcb66294ed79e88df2`.
Raw or lossless `.json.gz` is accepted only at that exact decoded identity.

Independent saved-source reads reconcile all 775 exact path/resource/property-source
triples in the native report, across its same five SHA-bound inherited scenes:

- 708 external RSRC files: 51,753 saved instances, 6 saved-empty groups
- 67 embedded text MultiMeshes: 6,044 saved instances, 11 saved-empty groups
- Total: 57,797 saved instances, 17 saved-empty groups
- Rain and Snow contribute 1,800 and 1,200 saved custom-data instances; hidden
  state is retained and never used to discard their placement records

All counts are from saved instance-count/buffer fields. No group name, node root,
nearest-house selection, visibility range, saved visibility, process mode, or
visible-instance limit is used as spatial clearance. Each of the full allocated
saved instance slots is intended to be checked. Saved-empty is not runtime-empty.

**The prior native report does not contain scatter transforms.** It supports
exact 775 identity/binding reconciliation, but cannot be presented as an old
native transform baseline. `scene_inputs62.py` independently parses each selected
node and ancestor through the complete five-scene override chain, records property
provenance and composes the saved transform. The new native collector must compare
all 775 resulting column/origin values to these prepared expectations. Alternative
transform properties, disable_scale, selected nested instancing, unknown ancestor
classes or malformed property layouts fail closed. The original native SceneState
merge/global-transform functions are reused unchanged through a snapshot of
`collect_saved62.gd`; no copied competing native scene merger is invented.

## Why the bulk buffer can be tested headlessly

Eleven complete official MIT-licensed Godot 4.5.1 source snapshots and their exact
SHA/URL identities are in `upstream/source-manifest.json`. The relevant chain is:

1. [MultiMesh](https://github.com/godotengine/godot/blob/4.5.1-stable/scene/resources/multimesh.cpp)
   stores instance count/format flags on the resource and binds saved `buffer` to
   `set_buffer`/`get_buffer`. It checks count × (12 + 4 if colors + 4 if custom) for
   3D, then delegates the bulk setter to RenderingServer
2. [Rendering storage](https://github.com/godotengine/godot/blob/4.5.1-stable/servers/rendering/storage/mesh_storage.cpp)
   forwards this to the backend when no interpolator is present. Dummy returns a
   null interpolator
3. [Dummy implementation](https://github.com/godotengine/godot/blob/4.5.1-stable/servers/rendering/dummy/storage/mesh_storage.cpp)
   copies bulk float bytes into its owned buffer and returns that buffer. Its
   per-instance setters/getters and aggregate AABB remain no-op/default paths,
   so this collector never uses them
4. [Renderer layout](https://github.com/godotengine/godot/blob/4.5.1-stable/servers/rendering/storage/mesh_storage.cpp)
   places each 3D matrix row in four floats: basis row XYZ then origin component.
   Translation is at slots 3, 7, 11. GDScript Basis construction takes columns,
   requiring the explicit swizzle in `collect_scatter62.gd`. Colors and custom data
   each add four finite floats after the 12 transform floats

This is a primary-source feasibility argument, not proof of this project's loaded
buffers. The future collection must match every resource-loaded bulk buffer to
an independently decoded exact saved float32-byte SHA, count, stride, flags and
bound mesh URI. A mismatch fails; a dummy identity transform never substitutes.

`decoder62.py` strictly decodes uncompressed little-endian RSRC format 6 / Godot
4.5 with the reviewed flags and no metadata/UID indirection. It validates all
internal records and references, property ordering, lengths, finite scalars,
container types and trailing markers. Unknown encodings/properties fail closed.
All 708 actual resources and their 5 external standalone ArrayMeshes were read.
Binary payload hashes use original bytes, not reserialized floats. Text
PackedFloat32Array values are independently converted to float32 and hashed;
actual ResourceLoader agreement remains a future native gate.

## Bounds and what they do not prove

For every instance, the intended operation is:

    instance_world_transform = saved_node_world_transform × saved_buffer_transform
    instance_world_bounds = instance_world_transform × complete_bound_mesh_AABB

`ArrayMesh.get_aabb()` is CPU-side cached saved surface bounds, as verified in
[mesh.cpp](https://github.com/godotengine/godot/blob/4.5.1-stable/scene/resources/mesh.cpp);
it is not Dummy RenderingServer's empty mesh AABB. The collector requires its exact
union to equal all retained `_surfaces` AABBs, and records surface counts/formats,
geometry-storage identities and LOD storage hashes. Any shadow mesh is followed,
cycle checked, independently bounded and conservatively unioned with the base.
Custom AABBs at mesh/MultiMesh/node levels are retained as culling metadata, never
used to shrink the saved-geometry bound. Unsupported mesh classes fail.

These are **undeformed saved bound-mesh metadata AABBs**, not a fresh vertex-payload
extents proof. The report says `vertex_payload_bounds_independently_recomputed:false`.
LOD index alternatives refer to the same saved surface vertex domain; generated
or script-swapped models are outside this guarantee. `model_scene` is recorded
but not instantiated, and its live replacement/collision extent is not inferred
from the bound MultiMesh mesh. This is deliberately narrower than universal
occupied footprint, collision clearance or all future runtime geometry.

Material identities, shader-code SHA, next-pass links and native billboard/grow
fields are retained. Shader/custom-data deformation envelopes, skeleton/blend
shape deformation and runtime material changes require separate review. Every
group carries the explicit unproved-envelope/runtime-model limitations. Merely
having a saved custom culling box does not prove it encloses those effects.

The native collector exports only query-overlapping instance records, including
source index, local/world transform, world origin, whole model bounds, and saved
color/custom data. It exports per-group exact buffer/source hashes, counts,
complete aggregate bounds, saved flags and unsupported reasons for all 775 groups.
No full-world second buffer dump is produced. A group AABB overlap is never used
as a substitute for actual per-instance footprint intersection.

The intended native success means only the above saved affine AABB intake was
read and checked. `all_occupancy_complete`, `runtime_generated_entities_proved`,
`shader_deformation_envelopes_proved`, `road_width_proved` and `visual_acceptance`
stay false. No terrain-edit clearance or approved footprint follows.

## Prepared metadata and checks

`prepared-inputs.json.gz` holds 2,283,728 decoded bytes of compact hashes, counts,
bindings and transform provenance, compressed to 109,534 bytes. There are no full
instance buffers inside. `prepared-inputs-identity.json` pins both representations.
The safe default runner independently rebuilds the metadata from the immutable
source bytes and requires exact byte agreement before any future native launch.

- `check_scatter62.py`: 173 Python-only math/text/source/terminal-schema cases, normal and `-O`.
  Nonsymmetric row/column transforms, exact origin slots, 100 seeded affine
  reflection/scale/shear cases, whole-footprint hits with roots outside query,
  closed-edge overlap, malformed numbers/text and forbidden native getter/setter
  mutations are covered. Child0 plus launcher-exception is explicitly rejected,
  and missing prepared-input/query identities, transforms or bound records fail
  the output validator. Synthetic complete-schema fixtures are not native runs.
  Numeric fixture tolerance is only an oracle comparison;
  it does not widen/relax production spatial query boundaries
- `test_decoder62.py --actual`: 14 synthetic test groups, including every-byte
  truncation and malformed references/typed values, plus all 708 actual buffers
  and 5 standalone meshes. Normal and `-O` logs are retained. Both passes retain
  the frozen 1,483 dependency identities before/after source reads
- `run_scatter62.py --static-only`: original full dependency/startup/cache/absence
  guard, unchanged 1,477 historical input manifest, all new preparation identities,
  metadata reconstruction, Python AST and source-scope checks. No engine invoked

## Future bounded commands, only after window coordination

From Aether:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/scatter-readonly-v1/run_scatter62.py --static-only
    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/scatter-readonly-v1/run_scatter62.py --parse-only
    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/scatter-readonly-v1/run_scatter62.py --collect

Do not substitute a collect for an unreviewed parse. Each explicit invocation
owns one child only, uses the pinned official 4.5.1 binary, first two available
CPUs, headless/Dummy audio, separate XDG dirs and the existing tested 60-second
hard-bound launch helper. It cannot start the project main scene. The original
full north dependency guard and old input identities run before and after,
including cache/startup settings, exact prior 51-file gap and absent sidecars.
Inputs are not adopted as a new baseline. Any changed input or failed guard clears
native success, including a child0 terminal path.

A unique evidence directory retains prepared metadata, source snapshots, raw
stdout/stderr, actual child exit/signal/elapsed/RSS, partial collector JSON and
terminal wrapper report. Success additionally requires launcher status finished,
no launcher exception, finite elapsed0–60s and no timeout/cancellation. The
collector atomically refreshes partial evidence
every 25 completed groups, and records a final completion marker. Timeout,
cancellation, exception, missing data and failed native comparisons do not become
success. The existing full dependency/launcher fixture results apply to their
unchanged reused code; they are not a new native test of this collector.

Git, publication, CLOUD_RESUME and active world-window ownership stay with the
coordinating parent. All original preparation and failed evidence remain intact.
