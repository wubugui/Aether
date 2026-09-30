# 1128 / 1129 shared lake: read-only geometry audit

2026-09-30. GOAL remains active; this is an actionable source/dependency intake, not visual acceptance. No scene, source asset, material, camera, or protected cliff master was edited. No full-world generator or history checkout was run.

## Useful result

The first problem is real land occupying the intended lake. `World/Ocean` is a 100 km plane at **Y=0**, whereas `Ground_1_-2` and `Ground_1_-3` put an almost continuous **Y≈15 m** meadow across the forward lake corridor. This explains the full-width green terrace in actual 47/42c images. Making the water more reflective or changing clouds cannot expose water beneath that terrain.

A second integration trap: the eight `props` entries shared by 1128/1129 in `assets/reference_views42.json` are **not instantiated by the current observation control**. `game42b.gd::observe_reference` changes camera, airship and environment only. They cannot be counted as existing lake islands or mountains. The actual persisted `World/Mountains` group is the authority.

## Evidence inspected

- `GOAL.md`, relevant 1128/1129 rows in `REFERENCE_SCENES.md`, and both actual reference PNGs
- Actual rendered `cloud-evidence/material47-20260930T211818Z-pG3XFd/candidate47/reference-1128.png`
- Actual rendered `candidates/round40-exclusive-20260930/evidence/gpu-i-particle42c-1757/reference-1128.png` and `reference-1129.png`;47 supplemental +150m-clear was also inspected
- Both references show broad open water continuing to the distant mountain feet, a low central opening between left/right peak masses, and a few tiny rocky pine islands. 1129 adds a near left shoreline and foreground rock; it is not an entirely green bank spanning the view
- Current fixed 1128 camera `(1150,10,-1000)` targets `(1150,160,-2600)`, FOV64; 1129 `(1300,7,-950)` targets `(1000,120,-2400)`, FOV66. Preserve these for acceptance. Parent's +350m collision/+150m-clear diagnostic remains a supplementary movement check, not permission to replace reference composition
- Godot **4.5.1** headless, static PackedScene instantiated **outside the tree**, with no ready/runtime processing: mesh AABBs, triangle-height samples, saved scatter transforms, route points. Data: `lake-geometry-data.json`. This is geometry evidence, not graphics/GPU evidence
- Four selectively fetched `.blend` copies opened in Blender 4.5.14 background with no save: `lake-source-intake/blend-inventory.json`. No whole-history checkout; total source intake ~8.2 MB
- At23:00UTC, also directly inspected both new `cloud-evidence/full-reference-survey-20260930T225223Z-Tc88Sk/images/reference-1128.png` and `reference-1129.png`. They corroborate the same unbroken green bank, compact central snow cluster, missing sparse islands, and non-mirror water; the new cloud revision does not resolve these geometry gaps. This audit does not independently certify hardware-GPU status of that parent render

## Actual node/source map

All node paths below are under `Skyfarer/World`. Current saved native scene is `candidates/round40-exclusive-20260930/project/scenes/candidate47/Game47.tscn`. Meshes are **embedded ArrayMesh subresources**, not live GLB instances: updating a GLB by itself will not change this saved candidate.

| Entity | Actual anchor / bounds in Godot metres | Persisted mesh |
|---|---|---|
| `Terrain/Ground_1_-2/Model/Ground_1_-2` | anchor `(768,0,-1536)`; X768..1536, Z-1536..-768; Y-95..36.736 | `ArrayMesh_8qjou` |
| `Terrain/Ground_1_-3/Model/Ground_1_-3` | anchor `(768,0,-2304)`; X768..1536, Z-2304..-1536; Y15..163.83 | `ArrayMesh_2wyc7` |
| `Terrain/Ground_1_-4/Model/Ground_1_-4` | anchor `(768,0,-3072)`; X768..1536, Z-3072..-2304; Y15..332.979 | `ArrayMesh_bj0ga` |
| `Mountains/massif_frost_crown` | `(1235.731,0,-2900)`; X732.705..1707.300, Z-3376.595..-2396.704; top459.655 | `ArrayMesh_tce3f` |
| `Mountains/massif_west_summit` | `(906.327,0,-2730)`; X490.170..1307.978, Z-3146.165..-2326.854; top390.298 | `ArrayMesh_0xxoi` |
| `Mountains/massif_east_summit` | `(1443.031,0,-2850)`; top299.981 | `ArrayMesh_m0ka6` |
| `Mountains/massif_needle_ridge` | `(877.049,0,-2350)`; top269.881 | `ArrayMesh_k8owo` |
| `Mountains/massif_east_spur` | `(1364.353,0,-2320)`; top172.357 | `ArrayMesh_5mkss` |
| `Mountains/massif_cirque_wall` | `(809.494,0,-1780)`; X574.619..1028.888, Z-2096.810..-1445.608; top136.554 | `ArrayMesh_w4pm8` |
| `Mountains/massif_east_foothill` | `(1269.851,0,-1810)`; X945.664..1578.297, Z-2154.191..-1466.473; top83.434 | `ArrayMesh_dv1gb` |

