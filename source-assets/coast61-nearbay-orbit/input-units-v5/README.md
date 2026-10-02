# Native orbit input units v5

The fourth world run stopped correctly when a nominal 0.05-radian motion
arrived as -17.7268886566 viewport pixels rather than the intended -12.5.
Its immutable evidence is at
`cloud-evidence/nearbay61-orbit-renderer-20261002T040614Z-kyawbpny`.
That run did not record the live matrix; no exact matrix is reconstructed here.

Only the harness changes. `native_mouse61.gd` maps intended viewport-local
relative motion by the actual root Window final transform's basis and maps the
viewport center by the full transform. It rejects nonfinite/singular mappings.
The unchanged game still receives actual `Input.parse_input_event` followed by
`Input.flush_buffered_events`; its .004 sensitivity, 0.05-radian maximum step,
0.00001-radian acceptance bound, and every world/physics/visibility gate remain
unchanged. No direct game-orbit writes are added.

Each motion records the actual final matrix and bytes, viewport rectangle,
window/display-server dimensions, texture dimensions, content scale settings,
intended local motion/center, sent window motion/position, and native witness
receipt. Exactly one motion must arrive with the held right-button state,
intended local delta (0.00001-pixel bound), and center (0.001-pixel bound).
The matrix/dimension snapshot must be identical before dispatch, inside the
independent _input witness, and after dispatch. The existing angular assertion
then checks the unchanged game independently. Emergency button release remains
possible even when a bad mapping makes a new press or motion unsafe.

## Primary API evidence (Godot4.5.1)

- [Viewport::_make_input_local and get_final_transform](https://github.com/godotengine/godot/blob/4.5.1-stable/scene/main/viewport.cpp#L1326-L1338)
  applies the affine inverse of the final transform to events; the final
  transform is stretch_transform multiplied by global_canvas_transform
- [Window::_window_input](https://github.com/godotengine/godot/blob/4.5.1-stable/scene/main/window.cpp#L1699-L1718)
  forwards input to push_input with its default nonlocal coordinates
- [InputEventMouseMotion::xformed_by](https://github.com/godotengine/godot/blob/4.5.1-stable/core/input/input_event.cpp#L891-L912)
  uses full transform for position and basis-only transform for relative motion
- [Transform2D API](https://docs.godotengine.org/en/4.5/classes/class_transform2d.html#class-transform2d-method-basis-xform)
  distinguishes basis_xform from full multiplication; affine_inverse supports
  nonuniform transforms, unlike inverse/basis_xform_inv's orthonormal assumption

## Focused fixture and limits

Default wrapper invocation starts no engine. Parent-coordinated command:

```
python source-assets/coast61-nearbay-orbit/input-units-v5/run_fixture.py --run
```

The actual engine fixture tests xformed_by round trips for identity, uniform,
nonuniform translated, sheared translated and reflected matrices, invalid
mapping refusal, then actual parse/flush dispatch to a synthetic Node._input
with canvas_items scaling and with additional shear/translation. The same
shared audit helper rejects missing/duplicate events, old wrong-unit deltas,
changed before/after/witness transforms, and unheld-button receipt.

The wrapper uses the pinned Godot4.5.1 executable, CPU2 affinity, isolated XDG,
a 19-second hard watchdog, new evidence directory, full raw terminal logs,
complete before/after source and protected manifests, actual exit/RSS/time.
All four existing failed world directories are protected byte-for-byte.
This is a headless synthetic engine test, not a real display, production matrix,
camera path, world image, hardware GPU, or orbit-runtime acceptance.

Main parse uses the existing wrapper only after coordination:

```
python source-assets/coast61-nearbay-orbit/run_orbit61.py --parse-only --wall-timeout 20
```

Prepared tests are not a passing result. Actual run evidence is recorded in new
cloud-evidence directories, including any failures; never overwrite old runs.
