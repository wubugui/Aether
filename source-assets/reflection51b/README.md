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
