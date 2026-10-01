# Cirque54 temporary-world material lifecycle probe

The original four-image54v1 run `cloud-evidence/cirque54-world-diagnostic-20261001T074721Z-neKnZe` returned process0 but logged four GLES3 errors:material_casts_shadows,material_is_animated,material_get_instance_shader_parameters,andmaterial_update_dependency received a null material. The original run remains failed as a clean execution; its four saved images remain valid observations of the separately rejected source shape.

The instrumented one-view v2 run `cloud-evidence/cirque54-material-phase-v2-20261001T082913Z-iogn_bj3` completed child0/**wrapper1**. All11material binding checks passed, onePNG saved, and frozen inputs/preservation checks passed. All four errors occurred in stderr's `cleanup.before_queue_free` phase at approximately59.49s. No errors occurred during construction, first draw, PNG capture or the final binding checks. Thus an initialization-only explanation is unsupported.

The v2 stderr markers place the error after its full-world and label queue_free call, before the8-frame cleanup completes. They do not by themselves identify the exact engine object or prove which resource destruction ordering is responsible.

## Minimal cleanup-only v3 comparison

Ready to run in the parent-scheduled graphical terminal:

```sh
python source-assets/lake-cirque54/world-diagnostic-v3/run_material_phase_probe.py
```

GDScript check-only and Python compilation passed. The source54v1 payload, single1128front capture, constructor ordering, inherited material, default empty mesh-surface material and instance override are unchanged from v2. It does not repeat the four-image shape review.

Only cleanup changes:queue_free the eight temporary visual meshes while the original world and material remain alive; wait3processframes plusframe_post_draw; verify all eight nodes are gone; then release the original world and label in the original order and wait8frames. Separate stderr phases distinguish temporary-mesh retirement from full-world retirement.

This is an unrun control until its actual result is recorded. It does not claim the null-material issue is fixed, and it does not establish the empty-surface-material hypothesis as the cause. If it still fails, use the recorded phase to choose the next minimal control.

The wrapper saves immutable inputSHA, source snapshot, raw stdout/stderr, ordered received events, phase timeline, onePNG, preservation/binding report, actual child exit and strict wrapper exit. Any ERROR/SCRIPTERROR/leak, unexpectedwarning, incomplete report, missing cleanup phase or changed frozen input makes the wrapper fail even if Godot returns0. Only the already-known unsupportedVSync warning is accepted and retained.
