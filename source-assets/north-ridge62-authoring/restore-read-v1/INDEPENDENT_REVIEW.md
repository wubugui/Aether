# Independent preparation review: restored-source read

Reviewed2026-10-02. Scope was source/AST inspection, independent execution of22 pure tests in normal and optimized Python, and an engine-free read of the parent's already restored four-file tree. No Blender/Godot was launched, no real source was restored/copied, no saved source was opened natively, and no image was created by this review.

## Outcome

**Prepared read-only probe passed independent source review and pure checks.** Native restored-source fresh-open remains pending. This is not full external-delivery completion, visual acceptance, support approval or world integration.

The actual existing restore root `/tmp/aether-native-reconstruction-z_1vwkc3/restored` passes the strict4-file/7-directory layout from the original storage manifest. Every restored size/SHA equals the original manifest, including the10,004,835-byte source `dd1d3c12b8c3f98fdcd42a21057d519f1cac48eeab468cbc7721d1c1673ab502`. No new reconstruction was performed. Original storage contract,11 chunks, canonical source/raw evidence and inherited115-file freeze plus its own manifest are rechecked by preparation_inputs.

## Read path and equivalence

- The only native open call uses the explicit restored-source argument, `load_ui=False`, `use_scripts=False`, and wrapper `--disable-autoexec`. It cannot select the canonical source through its accepted path contract
- Absolute normalized paths are required. Root must be separate from the original repository and its ancestors/descendants. Symlink ancestors/files, hardlinks, wrong source path, extra/missing files or directories and altered size/SHA reject before native admission
- Actual `bpy.data.filepath` is recorded before checking it against the supplied restored source, preserving the observed path even on mismatch
- Capture and validation directly reuse frozen recovery-v2 code. No native save, rebuild, render, export, world load or validator substitution appears in the probe. Actual raw is persisted before validation
- Full raw identity is compared to the original successful build after omitting only top-levelPID andCPU affinity. SortedJSON comparison additionally preserves number/boolean types and signed zero rather than relying on Python's permissive numeric equality
- A review-found false gate was removed: numeric historical PIDs can repeat across wrapper runs/namespaces. Freshness instead depends on this new one-shot process launch, actual wait4 completion, matching terminal/raw/current-childPID, and the exact restored filepath. Tests explicitly allow repeated historicalPID while rejecting a wrong current launchPID or opened path

## Protection and execution boundary

The new entry keeps the unchanged audited process helper, one child capped30s, a60s admitted-wrapper budget, CPU2 and1.5GiB aggregateRSS. Eight seconds are reserved for final protection checks. Read-only path/input qualification also occurs before admission. The wrapper never restores a missing file or falls back to opening the canonical source.

Before/after protection includes all source-assets and their directories, including the actual canonical `.blend` and all old attempt/terminal files, original blender/assets/ref, root project.godot, the complete main project/caches and original successful run evidence. No recovery-v2 mutable exclusion is inherited. The restored four-file tree and new native outputs are independently protected. Original-source and restored-source SHA must stay identical throughout.

The exclusive attempt marker is made once before the original tree snapshot and is not subsequently changed. Completion evidence lives only in the new evidence run. Failure leaves the attempt/evidence intact; no native retry is introduced.

## Pure verification

Independent reruns passed22/22 methods in both ordinary and `python -O` modes. Coverage includes exact layout, source-path restrictions, symlink ancestors/files, hardlinks, extra/missing files/directories, same-length byte changes, directory membership changes, complete raw differences, numericPID reuse, launchPID/path binding, no-launch default behavior, inherited canonical-source protection, raw-before-validation failure retention, and preservation of the actual wrong opened path in failed reports.

The tests' `NORTH62_STAGE` lines are explicitly from tiny fake-bpy fixtures, not actual Blender telemetry. Fixture files are synthetic text and removed after tests. No test executes the restorer, copies the real10MB source or starts an engine. The real original14.8MB raw is read as JSON for validator/negative-control tests only.

The known restored root default preflight passed again after independent tests. The next allowed runtime step is the separately scheduled single native command in README. All167 support cases, four source views, world/weather/visual acceptance and completeGOAL remain open.
