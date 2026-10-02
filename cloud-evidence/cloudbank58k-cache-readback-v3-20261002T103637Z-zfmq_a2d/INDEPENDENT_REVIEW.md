# Independent final readback review

2026-10-02, read-only review of the completed run. No engine was started.

Accepted narrowly: the preserved K native asset successfully saved and loaded in
a fresh Godot 4.5.1 process with faithful geometry and material. This is not world,
image, hardware GPU, reference, or complete GOAL acceptance.

- Both native reports passed the unchanged cache_guard58k geometry/material and
  tangent checks when recomputed against the source-bound evidence. PIDs 5 and 12
  match their successful process reports. The wrapper completed with exit 0,
  no logged errors, and both child exits observed.
- Positions, normals, indices, all 4608 tangent components, all 13 channel rows,
  format, stored surface, material, transforms, AABB position/size/end,
  dependencies, tangent semantics, and engine identity are exactly equal across
  the two reports. There are 1152 render vertices and 384 authored triangles.
- Original geometry gates remain unchanged: maximum position error 0 m;
  maximum normal component error 0.00010136112354180993, below 0.0002.
- Independently decoded both base64 PackedByteArray payloads in roundtrip.tscn.
  Their SHA256 values exactly match the original native cache vertex/index
  payloads and both actual native reports. No ext_resource is present; both
  native dependency lists are empty.
- roundtrip.tscn is 34772 bytes, SHA256
  `91ab3412c67b5f82449396677a30a9bbe1542a338c00150dc1822910cdf7f789`.
- Accepted Blender source remains SHA256
  `16eeb67dce6e89f05562b67f869c77dd7882942585241a2648ae46ff48012bee`.
  Actual source/corner evidence and preserved imported cache were rebound by
  the frozen reference loader. Main-project before/after manifests are exactly
  equal; the wrapper records all protected inputs and source unchanged.

No old failed export, readback, or transfer result has been reclassified.
