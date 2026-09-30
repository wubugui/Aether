# Lake48 first physical basin candidate

Scope: Ground_1_-2 / Ground_1_-3 and only intersecting eastern cirque / western east-foothill foot geometry. Source47 scene SHA256 `ba236fdb78f662351ad8e89d82df4642b27721638412c833f86f6e8f682caa32` remains unchanged. No global regeneration, water level, fixed reference cameras, cliff master, routes, settlements, snow summits or planned island props were edited.

## Source authority

Four original Blender meshes have exactly the same triangle topology as saved47 after nearest-vertex mapping. glTF quantization causes up to 0.01660345m vertex displacement, so they are not bytewise geometric equals. Each editable copy was mapped to the current saved47 positions before local sculpting. Outer adjacent terrain edges retain saved47 coordinates. Shared two-tile edge deforms with the same world-coordinate function.

`sculpt-report.json` records source triangle equivalence and individual changes. `base47.json` contains parent real-renderer exported four meshes and 500 live MultiMesh transforms. `support47.json` is a separate read-only triangle export of all 11 saved mountain meshes; no headless MultiMesh values are used. `draft01-zero-scatter-rejected/` and `draft02-incomplete-support-rejected/` preserve failed interpretations, not accepted candidates.

## Design and local topology

The asymmetric basin connects the southern existing water to Z=-2130 at sampled depths 22.2–30.5m. The shore curves around the east-foothill summit core at X1269.84/Z-1810 and preserves that peak. The west cirque peak at X809.49/Z-1780 is also untouched. This is deliberately a first narrow shared basin, not the final reference-scale lake or completed mountain composition. At Z=-2150/-2170 untouched northern mountain feet close the far shore; no claim is made to a channel farther north. Metric shore coordinates are authored inferences, not facts derivable from the images.

Each of four objects is independently editable in its own `.blend` with actual vertices, faces, material and vertex colors, and exported to its own uncompressed GLB. New terrain maintains its original open tile perimeter. Both mountain meshes remain closed. Selectively subdivided foot triangles avoid a few long faces bridging above water. Normals use Godot clockwise export convention.

## Scatter and geometry checks

All 500 saved indices remain: 206 unchanged, 104 vertically re-supported, 190 relocated onto genuinely dry support. Original rotation, scale and index are retained. Relocations use deterministic diverse interior dry candidates and >=12m spacing from recorded occupied positions; they are not projected into a line along the shore. `sculpt-report.json` lists every changed instance, reason, old/new world coordinates, and original support offset. Old and new support uses the highest actual triangle of both center tiles and all saved mountains, preventing false moves of trees on unchanged overlapping feet.

`geometry-verification.json`: 500 support probes, maximum absolute support residual ~0.00063m; no new degenerate/nonmanifold faces; both mountain meshes zero open edges; outer neighbor coordinates unchanged; shared edge maximum sampled height gap 0.000879m. The Godot builder separately checks actual saved collision faces and canonical preservation of all non-target state, then reloads from disk under a real renderer. Geometry evidence is not graphical acceptance.

## Runtime source

The existing `open_world.gd::_ready` reads each saved native tile's `first_mesh` into `chunks`, and `terrain_height` populates `terrain_samples` from that mesh's `get_faces()`. Replacing the actual native mesh updates this path; no procedural regeneration or shared-script mutation is required. The returned gameplay ground height is intentionally clamped to sea Y0; negative lakebed proof therefore comes from independent triangle/BVH probes, not a clamped gameplay height.

## Remaining gates

Parent must run real-renderer Game48 build/reload verifier and original1128/1129 plus neighboring mountain/side/back views. New basin does not complete small islands, mirror reflection, reference snow-mass layout, or total GOAL. No reference-view prop metadata is counted as instantiated artwork.
