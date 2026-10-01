# 58B final native source — visually REJECTED after all five faces

This is source work in the bounded52f research branch. It is not the coast56
world and has never been integrated, rendered in-world, or visually accepted.
The first58A source remains visually rejected and immutable.

All fiveB source images have now been actually viewed. The four-sidedA slab is
gone, butB remains a thick oval carrier with long near-uniform curved rolls,
basin-like channels, very large smooth underside lobes and visible long through
slots. Medium/small nested cloud forms are missing. **B is visually rejected**;
the source remains immutable and further modeling needs a separate revision.

Actual images and detailed review:
`cloud-evidence/cloudbank58b-source-preview-20261001T115851Z-hw20ss6g/`.
Child/wrapper0,61.75s,peak observed888928KiB; all16 frozen inputs unchanged.

## Final source constructed and freshly reopened

`cloud_bank58b.blend` SHA256:
`9158443c62cdf0c43ebc8909f6791b9162770adba5da15d1294bec1c02ecce50`

The final lower volume has9000 triangles; the three retained upper sources have
304 each. The saved native source contains the entire50572-triangle unsimplified
repaired shell, all11 editable lofts and the final mesh. Both source build and
fresh readback passed,14.04s, peak587540KiB:
`cloud-evidence/cloudbank58b-recovery-finish-20261001T114524Z-blve41d_`.

Simplification changes signed volume by−0.031985%. Every raw/native vertex and
triangle centroid was sampled against the opposite actual triangle surface:
75856 raw→reduced samples,max4.654m;13498 reduced→raw samples,max4.267m. These are
sampled offsets, not a continuous Hausdorff bound. Raw and final source geometry
are closed, single-component and free of reported self-overlap, duplicate or
zero-area triangles. Native GLB triangle correspondence and root mapping passed.

The original1216 camera point remains outside all four source volumes, nearest
lower surface378.10m. The original21-root source context still gives194 BVH
surface-overlap pairs against3 meshes on3 roots. Outer radial samples are
13.30…433.08m from old external triangles; this does not prove a continuous
boundary or an exact largest gap. These issues remain explicit and unaccepted.

Actual58B pixels reject the shape. Geometry gates do not accept the material,
reference composition or any whole-world integration.

## Current authoritative native shell

`cloud_bank58b_union.blend` SHA256:
`ed393ba932c0addf90fb23628604ea27f1779cb4ab69e7d3201bce3bbca8db06`

The actual saved repaired shell has25284 vertices,50572 triangles, one connected
component, zero boundary/nonmanifold edges, no duplicate or zero-area triangles,
and zero nonadjacent BVH candidate intersections. It preserves all11 native
editable loft controls and the three unacceptedA upper ribbons.

World bounds: (2517.623535,217.329376,2427.345215)…
(5090.606934,963.986298,4645.787598). Volume1,318,379,521.8137708m³.
These are source geometry facts, not a visual or whole-world pass.

## Preserved failure chain and actual correction

1. OriginalB build timed out after300.035s, peak546464KiB.11 source controls were
   valid; there was no finishedB `.blend` or GLB. The exact slow operation was
   not recorded. No old timeout evidence was relabeled
2. A staged same-input union showed join0.0025s and voxel union0.124s. With
   `use_remesh_preserve_volume=True`, the union contained286 nonadjacent BVH
   candidates. Fresh actual-triangle narrow-phase tests confirmed262 true
   interior segment crossings and24 false positives; longest crossing54.02m
3. The one-parameterFalse intervention preserved all11 input meshes, their
   topology and world matrices exactly. The resulting shell had no BVH overlap,
   but two components. Total signed volume changed+0.130677%; all six bounds
   changes were explicitly reported, maximum absolute14.245m. Output geometry
   was not claimed unchanged
4. The extra component was a negative-volume internal cavity,8 vertices,6 native
   quads/12 triangles, dimensions2.572×8.756×8.881m, volume−200.0244086m³.
   Its center and all8 vertices were inside the main shell on all3 ray tests,
   and no component/main surface triangles intersected. The center was outside
   every input control, between the middle fork and deep saddle. No cavity had
   been authored. OriginalTrue/False sources remain intact
5. This independent candidate fills only that cavity by removing its inner
   shell. Every surviving outer vertex, ordered oriented polygon, polygon
   smooth/material flag, object transform and overall bounds is exact. The
   signed volume increases only200.0244086m³. `explicit-cavity-fill58b.json`
   contains the full removed topology and old/new vertex index mapping

## Fresh readback, not a rewrite of failure

The fill operation saved its native source, then failed while serializing a
`numpy.bool_` report field. The original
`cloudbank58b-recovery-fill-20261001T113747Z-o2gz3_me` remains wrapper1.
No model was rebuilt to hide that failure.

Three new read-only Blender processes reopened the old/new sources, reconstructed
the exact repair proof, freshly reloaded the repaired shell and checked actual
triangle intersections. All3 children and wrapper passed;5.03s, peak~315MiB:
`cloud-evidence/cloudbank58b-recovery-recover-proof-20261001T114019Z-sbytwdqr`.
The repaired `.blend` SHA stayed unchanged through this recovery.

Authoritative current reports are `explicit-cavity-fill58b.json`,
`union-geometry58b.json`, `union-fresh-readback58b.json` and
`actual-intersections58b.json`, bound to the native SHA above. The old partial
`union-stage58b.json` belongs to the failed fill-report process and is retained;
it must not be used as the completion flag. Each run's own terminal proof and
unique wrapper exit file govern its status.

## Completed bounded facet operation and next visual gate

The scheduled `run_recovery58b.py finish` retained the complete native raw shell,
applied native Decimate, exported root-local GLBs and performed fresh readback.
The<3% volume/<35m sampled-offset gates and topology gates passed as recorded
above. The separately scheduled five-face source preview completed with:
`python source-assets/cloud-bank58/revision-b/run_preview58b.py --source
source-assets/cloud-bank58/revision-b/recovery-03`.

No source-context image, world image,
source flight clearance, player flight,56 merge, push or external delivery has
been performed at this checkpoint.
