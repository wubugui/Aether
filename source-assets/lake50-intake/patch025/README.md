# Additive 0.25m island patches for the Game49 depth diagnosis

These are new independent images. No Game49 mesh, scene, material, camera or old 1m image/report was changed. They are not a Game50 candidate or visual acceptance.

## Interface

Each named patch has `<name>-height025-rf.res` (an `Image` resource, `Image.FORMAT_RF`), `<name>-height025.exr`, and raw little-endian float32 data. Create `ImageTexture.create_from_image()` in the real renderer. RF and EXR both round-trip bit-exactly through Godot4.5.1; no half floats, sRGB conversion or mipmaps.

| Name | world_bounds (xmin,zmin,xmax,zmax) | size (width,height) |
|---|---|---|
| island_near_left | (996.75, -1182.75, 1089.75, -1116.5) | (373,266) |
| island_far_middle | (1009.75, -1682.75, 1106.75, -1616.5) | (389,266) |
| island_near_right | (1346.75, -1144.75, 1411.25, -1094.75) | (259,201) |
| foreground_rock | (1178.25, -1089, 1220.75, -1050.75) | (171,154) |

Spacing is exactly0.25m; endpoints are included. Columns increase world X; rows increase world Z. All bounds come from the entire actual saved island ground footprint, including root/shoulder/wetshore/solid grass caps, padded at least12m and snapped outward to0.25m.

Exact pixel-center texture UV:

```glsl
vec2 uv = ((world_xz - patch_bounds.xy) / 0.25 + vec2(0.5)) / patch_size;
```

Use `filter_linear, repeat_disable`, no mipmaps or color hint. Existing1m base uses its original pixel-center UV and unchanged bounds.

Blend signed heights, then compute depth:

```glsl
// Strictly outside bounds or exactly on an edge: return base_height unchanged.
float d = min(min(world_xz.x - patch_bounds.x, world_xz.y - patch_bounds.y),
              min(patch_bounds.z - world_xz.x, patch_bounds.w - world_xz.y));
float w = smoothstep(0.0, 8.0, d);
float height = mix(base_height, patch_height, w);
float depth = max(0.0, 0.0 - height);
```

The four patch rectangles do not overlap. The actual island footprint is at least4.0189m beyond the inner edge of the8m feather, so island shore samples receive full patch weight. The base map remains the authority outside the patch domains. No patch clamping should leak outside its bounds.

`patches.json` is the machine-readable interface and source/triangle/raw-image hash manifest. `image-package-report.json` holds `.res`/EXR hashes and exact read-back checks.

## Accuracy, including remaining failures

The frozen1m report's exact4,000 global random positions and exact2,180 exposed-source zero-line positions were reproduced. Their base-map results match the old report. An additional3,000 continuous random points and1,200 exact grid points were sampled per patch.

### Same387 actual island shoreline points

- Horizontal zero-line P95: 1m base1.0449m → patch/fused0.2781m
- Maximum horizontal offset: 1.9058m →0.9073m
- No texture zero found within±2m:1 →0
- Mean absolute vertical error:6.6866m →4.7351m
- Maximum absolute vertical error remains22.8686m. This is not a near-shore precision pass
- Foreground-rock maximum shoreline vertical error gets worse:19.1478m →21.1460m. It is retained in the report

### Same12,000 patch-domain continuous random points

- Mean depth error:0.18331m →0.03818m
- Depth P99:5.92074m →0.40684m
- Maximum depth error gets worse:18.43306m →19.72689m
- Ordinary continuous regions:11,455 samples; fused depth maximum0.05012m
- Continuous steep/creased regions:470 samples; fused depth maximum3.31611m
- Proven-nearby finite-jump regions:75 samples; fused depth maximum19.72690m

No discontinuity samples were removed from aggregate statistics. Classification uses actual saved-triangle BVH queries, not texture error thresholds: suspected transitions are bisected13 times to below0.1mm, requiring a remaining height jump>0.25m and three successive change ratios>0.8. Continuous steep planar slopes halve their change and are not classified as jumps. This is a numerical geometry diagnostic, not a symbolic topology proof.

A0.25m bilinear scalar field cannot exactly represent vertical/overhanging highest-surface jumps or all arbitrarily narrow wet rocks. Smaller maximum Y error is not guaranteed at every discontinuity even when horizontal shoreline localization improves. A/B/A visual inspection remains necessary.

## No-change evidence

-3,932 same global random points with zero patch weight: fused-minus-base exactly0
-4,128 patch-edge and just-outside probes: fused-minus-base exactly0
- Literal out-of-domain branch returns the old base sample directly
- All frozen1m RF/EXR inputs, source triangle export, old bake report and Game49 scene hashes are unchanged
-All347 independent49 assets match their existing build hashes

Detailed records: `fusion-verification.json` (per-patch, standalone patch vs fused, random/shore categories, worst examples and all shared sample records), `frozen-input-integrity.json`.

A first verification attempt exposed NumPy scalar-promotion differences in the test sampler; its script/logs are retained in `failed-check-01-scalar-promotion`. The verification sampler was changed to reproduce the frozen report's float64 interpolation arithmetic. No texture/input changed.
