# Dependency guard v2: Python-only preparation result

Both normal and optimized Python modes pass **29/29 fixture cases**. Both final
`run_intake62.py --static-only` runs return0 and produce identical checks:
**1543 total protected file identities**, retaining the original1477 manifest
unchanged and checking the full1483-file reviewed closure. No Godot, Blender,
world, display, native GDScript parse or saved-native collection was started.

The guard pins the91486-byte review gzip and its730050-byte decoded JSON by exact
SHA256. It checks all133839275 bytes represented by the1483 closure file lengths
and hashes, reconciles the exact51-file historical coverage gap, and separately
pins project.godot, UID and global class caches. The unchanged empty class cache,
absent override/extension list, and absence of new dependency `.remap`/`.import`
sidecars are mandatory. An empty new file or dangling link cannot satisfy an
absence requirement. New bytes are never adopted as an approved baseline.

The actual6884-byte graph auditor and4624-byte binary inspector are packaged
byte-for-byte under `audit-tools/`, match the sources embedded in the frozen
review, and have no geometry/scatter payloads. Their historical first-pass
limitations and replay procedure are documented there. The runner uses only the
Python standard library; it does not execute either auditor.

## What the fixtures establish

- AST parsing of the runner, guard, fixture and both original auditors
- Real current closure/startup identity pass, followed by an independent copied
  project baseline; no live input is mutated by a negative test
- Rejection of same-length edits to an omitted GDScript, a covered scene, an
  omitted imported scene, existing import metadata, UID cache and class cache
- Rejection of new autoload/remap settings, empty override/extension files,
  dangling override/remap links, new resource remaps/import sidecars, missing
  script/cache files, changed audit source and changed historical manifest
- Rejection of altered gzip bytes even when its decoded JSON remains identical
- Actual runner `main()` control flow with its launch function replaced by a
  Python mock: positive terminal path; prelaunch override blocks admission;
  postlaunch remap/cache changes clear all success flags; cancellation still
  rechecks absent-state controls
- Recheck that real dependency inputs and all frozen legacy preparation/audit
  evidence remain unchanged after the temporary-copy tests

The 29 cases run under normal Python and `python -O`; explicit exceptions remain
active without asserts. The real default static command also creates no bytecode
cache. Complete outputs and exact source hashes are in [RESULT.json](RESULT.json).

## Frozen boundaries and remaining work

The collector, plan, reused boundary index, PREPARATION_CHECK, original1477
manifest, frozen review JSON/gzip/Markdown and storage metadata remain unchanged.
The wrapper checks dependencies in preparation/manifest creation, immediately
before native launch, and in its terminal `finally` path. Even child exit0 cannot
override a failed terminal identity/absence check.

A post-run check cannot undo code already run following an external concurrent
edit. Future native execution must use a coordinated project window. These are
source/serialization identity and simulated wrapper results, not native loading,
parser, occupancy, house-membership, MultiMesh-placement or visual acceptance.
No new approved input baseline, engine run, asset or world edit is implied.
