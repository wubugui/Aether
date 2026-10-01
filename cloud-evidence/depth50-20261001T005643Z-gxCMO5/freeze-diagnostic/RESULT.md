# Verifier freeze regression, independently reproduced

This test creates one BoxShape3D and StaticBody3D in a new empty world. It loads no game scene or asset and saves no scene/MM resource.

Official Godot4.5.1 headless physics results:
- Active body: ray hits
- Parent `PROCESS_MODE_DISABLED`: ray no longer hits, because CollisionObject disable_mode is REMOVE
- Restored process mode with script process/physics callbacks disabled: ray hits again

Consequently all motion and camera_clear claims made after the first depth50 verifier's recursive process_mode disable are invalid physical evidence. Image A/B/A comparisons remain isolated render observations, not proof of live collision correctness. The first verifier also called global_shader_parameter_get in runtime, triggering renderer performance ERROR logs. Both issues require a new verifier-only run; Game50's successful saved-state/build evidence and files are not rewritten.

Actual stdout, stderr and exit code are retained here. The scene controller and water-depth implementation are not implicated by this dummy-world test.
