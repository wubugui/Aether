# Corrected v6 real graphical fixture:61/61 passed

Official Godot4.5.1, X11/gl_compatibility/opengl3 on Mesa llvmpipe,320×180: child/wrapper0,1.587523176 seconds,261028KiB,CPU2; the original59-second watchdog/60-second acceptance bounds were not triggered. Raw stdout/stderr and61 named native checks are retained. No engine errors. All1587 protected old inputs and39 current source inputs were unchanged. This is software rendering, not hardware-GPU acceptance.

All48 prior checks remain and13 new edge cases passed. Actual native instance setters/getters and full160-byte transform/color/custom buffer round-trip pass. Negative resource IDs resolve to the actual live RefCounted objects. Empty buffers hash to the native SHA256 empty digest without an invalid empty update. Fresh empty/zero-instance/zero-visible/null-mesh bindings retain complete identity and no fabricated finite drawable bounds.

The stale CPU-null/GLES3 server-RID discrepancy was directly observed: CPU mesh RID0 while server retained670014898183. The guard rejected it before unsafe bounds reads; restoring the retained original mesh restored the baseline. Mutation/removal/queued-removal, visibility, distant/hidden buffers, late mutation then restoration and exact process/physics ordering negatives all remain active. Disposal diagnostics are preserved; no errors were filtered.

This fixture loads no game world, captures no game images and does not prove real-world timing, full orbit completion, pixel coverage, mutable Mesh/material/shader universality or reference visuals. orbit_runtime_passed remains false. The first failure at20261002T054712Z is immutable and remains failed.
