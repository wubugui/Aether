# K recovery 01: native semantic-data lifetime repair

Status: source-only preparation. No Blender/Godot process, native save, render,
Git operation, CLOUD_RESUME edit, or Slack delivery was performed here.
The first native failure remains failed and byte-identical.

## Preserved failure

Original run: `cloud-evidence/cloudbank58k-contact-v1-20261002T072145Z-i0z0k2u2`.
It exited build `-11` / wrapper `1`, before saving any source or image. Its raw
`blender.crash.txt` SHA256 is
`c161427c2d022509acd84204e57d533f2e6c6c1429db99832755c396b01169f8`.
The Python backtrace ends inside frozen `rebuild58k.py:28` `group_signature`
while traversing vertex group membership, called by `source58k.py:52` and `:100`.
That reports where the failure surfaced, not which earlier write caused it.

`original-identities58k.json` binds all 773 original protected files, all 35
preparation identities, the original freeze/completion documents and available
terminal failure evidence: 828 distinct paths in total. None was edited.
The original preparation freeze retains SHA256
`8671ce4c4b2b384bbe8c1a3b6c8cc09e47690393fec4afe2974e1234dbbec086`.
The original recipe retains SHA256
`a3fef870bce69bbbc9e607c5a105a4e80da352035e491bc04f932d371db45bfa`.

## Source diagnosis and its limit

The frozen rebuild retains FACE handles across another FACE layer creation and
POINT handles across another POINT creation and the first vertex-weight add.
These are unsafe lifetime assumptions:

- Blender 4.5.14 RNA creates an Attribute pointer to a CustomDataLayer; its data
  iterator dereferences that layer. See `rna_AttributeGroupID_new` and
  `rna_Attribute_data_begin` in the [official RNA source](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/makesrna/intern/rna_attribute.cc)
- Layer insertion can resize the layer array and shift existing entries to keep
  type ordering. See `customData_resize` and `customData_add_layer__internal` in
  [official 4.5.14 CustomData](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/blenkernel/intern/customdata.cc)
- A mesh's missing deform data is allocated as a new POINT CustomData layer by
  `Mesh::deform_verts_for_write` in [official 4.5.14 mesh source](https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/blenkernel/intern/mesh.cc)
- The caller chain from `vgroup_vert_add` to `BKE_object_defgroup_data_create`
  and then `deform_verts_for_write` is verified in the official 4.5.0
  [group assignment](https://raw.githubusercontent.com/blender/blender/v4.5.0/source/blender/editors/object/object_vgroup.cc) and
  [object deform](https://raw.githubusercontent.com/blender/blender/v4.5.0/source/blender/blenkernel/intern/object_deform.cc) sources.
  The corresponding 4.5.14 URLs could not be retrieved in this research pass;
  do not describe that entire caller chain as independently checked at 4.5.14

Inference: an invalidated attribute handle could address moved/freed data and
corrupt the later group traversal. This is a plausible crash explanation and a
real source hazard to remove, not a demonstrated native root cause. No native
minimal reproduction or sanitizer run has been performed. Python API documentation
pages also failed to load; the evidence above is primary implementation source.

## Exact repair scope

- Corrected embedded `rebuild58k.py` finishes material/flat-face operations and
  every group/weight allocation before custom attribute creation
- All four custom attributes are created without keeping the returned RNA
  handles; a fresh name lookup occurs only after the last structural mutation
- Every 194 x 6 slot is read and checked against exact float32 recipe weights,
  including the expected membership/absence mask, valid index/range and duplicate
  rejection. All 1,156 FACE/POINT integer values, names, types and domains must
  match the recipe exactly
- The semantic audit runs before save and after each independent fresh open.
  It is added to the full saved-identity equality gate. The existing group
  signature traversal is deliberately retained, not skipped to hide the crash
- The original source builder/fresh-open functions are loaded intact. The
  supplemental entry only binds the corrected rebuild/Text, independent output
  `.blend`, and extra semantic identity check. Seven original source/recipe
  hashes are pinned before loading. Contact code identities include all corrected
  and original authoring/verification inputs
- The resource wrapper differs only in supplemental source/import/output paths
  and the new run prefix. Its 30-second total, CPU2, 1.5 GiB wrapper-plus-child,
  200,000-byte source, four-process, immutable-input and render-contact gates are
  unchanged

K's authored recipe, geometry function/preflight, 194 vertices / 384 triangles,
six Empty controls, source basis, original E cameras/material/light/settings,
7% margins, topology and actual-saved-array contact checks remain unchanged.
No game/world integration or shape improvement is claimed. Compressed source size,
native execution stability, saved identity and visual result still require the
single bounded native trial. A later native authoring failure can leave a partial
replacement mesh; the builder must fail and must not claim a successful save.

## Source-only verification

Normal and optimized Python each pass **2,375** checks in
`test_recovery_static58k.py`, including:

- A strict fake-RNA model that invalidates handles on every same-domain layer
  addition and on first deform allocation; both old lifetime patterns are rejected
- The corrected phases and exact semantic readback pass the same fake model
- One corruption tested at every one of 1,164 weight slots and 1,156 attribute
  values; schema/range/duplicate/group-order negative controls also fail closed
- Original function/preflight AST/text equivalence, exact wrapper-path-only diff,
  all original identities, import-only routing with empty Python module stubs,
  pinned source changes rejected, and unchanged limits are checked

This is static/protocol/fake-model evidence, **not a Blender run or native proof**.
Logs: `static-tests58k.log`, `static-tests58k-optimized.log`. The unchanged original
33 math and 36 contact protocol tests also pass in both normal and optimized
Python; supplemental `inherited-*.log` files retain these executions.

## One future authorized native command

After publication and the parent's scheduling decision, from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=2 python source-assets/cloud-bank58/revision-k/recovery-01/run_patch58k.py --run-approved-patch-trial
```

It creates a unique `cloudbank58k-recovery01-*` run and saves only
`revision-k/recovery-01/authored_envelope58k.blend`. It refuses existing recovery
source or terminal evidence, preserving either success or failure. The original
failed runner must not be relaunched. A success would establish this repaired
native path passed; it would not by itself prove the exact original crash cause
or visual acceptance.
