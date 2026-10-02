# Independent recovery-v2 review

Reviewed 2026-10-02 UTC. Scope: read-only comparison with build-v1 and retained failure evidence; Python/NumPy/AST checks; mock buffer readback; official Blender source inspection. This reviewer wrote this report only. No Blender or Godot process was started, and no `.blend` or PNG was created or inspected.

## Outcome

**Offline equivalence review passed. No blocking shape, binding, native-readback substitution, or batching-equivalence defect was found.** This is not a native API execution pass, saved-source/fresh-reopen pass, timing guarantee, visual acceptance, integration approval, or authorization to run an engine. Final preparation freezing remains the author's separate step.

A diagnostic issue was reported immediately and fixed before the final review: binding read/check now runs inside the main `try/finally`, with a `binding.validation.begin` marker, so binding exceptions reach the failed-result path. The reviewer checked that placement by AST. Early telemetry begins before importing bpy and NumPy, but it cannot observe Blender startup before Python entry.

## Independently checked identity and geometry

- All 77 files in original build-v1 `FINAL_SHA256.json` matched both frozen byte lengths and SHA-256. Freeze SHA: `5f330a85d21da0ffdf3c57c6183b52e86bb6b4c0fa976431946a6f9a46afcc49`.
- Original failed wrapper report remains failed, with no saved source, original-protection pass, and total wall 55.13863025000319 seconds. Report SHA: `8a89a9467a59d2ef971f07cc35bddfbf0d042d842ac3654191a97af55d024d50`. The reported child timeout and empty stdout/stderr/outputs establish failure, not its executing Python line. No root-cause attribution is added by this review.
- Recovery references the original binding and original offline mapping directly; no alternate binding is introduced. Its source destination is recovery-v2 only. Original mapping summary/artifact pins, preparation authority, packed source-channel checks, camera intake and original source mapping remain enforced.
- AST equality with build-v1 holds for `local`, `world`, `evaluate`, `materials`, `expected`, `check_binding`, `expected_camera_matrix`, `validate_cameras`, and `check_authority`, plus the unchanged utility functions. `mapping_authority` changes only the directory origin. `validate_raw` adds the BULK62 text hash, internal-text/path gate, actual attribute schema gate and full actual loop mapping gate; original geometry, masks, source slots, original XYZ/colors, weights, topology/material, polygon/corner normal, camera, render settings, object/mesh inventory and source-only flag checks remain.
- The original binding passed the full pure authority/shape gate: 4,326 shared master vertices, 8,192 original triangles, 2,479 changed triangles, 1,246 per-tile overrides. Position SHA remains `30b541d723bccaef3d5b7bae5f1569bfe65c9c67b256a451ddf33deb382f4a40`; candidate world-Y SHA remains `2eca5d39aedc03678f7d4611aa8aa497bb616ec9e7b5bade5da16db5284d13d5`; triangle SHA remains `b8e3c68f61e62ebc2b82ab8346a33aed6ed1336cd1ad0a53f6f6dc8de3536783`.

## Full-data batching equivalence

The reviewer independently reconstructed original positive `(local vertex, control group) -> packed float32 weight` mappings for all five meshes and compared them to expanded v2 batches. All entries and bytes matched. No original positive `(vertex, group)` pair repeats; grouping therefore cannot change REPLACE precedence. Original double differences that collapse to the same native float32 are equivalent at the native C-float boundary. Zero/negative slots are not introduced. All 27 group names and order remain unchanged.

| Mesh | Original adds / memberships | Batched adds | Attribute elements | Attribute scalar components |
| --- | ---: | ---: | ---: | ---: |
| Master | 3,659 | 3,492 | 59,184 | 89,466 |
| Ground_-4_-7 | 9,732 | 1,689 | 55,296 | 98,304 |
| Ground_-3_-7 | 2,086 | 385 | 55,296 | 98,304 |
| Ground_-4_-6 | 7,106 | 1,255 | 54,608 | 97,014 |
| Ground_-3_-6 | 1,983 | 371 | 54,216 | 96,279 |
| Total | 24,566 | 7,192 | 278,600 | 479,367 |

All 55 attribute buffers matched the original scalar assignment recipe byte-for-byte, with matching dtype, component count and contiguous storage. The eleven schemas exactly equal the original AST literal. Independent mock `foreach_get` tests preserved their values and scalar/vector/color shapes. Polygon flatness/material arrays preserve the original recipe. All CustomData allocations complete before an attribute/data handle is retained; no attribute handle survives another allocation.

Capture still reads every actual deform membership from native `v.groups`, all eleven actual attributes, actual coordinates, polygon flags/materials, and polygon/corner normals. No expected weight or expected normal is used as native evidence. Actual loop starts/totals and vertex IDs are captured independently, and faces are sliced using those actual values. Actual attribute schemas and full loop arrays are persisted before validation, which checks all triangle counts, starts and indices. This avoids a new pre-persistence schema/topology gate and does not assume flattening of a dynamic polygon-vertices property. Getter failure is not caught and replaced by planned data. Native field compatibility and actual normal realization must still pass the runtime gates.

The reviewer separately executed the final schema/loop gate expressions against all five nominal mesh recipes and 20 corrupted variants (one schema, loop-count, loop-start and loop-index corruption per mesh). Every nominal row passed and every corruption was rejected. AST checks confirmed that capture has no added `c.require` gate and that raw persistence precedes `validate_raw`. These are isolated pure gate checks, not fabricated native captures.

