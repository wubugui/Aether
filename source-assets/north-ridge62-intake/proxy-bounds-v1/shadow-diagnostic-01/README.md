# Exact replay of the first shadow-array stop

Completed offline against unchanged fixed inputs. No engine, download, main-project change, old evidence rewrite or tolerance change.

## What is established

The failed v2 report SHA is `12a9077d9cdbba6c402ad70d03d43b5d757e557c42fd179e1410a13e0857dad0`. Its engine guard passed, then it stopped on the first CoastalPines primary/shadow pair because the shadow API did not return vertex positions.

Reusing the existing strict RSRC decoder and the compressed-position arithmetic already present in `coast61-nearbay-orbit/visible_geometry61.gd` gives:

- Primary: 120 decoded vertices, byte SHA `76ae8f87cee80408e43fc1cb7f7dd629a3db981332c72a7d8dde731e676df22a`, exactly the actual native vertex hash
- Shadow: 36 decoded vertices, byte SHA `b192ee4890229a35f679f3ebc8e8dd58fb1e0c1aab27c599fc55ed4e1091cf04`
- Primary and shadow: exactly equal oriented multisets of 56 indexed triangles / 168 face vertices. Winding and multiplicity are retained; vertex numbering and triangle order may differ
- This pair has only threshold 0, no additional saved LOD. The same offline check also passed every saved base/LOD level for all five canonical pine/oak/poplar/rock/bush identities; all currently have only threshold 0. The proposed native reuse still checks every level, without assuming this remains so

## The ~2e-5 face-bound difference

It is the established `Mesh.get_faces()` 0.1 mm snapping path, not unexplained compressed-decoder drift. The checked `scene__resources__mesh.cpp` source routes `get_faces()` through `generate_triangle_mesh()` and `TriangleMesh::create(faces)`; the existing nearbay README explicitly distinguishes this snapped path from actual indexed visual triangles.

Applying float32-step snapping to all 168 decoded primary indexed face vertices reproduces the entire actual native `get_faces()` byte SHA exactly:

`509df225d3b50e9b177da02ce9146e73f4382368c7baf77e43a965ab5480afbd`

All six extrema also match. Float32 step is `0.00009999999747378752` (little-endian bytes `17b7d138`). Face-minus-vertex extrema differences are:

- Minimum XYZ: `+0.000019073486328125`, `0`, `+0.0000002384185791015625`
- Maximum XYZ: `-0.000019073486328125`, `0`, `+0.000021219253540039062`

The maximum Z demonstrates why exact snapped face extrema cannot be required to lie within unsnapped raw-vertex extrema. Both are legitimate distinct source products. The corrective plan records actual indexed visual bounds and actual `get_faces()` bounds separately, verifies the snap correspondence exactly, and unions their conservative bounds. No epsilon is introduced or enlarged. This is an exact reproduction for these fixed inputs, not a new general proof of engine internals.

## Reuse scope

The existing helper's `surface_positions`, `decoded_indices`, `audit_surface`, `oriented_triangles` and `audit_array_mesh` already cover the narrow position-only compressed-shadow null-API case. They validate actual payload sizes/formats/indices and require equal primary/shadow surface bounds, thresholds, winding and triangle multiplicity at base and every LOD. Metadata is a decoder parameter, not a substitute for decoded vertices. Helper SHA256 is `966c863a02d136aefacb78e76d7301649b96c628408c589d3a4345fac30086f7`.

An independent `shadow-arrays-v3` source patch can reuse these exact methods in the original small collector. It need not create a world, activate physics, read every world buffer again or perform a separate exploratory engine run. Its future scheduled read still needs to finish the six visual source identities and the first imported rock mesh, which the failed v2 never reached.

## Reproduce

`PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/proxy-bounds-v1/shadow-diagnostic-01/reproduce_shadow62.py`

Normal and `-O` output are byte-identical. `INPUTS.json` binds all consulted evidence and source files before/after. `DIAGNOSIS.json` retains complete numerical/hash results without dumping geometry or saved world buffers. All original occupancy/runtime/visual-acceptance limitations remain unchanged.
