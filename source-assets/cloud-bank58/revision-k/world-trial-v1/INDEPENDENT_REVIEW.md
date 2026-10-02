# Independent source review: K one-unit world trial v1

Reviewed 2026-10-02 11:21 UTC. Verdict: **source preparation accepted for the parent's separately scheduled, bounded parse and renderer stages** after the PNG-dimension correction below. No Godot/Blender process, project copy, scene generation or image generation was run by this reviewer. Native parse, actual rendering, visibility, visual suitability, hardware GPU and complete GOAL acceptance remain **unproved**.

## Resolved blocking finding

The first reviewed wrapper required native Image dimensions to equal ViewportTexture metadata. This repeated the already documented double-stretch metadata problem (actual PNG 1179×664 versus metadata 831×468 in the older observation). It could reject valid original pixels and conflated measurements that must stay separate.

The producer corrected only that gate and its documentation/test: the wrapper reads the original PNG signature and IHDR, requires dimensions to equal the native Image report and the fixed **1179×664**, and requires the paired original/K front dimensions to match. Requested window remains 1180×664. Actual window, visible rectangle, content-scale size, texture metadata, final transform and projection remain independently reported. There is no resize, resampling, metadata override or fallback budget/resolution adjustment. Synthetic in-memory header checks are not image/render evidence.

The producer also replaced only the inferred local `var path :=` with explicit `var path: String =` in the same path-concatenation expression. Reversing that single annotation reproduced the previously reviewed script SHA exactly. This removes a potential inference ambiguity without changing the target or behavior; no actual GDScript failure or parse success is claimed. Both 12-test modes below were independently repeated after that final source edit.

## Source and placement findings

- Independently followed Game61Coast → Game60Observation → Game56Coast → Game55Observation → Game53dWest. The saved scene contains exactly 25 CloudSea roots, each with one old46 continuous-crown child (variants 0/1/2, not 25 copies of one child name). This is not the historical 52f 125-part scene.
- The selected exact mesh path is uniquely SkyRegion39/CloudSea_1_1/cloud_sea_46_0_continuous_crown. It is ArrayMesh_d78o4 with 14374 vertices/15492 indices. The new node is default-disabled; the inherited scene/resource bindings are unchanged. The only existing mesh mutation in the trial is this mesh's visibility. Other roots are not hidden, deleted or rebound.
- SkyRegion39 is identity in the saved base. Trial activation requires its own world transform to be identity and places K once at (3958,0,3667), identity basis. The old root's rotated transform is not inherited. No second UV/world rotation, scale, recenter or vertical offset is applied.
- Independently hashed the accepted 34772-byte native scene: SHA256 91ab3412c67b5f82449396677a30a9bbe1542a338c00150dc1822910cdf7f789, with zero external-resource declarations. The trial checks this file identity, native node/mesh identity transforms, surface format and exact packed vertex/index payloads. Every capture rechecks packed geometry and the accepted material values, plus lit StandardMaterial, original fog, no textures/next pass or substitute vertex-color override.
- Synchronous switch witnesses cover every existing Node3D's transform/visibility and geometry resource bindings, excluding the newly added trial subtree; only the selected visibility difference is allowed. This is source/runtime-binding protection, not an independent all-world array readback. Frozen source identity and the absence of other mutation code support preservation of the original 25 saved clouds.
- The recorded 7.486% K/old XZ AABB-area ratio and sparse centroid-ray diagnostics explicitly leave gap/occlusion risk open. No bounds/ray result is promoted to pixel coverage or artistic suitability. This exact root selection is a documented new design experiment, not an invented historical instruction.

## Isolation, entry and process evidence

