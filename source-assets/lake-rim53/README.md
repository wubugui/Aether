# Lake rim53 native-source candidate (not integrated)

**Visual status: rejected and being revised.** Both first-west and revision-b source previews failed shape review. A later root-edge audit also found visible edge exposure between initially buried vertices. Read [REVIEW_STATE.md](REVIEW_STATE.md) before using this package; its numeric passes are not source or scene acceptance.

Candidate base is the saved Game51b SHA256 `b169f62527a52b9f2a3f091c2d7db136ad7cd67111e405f08f390eeb082e2bb1`. This work is a local four-mountain source candidate. Original `ref/1128.png`, `ref/1129.png`, and the actual 51b original1128 reflection-on screenshot were viewed before authoring. Coordinates below are authored inferences within the actual saved world, not metric facts established by the references.

No Game51b, project default, source48, source49, cliff master, world generator, route, saved terrain tile or shader was changed. The missing west source was obtained only with `git show HEAD:blender/mountain_kit/massif_west_spur.blend` into this independent directory. All final source assets have editable native Blender objects, per-corner vertex palettes, actual rock volume and closed snow volume; no camera-facing geometry or image billboards are used.

## What was authored

- West spur: unchanged original rock root plus an asymmetric longitudinal stone ridge, 326m highest rock and 328m snow, with a lower 261m saddle between its two principal shoulders. Two independent snow channels cross the slopes. Five editable mesh objects, 2,556 triangles
- Cirque wall: unchanged48 carved lake foot plus a broad continuation toward the lake, highest rock238m/snow240m. The initial footprint at X902/Z-1610 had actual support only2.87m and was rejected; the final eastern skirt ends farther inland. Five objects,3,024 triangles
- East foothill: unchanged48 original carved foot plus a broad eastern mass rooted into actual terrain, highest rock328m/snow329m, three uneven crest shoulders and a wide central saddle. Five objects,5,032 triangles
- Frost crown: only seven unprotected original vertices above355m lowered. Existing northern building footprint+50m triangles locked75 source vertices. This conservatively leaves a409m high point, above the proposed395m target; the visual goal is unresolved. Four objects,474 triangles. The inland crown has no newly invented shore apron

The three lateral roots are deliberately retained as native `rock_body` objects. Their new silhouette is authored by separate closed `ridge_shoulders`, `snow_cap`, `snow_gully`, and `shore_rock_apron` volumes rooted into measured saved support. Full side/back bodies are present. Snow lenses have bottom surfaces0.32m below their matching actual rock triangles and top thickness0.8–2.2m, with closed boundary walls. This is an additive source sculpt, not an equal scale of the old conical mesh.

## Authority, readback and protection

`base51b.json` is a real Compatibility-renderer read-only scene export. It includes all11 mountains, the six adjacent terrain meshes,18 actual building mesh bounds, and all1,261 actual scatter transforms. `base51b-headless.json` is the separate geometry-only intake; its empty scatter instance arrays were never used as scatter evidence.

`source-equivalence-intake.json` and `sculpt-report.json` show exact saved triangle topology after nearest-vertex mapping for all four native sources. West and crown source quantization differed by up to1.32cm/2.10cm, and source48 by≤0.14mm. Every native source was first remapped to the saved51b coordinates. The three lateral original body vertex positions are unchanged after this authority mapping; the crown report lists every changed original vertex. Original source files remain untouched.

`verification-report.json` independently reopens all four saved`.blend` files and confirms all19 components against the payload triangle topology at0.1mm precision. Every component is closed, with zero boundary edges, nonmanifold edges or degenerate faces, and positive signed volume. Building actual footprints plus the prescribed northern50m buffers were probed at2m spacing; highest-support differences are≤0.00037m numerical tolerance. The source lock uses whole original triangles conservatively, which is why the remaining crown peak was not forced down.

## Water and neighboring terrain

All six terrain meshes remain unchanged. New ridge perimeter/underside vertices sample the actual highest saved terrain/mountain support and initially embed7–23m below that dry support. Later0.5m edge sampling found intermediate exposed edge segments (west first1.01m and revision-b3.01m); full perimeter burial was not established for either. Revision-c changes the edge construction and has a measured minimum4m burial margin, but is still an unreviewed topology prototype. Existing carved cirque/east underwater roots are preserved.

`continuous-water-footprint-proof.json` clips every actual saved triangle at Y0, unions its dry XZ footprint with installed GEOS3.13.1, and subtracts that union from every new component's complete projected footprint. All added footprints lie on actual saved dry support (largest numerical outside area2.64e-12m²). This provides continuous planar containment evidence, rather than relying only on a drawn boundary or finite samples.

A second independent Blender BVH audit probes1,746,660 points on a1m grid across X150–2180/Z-2304–-1445. All214,309 original underwater columns have exactly unchanged highest support and no new dry column. With no changed underwater support, this source candidate does not introduce a new water-depth texture. Parent integration still needs a whole saved-World depth/zero-line check, since this source audit does not claim to be a new world bake.

## Scatter proposal

All1,261 indices and original instance rotations/scales remain. `verification-report.json` records every index, old/new position, support, slope and disposition.1,052 are unchanged,183 are relocated from newly exposed rock/snow to measured unchanged dry ground in the same tile, and26 rocks are vertically re-supported on suitable new stone triangles. Relocations avoid building buffers, slopes steeper than the stated criterion and occupied positions within10m. Maximum preserved support-clearance residual is0.000244m; no inherited>1m support outliers were found.

Per tile (unchanged / relocated / rock re-supported):

- Ground_0_-2:138 /2 /0 (140 total)
- Ground_0_-3:270 /106 /4 (380)
- Ground_1_-2:111 /0 /0 (111)
- Ground_1_-3:327 /59 /3 (389)
- Ground_2_-2:167 /1 /0 (168)
- Ground_2_-3:39 /15 /19 (73)

The payload contains the209 proposed transform updates. No scatter in the saved51b scene has been mutated. The three islands and their seven pines are outside this payload.

## Parent integration contract and outstanding gates

`rim53-payload.json` contains four mountain families,19 components, component world vertices/colors, merged collision world vertices, origin, existing asset node paths, and209 scatter updates with before/after transforms. Each added part must receive the existing51b verified mountain parent`surface_material` (including the dual-guard shader), both in saved and runtime-ready bindings. Existing layer5 includes the layer4 probe bit and must be retained; replace collision faces with all actual component faces using the asset transform inverse. Preserve non-target fields canonically. Independent native prefabs, saved mesh/collision files and a candidate scene are still the parent's integration stage; they are not yet claimed here.

`launch_preview53.sh`/`preview_sources53.gd` provide a native real-renderer, same-light five-view source preview. They do not save a gameplay scene. Every run must use its unique evidence directory. Source numeric checks do not constitute acceptance. Pending: inspect source front/side/back/top images, correct forms, then original1128/1129 and1275/1276, actual-world near/side/back views, material/normal/shadow/reflection continuity, actual collision probing, adjacent visual seams, scatter appearance and original150m/200m routes. Inherited350m route failures and all remaining GOAL gaps remain failures/unverified.

## Preserved failed attempts

The first unsaved snow extraction failed manifold checks at vertex-only patch contacts (west snow_cap8 nonmanifold edges); face-fan splitting fixed that topology. `draft02-water-edge-rejected.log` records the rejected cirque footprint at2.87m support. `draft03-sculpt.py`, `sculpt03.log` and `sculpt04.log` preserve the apron failure produced by folded small grid cells; removing cross-row Z jitter corrected the planar grid without relaxing checks. `sculpt05.log` is the successful19-component source write. These failures are not passes.
