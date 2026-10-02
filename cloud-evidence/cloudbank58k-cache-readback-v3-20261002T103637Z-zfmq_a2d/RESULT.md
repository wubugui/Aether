# K faithful native resource roundtrip completed

2026-10-02 10:36 UTC. One cache-only read/save child and one fresh reload child both exited 0, in .510768422 and .181182574 seconds. Wrapper exited 0 after 8.787844611 seconds; CPU2, maximum observed aggregate RSS 153204 KiB. No timeout, RSS limit or logged engine error. No Blender, export, GLB derivation, editor import, source save, world load or image occurred in this run.

The already-imported, SHA-fixed 11096-byte SCN was copied into a fresh minimal temporary project. The first resource-only process saved an embedded native PackedScene. The second fresh process reopened it. The actual result is `roundtrip.tscn`, **34772 bytes**, SHA256 `91ab3412c67b5f82449396677a30a9bbe1542a338c00150dc1822910cdf7f789`.

## Actual preserved resource data

Both complete native reports match exactly in every field except mode, PID and the first-stage roundtrip_saved flag. This includes:

- 194 authored positions mapped bijectively to 1152 render vertices and all 384 oriented triangles / 1152 indices
- Actual vertex position error 0; outward normal component error .00010136112354180993, within the unchanged original Godot 2e-4 gate
- All 1152 native normals, all 4608 tangent components, channel inventory, exact format and original packed vertex/index byte hashes
- Tangents with handedness +1, maximum unit error 1.1187863e-7 and normalized |T dot N| .00016838992018380905, below independently derived signed-oct16 bounds. The exact prequantization direction and insertion call remain unproved
- Original neutral material contract: sRGB albedo property, roughness .899999976, metallic 0, double-sided cull mode2, no shader/texture/normal map/emission/transparency
- Identity node transforms, exact AABB position/float32 size/float32 endpoint, and zero external resource dependencies on both reads

Actual vertex/bounds tolerances were not loosened. The separate AABB storage/API arithmetic is checked exactly, without adding an endpoint epsilon. The original unexpected-tangent and AABB-assumption limitations remain documented in the preparation; the old failed readback was not rewritten.

## Identity and acceptance boundary

All 1114 original/preparation identities, the accepted 136389-byte editable .blend, raw exporter GLB, adjusted NORMAL-only GLB, actual source-normal capture, imported SCN and every main-project file remain unchanged. Before/after complete project manifests are byte-identical and losslessly gzipped with original hashes and restoration commands. The protected native arrays/materials survived actual native serialization and a genuinely separate process reload.

This closes the faithful-resource transfer step using the earlier successful editor import plus this new successful cache-only roundtrip. The earlier complete v1/v2 runs still retain their failures. The adjusted GLB remains explicitly adjusted in its NORMAL bytes, not untouched exporter output.

There is **no world integration or new visual/hardware-GPU acceptance** here. K's earlier source-form decision is still only unit-form acceptance. The saved native coordinates remain world-axis aligned relative to anchor (3958,0,3667), with that anchor unapplied and object origin zero. Next is one correctly identified cloud-unit trial, with original world/reference camera/weather constraints and actual source/side/back imagery; do not apply an extra root rotation, recenter, roll out all four roots, or rerun the unchanged long orbit.
