# Actual Game48 lake-water intake (read-only)

The active saved Ocean uses embedded ShaderMaterial_ve4um / Shader_kirx7, not the project open_water.gdshader file. Its code is retained in actual-water-shader.txt. Editing open_water.gdshader alone would not change this saved candidate's actual material.

Actual shader provides piecewise-planar wind wave normals and day/night sky approximations. Moon reflection traces the authored sphere; registered nearby emissive surfaces have an80-slot response. This is not scene geometry reflection: no render-target sampler, reflected-scene camera or mountains/islands/airship reflection exists. Roughness tweaking cannot supply those missing images. Uniform global sea wind drives lake wave scale; any future calm-basin adjustment should be geographic in the shared water, not switch fake content on reference observation.

Godot4.5 primary API references for a candidate dynamic planar-reflection implementation:
- https://docs.godotengine.org/en/4.5/classes/class_viewport.html (shared World3D and SubViewport render targets)
- https://docs.godotengine.org/en/4.5/classes/class_camera3d.html (camera cull mask, FOV and projection configuration)

Potential next experiment, not implemented or accepted: a persistent secondary native camera rendering the same World3D into a SubViewport, mirrored across actual Ocean Y0 and sampled with world-projective coordinates only within the authored lake basin. Water excluded from reflection via an explicit layer to prevent recursion. Must test camera rotation/translation, moving object parallax, occlusion/near-shore underwater contamination, projection flip, aspect, sky and weather synchronization, view-layer preservation, no reference images, and save/reopen. Extra render pass cost and below-water clipping are unresolved. Do not claim a mirror-water fix from this plan.
