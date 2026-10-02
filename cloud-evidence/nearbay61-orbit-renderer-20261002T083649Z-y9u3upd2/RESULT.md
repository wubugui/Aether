# Completed fixed-ship four-view orbit, explicit 900-second observation

2026-10-02 08:36–08:48 UTC. Official Godot 4.5.1, X11/OpenGL3 compatibility, llvmpipe software renderer, CPU2. The native child exited 0 after 705.882763557 seconds, peak 2668516 KiB; the wrapper also exited 0. An independent total wrapper wall time was not recorded. The 1020-second outer bound did not fire. The complete native report/receipt/terminal hash chain finished at 694.579 seconds under the explicitly selected 900-second observation limit. No logged engine errors; one unsupported V-Sync warning is preserved in the raw stderr.

## Narrow runtime result

- 82 native mouse-motion events completed, each no more than .05 radians, final orbit exactly 4.0 radians (about 229 degrees, not a full 360-degree circle)
- 179 late-process samples map to 179 audited physics segments; no pending segment or active input event remains
- Actual camera path 264.458679139731 m; actual ship path after fixture placement exactly 0 m
- All 179 actual physical and isolated-visual sweeps are clear, with original near-plane radius, actual/desired line-of-sight and per-process/per-physics identity gates
- Four captures at 0, 2.6, pi and 4.0 radians, each capture's actual frame segment audited, with exact original PNG SHA binding
- All 1603 protected inputs and full 1483-file reviewed saved dependency closure, startup/cache and absent-control identities unchanged
- Default historical 600/720-second mode and its 15-second settle remain preserved. This run explicitly uses 900/1020/30; two stable samples within .02 m, event/capture budgets and all spatial/input gates are unchanged

Strict 600-second performance is **false**, retained in both completion receipt and terminal output. This observation success does not repair the six previous failed observations or demonstrate an acceptable game frame rate.

## Actual four images

All are original 1179×664 game PNGs, unedited:

1. `images/01-default-native-camera.png`, 378361 bytes: ship over open sea with cloud above
2. `images/02-shore-candidate.png`, 454499 bytes: near coastline, ship, trees, broad cliff, existing chained clouds
3. `images/03-ship-side-candidate.png`, 332305 bytes: shore-facing ship side, dark cliff across much of the frame
4. `images/04-further-side-candidate.png`, 307183 bytes: further side with cliff mass on the right and lower coastal land on the left

The supervising review actually viewed all four PNGs. The ship, water, vegetation and solid land have ordinary material pixels, with no obvious single-frame camera-inside-wall appearance. Large flat dark cliffs, low green hills and repeated chained cloud blobs remain obvious visual deficiencies. K's newly accepted unit cloud source has not been integrated into this world. Normal-material views alone do not quantify visible pixel coverage.

## Evidence limits and measurements

This is the predefined fixed-ship observation only, not flight, 360-degree coverage, universal live resource immutability, reference reproduction, hardware-GPU acceptance or full GOAL acceptance. Complete CPU MultiMesh buffers/binding/count/format/bounds are checked at the recorded late-process/physics/final witnesses. Same-resource arbitrary Mesh/LOD/shadow mutations, shader/material changes, renderer-only changes, between-observation reversions and animated-ship limits remain disclosed in the native report.

Telemetry records 1613 inventory validations totaling 73.061946 seconds and 1310080 buffer hashes covering 4689914496 bytes. Hash timing 18.680188 seconds is nested, not additive. Engine process delta totals 24.352009 seconds versus actual process-interarrival wall time 682.958182 seconds; unmeasured difference is not assigned wholesale to rasterization. Four capture calls total .352704 seconds. These are diagnostic observations, not a hardware performance pass.

The original 3079360-byte native JSON is retained locally and published as lossless gzip, 109999 bytes. `report-storage.json` records both exact hashes and the recovery command. Raw logs, source snapshots, input/output manifests, process and wrapper reports, receipt and original PNGs are retained. The independent read-only review is recorded separately and never edits the original machine result.