- Read the original startup, observation, environment/weather, reflection and world-loading code relevant to the trial. The prepared entry loads actual Game61 via the inherited scene; it does not rebuild/save the world or edit the main project entry. Reference 1216 uses its inherited observation method, original front position (3000,1150,4300), FOV 62, and fixed weather time .35. Front off/on use exact equal camera transform and projection; side/back and near views are separately fixed diagnostics. Weather callbacks are frozen only for these static observations, not claimed as flight/weather-continuity acceptance.
- All 4884 current main-project file identities, including 302 import sidecars and 938 .godot/cache files, matched the successful v3 protection manifest in the independently rerun preparation check. The source tree has no symlink. A narrow copy/import-path check found 903 sidecar remap/source/destination strings all res:// and present; the global script-class cache is empty. These are copy/entry safety checks, not a new all-resource geometry audit.
- Parse copies this existing project exactly once into a separate /tmp work tree, with normal copies rather than links. It adds only the three trial scripts, trial scene template and accepted embedded K scene. Renderer requires successful same-freeze parse, a SHA-bound terminal report and the unchanged complete work-copy manifest; there is no second copy or fallback recreation. XDG paths are isolated per evidence run. Main-project and frozen-input identities are checked before work and after terminal exit.
- Python helper imports are read-only at import and are included in the source freeze. No default invocation starts an engine. GDScript helper preloads and inherited resource loading will still require the actual Godot parse stage; Python AST/tests are not proof that GDScript compiles.
- Explicit fixed limits remain parse 30 s, renderer 240 s, wrapper 300 s, CPU affinity two and aggregate wrapper+child RSS 3145728 KiB. The support code matches the prior bounded helper except this explicitly agreed world RSS constant. One-shot exclusive admission, actual child PID/wait4 return status, process-group kill/reap, log-error rejection, final identity checks and failure/partial evidence retention remain present. No active-run extension or downsampling route was added.
- A successful future renderer must supply four exact ordered original PNGs, PID-matched native success, front camera/projection equality, original reference/time, exact geometry/material/visibility, PNG SHA/byte-count/IHDR dimensions and restored original state. The report explicitly keeps visual and hardware acceptance false. A numerical/process pass alone does not accept this cloud layout.

## Independent checks performed

- Re-read GOAL and the current CLOUD_RESUME entry, then reviewed only this bounded trial and its relevant existing entry/helper paths
- Recomputed the initial 46-file preparation freeze without changed entries
- Re-ran all **12 pure tests in ordinary mode**, exit 0, 2.156 s
- Re-ran all **12 pure tests in optimized mode**, exit 0, 2.069 s
- Before the final annotation below, re-ran check_preparation58k.py, exit 0: 46 frozen files, 4884 unchanged project files, engine_started=false, native_parse_passed=false, world_loaded=false, images=0
- No changes to producer code, main project, original source/native packages, CLOUD/GOAL, Git or Slack. This review file is the reviewer's only written deliverable

The pre-review freeze SHA was b15ea6db225b27df53c23fad4cb5972ba1b58c407009156ddc33c2e45e204a12. The producer must include this review in the final freeze and rerun the pure preparation check; reviewed code identities below define this verdict and avoid a circular self-hash.

## Reviewed final source identities

- `CloudKTrial.tscn.template`: `1b2ca256ab1430d918bb5104c10de1375bb91e969436c732dee058ac92e243c3`
- `trial58k.gd`: `aef681dbebe86d804293195651b1ce77a488d586cd2e974c51103f6056cd9a1c`
- `observe58k.gd`: `2002eee20544c9df89f2d52b1cae73e8df6b24f07f6be5afb2c6178954214309`
- `parse58k.gd`: `4b809654e45eebaeb2c92f99be631073e9ca34f92e3ff70af1ac3720dbdab2b3`
- `run_world58k.py`: `c0e32d375f52dd165cbae71f98f18dbf8542a8891d93efde215a5db682e627ed`
- `world_support58k.py`: `86863361c6b148055841ea649f6be76f730de478f09e27a5b4ee904722d9743f`
- `provenance58k.py`: `65ae9acd7a0823a5c63aa88cd160b39706ab1c7a1c7404066a6dce715dccedaa`
- `check_preparation58k.py`: `15fba14588f91d64b434c939856fd6f89ff0f004b08b40c6580720a026eab1b7`
- `test_world58k.py`: `95c8004808b329676ef82e105000ddecba908d2de7a30f995c9a6134bad84249`
- `placement-provenance.json`: `242d871ff36b4de075d2248d2381a74c70cf57f2b10f894b77a891c58fa3a545`
- `README.md`: `2c324965de9496d2f5bac155ed8f5991c4b43d45256125eadca34613c5430ae2`
