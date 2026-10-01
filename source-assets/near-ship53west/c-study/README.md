# Independent C study: main ship and complete water reflection

Prepared without a renderer run. The successful v2 harness, wrapper, original
A/B/A2 evidence and all source/world/preset files remain unchanged. The new
entry script inherits frozen v2 at its pinned SHA and adds C-only behavior.

## Measurements and CPU precheck

The original1128/1129 references were visually inspected for both the complete
real ship and its water reflection. Approximate reflection bounds are
1128 `(918,563)–(1262,790)` and1129 `(896,563)–(1252,794)` in1672×941 images.
The reflected centers are approximately `(65.19%,71.89%)` and
`(64.23%,72.10%)`. These hand measurements allow±8px for soft water edges;
they are not segmentation truth or a pixel-exact target. Both main/reflection
bounds, source hashes and uncertainty are in
`reference-main-and-mirror-measurements.json`.

`prepare_c_math.py` ran entirely on CPU using the successful v2's conservative
whole-ship bounds, including the full propeller revolution. It never loaded a
Godot scene. Each reference evaluated65,637 combinations over cameraY1–6m,
pitch−4°…+2°, horizontal ship distance32.5–65m and a padded ship bottom at least
.5m above water. CameraXZ/FOV, model scale and original1.08 optical overscan
were fixed. All candidates had to keep the complete conservative main,
virtual-mirror and raw-reflection projections inside the frame with2.5% margin.

Initial bounded best seeds:

|Reference|CameraY|Pitch|Horizontal distance|Ship originY|Main width/height residual|Mirror width/height residual|
|---|---:|---:|---:|---:|---|---|
|1128|1.5m|+2°|55m|6.887m|−15.8% /+15.4%|−14.9% /+19.4%|
|1129|4m|+2°|53.75m|5.387m|−20.1% /+3.2%|−19.4% /+17.3%|

These use a conservative box, not exact vertex silhouettes or live physics.
Pitch+2° is at the initial upper search boundary, so this is not a global
optimum. `c-math-proposals.json` records48 ranked seeds per reference. The
renderer tool reevaluates and locally refines them with the actual geometry;
its bounded pitch range extends to+3°. It always reports remaining main and
mirror center/width/height residuals. No low fitting score means visual success.

## Actual C run behavior

One unchanged saved Game53dWest scene, SHA
`6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18`.
For each reference, the sequence is original A → independent C → exact A2.

- C may change only camera height/pitch and the same ship's position/yaw;
  the reflected camera follows mathematically
- Original cameraXZ, FOV, optics, actual main/reflection texture dimensions,
  ship scale, environment, meshes, materials and presets remain protected
- A temporary convex support-point set accelerates search without being added
  to the scene or replacing geometry/colliders. Every selected candidate is
  reevaluated using all25,669 original visible mesh vertices
- Main ship, virtual ship mirror in the main view and actual ship in the raw
  reflection must all fit. The actual placed transforms are checked again
- Both original body shapes and the padded whole-visible envelope, including
  the full rotating propeller, keep actual overlap/downward-support/clearance
  checks at A, C and A2
- The C camera must clear native solids as a near-sized sphere. Eight real-ship
  envelope sightlines and25 actual first-hit rays across the conservative water
  footprint test occlusion and require the water surface to be the first hit
- Remaining shape/size/position errors are written as actual C residuals.
  PNG review is still needed; sampled physics rays are not a per-pixel visibility
  proof, and matching reference geometry/materials is not claimed

Output is six main plus six raw-reflection PNGs, complete state JSON/binary
snapshots, exact restoration diagnostics and atomic `images/near-ship-report.json`.
The distinct `limited_C_visibility_restore_physics_passed` gate requires both
references. Final reference and GOAL acceptance remain false. The old failed B
reflection and model proportion mismatch remain documented, not overwritten.

## Strict restoration and lightweight tests

The original camera comes from `look_at`. A small headless probe showed that
matrix-only restoration changes its derived rotation/scale caches even when
matrix bytes match. C therefore repeats the original position/scale/`look_at`
operation using the exact source target. The successful CPU probe
`check-camera-and-hull-cpu-v3.log` verified both cameras' local/global matrices,
position, rotation and scale exactly. The same probe verified the temporary
convex support API (27 cube points reduce to8 support vertices). No game scene
or renderer was loaded. Earlier probe failures remain as logs.

Ship restoration keeps the already proven v2 component path. All full-state
and exact A/A2 main/reflection pixel gates remain; only C comparison snapshots
exclude its three explicitly allowed transforms. They still protect every
other field. No tolerance, crop, model scaling or reflection-size expansion
was added.

Final full C script parse:
`cloud-evidence/camera-ship53west-c-parse-20261001T074949Z-yiwfjwjj/`:
official Godot4.5.1 `--headless --check-only`, exit0, empty stderr,
maxRSS100,536KiB, tracked input hashes unchanged. Runtime remains untested here.

## Parent's serial renderer entry

```sh
python /workspace/scratch/a29d03198654/Aether/source-assets/near-ship53west/c-study/run_camera_ship53west_c.py --run-renderer
```

Without `--run-renderer`, it only parses. The wrapper retains unique evidence,
isolated external userdata, source snapshots, child maxRSS, exit signals and
partial reports. Do not infer full-flight, hardware-GPU or final-reference
acceptance from a successful C comparison.
