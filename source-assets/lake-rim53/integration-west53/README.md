# Strict west-only53d native integration preparation

This directory contains the reviewed source gate, exact scatter reconciliation, immutable change manifest, real-renderer builder, and a separate fresh-process verifier. No builder or verifier GUI run has been started by this worker. A temporary two-view diagnostic is not an integrated scene.

The five real source views at `cloud-evidence/rim53d-source-preview-20261001T060759Z-o4Ypqq` were inspected individually. They establish enough form for a **limited west-only integration trial**, not reference acceptance. The pointed apex and inherited green base remain visible. The other three first-draft mountain families are explicitly excluded. Existing first/b/c/d source files are not overwritten.

## Run order

1. Run `launch_build_west53.sh` with the real Compatibility renderer. Its candidate is `res://scenes/candidate53d-west/Game53dWest.tscn`
2. Only after a successful build/reload report, start the separate `launch_verify_west53.sh` process
3. Default verification captures10images:1128/1129front,side,back,+200m approach, and original1275/1276. Optional`--front-only` produces only a2image smoke run and is recorded as such
4. Inspect actual images independently. Neither a numeric pass nor this limited source gate marks the reference scenes,350m route, full flight,1344pixel gate or totalGOAL complete

Both wrappers create unique evidence directories, write input SHA records, source snapshots, stdout/stderr and actual exit code, and update separate pointers in tools-feiting. They use tools-feiting runtime directories, Dummy audio and disabled VSync. They do not alter the project default. The builder refuses headless saving, existing destination files or changed immutable inputs; preserve a failed partial attempt and give any revision its own destinations.

## Exact allowed changes

- Existing `World/Mountains/massif_west_spur/Model/massif_west_spur` keeps the original native340triangle ArrayMesh **exactly**, including geometry, colors, normals, flags and original stored material fields. Its legacy node name is retained to preserve existing bindings. The Blender`rock_body` is its source-equivalent counterpart
- Add exactly four mesh leaves under that Model: `ridge_shoulders`, `snow_cap`, `snow_gully`, `shore_rock_apron`. Together with the unchanged root there are5meshes and1,780triangles
- Duplicate the existing west ConcavePolygonShape3D and change only its face data to the joined actual five saved mesh surfaces. Keep its properties and existing layer5/mask2; layer4 probes remain valid
- Change exactly120MultiMesh translation slots, all inGround_0_-3:oak72,poplar29,bush8,rock11. The109plants and4steep-slope rocks relocate to unchanged actual dry terrain in the same tile;7rocks are re-supported vertically. Original indices, bases, colors and custom data stay exact
- Preserve the remaining1,141instances in the six-tile pool exactly. Only four changed MultiMesh resources are copied/saved; no bulk scatter rewrite
- Save independent four mesh resources, the combined collision, four changed MultiMeshes, a reusable native west prefab and the candidate scene. The first package's209scatter edits are never reused

`integration-payload.json` contains full geometry and all120before/after transforms. `scatter-reconcile-report.json` records every1,261index, position, support and disposition. Relocation candidates must have unchanged highest support equal to actual terrain, slope normalY≥0.87, dry height≥5m,12moccupied spacing and no building-buffer overlap. Original support clearance is retained; no inherited>1moutliers were found.

## Strict preservation checks

`integration-manifest.json` pins141input files, including the53dsource, reconciliation, source-form gate, runtime probes, all114existing clipping material files and12shader files. Do not regenerate it after starting the build. The builder verifies the integration mountain data is exactly the53dsource data and only one mountain family is present.

The graph audit excludes only the four named added leaves, the west collider's`data`, and the120translation positions. It masks only MultiMesh buffer offsets3,7,11; basis and every other float remain audited. Owners, sibling order, groups, persistent connections, script fingerprints, resource flags and all other stored properties are compared before editing and after saved reload. The exact change report allows0deleted nodes,4added nodes,1shape-property change and two fingerprint fields per changed MultiMesh node. Original root mesh fingerprint is checked separately.

The original248material binding rows,114materials, controller clipping-path array and48,000weather floats must remain exact. Each new mesh binds the same existing dual-guard mountain material at node override, surface override and mesh surface. No new shader conversion occurs. A native prefab is packed from a copy; original full-scene ownership is not rewritten.

All source/candidate instances are off-tree while building. Deferred Sky resources settle3frames plus post_draw before release. On success, all local PackedScene references and large snapshot maps are dropped before node cleanup. Fresh verification drops baseline PackedScene references and audit caches before adding only the candidate to the live tree.

## Independent fresh runtime verification

The fresh process verifies exact input/asset SHA, saved graph and original root mesh again, then enters the candidate into the live tree. It checks actual ready-bound material identity and existing controller membership for all5meshes; freezes callbacks while preserving physics mode/layer/RID state; checks42mountain and171building/buffer support points with actual layer4rays and`ground_height`from above; and checks all1,261saved instance positions, physical support and runtime`prop_transforms`indices.

Original1128/1129camera positions/FOV are checked. The existing+350mfailures and+150m/+200mresults must match the recorded51bphysics results exactly; inherited350mfailures are never relabeled passes. Default captures also expose side/back and1275/1276weather views. The verifier writes its own report only and never saves the live scene.

The continuous source proof places all new components over existing actual dry triangles, with zero added footprint in an old water column, while the original root and all other Worldgeometry remain exact. The manifest keeps that proof and the4mroot burial check. Existing depth resources are retained; any geometry deviation during saved/live validation is a failure, not permission to reuse an invalid depth bake.

## Preparation checks and remaining limit

Builder, audit and verifier parse successfully under Godot4.5.1; the headless guard exits2intentionally. Both wrappers pass shell syntax checks. Blender4.5.14CPU native readback and reconciliation completed. Actual saved/native/physics success remains unestablished until the parent executes both real-renderer stages and reviews the resulting images.