The last two are important: **even after cutting the Ground tiles, their overlapping massif feet can still fill the intended central basin**. Also inspect `massif_valley_guard` `(749.505,0,-1430)`, `massif_west_spur` `(471.463,0,-1850)`, and the western foothill/buttress. All eleven mountain AABBs are in the JSON; do not infer that terrain-only lowering completes the lake.

### Native editing sources

`scenes/terrain/Ground_1_-2.tscn` references `assets/terrain/Ground_1_-2.glb`, `assets/collision/Ground_1_-2.res`, and `scripts/asset_instance.gd`; the corresponding native source is `blender/terrain_modules/Ground_1_-2.blend`. Same pattern for all terrain cells. `assets/mountain_kit.json` explicitly names each native source `blender/mountain_kit/<name>.blend`; mountain prefabs point to `assets/models/<name>.glb` and `assets/collision/<name>.res`.

Sources exist in repo HEAD `a8228e6323504416f855c57fc9e852636fc84502` but were sparsely absent from the working directory. Four were fetched into **evidence copies only**, not restored over production:

- Ground_1_-2: 5,874 editable vertices / 11,593 polygons, one meadow/stone/shore material; SHA256 `b6e4132f87b460b300355a3a0e53beb45325c94aa2d2507f8dae94a5f3b87da7`
- Ground_1_-3: 1,139 vertices / 2,142 polygons; SHA256 `b93b666d2fda1f317efa0ca34ce83504a2f029388049446477feb2fcc1247180`
- massif_frost_crown: 199 vertices / 394 polygons; SHA256 `f40b91da3e581310f94153fa3d8b4085fd968101eed3023e6d5b57cec41baa4d`
- massif_west_summit: 198 vertices / 392 polygons; SHA256 `18d4b30aa560157f8b5f2fa2ab8302e564810259d02372e2155cc02a40e4404f`

Blender local `(x,y,z)` maps to Godot local `(x,z,-y)`, then applies the saved node anchor. Their transformed bounds agree with the actual47 meshes. This verifies source suitability/bounds, **not a full every-triangle equivalence claim**. Before editing additional tiles, fetch only those specific sources and verify them likewise.

### Measured obstruction

On X1150, mesh heights at Z-1100/-1250/-1450/-1650/-1850 are 15.000/14.135/15.000/15.152/15.000 m. On X1300 they are 15.000/17.497/19.220/15.013/15.000 m. Both cameras currently sit in the southern water pocket; the land bridge starts roughly a hundred metres forward. At X1150,Z-2100 the ground already rises to34.850m. These are actual triangle intersections, not procedural height-function guesses.

## Three priority local entity revisions

