# First actual Game51 reflection smoke: diagnostic only

2026-10-01 01:39 UTC. Exit0, six real PNGs, official Godot4.5.1 Compatibility/Mesa llvmpipe. Saved51 SHA53e07e91b1bfafd0160749c5d90022d73029287cd36c51d54683339451a75408. No scene saved/modified by this test. Controller flags were enabled at runtime for the on images; saved51 still defaults OFF. Game50 remains the most recent candidate with completed bounded verification.

Developer inspected both on frames,1128off and raw reflection viewport. The lake now contains actual reflected mountains, islands, clouds and airship rendered from the same World3D. This is not a background image or duplicated world. The raw offscreen view has clipping at realY0, preventing the below-water opaque roots from obscuring reflected objects.

Visible defect: a blue strip at screen left/right/bottom comes from the reflection UV-edge feather blending back into the old water shader. This camera-framed border is rejected. Plan an independently saved revision with a slightly wider reflection projection and matching projective sampling, preserving this failed first appearance. No change to51 external assets in place. Texture mapping, dynamic camera/object behavior, material main-pass and full scene preservation still require the detailed verifier.

Separate-run50-enabled versus51-off comparisons show24changedpixels for1128 and544for1129. They are diagnostic only because initialization/timing differs; no zero-difference claim. Strict same-run original/new/clip-only/restored tests are pending. Clear mirror appearance does not fix the oversized rock-like clouds, simplistic mountains, small/distant frontal airship composition, shore geometry, weather or remaining references. HardwareGPU/visual/total acceptance allfalse.
