# North ridge62: independent recovery-v2 preparation

## Status and immutable failure

This is an implemented recovery pipeline, prepared and pure-tested only. No Blender/Godot, blend or PNG has been executed/created by recovery-v2. It never changes the original build-v1, its failure or its frozen candidate shape.

The first source attempt remains failed at `cloud-evidence/north-ridge62-source-20261002T111415Z-wlgkmd5l`: wrapper1/55.138630s; actual first Blender child−9,48.703885s against48.651942s granted, timeout=true,338460KiB childRSS/390320KiB observed aggregate. Its stdout/stderr and outputs are empty; no `.blend`, no fresh verification and no views exist. All77 frozen input identities and7336 original file identities remained unchanged. This is a timeout with no native stage heartbeat, not proof of a particular stalled function.

Original preparation manifest `12d9f492d3ae1251d37f6b8b94e9e5877eb85dd96f723f97542a5c4885818702`, build-v1 freeze `5f330a85d21da0ffdf3c57c6183b52e86bb6b4c0fa976431946a6f9a46afcc49`, and full frozen candidateY `2eca5d39aedc03678f7d4611aa8aa497bb616ec9e7b5bade5da16db5284d13d5` remain unchanged. Recovery reads the exact existing `build-v1/bindings62.json` and `build-v1/offline-mapping/`; no duplicate/modified binding is generated.

## Most likely code costs, without claiming a measured root cause

The five authoring terrain objects contain28,681 attribute vertices and16,384 triangles. Source v1 made24,566 single-vertex group calls and278,600 per-element custom-attribute writes, plus32,768 polygon setters. Its capture also reread each attribute's RNA type inside the element loop. See the independent [cost review](COST_REVIEW.md) for exact counts and official API/source references.

An earlier, stronger static candidate is the5,424,727-byte compact binding, all on one line, passed to `Text.write` before any terrain is constructed. The inspected official4.5 implementation inserts the first line character-by-character and repeatedly copies it, yielding quadratic cost. Its4.5.14 RNA route is confirmed; the exact4.5.14 `text.cc` body was not retrieved, so this is a supported code-path hypothesis rather than a measured48.7s stop location. `from_string` follows the same writer and would not fix that path.

## Equivalent changes implemented

1. `native62.text` writes the **same intended embedded bytes** to a new evidence-only file and uses official `bpy.data.texts.load(filepath=..., internal=True)`. Every text then requires identical `as_string().encode()` bytes, `is_in_memory=true` and empty filepath. The binding's embedded compact form intentionally has no terminalLF, exactly as v1; the original on-disk binding has one terminalLF. Source code/readme texts retain their existing terminalLF. There is no strip/pretty-print/reformat/truncation, and no external temporary-file dependency in the blend
2. `bulk62.weight_batches` groups only identical native float32 weight bits for the same group, retaining every positive source membership.24,566 memberships become7,192 `VertexGroup.add` calls. No threshold, weight quantization policy, group count or membership is changed
3.11 custom attributes per mesh use55 `foreach_set` calls, with the same float32/int32/bool values and all original schemas. Polygon flags/material indices are also batched. All layer allocation finishes before any Attribute/data handle is retained, preserving the previous RNA lifetime fix
4. Capture uses `foreach_get` for complete actual vertices, attributes, polygons, normals and loops. Nested deform groups still read **every real native group membership**, not planned weights. Actual schema and all loop data are saved in raw before their validation. The old complete float32/source-mapping/group/normal/material/camera gates remain; schema/loop/internal-text gates are added
5. `BULK62.py` is a fifth internally packed editable Text. The other four original text roles remain, and the native validator verifies exact code/data hashes and internal status. Rebuild remains self-contained, explicit and unsaved, with Edit Mode/object-transform guards

No control point, footprint, candidate elevation, seam policy, original source split vertex/index/localXYZ/RGBA, surface winding, original camera pose/FOV, material formula, render sampling or image dimensions changed. One27-control/15-handle source still derives one shared4326-position surface and four original attribute-slot tile meshes. All167 support cases remain nonaccepted; this recovery performs no scatter or world integration.

## Native telemetry and unchanged evidence rules

A flushed `NORTH62_STAGE` JSON line is written at Python entry before bpy/NumPy imports, then before/after binding checks, factory reset, each embedded text, each mesh, weight batches, evaluation, native capture, raw persistence, validation, save, reopen and rendering. Native events are also appended+fsynced to per-stage `*-events.jsonl`, with latest `*-progress.json`. Each event records actualPID, elapsed time since Python telemetry started, cumulative process user/system CPU seconds and peakRSS. These are stage observations, not successful completion claims.

The actual native raw is saved before validation, and actual terminal reports remain required. Fresh reopen compares the entire native raw identity apart fromPID/affinity. No-save sourceSHA is held across every verify/render stage and final protection check. Embedded file inputs and all other output files are recursively SHA-protected between stages.

The wrapper still directly reuses unchanged `bounded_support58k.run_child` for CPU affinity, true wait4 status/RSS, timeout, kill and reap, and unchanged `run_import58k.file_manifest` for full original protections. No replacement process framework is introduced. Whole source-assets, blender/assets/ref, root project.godot and the actual main project including caches/sidecars stay byte/membership protected. Old failure artifacts are frozen as additional inputs.

## Explicit new finite budget

The old60s source attempt remains a failed60s attempt. Recovery-v2 is a separate one-shot source attempt with **120s total wall**, build child capped75s, independent fresh-read child capped30s,8s reserved inside the total for final original-input checks, CPU2 and1.5GiB aggregateRSS. This allows one instrumented build+freshread at the actual28,681-vertex/5.4MB editable-text scale without repeatedly hitting the old60s ceiling. It is not a performance pass or automatic extension.

The views stage remains **90s total**, exactly four1179×664 PNGs at100%, original1131/1347 poses and verticalFOV55, plus the unchanged side/back source diagnostics; CyclesCPU2/8samples/no denoise. No reduced resolution or additional tuning loop. Both stages are independently admitted once, retain failures, and require parent scheduling with other source writers paused.

Safe default, no engine:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-authoring/recovery-v2/run_source62.py

Only after scheduling, one actual source build+fresh reopen:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-authoring/recovery-v2/run_source62.py --run-approved source

Only after that actual gate passes, separately scheduled original four images:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-authoring/recovery-v2/run_source62.py --run-approved views

The only candidate source destination is new `recovery-v2/north-ridge62.blend`. New evidence uses `cloud-evidence/north-ridge62-recovery-v2-{source|views}-...`. Never rerun v1 or overwrite its failure.

## Pure verification and remaining uncertainty

`test_recovery62.py` normal and `python -O` each pass17 methods, covering all24566 group membership bits,55 full attribute buffers479367 scalar components, entire fake-RNA construction, stale-handle negative control, exact text byte preservation, changed-shape/source/camera/weight negative controls, immutable77-input v1 identity and retained timeout evidence. Fake RNA checks recipes and API call contracts; it is not native Blender validation. Independent review also compares unchanged geometry/authority functions against v1.

Actual Text loading, native foreach semantics, saved/fresh source, runtime budget and all four images remain untested. World source materials/weather/cloud visibility,167 support, hardwareGPU and completeGOAL acceptance remain open.
