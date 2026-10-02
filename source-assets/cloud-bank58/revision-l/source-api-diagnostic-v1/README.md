# L API-consistency isolated diagnostic source v1

2026-10-02 UTC. **Preparation only. No engine/native process, .blend save, fresh-open, render, new stage admission, commit or upload has run.** Only this new directory is written. Parent narrow review and complete GitHub-plugin publication with actual remote readback are prerequisites for one future native source attempt.

## Why this is a new diagnostic acceptance mode

Original source-runner-v3 failed before saving because the shared mesh exposed fourteen groups. The subsequent source-recovery-v1 fixed the seven shared groups and original four projection sampling, but genuinely failed the original corner-to-mathematical-geometry normal criterion. Both consumed attempts, native failures, raw bytes, wrapper/launcher records and historical findings are retained, not reset.

The recovered default raw still fails that old **3e-5** criterion: **22 faces; maximum component difference 0.00015941344933428914; maximum angle 0.009158468662372497°**. Polygon normal RNA uses triangle cross products, while flat corners use cached sequential-float32 Newell normals in Blender 4.5.14. The frozen official-source/read-only diagnosis and narrow review remain in the second failed run. API agreement does not satisfy the old geometry comparison.

This package explicitly changes the **comparison semantics** for one isolated diagnostic mode. It does not change geometry, normal data, winding, thresholds, material, lighting, original camera poses/frusta, seven shared groups, float32 sampling or the 1567-vertex/3130-triangle candidate. It never writes a computed normal to mesh or raw, and contains no normal repair/remeshing or full-contact expansion.

## One oracle, separate facts

`native_support58l.validate_normals` reads actual vertices, faces, flat flags, polygon normals and all corner normals. It independently requires:

- Polygon-to-mathematical-geometry maximum component difference ≤3e-5
- Finite nonzero unit normals, outward agreement with the original oriented geometry, flat polygons and exactly equal three corners per triangle
- Actual corner-to-sequential-float32-Newell maximum component difference ≤3e-5, explicitly named API consistency rather than the old criterion

Sequential float32 arithmetic uses stdlib `struct` at every subtraction, addition, multiplication, accumulation, squared-length operation, square root and division. NumPy is used only in the pure independent replay test; the embedded support introduces no new dependency.

For every checked state the report also records the actual old corner-to-geometry maximum difference, failed face IDs, maximum angle and `original_corner_geometry_passed`. That boolean may genuinely be true or false for a particular edit/control test. A separate SHA-bound `historical_default_failure` always retains the original 22-face failure. `full_native_acceptance=false` never changes.

The saved scene has `acceptance_mode=api_consistency_isolated_diagnostic_v1`, `full_native_acceptance=false`, `historical_default_corner_geometry_passed=false` and the existing source-only/false world-contact-visual-GOAL flags. Capture checks those actual RNA properties. The embedded README explains the change and old failure. Admission, child, worker and supervisor records all identify the diagnostic scope; only the externally observed supervisor completion can grant diagnostic stage acceptance. Worker preparation remains `passed=false` until the existing completion-authority chain is checked.

Build, independent fresh-open and each pre-render baseline use the original complete `geometry.validate_native_raw`, whose support import resolves this single oracle. Moved/restored control states and manual/combined/restored states invoke the same complete capture validation and retain individual normal results. The wrapper independently recomputes and compares them, preserving exact prescribed control/PID/geometry/identity checks. Actual post-render raw uses the same normal oracle and unchanged actual mesh/material/camera identity; the restored raw receives the complete capture validator. The raw records are never edited to normalize temporary render settings.

## Exact chain and unique output

`SOURCE_BINDING.json` pins both original failure chains and commit `4cbe1f7cbf1ff690a2d2bd4693e42da5034309e2`:

1. source-runner-v3, run `cloudbank58l-source-runner-v3-source-20261002T175127Z-synllgmt`
   - Admission `3fc9d27fe46f83fc279b0902a852ac895c8c59a2d77e93f66a1fa651c5fee597`
   - Failed terminal `19bd0c016af2cb4ebae751e27f250408bdd30327e56792a69bb5c52e99102dc4`
