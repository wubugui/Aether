# Game61Coast integration preparation

Preparation only. No61 renderer build, actual resource save or61 world run has been performed. The saved57B source is accepted for limited integration testing, not visual/reference completion. Do not edit frozen `source-assets/coast57/revision-b` from this workflow.

## Fixed base and execution entry

`Game61Coast.tscn.template` is1453bytes and inherits `Game60Observation`, preserving56's low cape,55's lake observation and60's switchable1216 ship pose. The base scene SHA is `8fcb0d24d503133a7e6ba29645291a73314c88b40ab447e0802937f1c802ac45`. `base60-gate.json` binds its script/pose, aggregate verification and actual terminal scope/capture/ordinary-flight process/detail reports. Both wrapper and GDScript builder refuse an unready or altered base. `seal_base60.py` reproduces that binding from the completed60 evidence.

Commands, from Aether:

```
python source-assets/coast61-integration/run_coast61.py --parse-only
python source-assets/coast61-integration/run_coast61.py --build-renderer
python source-assets/coast61-integration/run_coast61.py --verify-renderer
```

The default is parse-only. Actual stages require the coordinated renderer window; they have not been executed by this preparation task. Use the official4.5.1 binary and absolute tools-feiting XDG paths configured by the wrapper. No headless MultiMesh save is permitted.

## Exact save scope

Builder output is only `res://scenes/candidate61-coast/Game61Coast.tscn`, its build report, and six independent resources in `res://assets/coast61/`: target Ground_-5_-5 mesh, matching ConcavePolygonShape3D, and four MultiMesh resources. No large scene packing, default change, unrelated node/material/script edit, or overwritten56/60 resource.

The mesh keeps original surface0 GPU bytes and8264 original vertices, drawing only2111 unchanged source triangles. Its2125 unused original vertices are explicitly unindexed. Surface1 draws759 changed triangles with original colors/material identity. Both original and new mesh must have no LOD or shadow data; otherwise the builder stops. The extra `surface_material_override/1` is the single verified null dynamic slot, and both active materials must equal the original. `surface-triangle-map.json` records the exact mapping.

All four source groups,81 instances and972 floats are checked against actual GL buffers. Only51 individual translation components may differ:5X,40Y,6Z, representing40 affected roots and7 explicitly recorded XZ relocations. Every other value, including basis, count, flags, old21 outside-envelope instances and20 unchanged inside roots, stays exact. Node owners/groups/order/persistent connections and all unrelated stored fields are compared against60 before ready, after save and in the fresh process.

## Fresh verification sequence

1. Load60 outside the tree with the actual GL renderer, capture the strict baseline, then free it before loading61. Require exact saved mesh/shape/MM resources and native inheritance before entering the world
2. Verify current2870 drawn faces via actual indices, collision mapping, original shape discrepancy and all60 actual roots. At a bounded coast focus, require51 native pine capsules and7 original rock collision bodies with exact new instance transforms and masks;2 bushes keep the original no-prop-body behavior
3. Check native terrain ray hits, actual `world.ground_height`,60 `prop_transforms` entries and current `terrain_samples[-5,-5]`. Repeat after the distant inheritance views to expose stale cache or restored-buffer regressions
4. Capture ten same-world images:1131/1347 front/side/back, near-bay shore, north/east boundary, inherited1128 and1216. Check exact source camera/ship transform hex for1128 and enabled1216, disable60's cloud opt-in and check fallback placement, then restore it and check the exact pose again
5. Export actual live GL drawn mesh faces, direct shape faces, full four buffers/group transforms, actual native prop mesh arrays and both60-root support passes. Exit Godot before the Python continuous-foot verification
6. `verify_runtime_feet61.py` verifies those actual exported arrays against the source and intersects every actual lower-foot polygon with actual rendered terrain and physics-shape triangles. It also checks burial bounds, actual above-terrain surface area/top clearance, the7 final neighbor clearances and unchanged source hashes. The wrapper cannot report overall success until this separate actual-data gate passes

