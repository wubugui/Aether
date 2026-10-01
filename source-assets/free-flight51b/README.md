# Game51b actual player-input flight harness

Preparation completed 2026-10-01. **Runtime flight has not been run by this worker.**
The parent schedules the renderer after the existing heavy jobs finish.

## Entrypoints

From `/workspace/scratch/a29d03198654/Aether`:

```sh
python source-assets/free-flight51b/run_player_flight51b.py --parse-only
python source-assets/free-flight51b/run_player_flight51b.py --run-renderer
```

The default is parse-only. The renderer command uses the official Godot4.5.1
binary at `/workspace/scratch/a29d03198654/tools-feiting/`, GL compatibility,
Dummy audio, and one scene instance. It does not start an editor. No command
changes the default project scene or saves gameplay/scene assets.

The script is
`candidates/round40-exclusive-20260930/project/tools/verify_player_flight51b.gd`.
It is pinned to Game51b SHA
`b169f62527a52b9f2a3f091c2d7db136ad7cd67111e405f08f390eeb082e2bb1`.
It intentionally does not accept Game52e under the same evidence identity.

## Runtime behavior

1. Verify the pinned prior audit/intake/build reports and current gameplay,
   scene, reflection controller and128 independent asset hashes. Reuse the
   matching completed structural/reflection audit, without rerunning1500 checks.
2. Load the scene once with its ordinary `_ready`, HUD, audio initialization,
   player physics, world streaming, weather and camera callbacks intact.
   Check that boot is anchored/stationary and all test/observation flags are off.
3. Invoke existing `observe_reference("1128")`. Record before/after explicitly
   as a setup/navigation teleport. Force focus at the corridor midpoint and wait
   physics ticks. No transform is directly assigned by the harness.
4. Query both real collision shapes plus a conservative whole visible-mesh
   envelope against actual loaded physics solids. Each visible mesh AABB has
   .5m padding, and propeller mesh bounds include a complete revolution. Check
   initial overlap,25m cast and endpoint overlap for yaw0/±.20rad and elevation
   0/+3m; also call the body's non-moving `test_move` with both native shapes.
   Failed clearance freezes the instance and stops; there is no relocation.
5. Send F2 press/release via `Input.parse_input_event` with physical keycode.
   Verify native physical-key state, viewport input delivery and both existing
   observation flags clearing. Wait .25 simulation seconds for the existing
   follow camera and capture `01-start.png`.
6. W down for .75 simulation seconds, release for .50, then one Space
   press/release. All changes are scheduled by a witness node after each actual
   game physics tick. Capture `02-moving.png` at the next rendered frame after
   W release; the report records that image's actual time/position/velocity.
   Screenshot waits never extend the W hold or coast period.
7. Require actual displacement and acceleration, throttle retention, fuel
   consumption, camera following, zero slide collisions/damage, consistent
   displacement and velocity, zero unexpected yaw/lift and a .25s stable stop.
   Capture `03-stopped.png`, release all keys, verify sources, write final report
   and quit. No restoration teleport or port docking is included.

Every active physics tick checks the20m displacement/path cap and5s simulation
watchdog. Unexpected keys, disabled/paused callback, changed override flags,
collision/damage or displacement inconsistent with velocity trigger immediate
key release and `test_frozen=true`, explicitly a failure. Engine time_scale stays
1 throughout. Wrapper wall timeout is separate and defaults to1800s.

## Evidence and failure handling

Every invocation creates a unique `cloud-evidence/player-flight51b-*` directory
and fresh userdata/cache/config directories under the external `tools-feiting`
directory. The wrapper snapshots source inputs, records pre/post source hashes,
child PID, `wait4` maxRSS (KiB on Linux), exit code and terminating signal.
It retains stdout/stderr, failed runs and partial reports, including SIGKILL
failures. SIGKILL cannot run in-process cleanup; killing the isolated child
terminates its synthetic input state.

The harness atomically replaces `images/player-flight-report.json` at each
stage, beginning before scene load. `complete=false` is never a flight pass.
The wrapper only credits runtime success if the child exits0, sources remain
unchanged, and the complete runtime report explicitly passes.

Latest successful pure parse:
`cloud-evidence/player-flight51b-parse-20261001T053029Z-ky8p46w6/`
(exit0, no stderr, maxRSS98,380KiB, all tracked sources unchanged).
Initial rejected type parse remains in
`cloud-evidence/player-flight51b-parse-20261001T052758Z-psqfow47/`.

This result covers preparation and parsing only. A future successful scripted
physical-input run still cannot prove real GUI focus/keyboard handling,
hardware-GPU performance, full-route gameplay or the original GOAL. Known1344
two-pixel conversion and inherited350m-route failures remain explicit false
fields. Optional steering/lift are clearance-prechecked but not flown here.
