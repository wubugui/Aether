# North-ridge62 source-specific proxy bounds, preparation v1

This is a bounded saved-source preparation. No engine has been started for v1, no world has been instantiated, and no terrain, scene, asset, Git, progress-document or Slack changes are made by these tools.

## Ready now

The exact original completed native report is pinned to SHA256 `62482b889a2dc6c5687274748397f5d4bf9da3be6898b8fbca6d372a5a2452bf`; the classification is pinned to `24341762139c49ae788aff4417e65ebfe90591312e6cc1d890ce9bb57def4186`.

The offline replay streams the immutable original buffers in memory using the existing strict binary/text decoder and recorded full ancestor transforms. It covers all **775 saved groups / 57,797 instances**, including neighboring groups outside the original hit list, and exactly reproduces every original query bound and path/index membership: **676 visual-query / 575 design hits**. It writes no full-world transform/buffer duplicate.

`source-bounds-preparation.json` contains:

- A path/index-keyed provisional keep/reconcile list with full composed transform, existing visual bounds, source-rule tree envelope, protection tag and individual query/design predicates
- All 775 groups' checked instance counts, source/buffer identities and membership lists
- 471 conservative tree-envelope query hits and **zero tree-proxy-only additions** to the original visual list
- Resource-based whole-neighbor protection: 81 saved instances in coast61 `-5_-5`, and 243 in coast56 `-4_-4`. Two coast61 entries intersect only the query buffer: `World/Vegetation/bush_-5_-5` index 3 and `World/Vegetation/oak_-5_-5_CoastalPines36b` index 32. Neither is a whole-group edit permission

The one tree visual hit whose capsule box misses the query is `World/Vegetation/oak_-4_-5_CoastalPines36b` index 121: foliage reaches Z=-3730.5344 while the source capsule envelope begins Z=-3729.5249. It stays in the visual keep/reconcile list.

## Exact source rule and conservative interpretation

The unchanged `world39.gd` → `open_world.gd` path reads `metadata/asset_kind`, not the misleading group name. It uses the complete saved instance transform. Trees use a capsule with radius 2.4, total height 11 and local center Y=5.5. The preparation transforms its enclosing local AABB (X/Z ±max(2.4,float32(2.4)), Y=0..11), using outward-directed binary64 interval arithmetic, and unions the result with the native-style float32 AABB transform. Reflection, nonuniform scale, shear and parent transforms are retained. This is a conservative source-rule envelope, not exact capsule contact or an observation of physics-server scaling behavior.

`open_world.gd` gets the first imported mesh from the rock prefab, calls that mesh's `get_faces()` and applies the saved body transform. It does **not** apply the imported mesh node transform or use `assets/collision/rock.res` for these scatter proxies. The existing read-only binary inspector pins the imported cache's primary mesh ID to `ArrayMesh_y2h1h`, shadow ID `ArrayMesh_yjhaa`, with compressed decoded-byte SHA `b951304ab279936309fcab78d566fe0ecd0e2cd67d7f3a53c94a1d0c5793cf4c`. This identifies the source resource; it does not yet establish native face bounds or equality with the saved visual rock mesh.

Collision activation remains conditional on the source 3×3 focus-cell neighborhood, ≤350 m horizontal root distance, ≤150 m vertical separation, and refresh after >0.4 s. Bushes are skipped for this proxy rule but remain visual/support constraints. No active collider is observed here.

## One later bounded read

From Aether, after the parent schedules the engine window:

`PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/proxy-bounds-v1/run_proxy62.py --collect`

This launches exactly one fixed Godot 4.5.1 headless resource-read process, CPU affinity 2, hard wall limit 60 s. It uses existing `run_intake62.launch`, absolute isolated XDG directories, the complete frozen 1483-file dependency closure, old 1477-file guard, startup/UID/class-cache and absent-sidecar checks before/after, and an exact preparation-file freeze. Any process/log/protocol/hash/closure failure rejects completion and retains the failure evidence. No separate parse or world run is part of this command.

The native script reads only six source-specific visual mesh identities, including their shadow meshes, and the rock prefab/import SceneStates. For visuals it checks the exact previously observed storage hashes and surface layouts, then records actual native vertex and face extrema, counts and byte hashes. For the rock it requires the unique imported MeshInstance3D and the pinned primary resource, records its path and transform witness, and reads actual `get_faces()` bounds. It never instantiates a scene, activates a collider, reads all world buffers or saves a resource.

The wrapper then streams the existing saved buffers offline once more and requeries the union of prior visual bounds, source-specific native vertex bounds and tree/actual-rock-face envelopes across all saved groups. It writes `native-proxy-meshes.json` plus `source-specific-keep-reconcile.json` in a new evidence directory. That completed path/index list is the stopping point before a constrained terrain sketch. If the native read fails, retain the failure and stop for diagnosis; do not treat the provisional rock list as complete clearance.

## Verification and limits

- 18 pure Python test groups pass normally and with `-O`, including affine/corner enclosure, exact-rational arithmetic fixtures, negative scale, proxy-only edge cases, resource protection, malformed native reports, exact freeze-file membership and process-limit failures
- An independent source review also replayed all saved groups and checked 500 seeded affine cases against exact rational corner arithmetic
- `run_proxy62.py` without `--collect` checks preparation and dependencies only; it does not start an engine
- `FINAL_SHA256.json` freezes every preparation artifact and executable helper; `immutable-source-inputs.json` pins consulted source/evidence identities

The six visual sources have five distinct prior primary-storage identities. Vertex extrema will be source-specific native observations, not an independently implemented compressed-array decoder. No replacement loader was written. Every original unresolved occupancy/runtime/deformation/road/independently-recomputed-vertex/visual-acceptance flag remains false. No footprint or deletion is authorized, and saved visibility is not proof of live visibility or terrain support. The coast61/coast56 neighbor terrain and current saved instances remain protected.