1. **Open a real continuous lake basin and two irregular shores.** Start with copies of Ground_1_-2/-3 and the overlapping cirque/east-foothill feet. Establish a central submerged basin through the Y15 barrier, retain short low rocky/green shore shoulders at the sides, and connect it to existing water at Z≈-1000. A design intake domain X≈350..2100, Z≈-1050..-2300 is reasonable but inferred, not a reference-proven map. Core work is the two center tiles; broadening the lake requires adjacent `Ground_0_-2/-3`, `Ground_2_-2/-3` plus synchronized shared edges. Do not simply flatten a rectangular trench. Keep a large open-water foreground and middle distance in both original views; prove actual continuous below-water bed and above-water shores with lateral/low-water/overhead observations.
2. **Separate left and right snow-mountain masses, preserving a low distant centre.** Work from editable mountain copies and assemble them persistently into the same World. Current dominant peaks are clustered directly behind the centreline instead of wrapping the lake; repartition the west/east summit/spur and reshape connecting foothills with broader ridges, snow gullies and varied ridge lengths. Frost crown can become a less central far mass rather than another centred cone. Decide anchors and silhouettes jointly with exposed lake width, not by arbitrary uniform scale. Mountain bases and terrain must meet, and neither cirque wall nor east foothill may re-close the basin. Recheck 1275/1276 and nearby mountain views because these are shared entities.
3. **Build and save the actual small rocky pine islands/near shore kit.** Use independent editable `.blend` island bodies with underwater roots, separate rock shoulders/grass caps and sparse pine groups; instance them once in World rather than in observation mode. The unconsumed 1080/-1150 and1300/-1120 prop tuples are only a starting clue and currently intersect dry terrain; do not preserve their heights blindly. Author near-left shore, middle-distance small island and a foreground stone at real positions that remain coherent across1128 and1129. Match tree/rock scale after the lake exists. No camera-facing cards, image backgrounds or per-reference duplicate landscapes.

## Dependencies and acceptance gates

- **Saved mesh + collision:** each affected terrain/massif needs updated exported geometry, prefab and current candidate's embedded mesh, plus matching ConcavePolygon collision resource under the node's `Collision/Shape` (layer5/mask2). Keep neighboring shared edges watertight. Never edit `blender/cliff_kit/cliff_eastern_plateau.blend`
- **Scatter:** current center tile -2 has111 instances (48oak/20poplar/17bush/26rock); -3 has389 (227oak/94poplar/2pine/23bush/43rock). Resources are `assets/scatter/Grounded_<kind>_1_-2.res` and `_1_-3.res`. Wider intake X0..2304/Z-3072..-768 contains4,403 instances in69 saved groups. Only actual affected instances should move/remove/replace, and those decisions must be recorded; don't leave trees floating over the new lake or artificially retain deciduous forest in the intended sparse alpine water region
- **Runtime collision/height caches:** `open_world.gd` rebuilds placement bookkeeping from saved MultiMesh transforms, generates nearby prop collision, and caches terrain triangles in `terrain_samples`. Reopen fresh after integration; update the saved scatter transforms as well as visuals. Do not rely on stale procedural `world_math` heights for edited core geometry
- **Existing building support (do not overlook):** expanded west shore X558..652/Z-1950..-1846 contains12 saved cottages `Settlements/cottage_57239` through `cottage_57250` (actual bounding boxes are in `other_meshes` in the JSON). Keep their stable support domains when shaping west-spur/shore, or explicitly design and validate relocation. The snow-mountain zone X905..1232/Z-2877..-2694 contains `dock_57188`, `observatory_57189`, cottages57190..57192 and crate57193. Summit movement/reshaping must account for their actual foundations and docking/flight approach. Prioritize the centre-two-tile basin first; widening west or moving the whole snow group is not dependency-free
- **Routes:** all3 persisted `World/Routes` curves are outside the intake: Crownreach X-36..120/Z-291..480; Amberfield X120..1320/Z380..880; HillHamlet X-4..10.58/Z-221..-87.07. No current saved road route crosses this lake area, so no evidence-based reason to regenerate global roads. Any introduced shore path would need its own explicit support test
- **Water:** actual OceanY0 is shared; changing global sea height to hide the meadow would disrupt the world. Mirror reflection of mountains/islands/clouds/airship remains an additional material/rendering goal. It cannot be accepted merely because a basin is present, and geometry work should not be stalled in another cloud/water parameter loop
- **Verification:** use unchanged1128/1129 views, side/back with clear cameras, actual lateral movement and shore approach; inspect all edited sources, full collision support and affected scatter. Repeat relevant nearby mountain references. Headless geometry and source intake are not GPU/visual acceptance; parent owns actual graphical survey
