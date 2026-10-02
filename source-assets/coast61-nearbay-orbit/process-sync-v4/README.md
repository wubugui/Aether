# Orbit61 process-order / diagnostic v4 preparation

Source preparation only. This revision has not been parsed or run with Godot.

The preceding world run drained actual queued deletions, then established its baseline while resuming from the `process_frame` signal. Godot emits that signal before node `_process`, so the weather follower had not completed that frame. The failed Rain branch did not capture its previous/current state; it does not prove that both endpoints were hidden or identify the exact changed transform.

## Minimal implementation

After the existing deletion drain, the verifier records these separate actual stages:
1. Drain returns at the process-frame signal start
2. The late witness emits after ordinary game/weather processing
3. RenderingServer emits frame_post_draw, before the inventory is established

Each stage records process/physics counts, ticks, native pause state, queued identities, and Rain/Snow identity, own/tree/effective visibility, layer/camera masks, transform bytes/position, native AABB and effective query scope. The diagnostic AABB is explicitly not a visible-shader coverage proof. Ship/camera pause invariants and the15-second bound are checked after both waits; the queue must still be empty after post_draw. Nothing freezes, moves, or disables weather.

Inventory diagnostics permanently retain a full before snapshot and produce a full current snapshot for live nodes. Deletion explicitly marks current state unavailable. The existing visibility/transform rejection predicate is unchanged: there is no new exception permitting hidden-object movement. New-candidate and buffer-change failures also carry the available state rather than a path alone.

## Prepared checks

The synthetic fixture uses an actual Node._process follower and a late witness to distinguish signal start from process completion. It exercises a prematurely frozen hidden follower (still rejected), a correctly synchronized stationary baseline, camera rotation independence, hidden/visible transitions, hidden layer changes, visible transform changes, effective mask changes, queued and actual deletion, and completeness of before/current diagnostics. It does not claim production post_draw or world behavior.

Authorized CPU window only:

```
python source-assets/coast61-nearbay-orbit/process-sync-v4/run_fixture.py --run
python source-assets/coast61-nearbay-orbit/run_orbit61.py --parse-only --wall-timeout 30
```

The synthetic wrapper retains sources, original logs, actual exit/RSS/time, case results and integrity checks in a new evidence directory, with CPU2 affinity and a59-second watchdog. Default invocation does not start Godot. These checks do not replace the next real world run and its recorded weather states.
