# Independent Game51b source preparation (not built)

This directory and the independent `lake_reflection51b.gd` / `assets/reflection51b/lake_water_reflection51b.gdshader` paths prepare a 1.08 optical overscan candidate. No saved Game51 resource is changed. The new shader is byte-identical to Game51's shader; the new controller expands the actual reflection frustum and uploads its actual projection, retaining world-space mapping. It also defaults clipping/reflection to enabled. The prospective builder has not been executed.

## Evidence and remaining gate

- Frozen Game51 scene SHA: `53e07e91b1bfafd0160749c5d90022d73029287cd36c51d54683339451a75408`
- Runtime-only overscan A/B/A: `cloud-evidence/reflection51-overscan-20261001T014352Z-1NnorN`. Parent inspected both lake views: screen-edge blue frame disappeared while world reflection remained aligned. Original/restored images were exact. This was not a saved51b test.
- Source-only optics test: `test_overscan_optics51b.gd`, `overscan-optics.log`. 1715 points, 120 camera states, all three projection modes, roll, horizontal/vertical camera offsets and both aspect policies. Maximum expanded NDC error 0.000063474 < 0.0001. Headless mathematical evidence only.
- Actual complete-material main-pass gate FAILED on first reference1128 in `cloud-evidence/reflection51-verify-20261001T015049Z-3Yd5WV`, exit1. All-off converted B differs from all-original A in five RGBA pixels; A/A2 restores exactly. No tolerance was relaxed. 663 checks, only that pixel gate failed. Source/candidate assets stayed unchanged.
- Five differing coordinates: (508,387), (510,387), (498,388), (279,405), (962,432); maximum channel delta30. These are observations, not a proven cause.
- Whole-world grouped-material and shadow-control diagnostic is prepared in `tools/diagnose_reflection51_groups.gd` and `source-assets/reflection51/diagnose_material_groups.sh`. Its GUI launch is blocked pending authorization resolution; it has not produced runtime findings.

Do not build, promote, or claim visual acceptance for51b until the exact main-pass failure is located and resolved. Native conversion, custom injection, Ocean shader, shadow-path changes and resource sorting remain hypotheses. Dynamic waterline-straddling clipping, future streamed bindings, non-Compatibility renderers and hardware GPU remain unvalidated. Reference1128/1129 composition and the inherited350m motion failures remain open.

## Subsequent diagnosis, 2026-10-01 02:35 UTC

The grouped run `reflection51-groups-20261001T022557Z-APneYQ` completed exit0: Ocean-only and custom-only were exact; only native group02 reproduced the five pixels. Disabling Sun shadows still retained five differing pixels, so a shadow-only explanation is insufficient.

The narrow run `reflection51-native-group2-20261001T023238Z-70jYXx` completed exit0. All32 affected materials belong to four islands' rockroot, shoulder and wetshore parts. Strictly identical StandardMaterial3D `duplicate(false)` copies, official un-injected shader templates and injected copies produced three byte-identical RGBA images. The original/restored-original pair was also exact. Independent decoded PNG comparisons are in `images/independent-native-controls.json`.

Material identity replacement alone is therefore sufficient to produce the five pixels. A specific ordering or depth-conflict mechanism remains unproven. The original main-pass gate remains recorded as failed. A new verifier-v2 is being prepared to retain original-versus-converted deltas, require original restoration, and separately require exact RGBA equality between same-value resource-copy baseline and converted materials across all references. It has not yet run;51b remains unbuilt.

## Shadow-pass guard, 2026-10-01 02:57 UTC

The saved51 v2 run reached1128/1129/1343 copy-baseline conversion equality, but1343 clip-only changed30pixels(maxchannel3), then restored exactly. A dedicated Sun-shadow control found clip-off/on exact with shadows disabled, and the original state restored exactly. Godot4.5.1 GLES3 creates shadow RenderData with visible-layer mask0xFFFFFFFF, so marker19 alone admits shadow passes.

`guard_shadow_pass.py` creates12 independent shader sources adding only `CAMERA_VISIBLE_LAYERS & 262144u == 0u` (with explicit parentheses) to the existing marker19 condition. The reflection camera excludes water18; main camera excludes marker19; shadow's all-bits mask fails the new guard. Exact source hashes, reversible replacement and negative controls are recorded in `shadow-guard-ledger.json`.

Runtime guard run `reflection51-shadow-guard-20261001T025511Z-FCy2Qp` exited0: old clip changed30pixels; guarded clip changed0, guard-off and original restoration were exact. The actual1128 reflection texture still changed967903pixels when underwater clipping was toggled, confirming clipping was not globally disabled. The texture was visually inspected: underwater terrain/root sections were removed, while above-water island/mountain/cloud/airship geometry remained. This is local evidence; the prospective saved51b still needs full seven-reference and dynamic checks.