The1mm runtime/cache/foot evaluation bound covers existing float/cache behavior. Terrain GPU preservation, native buffers and saved resource readback remain exact. This workflow does not replace original native meshes with the Blender preview reconstructions. The latter supply source provenance; actual GL prop geometry must match the original vertex/index/normal/color data before it can be used for physical calculations.

## Bounds and review requirements

Expected single live-world RSS budget is about1.8–2.2GiB, based on measured60 capture peak1771768KiB;61 is not measured yet. The builder should be lower, roughly the prior56 builder's0.9GiB. Python full-foot work runs after Godot exits. Disk output should be a small inherited scene and six small resources, approximately a few hundredKiB, not another100MB scene. These remain estimates until the actual run.

Native support and source screenshots do not establish final appearance. B still has broad facets and the original gray shore strip. Inspect the ten actual61 views before accepting this limited world stage. Hardware GPU,61 ordinary flight, opening/full-world regression and all21-reference completion remain outside this prepared gate.54 and the protected cliff source are unrelated and untouched.

The first parse attempt exposed an unintended workspace-ID replacement in copied paths and failed before loading any source or scene. Its evidence is retained. Corrected code is parsed again; `last-parse.txt` points at the latest result. A parse pass alone is not native resource or runtime success.


## 2026-10-01 actual native61 result (appended)

Game61Coast now exists as a 1453-byte scene inheriting Game60Observation. Six independent native resources total 327262 bytes. Default scene remains unchanged. Build passed in 32.56 s with peak 922592 KiB; the first fresh verifier failure and its eight images remain intact.

Verifier v2 passed in a fresh real llvmpipe process: 251.0737 s, 1691040 KiB, exit 0. The actual native continuous-foot post-check passed all 446 checks in 2.8058 s, 170700 KiB, exit 0. Ten actual images and 52 pinned inputs were independently hash-checked. All 106 frozen57B manifest files remain unchanged. Evidence: `cloud-evidence/coast61-v2-verify-20261001T124815Z-czvc76_r`; independent review: `cloud-evidence/coast61-independent-review/review.json`; aggregate: `scenes/candidate61-coast/verified61.json` under the Godot project.

The actual mesh has 2111 unchanged original triangles plus 759 changed triangles, with no stale LOD/shadow mesh. All preserved GPU fields and 81 complete instance buffers match their authority. Only 40 root translations changed, including seven explicit XZ relocations. Both initial and returned-to-coast checks have 60 identical support/collision/cache records. Maximum cache discrepancy is 0.244140625 mm; actual physics ray and direct collision heights match. Both native materials remain the original material.

Only the 40 adjusted objects pass newly required continuous mesh/collision foot contact, with zero positive gap in actual results. The other 20 retain original conditions: unchanged rock0 and rock8 still have approximately 0.150 m and 0.388 m of local bottom-surface air gap. No claim that all60 objects have zero gap is made. Rock7 retains 75.0472% of its original above-terrain triangle area, with 65.9849% of total mesh area now above terrain and 4.7796 m top clearance. Its extra seat depth is 1.2447 m (20.6609% of original above-origin model height); total maximum burial is 36.8225% of model height. These are surface-area/height measures, not solid volume or visual-occlusion acceptance.

The original post-check compares seven relocations against the 60 in-box objects. The independent review additionally checks all81 instances in their four complete groups; all nearest neighbors are the same and minimum conservative foot-radius clearance is 4.7578 m. Canopy clearance is not claimed.

1128 and enabled/restored1216 camera/ship bytes match unchanged expected hex exactly; 1216 opt-out also passes. The v2 fix restores its own temporary diagnostic camera state. Real user F2/flight/observe transition scale continuity remains untested.

The parent directly reviewed all10 world images and rejected overall reference match: the low bay is real, but broad facets, gray shore band, long straight far coast, missing high mountain chain, simplified water and cloud geometry remain. Existing millimeter tile seam discrepancies remain frozen. No61 ordinary flight, hardware GPU, original-opening/full-reference or GOAL acceptance is claimed. Next ordinary-flight design should use a statically cleared water route near the new bay, with actual controller input and continuous path evidence.
