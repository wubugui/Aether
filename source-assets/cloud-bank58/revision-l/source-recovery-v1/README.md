# L source recovery v1: shared groups and fixed projection sampling

2026-10-02 UTC. **Preparation only: no Blender/Godot/native process, source save, fresh-open or render was executed.** No Git or Slack operation is part of this preparation. Independent narrow review and full GitHub-plugin publication/readback must precede a separately authorized real source attempt.

## Scope and original failure

This is the sole explicit recovery of `cloudbank58l-source-runner-v3-source-20261002T175127Z-synllgmt`, published as commit `b896f45d96ca07f33886b5931204d75db68ba878`. That run really exited 1 at shared-group identity before saving; its 14-group raw, failed terminal, launcher observation and review stay unchanged. It is not reset, relabelled successful or replaced with a simulated result.

Original admission SHA-256: `3fc9d27fe46f83fc279b0902a852ac895c8c59a2d77e93f66a1fa651c5fee597`. Original failed terminal SHA-256: `19bd0c016af2cb4ebae751e27f250408bdd30327e56792a69bb5c52e99102dc4`. Original independent review SHA-256: `945a189a66fe4fd0a74ce2103838e96efbc2842577f4eb4d17cfaec855179a05`.

The parent verified all original remote bytes and restored the two unique gzip streams into four exact original JSON files in a fresh empty directory before this preparation began. `SOURCE_BINDING.json` pins the specific failure chain. A fresh checkout must restore the original failure's four JSON files with its existing `restore_storage.py` before using this package; no raw, candidate, model or 2 MB preparation bundle is copied here.

Only this new `source-recovery-v1/` directory is written. Original source-v1, runners v2/v3, all candidates, geometry, material, camera transform/projection bytes, gates, historic evidence and project progress are untouched.

## Two actual source changes

1. Master and hidden derived export still reference one canonical mesh. `create_shared_groups` checks that sharing and empty initial group tables, creates the seven groups **once on the master**, fills the same float32 weights, then requires both actual object tables to expose exactly those seven names. There is no `.001` filtering, raw rewriting, name/weight/membership relaxation, independent export mesh or new model.
2. The original self-imposed square-pixel sampling was inconsistent with the frozen frustum. It is explicitly replaced by a derived, slightly non-square pixel aspect, while output remains **1179 × 664 at 100%**, original poses, original frusta, lens/sensor settings, normal K material and lighting remain fixed. This is sampling calibration, not camera movement/reframing or a new reference-resolution guess.

Each of the four frozen projections is decoded separately. All four projection byte strings and exact rational P11/P00 ratios agree:

- P00 = 0.9366548657417297; P11 = 1.6642794609069824
- P11/P00 = 27921976/15714461 = 1.7768331984151413
- Pixel aspect x/y = (P11/P00) × 664/1179 = 18540192064/18527349519 = 1.0006931668767207
- Actual Blender float32 setting: `[1.0006932020187378, 1.0]`

A differing fourth ratio is rejected; no mean or tolerance merges distinct frusta. Native capture obtains x/y, percentage and pixel aspects from the **actual scene render RNA** and passes the same stored aspects to `calc_matrix_camera`. Each camera raw now records `projection_sampling`, checked against the actual captured settings. Renderer and camera-calculation paths use the same values. Original declared transform/projection bytes and original transform ≤2e-6 / projection ≤2e-5 gates are unchanged. The settings gate remains exact, now requiring the precisely derived stored float32 aspect rather than `[1,1]`.

The ideal algebra with stored float32 aspect predicts P00 = 0.9366548328485901, only about 3.29e-8 from frozen. This is **pure prediction, not native proof**. Real save/fresh-open/render must still provide the actual matrices and pass the unchanged gate. Relevant pinned Blender semantics: [RNA camera API](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/makesrna/intern/rna_object_api.cc) forwards scale_x/y as pixel aspect; [camera view-plane calculation](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/blenkernel/intern/camera.cc) uses ycor=aspy/aspx and VERTICAL viewfac=ycor×height.

## Minimal derivation and unchanged checks

