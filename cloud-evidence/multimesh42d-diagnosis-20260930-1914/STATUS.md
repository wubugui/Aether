# Candidate42d status, 2026-09-30

- Candidate SHA256: 5742de44e7f44070ca7475e801ea82b4f9be6433b8a1cef55e00aa667f1607e9
- Candidate bytes: 103,542,103 (below 100 MiB)
- Historical Game42c is unchanged
- Allocation test: 100/100 under official Godot 4.5.1 Compatibility, Mesa llvmpipe
- Build/readback buffer assertions passed, but build wrapper status remains **failed** due to two 349,524-byte leaked-texture errors at exit. Preserve that complete run; do not relabel it successful
- Real-tree smoke: exit 0; 17/17 checks; 12 actual rendered captures; only known unsupported-VSync warning, no leaked-texture errors
- Smoke evidence directory: /workspace/scratch/a29d03198654/Aether/cloud-evidence/smoke42d-20260930T191803Z-G76lbN
- Rain: all 1,800 visible transforms moved. Snow 1275: 1,200/1,200; snow 1276: 600 visible out of 1,200 allocated, all 600 moved
- Independent visual inspection by parent found rain lines and snow dots visible but sparse; blizzard intensity remains inadequate. This candidate is eligible for further comparison, not visual acceptance or hardware-GPU acceptance
- Snow on/off differences: 187 pixels (1275), 165 pixels (1276) over summed RGB threshold .03; restored-on control exactly zero for both
- Rain first on/off comparison is contaminated by residual lightning lighting (142,944 changed pixels in on/restored control). Parent independently compared final off/restored and measured 936 pixels; do not cite initial 143,724 as precipitation-only evidence

## Non-weather preservation

Strict normalized hashes differ because 1,524 shader parameters changed from null to explicit shader defaults during renderer-backed serialization. The separate shader-default audit found zero unexpected transitions. Excluding shader-parameter fields only, all 10,446 non-weather nodes and recursively referenced geometry/collision/material structural content hash identically. The only unpaired ShaderMaterial IDs are the two deliberately reconstructed weather materials. Both strict and narrowly factored reports are retained.

## Pending lifecycle diagnosis

Official 4.5.1 GLES3 source allocates Sky radiance and raw-radiance cubemaps; its accounting per 256 RGBA8 mip chain is exactly 349,524 bytes. Dirty-list Sky lifetime before the first renderer update is the current testable explanation, not yet a confirmed outcome. A three-mode diagnostic compares immediate Sky disposal, settled Sky disposal, and 42d instantiate-only with renderer settling before disposal. No original scene is modified or resaved.

Source: https://raw.githubusercontent.com/godotengine/godot/4.5.1-stable/drivers/gles3/rasterizer_scene_gles3.cpp (Sky allocation/free/dirty-list paths)

## Lifecycle outcome and recovery (19:23 UTC)

The controlled Sky-only immediate-disposal test reproduced both exact349,524-byte errors. Waiting3 process frames and frame_post_draw before disposal eliminated both errors. The same unchanged42d scene then passed an independent off-tree settled reload: Rain28,800 and Snow19,200 floats exactly matched original authored seeds; no texture errors. Combined with the real-tree smoke, this recovers42d for continued comparison without rebuilding or changing its SHA. The original build run remains failed and is not relabeled.

The builder and full verifier now settle newly loaded off-tree Sky resources before disposal, without invoking gameplay _ready or mutating/saving a live world. These tool changes parse under official4.5.1; the immutable42d was not rebuilt to exercise the builder revision. The upper43 worker received the same minimal fix. See recovery-report.json for exact evidence paths.
