# Northwest ridge62: saved-native intake preparation

Status: source preparation only, 2026-10-02. No Godot, Blender, world, render, asset generation or native collection has been run for this item. Python AST/source guards do not mean the GDScript parses. No terrain, house, scatter, material, camera, protected source or default entry is edited.

## Exact scope and next small item

The design envelope is world X[-3048,-2040], Z[-5160,-3770]. The entity query includes a 40 m XZ buffer: X[-3088,-2000], Z[-5200,-3730]. These are an intake envelope and protection buffer, not an approved edit footprint. Current `Game61Coast.tscn` is the authority, including all effective inherited overrides and nested PackedScene contents. The collector uses only read-only SceneState APIs; it does not instantiate nodes, invoke `_ready`, enter the world or save resources. [Godot 4.5 SceneState API](https://docs.godotengine.org/en/4.5/classes/class_scenestate.html) documents this access and the base-scene/instance methods.

The six target tiles are X indices -4/-3 by Z indices -7/-6/-5. Their one-edge neighbor ring yields 16 total tiles. Ground_-4_-4 (56) and Ground_-5_-5 (61) are whole-tile protected neighbors, not mountain-edit candidates. The lake/opening massifs and `blender/cliff_kit/cliff_eastern_plateau.blend` remain frozen.

The previous nonterrain survey stopped at Z=-5000. Its 940 object bounds cannot prove occupancy in the newly included northern strip. `native-coast.json` is reused only for prior indexed terrain positions, by its byte SHA and unchanged53d source. At native collection time each tile also requires exactly the same mesh resource binding and full composed transform in current61 and pinned53d. Any target mismatch fails closed.56/61 changed neighbors cannot use their old position records. Their boundaries are read from the current resource instead.

## Files

- `plan.json`: exact entry/old-source/position-data identities, boxes, six targets and 16 tile identities, frozen cameras, explicitly hypothetical peaks
- `reused-boundary-index.json`: compact position-only borders extracted from the existing SHA-bound survey; not new native evidence and not full GPU attributes. Each record is usable only when that tile's native collection permits reuse
- `collect_saved62.gd`: effective saved scene inventory, whole-object bounds, bounded terrain/border and collision summaries, unresolved-runtime disclosure
- `run_intake62.py`: safe default source checks; explicit future native parsing or collection; CPU2/60-second child boundary, source snapshots, input hashes, raw logs and terminal report
- `PREPARATION_CHECK.json`: result of the performed Python-only checks, when present

The previous survey contains position data for14 of the16 tiles; the two northern neighbors Ground_-4_-8 and Ground_-3_-8 are absent. Only their borders, plus any changed/protected-neighbor borders, are newly exported. There is no second whole-world or six-tile face-array dump. Terrain collision reports contain only identity, AABB, face count and native face hash, not all collision points.

## What collection will and will not establish

Saved mesh and supported collision bounds are composed through the effective saved transforms. All parts are joined into a conservative whole entity before intersecting the buffered query box. The output contains every saved World/Settlements identity and its complete part list, not an assumed set of12 roots. This small catalog allows the northern-house claim to be checked without taking the nearest12 or excluding a house whose root lies outside the box. The expected12 is an unverified historical note; exact membership stays false until independently reconciled.

Entity grouping uses settlement/landmark roots, prefab roots and `Model` parent boundaries. A fallback grouping can conservatively combine several pieces; its recorded root and parts must be reviewed before interpreting it as one object. Bounds include hidden visual meshes and disabled collision shapes for conservative protection. They are bounds of saved geometry, not detailed foundations, shader displacement, skeleton deformation, traversal or silhouette acceptance. Unknown shape kinds, placeholders, missing ancestors/tiles and unsupported transform forms are explicit issues, never silently cleared.

Even a saved settlement root with only a script, MultiMesh or no supported bounded geometry is retained as an explicitly unbounded identity and an issue. The16 expected tiles each require exactly one native mesh and one collision record. New boundaries require nonzero triangles, unscaled axis-aligned transforms, at least2 points on every side and exact full-side spans. Pure Node parents stop3D transform inheritance according to native semantics; unrelated2D HUD transforms are not interpreted as3D.

The collector does not read headless MultiMesh buffers or AABBs. Every such saved group is listed as unresolved with its effective resource path. Before any terrain change, its authoritative saved buffers must be decoded using the existing audited native-binary approach or read in a real renderer, then filtered by actual world positions and full object footprints. Group names are not spatial proof. The previous1785/567 root counts remain survey pools, not approved edits.

Scripts are inventoried by identity/SHA. The collector does not instantiate scene nodes or call their lifecycle callbacks. Loading dependencies can nevertheless execute static initializers or scripted Resource construction; that full dependency behavior has not been certified, and the report explicitly sets `dependency_load_time_initializers_excluded:false`. A limited read of the19 GDScripts pinned by the previous input manifest found no static-variable/static-constructor or direct Resource/Mesh/Shape/Material subclass declaration, but this is not a complete loading-callback proof. Review any unresolved dependency concern before running collection. Runtime-generated nodes, road width/generated surfaces, weather-dependent geometry, scatter collision caches and true live-world house presence remain unproved. `all_occupancy_complete`, `runtime_generated_entities_proved` and visual acceptance stay false even when the saved-data collection exits0. Roads are reported with their complete transformed Bezier control hull; this is conservative for the centerline only and not road width.

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

Each future engine child is pinned to the first2 CPUs available to the wrapper and killed at the60-second elapsed boundary. The runner uses official4.5.1's pinned binary, headless SceneState access, Dummy audio and separate absolute XDG directories outside the project. It does not start the project main scene. A new unique `cloud-evidence/north-ridge62-...` directory holds source snapshots, the1477 prior input identities plus new inputs, raw stdout/stderr, process RSS/duration/exit/signal/timeout and a terminal wrapper result. Startup exceptions and external cancellation also write terminal evidence. Original inputs are checked after the child; changes and engine/log errors fail the run. A zero parser exit cannot stand in for a collection result.

The current project has no autoloads. Preparation fails if the autoload section is nonempty or an override.cfg appears, because custom SceneTree execution would otherwise still start autoload nodes. Cancellation signals are blocked across Popen until the child PID is owned, then forwarded to its process group and reaped. The actual terminal elapsed time over60 seconds is a failure even if the child happens to exit0. Safety checks use explicit exceptions and remain active under Python optimization. These are source-level safeguards; their future engine behavior has not yet been exercised.

No Git, publication or CLOUD_RESUME update belongs to this preparation worker.