`SOURCE_DIFF.patch` shows complete differences against original native/support and runner-v3 source. Only those needed source files are derived. `geometry58l.py` is a small path adapter that verifies and executes the original geometry source bytes, then points candidate/bindings to the old originals and the new save path below. The embedded `GEOMETRY58L.py` remains the **original exact bytes**, so editable .blend reconstruction has no adapter-file dependency.

Original candidate is unchanged: 1567 vertices, 3130 triangles, seven controls plus valley width, prior eleven finite geometry states and profile work remain the prior evidence. They are not re-created or promoted to new native evidence. Eight exact non-auto-run embedded Texts remain; candidate and bindings embedded bytes are identical to the original files. Explicit rebuild/control/manual editing, nonaccumulation, restoration, complete raw capture, complete native validation, one save and independent no-save fresh-open are retained.

The launcher derives from v3 only to adapt paths and bind this one failure. It directly imports the already reviewed `source-runner-v3/deadline58l_v3.py`; no process supervision rewrite or new R1/R2/R3 framework/tests are introduced. Complete actual trial state/manual-combined checks, stage-specific protection, actual launcher completion authority, PID association, source SHA, raw SHA and all original stage verification remain. Only this recovery's absent exact outputs are excluded; old admission/terminal/evidence remain protected.

`recovery58l.py` permits precisely the two SHA-pinned old failed source attempt/terminal files and explicitly rejects old success, a saved old source, a different failure, other old/new runner or recovery attempts, and any second attempt at this recovery stage. Views may retain this recovery's source attempt/terminal only while the unchanged full successful `prior_source` chain is separately required. Records bind `recovery_of_failure_sha256` through admission, worker and supervisor.

## Future execution, still closed until review/publication

Unique future output:

`source-assets/cloud-bank58/revision-l/source-recovery-v1/cloud_bank58l_recovery_v1.blend`

The original source-v1 .blend was never saved and must still be absent; a saved old source causes rejection. Recovery output must be absent before source. There is no overwrite/fallback build, duplicate source or automatic retry.

Default `python run58l_recovery.py` and `python native58l.py` do nothing. Only after this preparation is independently reviewed, completely published via GitHub plugin and remote bytes verified may the parent explicitly launch `python run58l_recovery.py --run-approved source` **once**, using the real external caller observation method already established for v3. Launcher exit must be actually waited for; `prepared_passed` alone never means accepted. Keep all actual successes/failures, attempts, original raw and logs. No auto-run happens here.

Source: save once then independent fresh-open, total <120 seconds, CPU2, native build cap80s/verify30s, aggregate RSS limit1.5GiB and 20-second finish reserve. Views remain an independent one-shot stage, <120s total/render cap27s each, same CPU/RSS/reserve. Source complete evidence must again be plugin-published and remotely verified **before** `--run-approved views`. Four original absolute cameras and normal source material are retained; full contact J_i implementation is not made a prerequisite for seeing the isolated source.

`source_diagnostic_only=true`. Full contact, world, visual, weather and global GOAL acceptance all remain false. No new native validation or image exists yet.

## Focused preparation tests and freeze

Run `PYTHONDONTWRITEBYTECODE=1 python test_recovery58l.py` and repeat with `python -O`. Tests use pure fixtures, actual old failure read-only identities and mock group RNA; they never launch an engine. Coverage: one shared allocation and exact weights; old loop's fourteen-group mock reproduction; empty extra/weight/membership rejection; four exact ratios and mismatched-camera rejection; actual render parameter sourcing; old square sampling, original P00 mismatch, pose/hex changes rejected; complete pure capture; unique unsaved original failure and duplicate admission guards; unchanged edit/exercise/protection functions and resource constants; exact original candidate/geometry/Text reuse; all 208 prior dependency bytes unchanged.

`DEPENDENCY_SHA256.json` freezes the prior dependency/evidence bytes, not a model backup. `FINAL_SHA256.json` adds this package's preparation inputs; the runtime also hashes the freeze itself. `PACKAGE_MANIFEST.json` inventories every delivered file other than itself and SHA256SUMS; SHA256SUMS covers that inventory plus the manifest. Review additions must be separately inventoried by the publishing parent; no preparation file is silently rewritten after review.
