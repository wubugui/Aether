# 52g front: resource-rebind diagnostic, prepared only

Parent entry (GUI has not been run):

    python /workspace/scratch/a29d03198654/Aether/source-assets/cloud-sea52g/runtime-cache-diagnostic/run52g_cache.py front

Parse entry: same command with `parse`. Final preparation parse completed 0 in `cloud-evidence/cloudsea52g-cache-diagnostic-parse-20261001T084622Z-mlwyy0dx` (0.55 seconds, no scene instantiation).

## Why this probe

The preserved failure `cloudsea52g-d-ab-front-20261001T083354Z-3wbcs8h5` completed all three capture/state functions and restored all 11,423 audited nodes exactly. A/A2 differ at only three pixels: (436,452), (435,453), (434,458), with seven changed RGB channels, maximum 3/255, total absolute channel difference 11. At all three coordinates B equals A2. All other 782,853 pixels and every alpha value match exactly. That remains a strict pixel failure. The final generic “all3 complete” failure cascades from the pixel check; the recorded function-return and restoration proofs are complete.

Source triangle rays at each pixel center and four illustrative subpixel positions identify the unchanged `CloudSea_0_1/CloudSea52f_v0_low_drift`, triangles 520/2147, around 983–993m from the camera. Its next ray intersection is over 120m behind, so the current evidence does not support ordinary near-coplanar overlapping front surfaces. These are source-geometry ray diagnostics, not a GPU fragment or shadow-map readback. The four extra subpixel positions are a sensitivity check; the actual driver MSAA sample pattern was not queried. The original run did not capture shadow depth or repeated unchanged frames. A shadow/cache explanation remains a hypothesis.

Godot 4.5.1 `MeshInstance3D::set_mesh` calls `set_base`, which frees and recreates the internal renderer geometry instance. The game-node/resource snapshot does not capture that internal renderer history. This is a concrete mechanism worth isolating:
- https://github.com/godotengine/godot/blob/4.5.1-stable/scene/3d/mesh_instance_3d.cpp#L104-L128
- https://github.com/godotengine/godot/blob/4.5.1-stable/servers/rendering/renderer_scene_cull.cpp#L522-L545
- https://github.com/godotengine/godot/blob/4.5.1-stable/servers/rendering/renderer_scene_cull.cpp#L651-L674

## Single variable and four captures

1. Instantiate fixed Game52f once; prepare/freeze the same front camera, world time, weather, Sun, materials and reflection as the failed run. Build byte-equivalent mesh clones before the baseline. Do not load D geometry.
2. Capture A0 then A1 with no mutation. Keep one complete typed baseline plus exact phase differences.
3. For the same contracted ten original main nodes, bind an exact clone and immediately bind the retained original mesh. No await or capture occurs between these two assignments. Geometry arrays, material resource identities, transforms, flags and all other world state remain exact. No component setter is called by the restoration proof.
4. Capture R0 then R1. Compare the entire native state and viewport configuration unmasked to A0; verify all ten original identities and all six native components.

This tests renderer re-registration with identical geometry. It deliberately does not toggle shadows, modify light strength, disable antialiasing, reload the world, or load the rejected D shape. Those would introduce another variable.

Interpretation:
- A0 != A1: baseline already drifts without rebind, so the original 3-pixel discrepancy cannot be assigned solely to the mesh change.
- A0 == A1, R0 == R1, A0 != R0: supports a persistent renderer-side effect of the exact-resource rebind. Repetition of the original three coordinates strengthens linkage but does not prove a particular shadow implementation bug.
- R0 != R1: renderer does not settle after the current fixed wait; preserve the full difference rather than taking a later favorable frame.
- All equal: the rebind-only control did not reproduce it; changed bounds/geometry or a rarer effect remain possible.

Process exit 0 means diagnostic execution, exact state, file integrity and completeness only. Pixel equalities are recorded separately, and all visual/pixel acceptance and shadow-root-cause claims remain false. The probe is not an approval of 52g D.

## Requested versus actual size

The original failure's three PNG hashes all match their capture records. The old wrapper's combined dimensions/hash message was caused by size only. Requested window 1180×664 with fixed project content 1672×941 produces floor(664×1672/941) = 1179, so the actual texture is 1179×664. The camera projection's aspect is 1.776833198, agreeing with 1672/941 = 1.776833156.

Godot's fixed-aspect canvas-items path floors screen size and uses it as the actual render size: https://github.com/godotengine/godot/blob/4.5.1-stable/scene/main/window.cpp#L1148-L1213

This new diagnostic separately verifies requested size, fixed content size/mode/aspect/factor, actual texture size, native viewport/camera rect and projection, expected arithmetic, PNG signature, PNG dimensions and hash. It does not generalize the contract to arbitrary dimensions or change the old failed gate.

## Evidence protection

Original failure, scripts, source GLBs, Game52f and project settings are untouched. The wrapper freezes helper/script/binary/source hashes, retains stdout/stderr and true exit status, samples memory, rejects native/script errors and missing proofs, and uses the shared stage lock. The current diagnostic was only parsed; no GUI or full world was run during preparation.
