# Fixed-camera near-side ship study in saved Game53dWest

Preparation and pure parsing only. This worker has not started a renderer or
rerun the already successful Game51b12.229m player-input flight.

## What the original images show

Both original1672×941 reference images were opened and inspected, along with
the two1180×664 front renders from the completed53west v2 run.

Approximate complete real-ship silhouette measurements, including flag and
propeller but excluding the water reflection:

| View | Reference pixel bounds | Reference width / height | Reference center | Current front width |
|---|---|---|---|---|
|1128|(919,249)–(1261,470)|20.45% /23.49%|(65.19%,38.20%)|about2.54%|
|1129|(896,311)–(1250,555)|21.17% /25.93%|(64.17%,46.02%)|about3.56%|

These are approximate hand measurements with±5px uncertainty, not automatic
segmentation or pixel-perfect truth. The source images, hashes, bounds and
method are recorded in `reference-measurements.json`. The current narrow front
view corresponds to the unchanged original yaw1.6/1.7 at dist120/85.

A reasonable initial broadside estimate is1128 dist42/right14/up2/yaw0 and
1129 dist40/right13/up−2/yaw0.204. These are estimates, not tested placements.
The actual tool projects the current visible mesh vertices, keeps the nose
pointing screen-left, searches optical depths25–90m and balances relative
width/height errors before centering the ship. It translates that result back
into the existing `observe_reference` dist/right/up/yaw formula and reports it.
Different model proportions may prevent both reference dimensions matching
simultaneously. The tool preserves scale and reports the resulting dimensions.

## Parent-run commands

From `/workspace/scratch/a29d03198654/Aether`:

```sh
python source-assets/near-ship53west/run_near_ship53west.py --parse-only
python source-assets/near-ship53west/run_near_ship53west.py --run-renderer
```

Default mode is parse-only. The second command is for the parent's serial
renderer schedule. It opens one saved Game53dWest instance at SHA
`6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18` and uses
the exact completed202-check v2 audit; it never loads a second baseline scene.
The wrapper uses fresh external `tools-feiting` userdata/cache/config and
records `wait4` child maxRSS, signals, exit status, logs and source hashes.

## Controlled comparison

Each reference is entered through the existing `observe_reference` function.
Before A, callbacks are frozen without disabling collision bodies; weather is
placed at the prior verifier's .35 time and the shared shader time is fixed.
After A begins, only the same airship's position/yaw changes. Camera position,
rotation, FOV, scale, world meshes, materials, environment and presets remain
unchanged. Candidate projection and physics queries are hypothetical until B
is selected. No geometry is moved to make room.

For A and B, clearance checks use both original collision shapes plus an
independent full-visible-mesh AABB padded by .5m per mesh. The latter includes
the propeller's full local-X revolution. Actual world physics queries use the
body's layer1 mask and the combined1/4 mask5:

- Initial overlap must be empty
- Whole-shape downward casts must find a native solid within500m and retain at
  least .25m conservative clearance
- Five footprint rays report actual support/collider heights and distances
- Eight camera-to-envelope corner rays must be clear
- Camera distance to the conservative envelope must exceed2m and its near plane

The body is then placed once at B, actual scene transforms settle through a
physics frame, and the same checks repeat. A2 restores the complete original
ship transform. Flight/HUD state, body velocity, full local transforms, visibility, resource bindings,
MultiMesh buffers, environment stored properties, camera settings and collision
modes/layers/RIDs must equal A; only the parent ship transform is excluded when
checking B. Main and reflection A/A2 pixel hashes must match exactly, while B
must change both images. Failed restoration or clearance is reported as failure.

Expected output is six main PNGs plus six raw-reflection PNGs and atomic
`images/near-ship-report.json`, with explicit stages and complete/pass fields.
This is same-world pose/composition evidence, not a flown A-to-B route, a world
rebuild, saved-preset change or final reference/GOAL acceptance. Known1344 and
350m failures remain false. Original51b flight evidence remains separate.

Final preparation check:
`cloud-evidence/near-ship53west-parse-20261001T070605Z-g0vjwvjh/`
passed official Godot4.5.1 `--headless --check-only`, exit0, maxRSS95,340KiB,
empty stderr and unchanged tracked input hashes. No runtime acceptance is claimed.
