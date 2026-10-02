# L first actual isolated source attempt: rejected at native group identity

2026-10-02 UTC. Executed only after preparation commit `cc4cce48963459683ea6ae5c72e3d12439571f2a` had been uploaded using the GitHub plugin and all 33 paths/33 unique blobs independently read back byte-for-byte. No renderer or follow-on attempt was launched.

## Actual outcome

- Caller started the real launcher at 17:51:27.572968 UTC; launcher PID 5 returned 1 after **16.113453020 seconds**, measured from before Popen until actual wait completion, not tool waiting time
- Supervisor observed worker PID 6 return 1 after 16.037445594 seconds; ownership remained observable and all children were reaped
- Official Blender 4.5.14 build PID 7 returned 1 after **2.107592981 seconds**, CPU affinity [0,1], native peak 284080 KiB; no wall-time or RSS limit fired
- Native creation reached 1567 vertices/3130 triangles and persisted a complete 1,556,139-byte raw capture. The failure capture is exactly the same bytes
- **No source saved, no fresh-open executed, no PNG or world changes.** `saved_source_unchanged=false` means the new output does not exist; it does not indicate damage to an older source
- All 152 frozen inputs and 14014 protected pre-existing files remained unchanged during the operation. Earlier outputs were unchanged; external observation found no remaining owned PID

The overall 16.113 seconds includes preparation and complete project protection checks. It must not be described as 16 seconds of Blender execution.

## Actual rejection and bounded diagnosis

The unchanged complete validator stopped at `Actual vertex group identities`. Expected groups were the seven `CONTROL_C01_Crown_A` through `CONTROL_C07_Meso_Relief` names. Actual RNA has fourteen names: each expected name is followed by an extra `.001` name, in both `L58_EDITABLE_MASTER` and `L58_DERIVED_EXPORT`. The capture confirms exactly one `L58_CANONICAL_MESH`, shared by those two objects.

The frozen creation loop calls `master.vertex_groups.new(name=name)` and then `export.vertex_groups.new(name=name)` for each of the seven controls. In this actual shared-mesh run, both object tables show both creations. This is direct source/RNA evidence of the group-creation conflict; the seven-group gate correctly rejected it. It is not a reason to accept fourteen groups, drop names from captured evidence, or relax the native validator.

Checks after that gate did not execute in the real native validator. The pure candidate geometry had previously passed its bounded checks, but that is not full native acceptance. Any in-memory hypothetical remapping used in independent diagnosis must remain labelled hypothetical and must not modify the actual raw capture.

The independent review confirmed that all seven extra `.001` groups are actually empty across all 1567 rows and memberships. In a clearly hypothetical in-memory copy only, it removed those empty names and remapped even group indices to 0–6. The original unchanged full validator then rejected `Actual fixed camera numerical transform/projection`: all four actual P00 entries are 0.9373040795326233 versus frozen 0.9366548657417297, a difference of 0.0006492137908935547, exceeding the unchanged 2e-5 gate by about 32.46 times. Other projection entries agree; pose error is at most 2.2352e-7. The frozen P11/P00 ratio is approximately 1.776833198 (close to 1672/941), whereas the current 1179/664 square sampling is approximately 1.775602410. This identifies a second prospective calibration issue; it is not a second executed native attempt or permission to reframe a camera or widen tolerance. No actual raw file was normalized or overwritten.

The native stdout records exact Text loading/readbacks, source construction, capture and rejection phases. The external caller code and actual process observation are in `external-caller/`. The original factual observation was written before subsequent source-chain validation; validation remains false for this failed run. No one-shot admission is deleted or reset.

## Storage and next gate

See `STORAGE.md` and `storage.json` for lossless storage of the two unique large raw byte streams, including the identical before/after and raw/failure aliases. Small original logs and native input/readback records stay direct. Model output is absent, so there is no model file to upload or reconstruct from this attempt.

First publish this entire failure, caller/runner observations, raw storage, independent review and progress entry through the GitHub plugin; independently verify remote bytes and exact raw reconstruction. Only then may a separate minimal recovery correct shared group creation and explicitly reconcile original fixed projection with native sampling. Keep geometry, seven expected group identities, material, original camera poses/projections, resource limits and full native checks. Do not silently relax the projection gate or claim that fixing only groups suffices. No automatic rerun, fallback build, visual/contact/world or GOAL acceptance is authorized by this failure report.
