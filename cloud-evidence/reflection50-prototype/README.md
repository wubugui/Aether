# Dynamic planar reflection feasibility, not Game50

This is an isolated primitive diagnostic project, not a replacement for any game screenshot or visual acceptance. Official Godot4.5.1 Compatibility/llvmpipe actual GUI runs. Same World3D shared by primary/reflected cameras; reflection is a live viewport texture on real Y0 water surface, with world-projective mapping. No reference-image textures used. Camera lateral and object movement update the reflected scene.

First normal prototype exited0. Adding a wholly submerged yellow box exposed a real error: reflection rendered submerged geometry as though above water (70610 yellow pixels). Its failed images/source remain evidence-underwater-failed/probe-underwater-failed.gd.

A reflected-camera-only clipping condition uses reserved camera layer bit19 and actual interpolated worldY<0 fragment discard. Main camera omits marker bit; reflected camera includes it. Water itself has separate layer excluded from reflection, avoiding recursion. This removes the submerged box while retaining elevated blue box, grounded geometry and their live reflections.

Final same-shader clip_enabled off/on control exited0 with no ERROR (knownVSync warning only). Yellow pixels70610→0, differences71742pixels confined rectangle[56,367,429,580]; top300 rows unchanged exactly0pixels. Actual lateral and moving-object frames were viewed. Earlier standard-to-custom-material comparison had41970 top300pixel differences, so it was NOT used as a preservation control; retained in evidence-clipped/pixel-checks.json.

Remaining integration work: reserve/crosscheck available layers in real world; apply clipping only to actual relevant material copies while preserving every original shader/material semantic and editable source; handle terrain/rock surfaces straddling water, particle and dynamic geometry, depth/sky/time synchronization, geographic lake calm response, performance and actual full-scene save/reopen. Do not change another candidate during49 builds. No Game50 exists and no lake reflection is accepted from this primitive test.

API grounding: https://docs.godotengine.org/en/4.5/classes/class_viewport.html and https://docs.godotengine.org/en/4.5/classes/class_camera3d.html ; camera visibility built-in https://docs.godotengine.org/zh-cn/4.5/tutorials/shaders/shader_reference/spatial_shader.html
