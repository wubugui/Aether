# North ridge source recovery: independent offline cost review

Reviewed 2026-10-02 UTC. Scope: read existing `build-v1` Python/JSON and failure evidence; inspect official Blender source; write this report only. No Blender or Godot process, `.blend`, PNG, or native performance benchmark was run or produced. Original shape, build-v1 and failed-attempt evidence are unchanged by this review.

## Finding and limits

The strongest specific cost hypothesis is the first 5.4 MB, single-line `Text.write`, which precedes all terrain mesh construction. Official Blender 4.5 source exposes a quadratic first-line insertion path. This is **not proof that the killed process was at that call**. The substantial per-element RNA work is a separate avoidable cost.

The actual evidence is `cloud-evidence/north-ridge62-source-20261002T111415Z-wlgkmd5l`: child wall 48.703885 s, timeout budget 48.651942 s, return -9/SIGKILL, peak RSS 338,460 KiB, aggregate 390,320 KiB, RSS limit not triggered; wrapper 55.138630 s under its 60 s total limit. Logs and output directory are empty; no source was saved. These establish timeout, not the executing Python line. Native phase logging is absent, `check_binding` runs before its `try`, and the first result write follows `capture`; empty output cannot distinguish startup, validation, text creation, mesh creation or capture. No per-stage timing attribution is defensible.

## Exact planned Python/RNA operation counts

Counts come from the frozen binding and loops, not an executed native profile. Each vector/color assignment is one Python property assignment; its scalar components are shown separately.

| Mesh | Vertices | Triangles | `VertexGroup.add` | Exact grouped add calls | Attribute element writes |
|---|---:|---:|---:|---:|---:|
| Master | 4,326 | 8,192 | 3,659 | 3,492 | 59,184 |
| Ground_-4_-7 | 6,144 | 2,048 | 9,732 | 1,689 | 55,296 |
| Ground_-3_-7 | 6,144 | 2,048 | 2,086 | 385 | 55,296 |
| Ground_-4_-6 | 6,058 | 2,048 | 7,106 | 1,255 | 54,608 |
| Ground_-3_-6 | 6,009 | 2,048 | 1,983 | 371 | 54,216 |
| **Total** | **28,681** | **16,384** | **24,566** | **7,192** | **278,600** |

- Eleven attributes per mesh: eight POINT fields and three FACE fields, hence `8*N + 3*F = 278,600` element writes, representing `15*N + 3*F = 479,367` scalar components. There are also 32,768 individual polygon assignments (`use_smooth`, `material_index`), 135 group creations and 55 attribute allocations.
- Grouped counts use one key per mesh `(control index, exact weight)` and collect local vertex indices. Both exact original-double and exact IEEE float32 keys give 7,192 calls, a 70.72% reduction. No vertex has a repeated positive control index; all original positive memberships remain 24,566. Do not group by rounded decimal/tolerance, introduce zero memberships, or change 27 group names/order.
- A pure-Python reconstruction compared original `(local vertex, group) -> packed float32 weight` maps against grouped assignment maps for all five meshes: exact equality passed. This proves the proposed batching's frozen-input membership/weight equivalence, not native API execution.
- Capture traverses 28,681 vertices and 24,566 actual group memberships, producing 774,387 dense weight cells. Its current group assignment expressions read `v.index`, `g.group`, `g.weight` 73,698 times in total.
- Capture reads 278,600 attribute values. Its conditional rereads `att.data_type` **499,838** times, because every non-vector element evaluates both tests. Merely hoisting type outside the element loop cuts this to at most 55 without altering data.
- Capture additionally reads 28,681 coordinate vectors, 16,384 face-index arrays, 32,768 polygon material/smooth flags, 16,384 polygon normals and 49,152 corner normals. These main expressions total **995,505 named property evaluations**, excluding collection lookup/iteration, vector component extraction and small scene metadata. This is a source-level count, not a literal count of all internal C/RNA calls.
- The binding is converted back to a string three times across rebuild and capture. Python JSON parsing/serialization, dense result conversion, authority checks and geometry evaluation also cost time; RNA batching does not eliminate them.

## Large Text path: evidence and byte-preserving replacement

The native call serializes `json.dumps(b, separators=(',', ':'), ensure_ascii=False)`: **5,424,727 bytes**, all ASCII, no LF/CR/TAB/NUL, SHA-256 `40bb1d7510384575421b4c8a588b48692ef5bced8e5cb02fa7439abab93cb310`. The on-disk binding is 5,424,728 bytes because it adds a final newline; loading that file unchanged would fail the embedded byte-identity gate.