2. source-recovery-v1, run `cloudbank58l-source-recovery-v1-source-20261002T183837Z-52w0vvfv`
   - Admission `b8cc9985e206be4fc8f69b80c6e51ebebccaac4e8b1eb177ad6ced4784efe814`
   - Failed terminal `ab1e24362106a9c0be9cf3cd3c892cce3f10f0972bd987dddceb0fb6537934c7`
   - Supervisor `01fdc93d2f847ab7285f69dd5e593b19fc83c5909aff4f09d2cdbf2c76c6e144`

Only those four exact old attempt/terminal files are allowed as prior consumed admissions. Their full source failure chains must still be failed, unsaved, actual-exit-observed and reaped. Old success, other attempts, any second new attempt, wrong outputs or an existing old/new .blend are rejected. All old records remain protected; no record is deleted to retry. Views may retain the new source's records only while the independently successful full source chain is separately required.

The sole new future output is:

`source-assets/cloud-bank58/revision-l/source-api-diagnostic-v1/cloud_bank58l_api_diagnostic_v1.blend`

No candidate, old model, raw or preparation bundle is copied here. The path-only geometry adapter executes the exact old source-v1 geometry bytes. Original candidate, bindings and geometry are embedded unchanged; native/support/README reflect the diagnostic mode. Eight non-auto-run Texts, explicit editing, one canonical shared master/export mesh, all controls, manual edit preservation, nonaccumulation and exact restoration remain.

## Existing supervision and future execution

`run58l_api_diagnostic.py` derives only from source-recovery-v1 and directly imports the reviewed, unchanged `source-runner-v3/deadline58l_v3.py`. There is no new supervision framework or process test. `SOURCE_DIFF.patch` contains the full narrow code differences from source-recovery-v1, including the two-failure admission helper.

Default calls to the runner and native adapter are no-ops. After the parent reviews and completely publishes/readbacks this package, the parent may explicitly invoke **once**:

`python -B source-assets/cloud-bank58/revision-l/source-api-diagnostic-v1/run58l_api_diagnostic.py --run-approved source`

This is the actual bound entry for build → editable control/manual exercises → one save → separate no-save fresh-open → the same full exercises. CPU2, total <120 seconds, native build80/verify30, aggregate RSS1.5GiB and 20-second finish reserve are unchanged. The external caller must actually launch/wait and observe launcher exit0 within120s and then verify the complete source evidence; preparation or a self-reported receipt is insufficient.

All real source results, including failures, must again be fully plugin-published/readback before the separate one-shot `--run-approved views`. Four original absolute cameras, 1179×664, calibrated float32 sampling `[1.0006932020187378,1]`, Cycles CPU8 samples, per-render27s, total120s remain. No world integration, full contact, visual, hardware GPU or global GOAL acceptance is claimed.

## Pure checks and freeze

`python -B test_api58l.py` and `python -B -O test_api58l.py`: **51 tests pass each**. Tests cover unchanged source/geometry/groups/sampling, actual historical raw API replay and actual old-validator failure, finite/outward/flat/three-corner/API/polygon negative controls, true per-state old criterion without erasing history, exact two-failure admission, duplicate/foreign attempts, the complete prescribed control/manual wrapper and unchanged budgets/protection. Small tetrahedron fixtures are expressly synthetic; no fixture is represented as actual Blender output. `HISTORICAL_RAW_REPLAY.json` is a pure reanalysis of the unchanged failed run, not a new native result.

The first test-run log has a missing-import assembly failure; the later 51-test attempt has one stale expected-error-text failure because the new report-consistency gate rejected the deliberately altered fixture earlier. Both logs remain. The fixture now recomputes its diagnostic report before checking the unchanged prescribed-state rejection. Final normal and optimized logs are retained, and do not falsely describe those earlier runs as passing.

`DEPENDENCY_SHA256.json` captures prior immutable dependencies and both failures. `FINAL_SHA256.json` adds this preparation's runtime inputs and evidence; runtime also hashes the freeze itself. `PREPARATION_CHECK.json` records the final pure checks and absence of native output/admission. `PACKAGE_MANIFEST.json` inventories every delivered file except itself and SHA256SUMS; SHA256SUMS covers those plus the manifest. Parent review/progress additions are inventoried by the parent; this preparation is frozen for narrow review.