## Text construction and official API inspection

Independent compact serialization reproduced exactly 5,424,727 ASCII bytes, with no LF/CR, SHA `40bb1d7510384575421b4c8a588b48692ef5bced8e5cb02fa7439abab93cb310`. The original on-disk binding has one additional final LF. The v2 temporary compact file preserves the original embedded-byte recipe instead of loading that extra LF. No whitespace reformatting, compression, precision reduction or shape change is used.

The loader reads `as_string()` once, records actual name/internal/filepath/byte length and actual/expected SHA in `loaded-fields.json`, and asserts exact name, bytes, internal status and empty filepath. If loaded bytes differ, it persists `unexpected-loaded-bytes` before rejecting. Independent in-memory mocks covered success plus byte, internal-status, filepath and name failures: exactly one `as_string` read in every case, field evidence before every gate, and unexpected bytes saved before the mismatch rejection. These mocks performed no filesystem writes. Full capture also checks the exact five names and exact code/binding hashes; those checks recur after fresh reopen. BULK62.py is embedded before the initial rebuild and is loaded by the embedded rebuild, preserving explicit, self-contained authoring. No autoexec, save, render or export call is introduced into the rebuild.

Official source checks support the selected APIs:

- [Blender 4.5.14 Text load API](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/makesrna/intern/rna_main_api.cc): `filepath` and `internal` reach the native loader.
- [Blender 4.5 maintenance Text implementation](https://raw.githubusercontent.com/blender/blender/blender-v4.5-release/source/blender/blenkernel/intern/text.cc): the load path constructs complete line spans, retains a terminal newline through a final empty line, sets fake-user/internal flags and omits an external filepath for internal loading. This supports both the large single-line JSON and the newline-terminated code texts. The exact pinned executable's low-level Text implementation was not executed or independently verified; runtime byte checks remain essential.
- [Blender 4.5.14 VertexGroup API](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/makesrna/intern/rna_object.cc): group-add takes an integer index array and C float weight, visits each index, then performs tagging/notifying for the batch.
- [Blender 4.5.14 foreach implementation](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/python/intern/bpy_rna.cc): compatible buffers and sequence fallback are supported, errors propagate, and successful sets update the property. [Mesh RNA definitions](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/makesrna/intern/rna_mesh.cc) expose the referenced topology/material/normal properties. These inspections support API plausibility; the mocks cannot establish native execution or performance.

## Bounds, preservation and remaining gates

The new source attempt is explicitly separate: total 120 seconds, build cap 75, verify cap 30; source caps also honor remaining total time minus the wrapper reserve. Four views retain a 90-second total stage, original 1179×664 resolution, CPU2, eight samples and no denoising. Existing supervisor enforcement remains: two-CPU affinity, 1.5 GiB wrapper-plus-child RSS checks, kill/reap on timeout/cancellation, observed native exit, terminal/PID checks, logs, one-shot attempt files and no source overwrite.

Fresh verification remains a separate process and must match the entire raw capture except PID/affinity. Saved bytes and previous outputs are rechecked between processes. Recursive output hashing now also covers embedded temporary input files and native telemetry. World loading/integration and visual acceptance remain false. The source-only material study does not resolve the 167 pending support rows.

Before any separately authorized execution, final freeze must include all recovery source/helpers/tests/reports, original binding/mapping and authority inputs, and retained failed-attempt evidence. At this review's check, recovery FINAL_SHA256.json had not yet been generated. Review/source edits made after hashing must be included in that final freeze. Runtime success still requires actual text load, all actual RNA gates, raw-before-validation persistence, source save, fresh reopen equality, source-byte preservation and all wrapper limits. Rendering/visual acceptance remain separate.

## Reviewed source identities

The following hashes identify the final reviewed code snapshot, including the diagnostic and raw-persistence improvements above.

- bulk62.py: `e6ea39b833d2dbc74b64d1b4071b268f410c09c0dd37ee97ba82aac979e8e2ab`
- contract62.py: `0e66f8ab1fb7e46563a11f0ee1d1515e2c003ca07f8415655baeb40f7a4c0193`
- native62.py: `cd570eb5b8ecee7292627f424e72e88000254ad7c358951271a1ffcec3d46def`
- rebuild62.py: `e4d8b9b1de18cf2df65480d41dc5a6d408ccdad38983356390529129cc36e5c4`
- run_source62.py: `4ef00afa92d4175bcfcced0a16d4a44d7d2288bb3c2b525a8bc83a663a1255ce`
- telemetry62.py: `3333d5915f1746a2326580fab665b1112db08eda5cc101721ad18c65221ac691`
- test_recovery62.py: `132e442d8ff1dc9c0c9b30f29d2e36ef00ec3103e0ddb004b4092124c69ca220`
- README.md: `600b5b961244d0a2afc2b6c906319a7e541cc340f2ac05d4fa751fef068a210f`

The author's captured 17-test normal-mode and optimized-mode logs were read and both report all tests passed (5.299 seconds and 5.383 seconds respectively). The added seventeenth method checks binding-failure terminal scope and raw-before-validation placement. Those logs are additional author-run mock/pure evidence, distinct from the reviewer's independent full-data comparisons above. They are not labeled native evidence.
