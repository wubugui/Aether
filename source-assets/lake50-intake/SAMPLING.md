# Saved Game49 static-support depth diagnostic

This is an independent material-intake artifact for diagnosing Game49 underwater cyan columns. It creates no Game50 candidate and changes no Game49 resource.

## Authoritative input

- Actual saved Game49 SHA-256: `52d13fcb7ea412d3a0fae2eedb1d0f9c369dbe06c0da320d786c26c97c475ec8`
- Export reads the saved PackedScene's node transform chain and actual `Mesh.get_faces()`. It never instantiates the world or accesses/re-saves MultiMesh buffers
- `support49-export.json` lists all 55 included meshes, local/world triangle hashes, transforms, geometry byte ranges and every excluded geometry node
- `support49-world-f32.bin` is little-endian world XYZ float32 triangle soup, with offsets in that manifest
- Includes Terrain, intersecting Mountains, all four island roots/shoulders, 24 wetshore pieces and six solid grass caps. Cliffs were inspected but all lie outside the domain
- Excludes Ocean (not its own bottom), vegetation/branches/crowns/grass tufts (suspended or decorative geometry), clouds/weather, airship, settlements and flight props. No dynamic script or procedural terrain generation runs

## Texture contract

- `height49-1m.exr` or `height49-1m-rf.res`: signed highest support Y
- `depth49-1m.exr` or `depth49-1m-rf.res`: `max(0, -height)` at exact lattice points
- The `.res` files are `Image` resources with `Image.FORMAT_RF`, not prebuilt ImageTexture resources. Load the Image, then create `ImageTexture.create_from_image(image)` in the real renderer
- EXR and RF resources both round-trip through Godot 4.5.1 with bit-exact float32 image data. No half-float compression or sRGB conversion
- Resolution: 769 columns × 1537 rows, 1 metre spacing, both endpoints included
- Uniform `world_bounds = vec4(768.0, -2304.0, 1536.0, -768.0)` means xmin, zmin, xmax, zmax
- Pixel `(i,j)` represents world `(x=768+i, z=-2304+j)`; X increases across columns, Z increases down rows. No image flip
- Exact half-texel-correct sampling: `uv = (world_xz - world_bounds.xy + vec2(0.5)) / vec2(769.0, 1537.0)`
- Sampler: linear filtering, repeat disabled, no mipmaps, no color/source_color hint
- Prefer sampling signed height then `depth = max(0.0, sea_level_y - height)` with sea_level_y=0. This preserves the interpolated signed zero crossing; interpolating already-clamped depth is a different approximation
- Do not use `(world_xz-min)/(max-min)` directly as hardware texture UV: it is shifted relative to this endpoint lattice

## Boundary behavior

The bake has no missing lattice samples, no invented fill, no shoreline painting, blur or dilation. Domain edges are not all dry:

- West X=768: water continues across Z=-1004..-895, minimum Y=-23.1503m
- South Z=-768: water continues across X=826..1248, minimum Y=-1.0532m
- East and north boundaries are dry

For the bounded A/B/A diagnostic, strictly mask outside the domain and retain the original depth input there. Do not clamp this map across adjacent lakes. If a continuous regional replacement is intended later, inspect an expanded actual-source domain toward X=0 and Z=0; those suggested bounds have not yet been baked or proven enclosed.

## Accuracy and limits

`depth49-bake-report.json` contains deterministic seed, source/map hashes, 2,500 independent BVH grid checks, 4,000 continuous random checks and 2,180 actual exposed shoreline crossings. `island-side-probes.json` adds 256 probes across eight sides of each of the four islands.

- Grid-point maximum height error: 0.00000751m
- Continuous bilinear height: P95 0.00969m, maximum 6.865m
- Overall shoreline zero-offset: P95 0.724m, maximum 1.906m; 15 of 2,180 tested crossings had no interpolated texture zero within ±2m
- New-island shoreline specifically: P95 horizontal offset 1.045m; maximum sampled vertical error at narrow/steep wetshore pieces 25.016m

The large local errors are explicit 1m sampling aliasing near steep upper-envelope changes and sub-metre wetshore fragments. The artifact can test whether view-dependent screen depth causes the cyan columns; it is not final nearshore-quality acceptance. A later precision fix may require higher-resolution island tiles or analytic shoreline handling. Do not claim the 1m map reproduces every actual shoreline exactly.

All image-package read-back checks are in `image-package-report.json`. Existing Game49 scene and resources remain unchanged.
