# v6 prepared: explicit continuous native input and observed MultiMesh identity

Prepared after the fifth real-world run, retained unchanged at
`cloud-evidence/nearbay61-orbit-renderer-20261002T044043Z-8wi327py`.
That run terminated with the original 600 s internal watchdog: child/wrapper1,
609.427 s process wall, three images, 65 correctly scaled native motions,
395/395 audited samples, camera path210.949 m and ship path0. Its engine `_process`
delta totals52.6818 s. This is observed delta/wall divergence, not proof of which
operation consumed the missing wall time. No old report, image or snapshot is
modified by v6; the old runtime pass stays false.

## Exact protocol change

The prior controller waited for two consecutive camera-to-desired distances
<=.02 m after **every** <=.05 rad input. v6 instead:

1. Begins an event only with empty pending segments and matching sample/audit counts
2. Sends the existing v5 transformed native mouse event, keeping the .05 rad maximum,
   the unchanged .00001 rad result tolerance, delivered-event and matrix checks
3. Requires a strictly newer late-process frame and a successful physics audit of
   that exact sampled frame; any additional queued frames must also be audited
4. Only then permits another event. No direct orbit writes, larger steps, framerate,
   time_scale or native game/source changes
5. At each of the three named target angles, releases right mouse, waits for two
   consecutive <=.02 m actual samples and their physics audit, and captures normally
6. Startup retains the same two-sample settling. Every capture waits for its own
   actual process-frame audit **on the physics completion signal**, so returning
   cannot enqueue a new unaudited process segment before the next input

This is a different, explicit driving protocol: the camera is allowed to follow
continuously between small inputs. It does not claim the old intermediate settles
occurred. Actual camera Lerp explanation, every actual swept near-plane segment,
all physical layers including ship, isolated visible geometry sweep, native LOS,
old desired-arc sagitta preflight, unchanged anchored ship and input release remain
required. Original600 s internal /720 s wrapper limits remain. There is no new real
orbit result and no claim the new timing fits those limits yet.

`native_sequence61.gd` is a small production ordering guard also used directly by
the planned synthetic native fixture. Missing/duplicate/out-of-order samples or
audits, pending segments, overlapping events and premature captures cannot be
accepted. The full report plus actual wrapper exit and input hashes remain the
completion authority.

## Per-witness MultiMesh guard

Every inventoried MultiMesh includes hidden nodes, null bindings and nodes outside
the finite query domain. Before any process segment is appended, the late witness
reads and compares its complete current CPU buffer against the baseline:

- MultiMesh node/resource identity and mesh resource binding, including explicit null
- Instance count, visible count, transform format, use_colors and use_custom_data
- Full buffer byte length derived from exact format/count, then SHA256 of the full
  float32 buffer, including every transform/color/custom-data slot
- MultiMesh bounds/custom bounds and bound mesh surface count/AABB

No Resource.changed signal is used or assumed to cover native buffers. Missing or
failed Dictionary results, absent baseline identities, invalid counts/layouts and
null/rebound resources fail explicitly before unsafe dereferences. Full buffer
checks also run at existing physics/final checkpoints, and each stored segment
includes its exact late-process identity witness serial/frame and the physics
identity witness used for queries. Existing removal/queued-deletion, visibility,
transform, new-geometry and final identity gates remain. Newly added geometry is
classified before both late-process and physics identity witnesses; a newly added node removed
before classification now also fails instead of being silently dropped.

This is observed identity at process/physics boundaries. A mutation reverted
between all these observations is not generally detectable. It is not a proof
that mutable rendering resources never changed during the whole frame.

## Remaining mesh/material identity limits

The existing decoder audits actual saved/runtime ArrayMesh base/LOD/shadow triangle
contents when constructing the isolated query world, and classifies supported
material deformation then. Those classifications are still **not universal live
resource freezing**:

- Same-resource Mesh vertex/index/LOD/shadow contents can mutate without an ID,
  surface-count or AABB change. The new MM guard does not rehash those arrays
- MeshInstance3D mesh/resource rebinding and same-resource mutable mesh fields are
  not fully checked by this MM-specific extension
- Material/shader rebinding, code/parameter mutation and arbitrary shader semantics
  are not covered by a complete per-witness material fingerprint. Native weather
  legitimately changes time uniforms, so freezing all properties blindly is wrong
- Animated ship descendants still use the documented conservative envelope; they
  do not receive a universal live resource identity proof from this change
- Runtime rendering-server-only mutation and changes reverted between observed
  boundaries remain outside this CPU snapshot method

No universal geometry-freeze, pixel-coverage, reference-visual, hardware-GPU or
full-goal acceptance follows from this preparation or eventual light fixture.

## Small atomic progress and measured costs

