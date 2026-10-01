# Two-bit reflection guard preserves main shadows and clips reflected roots

2026-10-01 02:57UTC. Godot4.5.1 Compatibility/llvmpipe, exit0,7PNG. Kept existing Shader/Material RIDs, changed only the audited marker predicate at runtime, then restored every original shader byte and file hash.

At1343, the old clip toggle changes30pixels. The guarded clip-on and guarded clip-off images each exactly match the original clip-off image, with Sun shadows enabled. Restored original code/clip-off is also exact. This demonstrates the corrected branch removes the unintended main-shadow change without hiding shadows or changing material colors.

The two raw1128 reflection images show existing underwater roots/lakebed when clipping is off and their removal when clipping is on. Developer directly inspected both full-size raw images and the1343 guarded main image. Actual above-water mountains/islands/trees/ship remain in the same World3D. Dynamic objects crossing the water plane and arbitrary future streamed geometry are not tested here. No candidate was saved. The independent persistent51b still needs build/reload and full scene/reference/flight checks; all visual and hardwareGPU acceptance remainsfalse.
