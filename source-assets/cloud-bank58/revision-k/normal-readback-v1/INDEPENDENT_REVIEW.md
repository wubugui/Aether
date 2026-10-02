# Independent preparation review

Reviewed 2026-10-02 by a separate read-only reviewer. This is code/pure-test
approval only, not permission to launch and not actual native validation.

Initial review withheld approval because the inherited camera helper modifies
the active scene camera and render resolution/aspect. That finding was fixed in
this new collector only. The old helper and all frozen prior code remain unchanged.
The collector now computes camera projections using explicit saved camera metadata,
without assigning scene properties, and verifies active camera plus five render
fields before/after. No restoration-based mutation is needed.

The reviewer then approved the revised code, independently reran normal and
optimized Python (10 methods each, including 384 separate face-normal reversal
controls), and exercised a pure fake camera forbidding property writes plus
individual mutations of all six scene-state fields. All passed. PID type,
exact two-integer CPU affinity and binding to the supervising wrapper were also
hardened following review.

Reviewed scope: original source SHA and full identity, exact saved geometry,
384 polygon/1,152 corner normal arrays, loop ownership/bijection/vertex mapping,
float32 integrity, unchanged 3e-5 source-normal gate, original failed GLB exact
round/normalize replay, raw arrays saved before validation, native terminal SHA/PID
binding, actual wait4, CPU/RSS/wall guards, kill/reap, source/input/main-project
before/after hashes and one-shot markers. No remaining code blocker was found.

The sole Blender operator is opening the existing source. No source save, export,
Godot, rendering, image, GLB patch, project mutation or native execution occurred
during preparation or review. Final frozen-file verification is recorded separately
after the manifest is created; the parent owns scheduling and publication.