`orbit-progress.json` is a compact atomic engine heartbeat, throttled to about1 s
at available main-thread checkpoints. It records stage/goal/event index,
last sampled/audited frames, pending count, progress counters, actual monotonic
process interarrival wall time and actual engine delta separately. Timers measure
preparation, source hashing, scene load/instantiate, inventory preparation and
validation, MM buffer hashing/bytes, preflight, native rays, physical/visible
sweeps, capture/rays and full report serialization. Open-operation elapsed fields
make incomplete operations explicit. Engine heartbeat cannot refresh while the
main thread is blocked; independent wrapper `<process>.progress.json` updates
about1 s with child wall time and the engine heartbeat age. It never grants a pass.

## Prepared validation, execution still pending

- Pure Python AST, main source/scope/old1477 checks, and the exact frozen saved
  dependency closure/absence checks have passed without starting an engine
- `fixture.gd` exercises actual native small MultiMeshes and the exact production
  ordering guard; `run_fixture.py --run` requires a separately coordinated actual
  DISPLAY/X11 GL compatibility window, 320x180, CPU2/<=60 s child invocation in
  an empty temporary project, no game/full world
- Planned native positives: real display/render method/driver, actual setter/getter
  round-trip, baseline full-buffer/witness layout, null-stays-null, exact event/audit
  sequence, capture after same-frame audit and monotonic/delta telemetry
- Negatives: transforms/colors/custom data, counts/visible count, null/resource/mesh
  binding, AABB, hidden/outside-domain/new-distant MM changes, removal/visibility,
  absent/empty identity, changed-then-restored buffer caught at the late witness,
  missing/duplicate/out-of-order frames/audits, pending/overlapping events and early
  event/capture completion
- Parse all four main/helper entry scripts in the coordinated light window afterward;
  this syntax-only stage may remain headless and is not a native mutation test
- Fixture and parsing success will still not establish production draw timing,
  full-world costs, native input delivery in that world or the full continuous orbit


## Correct execution backend and terminal evidence