In the official 4.5 maintenance source, `BKE_text_write` calls `txt_insert_buf`. Its first line is inserted character-by-character; the insertion helper allocates a new line and copies the prior prefix each time. For this ASCII input, a complete pass implies 5,424,727 insertions and 14,713,828,799,901 cumulative prefix bytes copied, approximately 14.7 TB, plus other scans/copies. This is a theoretical work estimate, not measured traffic or elapsed time. [Official 4.5 text implementation](https://raw.githubusercontent.com/blender/blender/blender-v4.5-release/source/blender/blenkernel/intern/text.cc), functions at lines 488, 1463 and 1781.

`Text.from_string` is not an effective substitute in the inspected 4.5.4 source: it clears then calls the same `BKE_text_write`. [Official 4.5.4 RNA Text API](https://raw.githubusercontent.com/blender/blender/v4.5.4/source/blender/makesrna/intern/rna_text_api.cc), lines 24-34.

Recommended minimal replacement: materialize the exact compact bytes without a trailing newline in the new attempt's temporary/evidence area, then `bpy.data.texts.load(filepath=..., internal=True)` and set the expected name. Blender **4.5.14** explicitly exposes `filepath` and `internal`, forwards the flag to `BKE_text_load_ex`, and returns a Text. [Official 4.5.14 load API](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/makesrna/intern/rna_main_api.cc), lines 551-570 and 1615-1625. The inspected 4.5 load implementation builds lines from whole buffer spans, and internal loading sets in-memory/dirty flags without retaining an external filepath. The frozen ASCII JSON has none of the control/encoding cases that its cleanup would change. [Official 4.5 text loading](https://raw.githubusercontent.com/blender/blender/blender-v4.5-release/source/blender/blenkernel/intern/text.cc), lines 318-388 and 425-474.

Immediately assert exact name, `is_in_memory`, empty `filepath`, and `as_string().encode('utf-8')` equality/hash. Do not add whitespace, alter key ordering/float formatting, truncate, or compress the embedded contract. `TextLine.body` also uses one allocation/copy in inspected 4.5.4, but loading internally is the better-audited complete Text construction route. [Official TextLine setter](https://raw.githubusercontent.com/blender/blender/v4.5.4/source/blender/makesrna/intern/rna_text.cc), lines 140-153.

Version limitation: web retrieval of the exact v4.5.14 `text.cc` and `rna_text_api.cc` failed. Their low-level behavior is evidenced by official 4.5.4/4.5-maintenance sources, not verified against the pinned executable. The 4.5.14 load, group-add and foreach Python entry sources were available. Runtime equality checks remain necessary.

## Minimal equivalent batching and capture

1. Allocate all mesh attributes before retaining any attribute/data handles, preserving the existing CustomData invalidation precaution. Replace eleven attribute loops per mesh with `attr.data.foreach_set('value'/'vector'/'color', flat_array)`: **278,600 writes become 55 calls**. Use contiguous native float32, int32 and bool arrays with exact component count; keep FLOAT_COLOR `color`, not `color_srgb`.
2. Set polygon `use_smooth` and `material_index` via two calls per mesh: **32,768 assignments become 10 calls**. Retain `mesh.update`/view-layer updates needed to realize normals; do not write expected normals into the evidence.
3. Group `.add(indices, weight, 'REPLACE')` by exact `(group, weight)` per mesh. Its official 4.5.14 RNA signature accepts a dynamic integer-index array and one float weight; internal work still visits each vertex, but tagging/notifier overhead occurs once per batch. [Official VertexGroup implementation](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/makesrna/intern/rna_object.cc), lines 1826-1847 and 2093-2102.
4. Use `foreach_get` for all actual attribute/coordinate/polygon/normal arrays, then reshape/to-list in Python. Attributes need 55 calls. For triangle topology, prefer bulk actual `loops.vertex_index` plus actual polygon `loop_start` and `loop_total` checks over assuming dynamic polygon `vertices` arrays flatten identically. Verify all loop totals are three and preserve original polygon/corner order. Keep actual vertex-group readback; synthesizing weights from the binding would invalidate the native proof.
5. The 4.5.14 Python RNA implementation explicitly implements collection `foreach_get/set`, accepts compatible buffer objects, has a sequence fallback, and performs a property update after a set. [Official foreach implementation](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/python/intern/bpy_rna.cc), lines 5290-5516. Specific property/dtype compatibility must still be verified on the pinned native build. Do not silently catch a failed getter and substitute planned values.
6. Add flushed, monotonic phase markers before/after binding check, Text load, each mesh build, capture, raw write, validation and save. Keep the failed v1 immutable and use independent recovery-v2 paths. A larger finite source budget may avoid wrapper/preflight squeeze, but is not evidence of fixing a root cause or proof that any particular runtime will fit.

## Review input identities

- `build-v1/native62.py`: `56a047e91c27e6ae715cae0dc86dad40ebaddc3663045b93797d536d700f7fec`
- `build-v1/rebuild62.py`: `56cecf1c8cebefa986de3d7301a620eafecad0004ce29e6e03a2b92711c27159`
- `build-v1/contract62.py`: `f1ac7098eb511bdc6d292c18ae233bb13fbcd798719a73a314fba7d2fc8363ac`
- `build-v1/bindings62.json` including final newline: `a8b634d10c5e1dd57884f9a782b43853ffac9119a290609351c225ddb4df3c27`

Outcome: offline review complete. These are cost-reduction recommendations and static equivalence constraints, not a native build pass, saved-source verification, visual acceptance, or authorization for engine execution.
