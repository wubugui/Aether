# Shadow v3 first native attempt: preload-class member parse rejection

2026-10-02 09:29 UTC. Child and wrapper exited 1. Actual child duration .505774035 seconds, peak 117600 KiB, CPU2; no timeout. All protected input and full 1483-file reviewed dependency/startup/absence identities stayed unchanged.

The collector never initialized and no mesh was read. Godot rejected line 69 of read_proxy_meshes62_v3.gd: `Cannot find member resource_path in base .../visible_geometry61.gd`. The expression `ShadowAudit.resource_path` refers to a preload class as though its Script resource property were a class member. The actual helper source-hash guard must remain, but resource_path must be obtained from the script resource of the actual helper instance (with an explicit type check), not that invalid class-member expression.

Both original engine error lines are retained in stderr and wrapper.log_errors. No native-proxy-meshes report exists, so the wrapper additionally reports FileNotFoundError; that is secondary to the parse error and not evidence that a mesh read started. No world, geometry, source asset or original helper changed.

Original v3/freeze/failed outputs remain immutable. A separate one-point API/type compatibility correction is being prepared, with all six-mesh/rock bindings, strict all-LOD shadow equivalence, exact snapping and existing helper-SHA verification retained. No automatic retry, tolerance change or additional audit scope is authorized by this failed run.
