# CloudSea52e integration and observation

This work is a limited cloud-geometry candidate for the unchanged full GOAL. It is not a visual pass, hardware-GPU pass, or player-flight pass.

## Actual saved candidate

- Baseline: `scenes/candidate51b/Game51b.tscn`, SHA256 `b169f62527a52b9f2a3f091c2d7db136ad7cd67111e405f08f390eeb082e2bb1`
- Candidate: `scenes/candidate52e/Game52e.tscn`, SHA256 `5abbabf7487766412592f0b93ccd12c01e7bbb70f28e96ffd829e7ae78919079`
- Actual renderer build: `../cloudsea52e-build-20261001T045451Z-Dc99Jb`, build and wrapper exit 0, only known unsupported VSync warning
- Exact native change ledger: 25 old child meshes removed, 75 new child meshes added, zero changed properties on common nodes
- 25 CloudSea root transforms, all unaffected node/resource semantics, ownership, sibling order, persistent groups, connections, editable-instance state, and all 48,000 precipitation floats survived real-renderer save/reload
- All 248 existing guarded material bindings and the ordered 114 clipping-material paths remain exact

The earlier assertion that CloudSea had already been converted to guarded shaders was incorrect. Actual saved51b uses three `StandardMaterial3D` resources with Lambert Wrap (`diffuse_mode=2`), vertex colors and physical lighting. The new children use those exact active material resources and original render flags. No new guard conversion or controller-list change was made.

## Source provenance and axes

`integration-manifest.json` records verified 52e source file hashes from the source worker's actual Blender reopen, GLB inspection, manifold/component and non-adjacent-triangle checks. Source preview acceptance is separate; the parent reviewed all 15 actual source images before launching the builder.

The source uses Blender `export_yup=True`. Actual source vertex bounds mapped `(x,y,z) -> (x,z,-y)` match all nine exported GLB POSITION bounds. The builder takes every imported mesh's complete ancestor transform chain. It adds no guessed corrective rotation and never treats bounding boxes as proof of geometric separation.

## Runtime environment compatibility

`scripts/environment42b.gd:54` recursively visits every child in `collect`; it does not use old cloud names or assume `get_child(0)`. `register` intentionally applies shader uniforms only to ShaderMaterial. The retained CloudSea StandardMaterial resources respond to the same shared Sun, Environment ambient light, and fog.

The verifier checks after every reference/environment switch that all 25 baseline or 75 candidate cloud mesh instances are visible, registered with the renderer, in the actual same World3D, and use exactly three live material objects with wrap diffuse, vertex colors and physical per-pixel lighting. The full per-mesh result goes to `live_cloud_bindings`.

## Launch contract

The parent owns graphical execution. No graphical process was started by the integration worker. Run from the existing cloud desktop terminal, never an unsupported shell display or headless whole-scene save:

1. `bash cloud-evidence/cloudsea52e-integration-preparation/run_build52e.sh` was already completed; do not rerun it or overwrite the saved candidate
2. `bash cloud-evidence/cloudsea52e-integration-preparation/run_verify52e.sh` runs fresh51b and52e processes sequentially; actual evidence path is written to `tools-feiting/feiting52e-verify-last.txt`

The paired observer captures 16 images per scene at 1180×664 and frozen time0.35 with the actual default-on reflection:

- 1128,1343,1216: front, +50° side, 180° back (nine matched views)
- Three fixed close views of the real central main-ridge part
- Four staged climb camera stations, at world heights950,1200,1500,1900m

The supplementary poses derive from candidate geometry and are identical for both scenes. Bounds are used only to frame these poses. Every capture records actual cloud-triangle ray-parity status at the camera center. Each climb segment records actual cloud-triangle crossings and the live terrain/physics camera-sphere test. This does not prove cloud-surface sphere clearance, full-ship clearance or actual player-controlled flight. Blocked observations remain failures or explicit route evidence rather than being silently replaced.

The original +350m routes are tested and recorded independently for all three reference positions. The 1128 failure must remain in the paired comparison. The old1344 two-pixel conversion gate remains false and is not part of this geometry experiment.

`compare_pair52e.py` requires exact camera, environment, time, reflection, dimensions and path-physics pairing. It reports raw full-image pixel differences without a similarity score or visual acceptance claim, and creates labelled side-by-side image sheets.

## Preparation checks

- Godot4.5.1 pure `--headless --check-only` builder parse-v2 exit0; no instantiation, render or save
- Observer parse-v2 exit0
- Both shell wrappers pass `bash -n`; comparator passes Python compile
- The first builder parse invocation lacked isolated XDG directories and crashed before parsing; `build.parse.log` preserves it. It is not counted as a pass. The corrected XDG invocation is in `build.parse-v2.log`

Default project42c, saved51b, controllers, prior source assets, world generator, terrain and protected cliff master were not edited by this integration.
