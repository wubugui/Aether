# F shared-skin patch: native checkpoint rejected before rendering

Actual run: 2026-10-01 19:03 UTC, `cloud-evidence/cloudbank58f-patch-20261001T190306Z-xl109553`.
Recovered and checked at 19:25 UTC. The prepared README is an immutable pre-run record; this result supersedes its statement that no source exists.

- Blender 4.5.14 saved `shared_patch58f.blend`, 101969 bytes, SHA256 `c505c969c4f586075a420e9d2984de710e7c2670a77293dcddae199572f474be`
- Source identity passed: 182 vertices, 360 ordered triangles, all 11 editable groups, flat shading, no modifier, exact float32 coordinates, shared-edge incidence two
- Both inherited E cameras retained exact matrices and projections; the 1216 front camera check passed
- The fixed shared-side-back camera failed its 7% margin gate. Actual normalized bounds were X [0.09700547, 0.87412339], Y [-0.06379338, 0.81274396]. The bottom of the mesh would be clipped, so the builder deliberately stopped after preserving the native source
- Child exit 1 and wrapper exit 1; elapsed 0.87273 seconds, actual peak RSS 259520 KiB. No images, world loading, final intersection proof, or visual acceptance
- All prepared and protected C/D/E inputs remained SHA-identical. No failed source or report was overwritten

Next action is a separate geometry-only candidate, after studying the offending authored belly vertices. Do not move the comparison camera or relax the 7% gate to label this run successful. Retain this original failure. The game remains candidate61 and the full GOAL remains unaccepted.
