# Coast61 verifier v2

This directory changes the verification harness only. Native Game61 scene, mesh, collision, scatter, materials, controller, 55/60 pose data and the original byte-exact acceptance checks remain unchanged. First actual build and failed fresh run are retained in `cloud-evidence/coast61-build-20261001T123605Z-gq87o4e1` and `cloud-evidence/coast61-verify-20261001T123638Z-b66cdbe8`.

## First actual run

Build passed: 32.56 s, 922592 KiB. It saved a 1453-byte inherited scene and six independent native resources. The fresh run exited 1 after 186.90 s, peak 1604300 KiB, at the exact 1128 camera/ship-pose gate. Strict saved readback and the initial 60-root physics/cache checks passed. Eight coast images were written and all hashes match. All 44 pinned inputs remain unchanged. The maximum runtime-height/cache discrepancy was 0.000244140625 m; physical ray heights equal sampled collision heights at all 60 roots.

The failure prevented 1128/1216 smoke images, 1216 toggling, the return-to-coast support pass, actual-native export and the full continuous-foot/visibility post-check. A passing build, eight images and root support are not a completed fresh verification.

## Evidence for diagnostic camera-state pollution

The original 55 expected pose file is byte-identical to the file used by the passed actual 60 capture. No expectation is replaced or loosened.

`probe_camera_sequence61.gd` uses only two bare Node3D objects. It starts with the actual saved Camera Transform3D and simulates the original observe and diagnostic operations. No world, scene instantiation, mesh, collision or GUI is used. Final probe: exit 0, 0.166 s, 93796 KiB.

- Pristine 1128 and the 60 observation sequence reproduce the original expected camera and ship bytes exactly
- The original 61 temporary side/back/local sequence changes camera scale from `[1, 0.999999940395355, 0.999999940395355]` to `[0.999999940395355, 0.999999940395355, 0.999999880790710]`
- Two camera matrix components differ from expectation by -0.00000005960464477539063. Ship bytes remain exact
- Restoring the saved transform, derived rotation, scale, position and rotation order after each diagnostic view recovers the original exact 1128 camera and ship bytes

The native scale itself is retained; normalizing it to 1 would produce different bytes. The initial unit-scale control and one constructor parse failure are retained separately and do not support the final native-scale conclusion. `diagnosis.json` and `bare-node-sequence.json` contain the detailed arithmetic evidence. The first world failure logged a rounded Transform string, so its exact float bytes cannot be reconstructed after exit. The bare-node result proves the harness sequence can cause this failure; v2 will record all actual and expected world bytes and component differences.

## v2 behavior and execution

`verify_coast61_v2.gd` restores the exact pre-diagnostic camera state after each temporary front/side/back and local view. It logs camera transform/rotation/scale bytes before and after restoration, and actual/expected camera and ship bytes with component differences at every inherited-pose assertion. All original exact mesh/shape/scatter, 60 roots, 7 relocations, collision/cache, 10 images, 1128/1216 and offline full-foot gates remain.

`run_coast61_v2.py --parse-only` is safe preparation. `run_coast61_v2.py --verify-renderer` is the separate actual-renderer entry point, to be scheduled by the parent. The wrapper refuses build mode, includes the already-built Game61 scene and six native resources in its immutable before/after hashes, and runs the unchanged full-foot post-check only after Godot exits successfully. No v2 renderer was started during preparation.

This closes only the verifier's temporary-view state pollution. It does not prove real user sequences such as repeated F2 flight → native observation are free of scale drift. The original controller and inspection views also call camera.look_at, and 55 preserves inherited scale. A later ordinary-input test must record those real transitions. If that path reproduces a defect, it requires a separate small controller candidate; this verifier does not alter native scale or source scripts to make an exact numeric gate pass.


## Actual v2 completion

Fresh v2 and the446-check actual native full-foot post-check now both passed, exit0. Evidence: `cloud-evidence/coast61-v2-verify-20261001T124815Z-czvc76_r`. All three inherited camera/ship hex comparisons have empty difference lists. The40 adjusted objects passed continuous foot support; unchanged20 conditions and actual visibility limits are detailed in the parent README and `cloud-evidence/coast61-independent-review/review.json`. No ordinary-flight/UI-sequence or visual-reference acceptance follows.
