# World boundary classification preparation and saved catalog reconciliation

Status: source-only preparation. No Godot invocation, GDScript parse, new native collection, scene instantiation or collision test was performed for this revision. The prior failed run remains immutable. Only `collect_saved62.gd` and this new analysis directory belong to this change.

## Actual saved sea and supported semantics

`saved-sea-source-facts.json` records the exact relevant node/resource blocks and SHA-checked five-scene inheritance chain. `World/Ocean/SeaCollision/Shape` binds `WorldBoundaryShape3D_qam02` in pinned53d. The resource has no plane override, so its native default is Plane(0,1,0,0). The root, World, Ocean, SeaCollision and Shape have identity effective saved transforms; later55/56/60/61 have no sea overrides. The default CollisionShape disabled flag is false. Its StaticBody has collision_layer=5 (World solid + Ground probe) and collision_mask=2 (Airship); default disable_mode=0. This describes saved configuration, not whether live scripts or processing state leave collision enabled.

The current source would record local/global normal(0,1,0), world equation y=0, outward direction +Y, strict solid interior y<0 and conservative closed solid half-space y<=0. It stores transform basis columns, origin, native encoding, resource identity, property provenance, shape/body collision flags, process-mode ancestry and metadata. It retains every world boundary in a separate `unbounded_world_boundaries` array, regardless of the finite query rectangle or disabled flag. The Ocean's separate saved mesh AABB remains finite visual geometry; it is never substituted for the plane.

The algorithm follows pinned4.5.1 `Transform3D::xform_fast(Plane)`: inverse-transpose the normal and normalize it; transform normal*d as a point on the unit-normal plane; dot the resulting world normal and point for world d. It does not just multiply a normal by the basis. Negative determinant transforms preserve the oriented half-space through the inverse transpose, with no extra determinant-sign flip. Non-unit local normals fail closed: the native resource setter does not normalize them and xform's chosen point assumes a unit normal. The collector never silently rewrites that saved resource. Finite plane/transform/determinant, nonzero normal, invertible finite basis inverse and finite nonzero transformed normal/result are all required.

`CollisionShape3D` supplies its local transform to its direct CollisionObject parent. This revision requires that parent and rejects top_level shapes rather than mistake their independent scene-global transform for collision placement. Unsupported disable_scale/alternative transform representations and invalid ancestry, process/collision flags fail closed. Unknown Shape3D classes still produce the original unbounded_saved_shape issue. Mathematically correct nonuniform/shear plane transformation is not a physics-backend test; the engine documentation warns about scaled collision nodes.

Godot Physics' enormous broadphase sentinel AABB is not a true finite bound. Jolt's finite world-boundary implementation is also recorded as a backend caveat rather than used for clearance. Both finite_occupancy_clearance_proved and runtime_physics_behavior_proved stay false. Existing runtime/MM/road-width gaps, all_occupancy_complete=false and visual_acceptance=false are unchanged.

## Pinned official references

Full official source snapshots, including upstream license headers, and their byte SHA256/URLs are in `upstream/source-manifest.json` (all at4.5.1-stable):

