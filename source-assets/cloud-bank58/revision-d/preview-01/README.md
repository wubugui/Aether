# Five isolated D source views, prepared but not run

This item consumes the exact published `native-01/fold58d.blend` and its saved
five cameras, neutral material and lighting. Each image opens the source in its
own fresh Blender 4.5.14 process. Processes run sequentially; no rendering takes
place merely by preparing or importing these scripts.

`render_one58d.py` renders one named camera and records the native source SHA,
actual camera matrix and projection, all-vertex framing, effective visibility,
render settings and unmodified PNG SHA. It verifies the actual 325/646 stored
mesh and saved material/light values before rendering. It never saves the source
or adds geometry, light, texture, denoising, compositor or image processing.

`run_preview58d.py` schedules the five processes with a total 90-second budget,
two CPU threads and a 1.5 GiB RSS limit. Each real exit is retained; a failed view
stops the remaining views. Every partial image, current false/running status and
log is preserved. It verifies PNG chunk CRCs and decompressed scanline length,
not only file existence. No lower-detail fallback or automatic retry is applied.

## Prepared views

1. Exact saved 1216-source-front: 836×471, pixel aspect 942/941. The actual
   reference camera crops part of the underside. This is expected and explicitly
   recorded, not corrected by moving the camera. Reduced resolution is not a
   reference-pixel match test
2. Back: 836×586, square pixels, every actual native mesh vertex inside the frame
3. Side: same complete-shape dimensions and actual-vertex requirement
4. Underside: same requirement, including the entire lower outline
5. Top: same requirement, including all edge folds

The four complete-shape views require at least 7% margin; native readback measured
about 9%. The checker compares the actual saved matrices and projection again
for each image. It does not reconstruct cameras from boxes or infer silhouette
visibility from vertex bounds.

The saved settings are CPU Cycles, eight samples, denoising off, Standard color
transform, exposure 0 and gamma 1. PNG output is the renderer's RGB8 file with
that saved color transform. No external image manipulation is performed.

Estimated total is 30–70 seconds and roughly 0.25–1.5 MiB across five PNGs;
both are planning estimates, not measured output. Every actual image byte count,
SHA and resource peak must be reported after the run.

## Launch prerequisite

Do not launch until the parent confirms the complete native publication and
binary fetch/readback, then allocates the rendering window. Supply the exact
parent-verified remote commit. The wrapper independently compares the source
blob at that commit with the local source bytes, while remote publication
verification itself remains the parent's responsibility.

```sh
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python3 -B \
  source-assets/cloud-bank58/revision-d/preview-01/run_preview58d.py \
  --run-approved-five-view-preview \
  --published-native-commit EXACT_PARENT_VERIFIED_40_CHARACTER_COMMIT
```

All versioned preview inputs are SHA-bound in `preview-input-freeze58d.json`;
the native, static D and C freeze manifests protect existing evidence. The new
run uses unique paths and `inputs/` namespacing without asset/report copies.
After the actual five views finish, inspect every PNG and the original 1216
reference before making any shape judgment. Image generation success is not
visual acceptance. This isolated source has no world, ship, other cloud roots
or hardware-GPU acceptance.
