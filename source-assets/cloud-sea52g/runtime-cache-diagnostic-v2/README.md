# Exact-resource cache diagnostic v2 — prepared, not rendered

Parent entry:

    python /workspace/scratch/a29d03198654/Aether/source-assets/cloud-sea52g/runtime-cache-diagnostic-v2/run52g_cache.py front

The sole revision fixes which native API supplies the actual captured image dimensions. Geometry, material, lighting, camera, four-image sequence, all-world state scope, resource restoration and pixel comparison requirements are unchanged. The original runtime-d-ab strict pixel gate is untouched. No GUI or complete world was run during this preparation.

## Precisely diagnosed v1 failure

Preserved evidence: `cloud-evidence/cloudsea52g-cache-diagnostic-front-20261001T085521Z-7t1wqghy`.

Only A0 exists; the resource-rebind intervention never began. `native_full_exact=true`, `viewport_exact=true`, stored/runtime differences both empty for all 11,423 audited nodes. The sole failed subcondition was dimensions. The captured Image and physical PNG are 1179×664, but `ViewportTexture.get_width()/get_height()` reported 831×468. The requested Window is still 1180×664, content scale is 1672×941, canvas-items/keep, factor1, and camera projection is unchanged.

This is explained directly by Godot 4.5.1 source: for Window viewports, ViewportTexture.get_width/height multiplies the internal viewport size by the Window stretch scale. The same class's get_image reads the actual RenderingServer texture. With recorded stretch values, int(1179×1179/1672)=831 and int(664×664/941)=468. It is not evidence of a changed render target or a second image resize.

Official source: https://github.com/godotengine/godot/blob/4.5.1-stable/scene/main/viewport.cpp#L124-L172

V2 names these quantities separately. Actual dimensions come from the native Image already read during the frame-post-draw capture. The external wrapper independently checks the physical PNG IHDR and SHA. ViewportTexture metadata is preserved and additionally required to match the exact engine formula and 831×468. Requested 1180×664, fixed project 1672×941, native viewport/camera state, projection aspect and actual1179×664 remain strict requirements. Each subcondition now has a separate check label.

## The one-variable experiment

A0/A1 are two unmodified original52f frames. Then only the contracted ten original main mesh resources are rebound to byte-equivalent original-geometry clones and immediately restored to the retained originals, with no await or image between assignments. R0/R1 follow. No D geometry is loaded, no light/shadow toggle occurs, and no component setter is called by the restoration proof.

Every phase compares the entire typed native state and viewport configuration exactly. Only one full baseline is written; phase outputs contain digests and precise differences. Four actual PNG files are required. Pixel comparisons remain full-RGBA exact comparisons and are reported separately; process0 indicates complete diagnostic execution and invariant checks, never a visual/pixel acceptance or proven shadow root cause. The original rejected D world trial remains failed.

Interpretation is unchanged from v1: first distinguish preexisting A0/A1 drift, then a stable change after rebind, then R0/R1 settling. A repeat of the old three pixels would support renderer re-registration as a cause class, not prove a specific shadow bug.

Parse-only passed0 in `cloud-evidence/cloudsea52g-cache-diagnostic-v2-parse-20261001T090108Z-5m541w72`; this did not instantiate the scene.