Godot 4.5.1's dummy headless mesh storage makes per-instance transform/color/custom
setters and AABB methods no-ops. Its explicit buffer setter/getter is a separate
path. A headless fixture using the former cannot prove actual native mutations:
[official 4.5.1 dummy mesh storage](https://raw.githubusercontent.com/godotengine/godot/4.5.1-stable/servers/rendering/dummy/storage/mesh_storage.h).
The native fixture therefore uses the real graphical GL backend and retains all
actual instance setters and full-buffer/native getter readbacks. It does not
replace them with assigned fake buffers. Its changed-then-restored negative uses
the explicit buffer setter only to restore the actual earlier native buffer.
The native result records the actual display, rendering method and driver; the
wrapper requires X11 and GL compatibility with a recognized GL driver. No
framebuffer or hardware-GPU correctness is claimed by the little window.

Both wrappers use `wrapper_support.py`. SIGINT/SIGTERM are blocked across process
admission until its PID is owned, then kill the owned process group. Timeout,
logging failure, Python exception and cancellation all go through `finally`
kill/reap and terminal process evidence with the actual wait4 exit status. Child
CPU affinity is exactly two available CPUs. The fixture hard watchdog is59 s,
with a <=60 s acceptance bound; the real-orbit wrapper cannot request above its
original720 s hard child limit. There is no implicit extra termination window.
Every admitted child retains raw logs and its separate native exit report. Both
wrappers perform input afterchecks during finalization, including native result
parse failure. Main-wrapper reviewed-absence checks also run there. SIGKILL of
the Python wrapper itself or an unwritable output filesystem cannot guarantee a
terminal report and is not represented as a success.

The light wrapper separately protects the historical1477 input identities, every
file in all five saved real-orbit failure directories, and all previous/current
fixture sources. It saves full before/after manifests and exact source snapshots.
It rejects missing/changed/deleted sources, corrupt/duplicate-key/nonfinite JSON,
truthy strings, empty/duplicate/incomplete native check sets, unsuccessful child
exits, timeout, cancellation and logged engine errors. Checks cannot silently
become a default-zero success after a native script failure.

## Exact saved dependency closure now integrated

The real-orbit wrapper reuses the already verified, byte-pinned
`north-ridge62-intake/dependency_guard62.py` unchanged (SHA256
`67c53dea3c1ab20b30a30fb81e3449cb7c505bc1863eeaea823827f26568014f`).
It validates the immutable compressed review plus exact embedded/packaged auditor
identities, all1483 reviewed saved loading-closure files, the exact51-file gap
relative to the unchanged historical1477 manifest, startup/cache controls, and
reviewed absence of override/extension/remap/import sidecars. The original1477
files are still guarded independently. No baseline is refreshed or adopted.

Validation runs at static/preparation time, immediately before every admitted
renderer or check-only child, and unconditionally in finalization. Hash-only
manifest equality is insufficient for absence claims, so the full validator is
rerun after the child. The guard, compressed review and both packaged auditors
are in the input manifest and copied verbatim into each run's
`dependency-review62/` evidence directory. A final mismatch, newly appearing
sidecar or failed recheck prevents every acceptance flag.

This closes the known saved loading-dependency identity gap for this wrapper.
It does not close the live Mesh/material/shader/animated-ship identity limitations
above. Those limitations are also serialized in every full engine orbit report
under `live_resource_identity_scope`, with universal live resource freeze false.

## Python-only failure-path verification

`python continuous-v6/test_wrappers.py` runs29 isolated-copy cases. They cover
before/after guards, copied immutable-guard/review corruption, saved failure/source
changes, malformed native JSON, cancelled parse sequences, setup SIGINT/SIGTERM,
and actual Python child spawn failure, deadline, signal, logging-exception and
KeyboardInterrupt kill/reap paths. The admission-window case injects cancellation
while the child PID is being acquired. Reaping is checked by requiring a later
waitpid to report no remaining child. Mock native JSON is explicitly test data.
`WRAPPER_TESTS.json` records results and tested-source hashes; `check_static.py`
checks those hashes, so stale wrapper tests cannot count as current preparation.
No Godot, native MM, GDScript parser, full world or framebuffer runs in this suite.

No engine was started during this preparation. No new heavy world is authorized
by this file. The parent owns publication and any later engine/display scheduling.


## First native light failure and empty-resource correction

The first real X11/GL v6 light fixture is immutable at
`cloud-evidence/nearbay61-continuous-v6-20261002T054712Z-k649_9in`.
It completed with 47/48 named checks passing, child/wrapper1, and two logged
engine errors. The sole named failure assumed RefCounted ObjectIDs were positive;
the log errors were an empty SHA256 update and a delayed null Mesh lookup during
node disposal. The preceding parse pass only applies to its saved source snapshot.
Neither old result is rewritten or upgraded by this correction.

The current prepared fixture retains all48 existing names and adds13 explicit
checks (61 total). It still requires the same real X11/GL/native APIs and rejects
any logged engine error. Its current corrected source has not been parsed or run
natively yet. Python-only wrapper tests and source assertions do not count as
native acceptance.

- ObjectIDs are checked by nonzero value, live ID validity and exact object
  resolution, independent of sign. The pinned ObjectID implementation uses the
  top bit for RefCounted instances and exposes signed int64 conversion
- A count-zero full buffer hashes through SHA256 start/finish without an empty
  update. The exact format/count/length gate stays ahead of hashing, including for
  nonzero counts; the expected empty digest is checked in native positives
- CPU mesh binding is compared to RenderingServer.multimesh_get_mesh's stored
  mesh RID before any mesh AABB/surface query. The native report records both
  RIDs. This narrow binding check does not freeze arbitrary renderer state
- A fresh null binding or zero-instance/zero-visible-instance resource has no
  finite drawable bounds. Its coverage fields are null, query candidacy is false,
  and its binding/count/layout/full buffer still participates in every identity
  witness. Mesh/server surface and computed-AABB queries are skipped for it
- An earlier bound Mesh followed by CPU mesh=null is different: pinned GLES3
  ignores the null setter and retains the server RID. This mismatch is rejected
  explicitly, including at baseline creation. CPU null is never treated as
  sufficient proof of a null renderer binding
- Negative fixtures retain their original resources, restore bindings immediately
  after the rejection witness, then dispose the node. Case/stage markers precede
  mutations, witnesses and cleanup. The null and actual/queued removal negatives
  remain present; raw errors are never ignored or filtered
- New positives cover a default empty MultiMesh, a bound mesh with zero instances,
  an allocated never-mesh-bound buffer, zero visible instances, fresh empty-node
  classification and valid restoration. New negatives cover count/layout/buffer/
  visible-count/binding changes and stale CPU/server binding mismatch

The precise source chain and downloaded SHA256 identities are recorded in
`EMPTY_RESOURCE_SOURCES.json`. All links are pinned to the executed engine commit:
[ObjectID](https://raw.githubusercontent.com/godotengine/godot/f62fdbde15035c5576dad93e586201f4d41ef0cb/core/object/object_id.h),
[hashing](https://raw.githubusercontent.com/godotengine/godot/f62fdbde15035c5576dad93e586201f4d41ef0cb/core/crypto/hashing_context.cpp),
[GLES3 storage](https://raw.githubusercontent.com/godotengine/godot/f62fdbde15035c5576dad93e586201f4d41ef0cb/drivers/gles3/storage/mesh_storage.cpp),
[CPU MultiMesh](https://raw.githubusercontent.com/godotengine/godot/f62fdbde15035c5576dad93e586201f4d41ef0cb/scene/resources/multimesh.cpp),
[renderer disposal](https://raw.githubusercontent.com/godotengine/godot/f62fdbde15035c5576dad93e586201f4d41ef0cb/servers/rendering/renderer_scene_cull.cpp),
and [binding getter API](https://raw.githubusercontent.com/godotengine/godot/f62fdbde15035c5576dad93e586201f4d41ef0cb/doc/classes/RenderingServer.xml).

No engine was started for this correction. Coordinated parse and strict native
light validation remain required; no new full-world run is authorized by it.
