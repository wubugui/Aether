# K normal export failure: independent pure-Python diagnosis

This is a new diagnostic record. The first import attempt, frozen code, accepted
`.blend`, raw GLB, and main project have not been changed. No native process,
export, import, image, or world execution was used for this diagnosis.

The raw 31,144-byte GLB has SHA256
`48a0aa816dc5dd247958fb883d4114b8d07e7fdf2d458af6a408e0af4c22dd60`.
All 1,152 split vertices map exactly to the 194 saved authored positions; all 384
oriented triangles match bijectively. Each triangle's three normals are identical.
The unchanged `3e-5` normal gate fails 216 faces. First failure is triangle 0,
authored vertices `[0,1,13]`, component error `4.715106582042772e-5`. The largest
error is triangle 302, `[151,152,163]`, `5.993405823961906e-5`.

## Cause supported by full numerical replay

The installed official Blender 4.5.14 glTF add-on reads native corner normals,
rounds them to four decimal digits, then normalizes and applies Y-up swizzling:
`blender/exp/primitive_extract.py:1428-1475`; its
`io/com/constants.py:159` sets `ROUNDING_DIGIT = 4`. The hashes of these local
primary sources and exporter properties are recorded in `diagnosis.json`.

The exact saved geometry can be reconstructed from the accepted recipe with an
identical saved-array SHA fingerprint. Cross-product normals plus the exporter
rounding reproduce 377/384 faces bit-for-bit. A float32 Newell sum starting with
the first-to-second edge reproduces 381/384. Both incomplete attempts are reported,
not hidden. The official 4.5.14 source calculates cached face normals with Newell's
method starting at **last-to-first**, then visits the remaining corners in order.
Following that operation order, float32 rounding, normalization, and the installed
exporter's round/normalize/swizzle reproduces **384/384 faces and every exported
normal component exactly, maximum error zero**.

Primary implementation references, inspected 2026-10-02:

- [Blender 4.5.14 mesh normals](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/blenkernel/intern/mesh_normals.cc), normal_calc_ngon and normals_calc_faces, lines 113–177; corner face-domain expansion, lines 427–443
- [Blender 4.5.14 vector routines](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/blenlib/intern/math_vector_inline.cc)

This is a complete numerical reconstruction of the observed GLB, **not a fresh
native source-normal readback**. The original failed export did not write its
source report before validation failed. Native polygon/corner normals therefore
remain to be independently collected. The new `normal-readback-v1` preparation
does only that, under a separately scheduled native window. No import success is
inferred from this diagnosis.

## Faithful transfer proposal, not implemented or run

The inspected installed exporter has no public switch around its unconditional
four-decimal `np.round`. gltfpack/Draco precision options are separate stages and
do not bypass this line. Do not modify the installed exporter, its module globals,
the accepted source, the original failure, or the `3e-5` gate.

A separate transfer version can preserve the raw GLB and create a second GLB whose
only changed bytes are NORMAL accessor payload values restored from **fresh actual
source polygon/corner normals**, with the documented `(x,z,-y)` mapping. Authoritative
position/triangle bijection determines normal ownership; exporter vertex ordering
must not be assumed. Reused render vertices must have one unambiguous source normal
across all referencing faces or the operation must fail. The current file has 1,152
split vertices, disjoint NORMAL bufferView 1, 13,824 bytes at BIN offset 13,824, no
sparse/compressed representation and no normal min/max metadata. A general routine
must explicitly validate these facts rather than assume them.

Required evidence before any such transfer proceeds:

1. Fresh actual arrays, full source identity before/after, source SHA and native
   PID/terminal binding; source normals pass the unchanged outward/unit/flat gates
2. Preserve and hash the raw failed GLB, show exact 384-face replay from those
   actual source normals, then leave all original evidence untouched
3. Bound every normal byte slot, prove no overlap with any other accessor or JSON,
   and prove **every byte outside those slots is unchanged**, including header,
   JSON, position/index/material buffers, layout and padding
4. Verify every new NORMAL equals the mapped native float32 source normal exactly;
   replay all original geometry/material gates with their original tolerances
5. Keep native Godot import/save/fresh-load gates separate and still pending until
   they actually run. This adjustment preserves authored normals; it is not a
   world integration, source edit, or visual acceptance

Risks are wrong face-to-split-vertex ownership, shared normal slots, buffer overlap,
accidental JSON/material changes, stale or mathematical substitute normals, and
misreporting an adjusted GLB as untouched official exporter output. The above
guards must reject those cases. This record only proposes the approach.
