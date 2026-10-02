# Northwest ridge62: saved-native intake preparation

Status: dependency-guard v2 source preparation only, 2026-10-02. No Godot, Blender, world, render, asset generation or native collection has been run for this item. Python AST/source guards do not mean the GDScript parses. No terrain, house, scatter, material, camera, protected source or default entry is edited.

## Exact scope and next small item

The design envelope is world X[-3048,-2040], Z[-5160,-3770]. The entity query includes a 40 m XZ buffer: X[-3088,-2000], Z[-5200,-3730]. These are an intake envelope and protection buffer, not an approved edit footprint. Current `Game61Coast.tscn` is the authority, including all effective inherited overrides and nested PackedScene contents. The collector uses only read-only SceneState APIs; it does not instantiate nodes, invoke `_ready`, enter the world or save resources. [Godot 4.5 SceneState API](https://docs.godotengine.org/en/4.5/classes/class_scenestate.html) documents this access and the base-scene/instance methods.

The six target tiles are X indices -4/-3 by Z indices -7/-6/-5. Their one-edge neighbor ring yields 16 total tiles. Ground_-4_-4 (56) and Ground_-5_-5 (61) are whole-tile protected neighbors, not mountain-edit candidates. The lake/opening massifs and `blender/cliff_kit/cliff_eastern_plateau.blend` remain frozen.

The previous nonterrain survey stopped at Z=-5000. Its 940 object bounds cannot prove occupancy in the newly included northern strip. `native-coast.json` is reused only for prior indexed terrain positions, by its byte SHA and unchanged53d source. At native collection time each tile also requires exactly the same mesh resource binding and full composed transform in current61 and pinned53d. Any target mismatch fails closed.56/61 changed neighbors cannot use their old position records. Their boundaries are read from the current resource instead.

## Files

- `plan.json`: exact entry/old-source/position-data identities, boxes, six targets and 16 tile identities, frozen cameras, explicitly hypothetical peaks
- `reused-boundary-index.json`: compact position-only borders extracted from the existing SHA-bound survey; not new native evidence and not full GPU attributes. Each record is usable only when that tile's native collection permits reuse
- `collect_saved62.gd`: effective saved scene inventory, whole-object bounds, bounded terrain/border and collision summaries, unresolved-runtime disclosure
- `run_intake62.py`: safe default source checks; explicit future native parsing or collection; CPU2/60-second child boundary, source snapshots, input hashes, raw logs and terminal report
- `dependency_guard62.py`: pinned full-closure, startup/cache and absence checks; standard-library only
- `audit-tools/`: actual byte-identical Python auditors embedded in the frozen dependency review, with replay limitations
- `dependency-guard-v2/`: new normal/optimized Python-only fixtures and results; includes simulated runner terminal paths
- `PREPARATION_CHECK.json`: original preparation result, preserved unchanged; it does not describe this v2 runner

The previous survey contains position data for14 of the16 tiles; the two northern neighbors Ground_-4_-8 and Ground_-3_-8 are absent. Only their borders, plus any changed/protected-neighbor borders, are newly exported. There is no second whole-world or six-tile face-array dump. Terrain collision reports contain only identity, AABB, face count and native face hash, not all collision points.

## What collection will and will not establish

Saved mesh and supported collision bounds are composed through the effective saved transforms. All parts are joined into a conservative whole entity before intersecting the buffered query box. The output contains every saved World/Settlements identity and its complete part list, not an assumed set of12 roots. This small catalog allows the northern-house claim to be checked without taking the nearest12 or excluding a house whose root lies outside the box. The expected12 is an unverified historical note; exact membership stays false until independently reconciled.

Entity grouping uses settlement/landmark roots, prefab roots and `Model` parent boundaries. A fallback grouping can conservatively combine several pieces; its recorded root and parts must be reviewed before interpreting it as one object. Bounds include hidden visual meshes and disabled collision shapes for conservative protection. They are bounds of saved geometry, not detailed foundations, shader displacement, skeleton deformation, traversal or silhouette acceptance. Unknown shape kinds, placeholders, missing ancestors/tiles and unsupported transform forms are explicit issues, never silently cleared.

Even a saved settlement root with only a script, MultiMesh or no supported bounded geometry is retained as an explicitly unbounded identity and an issue. The16 expected tiles each require exactly one native mesh and one collision record. New boundaries require nonzero triangles, unscaled axis-aligned transforms, at least2 points on every side and exact full-side spans. Pure Node parents stop3D transform inheritance according to native semantics; unrelated2D HUD transforms are not interpreted as3D.

The collector does not read headless MultiMesh buffers or AABBs. Every such saved group is listed as unresolved with its effective resource path. Before any terrain change, its authoritative saved buffers must be decoded using the existing audited native-binary approach or read in a real renderer, then filtered by actual world positions and full object footprints. Group names are not spatial proof. The previous1785/567 root counts remain survey pools, not approved edits.

Scripts are inventoried by identity/SHA. The collector does not instantiate scene nodes or call their lifecycle callbacks. Loading dependencies can nevertheless execute static initializers or scripted Resource construction. The frozen [dependency review](DEPENDENCY_REVIEW.md) closes the inspected current1483-file/2304-edge set, including23 GDScripts and1301 completely traversed native binary property streams. It identified no project-code loading trigger in those exact bytes. This remains bounded source/serialization evidence, not a general ResourceLoader safety claim or native execution test. The unmodified collector conservatively retains `dependency_load_time_initializers_excluded:false`; the wrapper records the separate identity guard rather than rewriting that historical claim. Runtime-generated nodes, road width/generated surfaces, weather-dependent geometry, scatter collision caches and true live-world house presence remain unproved. `all_occupancy_complete`, `runtime_generated_entities_proved` and visual acceptance stay false even when the saved-data collection exits0. Roads are reported with their complete transformed Bezier control hull; this is conservative for the centerline only and not road width.

## Fixed reference and design hypotheses

Both original world camera positions are(-2600,330,-2350), FOV55.1131 targets(-2969,156,-3263);1347 targets(-3033,174,-3238). Existing real evidence is1179x664 in `cloud-evidence/coast61-v2-verify-20261001T124815Z-czvc76_r/verify-report61.json`. No camera, weather or ship mutation occurs here.

Initial peak hypotheses are world(-2620,720,-4620),(-2830,650,-4880),(-2310,580,-4290). Heights are absolute worldY. No control mesh exists from this intake and no peak is approved by the screenshots. A later continuous single control surface must preserve shore/river/house/road guards, provide sufficiently wide shoulders and avoid per768m-tile falloff trenches. Build no mountain before reviewing the saved occupancy gap and agreeing the actual editable footprint.

## Commands from Aether

Current safe Python-only preparation check (no files, no engine):

```sh
python source-assets/north-ridge62-intake/run_intake62.py --static-only
```

Future explicit Godot GDScript check, after coordinating the active world window:

```sh
python source-assets/north-ridge62-intake/run_intake62.py --parse-only
```

Future explicit saved-native collection, only after the parse result is independently checked:

```sh
python source-assets/north-ridge62-intake/run_intake62.py --collect
```

Each future engine child is pinned to the first2 CPUs available to the wrapper and killed at the60-second elapsed boundary. The runner uses official4.5.1's pinned binary, headless SceneState access, Dummy audio and separate absolute XDG directories outside the project. It does not start the project main scene. A new unique `cloud-evidence/north-ridge62-...` directory holds source snapshots (including the pinned gzip review and packaged auditors), the unchanged1477 prior identities plus all1483 reviewed closure identities and startup controls, raw stdout/stderr, process RSS/duration/exit/signal/timeout and a terminal wrapper result. The original1477 manifest and `PREPARATION_CHECK.json` remain unchanged; the extra51 closure files are explicitly validated against the frozen review, never silently folded into an old historical claim. Startup exceptions and external cancellation also write terminal evidence. Original inputs are checked after the child; changes and engine/log errors fail the run. A zero parser exit cannot stand in for a collection result.

The current project has no autoloads. The v2 guard first verifies the exact91486-byte gzip SHA and decompressed730050-byte review SHA, then all1483 file lengths/hashes and the exact51-file difference from the pinned old manifest. Project settings, UID cache and the empty global class cache must retain their reviewed bytes. Override and extension-list files must stay absent, including empty files or dangling links. Every dependency must retain the absence of unreviewed `.remap` and `.import` sidecars; existing importer metadata and imported cache bytes are themselves pinned. No current cache or setting is adopted as a new approved baseline.

These checks run in static preparation, manifest creation, immediately before native launch and again in the terminal `finally` path after success, exception or cancellation. A new remap or cache/settings mismatch fails closed and clears native/parse success even when the child exited0. A post-run check cannot undo code already executed after a concurrent external edit: coordinate the project window and do not mutate its inputs during a native run. Preparation also explicitly rejects a nonempty autoload section, because custom SceneTree execution would otherwise still start autoload nodes. Cancellation signals are blocked across Popen until the child PID is owned, then forwarded to its process group and reaped. The actual terminal elapsed time over60 seconds is a failure even if the child happens to exit0. Safety checks use explicit exceptions and remain active under Python optimization. These are source-level safeguards; their future engine behavior has not yet been exercised.

The v2 fixture command is `PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/dependency-guard-v2/check_dependency_guard62.py`; repeat with `python -O`. Negative cases use independent temporary copies, never modify live project inputs, and mock the runner launch. Their simulated parse flow is not a Godot parse result.

No Git, publication or CLOUD_RESUME update belongs to this preparation worker.
