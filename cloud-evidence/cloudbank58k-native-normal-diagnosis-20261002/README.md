# Actual native polygon/corner-normal diagnosis

The readback attempt in
`cloudbank58k-normal-readback-v1-20261002T091816Z-whfkeukw` remains **failed**:
native exit 1 after 0.587596 seconds, wrapper exit 1 after 5.561373 seconds.
It nevertheless preserved the complete 281,016-byte native array capture before
validation, SHA256 `35cde26e14f8767c015295cff3b8f271a85052a111d8fd68e066784a18e1b1c7`.
The native result binds its SHA and PID to the observed wait4 process. Source,
full identity, camera/scene state, protected inputs and main project were unchanged.

## What the actual data proves

- All 384 triangles' three actual corner normals are individually bit-identical;
  same-face corner difference is exactly zero. Native `flat_faces` is true
- Polygon normals differ from their corner normals on all 384 faces. Maximum
  component difference is `8.52346420288086e-6`, on face 270
- Polygon versus double-precision geometric normal: maximum `1.0260302307774083e-7`
- Actual corner versus geometric normal: maximum `8.509929039529629e-6`
- Both independent outward/unit-normal tests satisfy the **unchanged `3e-5` gate**
- Actual native corner normals through the installed exporter's
  round(4) → normalize → Y-up produce all 384 raw GLB faces exactly, maximum error 0

The failed guard equated two different Blender API computations bit-for-bit.
That assumption was wrong. The original failure and code are not modified or
reclassified as a native pass. Collection of actual data succeeded; the complete
native validation and wrapper did not.

## Why the APIs differ

[Blender 4.5.14 RNA](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/makesrna/intern/rna_mesh.cc)
lines 498–506 show `MeshPolygon.normal` calls `face_normal_calc` directly.
Its corner-normal collection instead reads the mesh's cached corner normals
(lines 1566–1591). [The same-version mesh implementation](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/blenkernel/intern/mesh_normals.cc)
uses a triangle cross-product path for the direct polygon call, but Newell
accumulation for the face-normal cache; face-domain corner normals expand that
cache to each corner. Different float32 operation order therefore need not yield
bit-equal polygon and corner API results.

The earlier mathematical Newell prediction is within `5.960464477539063e-8` of
every actual corner; 166 faces are exactly equal before exporter rounding. It
must not replace the now-available native values. The exporter explicitly reads
`corner_normals`, so actual captured corners are the faithful transfer authority.

There is no observed smoothing error: every actual triangle is exactly flat and
both normal streams match its outward geometric direction within the original
tolerance. The capture did not enumerate the `custom_normal` attribute itself;
this report does not claim an independent proof that that attribute is absent.
The documented API paths and actual values explain the failure without invoking
a source-shape defect or requiring another native read.

## Next transfer, still not executed

Use the existing SHA/PID/source-bound actual corner arrays and existing raw GLB.
Map oriented source triangles and their corners to every split render vertex,
reject ambiguous shared ownership, and derive a new GLB by replacing only NORMAL
float32 slots with the mapped actual values. Keep the raw GLB unchanged; this is
explicitly an adjusted transfer artifact, not untouched exporter output.

An in-memory array-only experiment passes the entire original geometry contract
unchanged, with maximum normal error `8.509929039557385e-6`, position error zero.
No adjusted GLB was written and no native engine ran in this diagnosis. A future
implementation must retain source/actual-data binding, byte-for-byte identity of
every non-NORMAL byte, original material checks, flatness/orientation gates and
isolated Godot import/save/fresh-load verification. Neither source acceptance nor
this offline result establishes transfer, world or visual acceptance.

`diagnosis.json` contains all 384 actual polygon/corner comparisons. The original
validator is rerun and required to fail with its original message before the
separate diagnostic checks are recorded. `analyze_actual_normals.py` is the pure
reproducer; it refuses to overwrite its evidence output.
