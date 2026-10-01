# Strict restoration v2, with preserved first failure

The first renderer run remains untouched:
`cloud-evidence/near-ship53west-renderer-20261001T071537Z-npkdb41t/`.
It exited1 after1128 A/B (four PNGs), before A2 or1129. Source hashes stayed
unchanged. Its restoration checks unfortunately stored `details: null`; no
complete A/restored state was persisted. Therefore the old JSON cannot uniquely
identify every changed field or prove there were no additional differences.

## Isolated numerical diagnosis

`diagnose_transform_roundtrip.gd` uses only three nodes in headless Godot. It
loads no game scene, assets or rendered viewport. The valid run is
`diagnose-transform-roundtrip-v3.log` with its accompanying metadata file.

With yaw1.6, the original cached scale is exactly `(1,1,1)`. Setting a different
global transform and then writing the original matrix back preserves every
global/local matrix byte, but reading scale yields
`(0.999999940395355,1,0.999999940395355)`. This fails the v1 exact scale check.
Restoring the original position/rotation/scale components instead reproduced
the original global matrix, local matrix, rotation and scale exactly.

This proves a numerical mechanism sufficient to trigger the old check, and
matches the failed code path. Because v1 omitted state snapshots, it is not a
retrospective proof that this was the only difference in that actual run.

The first probe lacked external writable userdata and aborted; its log remains.
The second probe inspected nodes before entering the tree and is invalid; its
errors and metadata also remain. Only v3, with deferred execution, external
userdata, exit0 and empty stderr, supports the numerical conclusion.

## Independent v2 changes

The original harness and wrapper are preserved. V2 lives at:

- `project/tools/observe_near_ship53west_v2.gd`
- `source-assets/near-ship53west/run_near_ship53west_v2.py`

B is now set through local position/yaw components while retaining the original
scale cache. Restoration sets the exact original local position, rotation
order, rotation and scale. The original global/local matrix, exact scale,
camera/FOV, full state digest, collisions and A/A2 main/reflection pixel gates
remain strict. New component checks and recursive exact-value differences add
protection; no tolerance or protected-state exclusion was introduced.

V2 saves full A/B/restored snapshots under `images/states/`, both readable JSON
and exact Variant binary. Transforms/vectors include full numeric components
and exact bytes. Every restore reports individual component equality, expected
and actual state/collision digests, and all field differences with node paths.
The original snapshot is deeply copied so later dictionary mutation cannot
silently alter the expected values.

## Known composition problem remains

Both first-run B images were inspected. The main image shows a nearer side
view, but almost the entire ship falls beyond the raw reflection texture's top
edge and its complete water reflection is missing from the main image. V2
records this unresolved result and adds projection bounds for the real ship
in the raw reflection and its virtual mirror in the main camera. A small main
image target error is not reference acceptance.

No camera, FOV, geometry, ship scale, original preset or saved scene is changed
by this revision. A later separate C study may consider camera height/pitch
and ship pose together; it is outside v2's scope. A v2 mechanical comparison
pass would only establish clearance, actual A/B image changes and exact A2
restoration, with reference/GOAL acceptance still false.

## Parent execution

```sh
python /workspace/scratch/a29d03198654/Aether/source-assets/near-ship53west/run_near_ship53west_v2.py --run-renderer
```

Default remains parse-only. This worker did not rerun the renderer. Final pure
parse evidence is
`cloud-evidence/near-ship53west-v2-parse-20261001T072442Z-z8q5njoo/`:
official Godot4.5.1 `--headless --check-only`, exit0, empty stderr,
maxRSS96,428KiB, and unchanged tracked source hashes. Actual scene restoration
must still be established by the parent's next renderer run.
