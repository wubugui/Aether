# Four original terrain resources: offline mapping

Status: verified, read-only source extraction and index mapping. No Blender or Godot process was launched. Only files in this directory were created. Original project, survey, intake and preparation inputs have identical before/after hashes.

## Result

All four primary surfaces use format `34896613391` (`0x82000100f`): vertex, normal, tangent, color, index, compressed attributes and current version. Each has 6,144 indices, 2,048 triangles and 1,089 unique local positions. Original attribute vertices are deliberately not welded:

| Target | Original vertices | Index order | Original shadow reference |
| --- | ---: | --- | --- |
| Ground_-4_-7 | 6,144 | Sequential | ArrayMesh_4eksh |
| Ground_-3_-7 | 6,144 | Sequential | ArrayMesh_e6cp0 |
| Ground_-4_-6 | 6,058 | Non-sequential | None |
| Ground_-3_-6 | 6,009 | Non-sequential | None |

Each `Ground_*.mapping.json.gz` contains:

- `source`: identity, source range/hash, raw payload hashes, format/counts, transform and precision summary
- `source_vertices`: original source vertex IDs and local XYZ, world float32 XYZ, exact original survey JSON XYZ, explicit reverse survey expanded-corner / face-corner membership, original RGBA8 and normalized float32 color
- `index_sequence`: unchanged primary surface index order; for expanded corner k, original source vertex is index_sequence[k], face is k//3 and corner is k%3

`Ground_*.source-block.tscn.txt` is the exact original primary ArrayMesh block. The three `.bin` files per mesh retain its exact vertex, attribute and index storage bytes. `mapping-summary.json` contains all input and artifact SHA256s. No additional terrain, shadow, collision, material or scene dependency was decoded.

## Source and survey association

The existing frozen survey script `read_saved_coast.gd` uses `surface_get_arrays`, reads ARRAY_VERTEX / ARRAY_INDEX, expands each index in source order and applies the composed world transform. It does **not** call Mesh.get_faces, snap, weld, or nearest-match terrain vertices. The same script's separate collision branch calls Shape.get_faces; that is not this mesh mapping.

Here the saved local compressed positions are decoded using the already reviewed `visible_geometry61.gd` float32 formula: u16 XYZ / 65535, then component-wise AABB scale and offset. The intake's exact 12-float transform witness is identity basis plus translation; any other transform fails closed in this narrow extractor. Expanding the original index sequence and applying that float32 translation gives byte-for-byte identical float32 XYZ for all 24,576 frozen survey corners, in the same order. There is no tolerance-based acceptance.

Max component mismatch against survey cast to float32: 0.0 m. The survey's textual JSON decimal representation differs from those exact float32 values by at most 5.002220859751105e-12 m. The local-to-world float32 translation itself rounds by as much as 0.000244140625 m. Keep `source_local_xyz` as the original local-coordinate authority; do not reconstruct it by subtracting the tile origin from world survey coordinates. `survey_world_xyz_json` is supplied for exact tuple association to the frozen candidate's `before_xyz` entries.

## Attributes and preservation limits

All four source surfaces contain RGBA8 colors, one four-byte unsigned-normalized record per original attribute vertex. The Godot 4.5.1 GLES storage source confirms four GL_UNSIGNED_BYTE normalized channels. The exact bytes are preserved and directly associated with source IDs and every survey corner. Colors can therefore be carried into an editable source without estimating them from position, screenshots or a palette. Attribute vertices that share XYZ may carry distinct normals/colors; do not position-weld them as a lossless operation.

Neither UV nor UV2 is present in any of these four formats. `uv_scale = Vector4(0,0,0,0)` is surface metadata, not UV samples. An authored UV layer would be new data, not preserved source UV.

Packed normals/tangents are retained as exact raw bytes only. The first vertex_count*8 bytes of vertex_data store the compressed vertex/tangent section; the following vertex_count*4 bytes hold the packed normal/tangent section. This work does not semantically decode or regenerate normals/tangents. It does not test Blender color-space interpretation or source-to-native roundtrip. Original material references and optional shadow references are recorded but not followed.

Changing height/AABB and recompressing a complete surface may requantize otherwise unchanged positions. This extraction does not authorize or validate that pipeline. Future integration must demonstrate the untouched geometry/attributes and derivative policy separately; raw color preservation here is not a blanket native integration pass.

## Parsing support and nonclaims

The existing RSRC parser does not apply to these embedded text resources. The existing selected-node text parser rejects multiline `_surfaces`. This workflow reuses its reviewed section-header and strict numeric helpers and the established compressed-position decode formula, plus a deliberately narrow exact line-literal extraction for these four pinned, one-surface blocks. It rejects unrecognized layout, properties, fields, format, counts, transform, UV scale, base64 encoding or mismatch; it is not a newly claimed general TSCN parser.

The source scene hash is the same as the frozen native survey and intake. Native `surface_storage_sha256` values are quoted as pinned evidence, not recomputed offline; that variant-serialization hash requires a separate exact serializer/native path. No hash equivalence is claimed between a source block hash, its packed buffers, and a native surface variant hash.

## Reproduction and tests

From Aether, default is read-only and writes nothing:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-authoring/build-v1/offline-mapping/extract_mapping62.py

Adding `--write` writes only this directory. Both ordinary and `python -O` test runs passed 9 positive/negative tests, including all corner matches, artifact hashes, complete reverse membership, malformed base64, changed format/primitive/UV metadata, duplicate/unknown fields and hidden trailing properties. See `tests.txt` and `tests-optimized.txt`.
