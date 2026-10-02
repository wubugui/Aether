# K faithful corner-normal transfer v2: preparation only

No adjusted GLB has been written and no engine process has run. Pure tests operate
on byte arrays in memory. Both original failed native attempts, all frozen code,
the accepted source and installed exporter remain unchanged.

## Fixed authorities and honest failure boundary

- Accepted editable source: `recovery-01/authored_envelope58k.blend`, 136,389 bytes,
  SHA256 `16eeb67dce6e89f05562b67f869c77dd7882942585241a2648ae46ff48012bee`
- Original official raw GLB: 31,144 bytes,
  SHA256 `48a0aa816dc5dd247958fb883d4114b8d07e7fdf2d458af6a408e0af4c22dd60`
- Actual native corner/polygon capture: 281,016 bytes,
  SHA256 `35cde26e14f8767c015295cff3b8f271a85052a111d8fd68e066784a18e1b1c7`
- Raw capture owner:
  `cloud-evidence/cloudbank58k-normal-readback-v1-20261002T091816Z-whfkeukw`
- Independent actual-data diagnosis:
  `cloud-evidence/cloudbank58k-native-normal-diagnosis-20261002`

The raw readback was saved before its validator failed. That validator incorrectly
required different Blender polygon/cached-corner API results to be bit-identical.
The original native exit 1 and wrapper failure remain failures. This pipeline
independently checks the preserved raw capture's SHA, PID/wait4, original failed
validation, exact source identity and protected finalization. Every corner is
actual native float32 data, not inferred from mathematical normals. All three
corners of each face are bit-equal and their outward/unit errors satisfy the
original `3e-5` gate. Their round(4)/normalize/Y-up output matches the entire raw
GLB exactly. No new Blender read or export is needed or included.

## Only NORMAL bytes change

The transfer maps each render position **uniquely and exactly** to a source
position, proves a bijection of all 384 oriented triangles, and follows actual
polygon-loop/loop-vertex ownership to assign source corner normals. Reused render
vertices must have identical normal ownership or fail. The unchanged standard
`(x,y,z) → (x,z,-y)` map is used; no anchor, root inverse or recentering is applied.

The raw GLB must have the observed uncompressed float32 NORMAL representation,
exactly three accessors, aligned bounded nonoverlapping normal slots, no sparse or
normalized data, and no normal min/max metadata that would require JSON edits.
The routine changes only the 1,152 12-byte NORMAL slots. It independently verifies
that **every other byte** is identical, including header, JSON, materials, position
and index payloads, padding and layout. Every new normal must equal the mapped
actual source corner exactly. It then runs the original geometry/material contract
unchanged: `1e-5` positions, `3e-5` GLB normals, `1e-7` per-triangle flatness,
oriented triangles, bounds and all original material/schema rules.

The derived file is explicitly named `cloud58k-restored-corners.glb` and marked
`unmodified_official_export=false`. Its raw exporter input is retained separately
with a SHA/byte-change receipt. This is precision-preserving transfer, not a claim
that the official exporter emitted these unchanged bytes.

## Material evidence

Base color and roughness expectations come from the pinned accepted authoring
settings and their native `light_material_identity` check, which the actual
collector executed before capturing raw arrays. Metallic 0 and double-sided true
remain the same source-authoring/default and v1 transfer contract values. The
actual corner capture did not separately record those two material fields; this
package does not label them newly measured. The preserved raw GLB satisfies all
original material checks, its material bytes are untouched, and actual imported
Godot material values are independently checked under the original v1 rules.

## One future isolated transfer

Only after the parent's scheduling decision:

`PYTHONDONTWRITEBYTECODE=1 python source-assets/cloud-bank58/revision-k/transfer-v2/run_transfer58k.py --run-approved-transfer`

Without that flag, no output directory, GLB derivation or native process occurs.
A persistent exclusive one-shot marker prevents retries over the original result.
The adjusted GLB is derived once from the above inputs, then three serial Godot
4.5.1 stages run in a fresh `/tmp` minimal project:

1. Editor import, maximum 30 seconds
2. Actual resource-array/material readback and embedded native PackedScene save,
   maximum 20 seconds
3. Fresh process reload, maximum 20 seconds; exact native arrays/materials/
   transforms/AABB equality and zero external dependencies

The original `probe58k.gd` is byte-identical. Its report retains the original
`cloud58k-import-v1` schema identifier; the enclosing pipeline/report is v2.
The original import options and `2e-4` Godot normal allowance are unchanged.
The native probe has not yet been parsed or executed; future failures remain
visible instead of being counted as preparation success.

Whole-wrapper time is capped at 120 seconds, including full main-project hashing;
children use two CPUs/threads and the inherited 1.5 GiB aggregate RSS guard. The
same audited helper observes wait4, owns PIDs and kills/reaps on timeout/signal/RSS
failure. All source/prior/current frozen inputs and every main-project file,
including `.godot`/`.import`, are checked before/after. Source and earlier transfer
artifacts are rechecked between stages. Temporary import caches stay outside the
main project. No Blender, new source, main-world load, image or visual acceptance
is part of this transfer.

## Pure preparation checks

Normal and optimized Python run the same bytes-only suite, including all 384
triangle-reversal controls, source corner/loop corruption, original rounding
replay tampering, wrong restored normal values, overlapping/misaligned slots,
normal metadata, material/schema changes, header/JSON/non-normal-buffer corruption,
original gates and no-launch/no-output defaults. The independent review and
frozen manifest must be checked before the actual one-shot run.
