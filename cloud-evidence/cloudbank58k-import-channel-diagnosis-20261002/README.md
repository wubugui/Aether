# Actual imported channels: offline diagnosis

The preserved native cache is
`cloudbank58k-transfer-v2-20261002T094351Z-egb4wx8d/imported-cache/cloud58k-native-import.scn`,
11,096 bytes, SHA256
`1b94f241fba9cc48a7879ec71dee4ecff3854955be37f344158494997d3c3e42`.
It is the exact cache named and hashed in the original wrapper manifest, copied
without a new import. The original Godot import succeeded; its subsequent probe
failed before recording array values or saving a scene. Both original results
remain unchanged. No engine was started for this diagnosis.

## Actual saved content

Bounded RSCC mode-2 decompression yields 29,492 bytes. The existing strict RSRC
decoder is reused with local in-memory extensions for the actual PackedScene,
material color and NodePath fields; the original decoder file is unchanged.
All record boundaries, packed payload extents/hashes and reference targets pass.

There is one embedded material, one ArrayMesh and one PackedScene, no external
dependency. The only surface has exact format `34359742471` / `0x800001007`:
bits 0, 1, 2 and 12 are **VERTEX, NORMAL, TANGENT and INDEX**; bit 35 is current
format version. There are 1,152 vertices, 1,152 indices, 384 triangles, 23,040
vertex/normal/tangent bytes and 2,304 index bytes. All UV, color, custom, skin,
blend-shape and compression-format flags are absent.

The actual sidecar SHA `a21107419255bdf37968d48464e4f5996bf3289c266f5d832447e256ac6b2d1d`
still has `meshes/ensure_tangents=false` and `meshes/force_disable_compression=true`.
Thus the failing channel is definitely TANGENT, not missing indices or UVs.

Offline decoding of the saved float32 positions, oct-packed normals and uint16
indices passes the **unchanged original Godot geometry contract**: position error
zero, maximum outward-normal error `0.00010136112354180993 < 2e-4`, exact triangle
bijection/winding and flatness. These decoded arrays are not relabeled as a new
native API readback. Fresh native read/save/reload is still pending.

TANGENT has 1,152 four-component values: all finite, handedness +1, unit error at
most `1.1920928955078125e-7`, and three identical tangents per triangle. Maximum
absolute tangent·normal is `0.00016838312149047852`; versus the original unquantized
source corner normal it is `0.0001653432846069336`. The full packed tangent-byte
SHA is `9abbd7ac9e2aa0960922abde0d5d32757d718348e386d642b895a088a0310aba`.

## Mechanism evidence and boundary

The [official Mesh array documentation](https://docs.godotengine.org/en/4.5/classes/class_mesh.html)
defines tangent groups as XYZ direction plus signed binormal handedness. The
[same-version vector implementation](https://raw.githubusercontent.com/godotengine/godot/4.5.1-stable/core/math/vector3.cpp)
defines oct normal encoding and the tangent encoding that stores sign in half
the second component's range. Existing pinned `mesh.cpp` routes surface creation
and array decoding through RenderingServer; existing GLES storage source confirms
12-byte positions plus separate two-uint16 normal and two-uint16 tangent storage
for this uncompressed format.

Allowed primary-source inspection also verified that
[scene import flags](https://raw.githubusercontent.com/godotengine/godot/4.5.1-stable/editor/import/3d/resource_importer_scene.cpp)
only request explicit tangent generation when `ensure_tangents` is true, and the
[glTF parser's no-UV dummy-tangent branch](https://raw.githubusercontent.com/godotengine/godot/4.5.1-stable/modules/gltf/gltf_document.cpp)
is conditional on that request. [SurfaceTool](https://raw.githubusercontent.com/godotengine/godot/4.5.1-stable/scene/resources/surface_tool.cpp)
preserves the incoming channel mask. The actual cache establishes a tangent was
introduced during native conversion/storage despite that option, but its exact
insertion call is **not independently established here**. Previously denied
RenderingServer/header/capsule source downloads were not retried or substituted.

## Minimal next check, not performed

Read this same SHA-fixed native scene in a fresh minimal project, without importing
or deriving the GLB again. Permit exactly its four observed channels and exact
saved surface format/payload identities. Record all channel types/counts and full
tangents before a possible gate failure. Validate finite/unit/handedness and
quantization-bounded tangent/normal orthogonality; retain the original position,
normal, flatness, winding, material, no-texture and no-normal-map gates. Save an
embedded native scene and fresh-load it with exact equality of **all** arrays,
including tangents. Do not delete the channel check or permit arbitrary channels.

Any new tangent tolerance must be derived from the known signed 16-bit oct storage
error, not selected just above this observed maximum. The original geometry
tolerances remain unchanged. `diagnosis-final.json` additionally verifies original
failure, sidecar, source-array and protected-finalization identities;
`diagnosis.json` preserves the earlier numerical snapshot.