- [WorldBoundary resource default and unchanged setter](https://github.com/godotengine/godot/blob/4.5.1-stable/scene/resources/3d/world_boundary_shape_3d.cpp)
- [Plane transform and inverse-transpose implementation](https://github.com/godotengine/godot/blob/4.5.1-stable/core/math/transform_3d.h)
- [Plane sign/equation implementation](https://github.com/godotengine/godot/blob/4.5.1-stable/core/math/plane.h)
- [CollisionShape parent/local-transform behavior](https://github.com/godotengine/godot/blob/4.5.1-stable/scene/3d/physics/collision_shape_3d.cpp)
- [Godot Physics world-boundary point test and sentinel](https://github.com/godotengine/godot/blob/4.5.1-stable/modules/godot_physics_3d/godot_shape_3d.cpp)
- [WorldBoundary documentation and Jolt caveat](https://github.com/godotengine/godot/blob/4.5.1-stable/doc/classes/WorldBoundaryShape3D.xml)
- [Plane unit-normal requirement](https://github.com/godotengine/godot/blob/4.5.1-stable/doc/classes/Plane.xml)

## Failed-run saved catalog reconciliation

Input: `cloud-evidence/north-ridge62-collect-20261002T050835Z-k8_cwtci/native-intake.json`,1211462bytes,SHA256 bd48c7ccbaee51cbf43dba1efeac7a78957de59166eeafcecddbfb1038744b04. Its saved_data_read_complete=false and unbounded_saved_shape issue remain historical facts. The analysis script reads that raw file or the lossless gzip and rejects changed bytes.

`saved-settlement-catalog.json` contains all172 exact names, complete min/max XYZ bounds, original40m-padded bounds and every contributing part path. Every recorded full bound was independently recomputed as the exact union of all recorded parts. The172 identities comprise149cottage,6dock,6crate,3mill,3mill_rotor,2lighthouse,1castle,1observatory,1ruins. This is not a172-house claim.

The buffered query is X[-3088,-2000],Z[-5200,-3730]. Zero of172 saved settlement bounds overlaps its X interval; hence zero intersects the XZ query, even though24 overlap Z. Of those24,12 are entirely west and12 entirely east. No nearest12 selection occurs, and the historical northern12 identity claim remains unverified.

The four bounded entity intersections are:

- `World/Ocean`: min[-50000.0, 0.0, -50000.0],max[50000.0, 0.0, 50000.0]; 1/1 individual parts overlap query
- `NativeCoastalSky27f/_Node3D_712`: min[-2653.443359375, 594.208923339844, -4661.7880859375],max[-1848.7890625, 800.850708007812, -4230.63427734375]; 4/4 individual parts overlap query
- `Weather42b/Rainbow`: min[-3200.0, -250.0, -3900.0],max[-1400.0, 650.0, -3900.0]; 7/7 individual parts overlap query
- `Weather42b/CoastalStorm`: min[-4599.126953125, 341.736083984375, -4925.72705078125],max[-3000.0029296875, 830.854370117188, -3488.33666992188]; 0/87 individual parts overlap query

All four whole-group AABBs overlap both query X and Z; none is a settlement. CoastalStorm is an especially conservative grouping: its87parts span a large box but no individual part box intersects this query. This is an expected false-positive from preserving whole-entity ownership, not proof of actual storm occupancy or visibility. Ocean, cloud and Rainbow have1,4and7part hits respectively. These are saved bounds including potentially hidden geometry, not live renders.

### Western Z-overlapping cottage cluster

Selection: all catalog entries overlapping query Z and strictly west of query X. Union min[-3360.1787109375, 22.5930004119873, -5048.17041015625],max[-3241.00390625, 39.6990013122559, -4946.12548828125]. The nearest full-bound X edge is 153.00390625m west of the buffered query and 193.00390625m west of the design envelope. Do not reinterpret this adjacent12-member cluster as the historical intended12.

- `World/Settlements/cottage_57299`: min[-3266.55151367188, 22.5930004119873, -4970.55419921875],max[-3258.00268554688, 28.925500869751, -4962.52978515625]
- `World/Settlements/cottage_57300`: min[-3275.92407226562, 23.4459991455078, -4985.6435546875],max[-3270.28784179688, 29.7104988098145, -4978.6787109375]
- `World/Settlements/cottage_57301`: min[-3312.1982421875, 25.7129993438721, -5021.6982421875],max[-3297.93359375, 36.2275009155273, -5008.18359375]
- `World/Settlements/cottage_57302`: min[-3250.90625, 23.7029991149902, -5004.28564453125],max[-3241.00390625, 31.0809993743896, -4995.07275390625]
- `World/Settlements/cottage_57303`: min[-3355.48266601562, 27.1580009460449, -4991.47216796875],max[-3348.74340820312, 33.3629989624023, -4986.09423828125]
- `World/Settlements/cottage_57304`: min[-3271.14282226562, 23.7840003967285, -4995.41552734375],max[-3257.46508789062, 33.9075012207031, -4982.56005859375]
- `World/Settlements/cottage_57305`: min[-3300.79907226562, 28.9589996337891, -5047.12548828125],max[-3291.40698242188, 35.9119987487793, -5038.30029296875]
- `World/Settlements/cottage_57306`: min[-3360.1787109375, 29.1420001983643, -5048.17041015625],max[-3346.76123046875, 39.6990013122559, -5033.90185546875]
- `World/Settlements/cottage_57307`: min[-3268.20458984375, 24.8700008392334, -5016.48583984375],max[-3259.33740234375, 31.4660015106201, -5008.21630859375]
- `World/Settlements/cottage_57308`: min[-3296.6162109375, 22.806999206543, -4976.63134765625],max[-3287.5556640625, 30.1679992675781, -4968.81298828125]
- `World/Settlements/cottage_57309`: min[-3354.89282226562, 27.2940006256104, -5037.58642578125],max[-3342.67309570312, 36.8819999694824, -5024.61572265625]
- `World/Settlements/cottage_57310`: min[-3334.33862304688, 23.8460006713867, -4955.96044921875],max[-3323.47534179688, 32.1420021057129, -4946.12548828125]

The eastern Z-overlapping group is cottage_57275 through cottage_57286; union min[2191.8994140625, 15.2019996643066, -4255.0390625],max[2301.03955078125, 28.2224998474121, -4143.9228515625]. It is 4191.8994140625m east of the query. Full individual bounds are in both JSON catalogs.

775MultiMesh groups remain unresolved,3curves provide control-hull bounds only, and runtime-generated entities remain unproved. No terrain-edit clearance or approved footprint follows from this catalog.

## Verification and next authorized boundary

- `check_world_boundary62.py`:106positive plane-math cases (identity, offset, rotation, nonuniform scale, shear, reflection and100seeded affine cases),12negative numeric cases,25negative source-guard mutations. Passed under ordinary Python and python -O; all9official-source snapshot hashes checked
- `analyze_saved_catalog62.py`:all172unique identities, exact full-part unions and spatial tests rechecked under ordinary Python and python -O
- `static-preparation.json`:existing full dependency/source preparation check, with1483closure identities, passed for this collector SHA. This is not a GDScript parse
- Old PREPARATION_CHECK, plan, dependency guard/auditors/review, failed run, world/resources, Git and publication records are not modified by this work

Commands (Python only):

    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/world-boundary-v1/check_world_boundary62.py
    PYTHONDONTWRITEBYTECODE=1 python -O source-assets/north-ridge62-intake/world-boundary-v1/check_world_boundary62.py
    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/world-boundary-v1/analyze_saved_catalog62.py
    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/run_intake62.py --static-only

A separately coordinated future parse and then native collection are still needed. Only that new run may establish whether the changed GDScript parses and emits its expected record; neither this preparation nor a later saved read proves live collision behavior, runtime occupancy or visual acceptance.
