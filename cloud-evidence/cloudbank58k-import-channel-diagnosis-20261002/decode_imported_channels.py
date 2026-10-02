"""Bounded offline decode of the preserved imported cache. Never starts Godot."""
from pathlib import Path
import hashlib
import struct
import sys
import numpy as np
import zstandard
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'source-assets/cloud-bank58/revision-k/import-v1'))
import contract58k as c
DECODER = ROOT / 'source-assets/north-ridge62-intake/scatter-readonly-v1/decoder62.py'
decoder = c.load(DECODER)
RUN = ROOT / 'cloud-evidence/cloudbank58k-transfer-v2-20261002T094351Z-egb4wx8d'
CACHE = RUN / 'imported-cache/cloud58k-native-import.scn'
CACHE_SHA = '1b94f241fba9cc48a7879ec71dee4ecff3854955be37f344158494997d3c3e42'

# Extend only this private imported decoder module's explicit schemas. The
# existing decoder file, data and process-wide native engine are untouched.
decoder._SCHEMAS['PackedScene'] = dict(decoder._COMMON, _bundled=(26,))
decoder._SCHEMAS['StandardMaterial3D'].update(albedo_color=(20,), metallic=(4, 41))


class CompressedReader(decoder._Reader):
    def __init__(self, data):
        super().__init__(data)
        self.initial_magic = True

    def take(self, size):
        # RSCC wraps the resource body without a leading RSRC marker; body
        # offsets are already correct and must not be shifted by four bytes.
        if self.initial_magic:
            decoder.require(size == 4, 'Initial logical resource magic')
            self.initial_magic = False
            return b'RSRC'
        return super().take(size)

    def variant(self, depth=0):
        decoder.require(depth <= decoder.MAX_DEPTH and self.end - self.pos >= 4, 'Variant bounds/depth')
        if struct.unpack_from('<I', self.data, self.pos)[0] == 22:
            self.read('I'); names, subnames = self.read('2H')
            count = names + (subnames & 0x7fff)
            decoder.require(count <= (self.end - self.pos) // 4, 'NodePath count bounds')
            self.kinds.add(22); self.variants += 1
            decoder.require(self.variants <= decoder.MAX_ITEMS, 'Variant budget')
            return dict(node_path_names=[self.named() for _ in range(names)],
                        node_path_subnames=[self.named() for _ in range(subnames & 0x7fff)], absolute=bool(subnames & 0x8000))
        return super().variant(depth)


def decode_cache(path=CACHE):
    raw = Path(path).read_bytes()
    c.require(len(raw) == 11096 and hashlib.sha256(raw).hexdigest() == CACHE_SHA, 'Preserved actual cache identity')
    c.require(raw[:4] == b'RSCC', 'Actual RSCC container')
    mode, block, total = struct.unpack_from('<3I', raw, 4)
    c.require((mode, block, total) == (2, 4096, 29492), 'Exact bounded observed compression layout')
    count = total // block + 1
    sizes = struct.unpack_from('<' + 'I' * count, raw, 16); pos = 16 + 4 * count; chunks = []
    for index, size in enumerate(sizes):
        c.require(0 < size <= len(raw) - pos - 4, 'Compressed block extent')
        expected = min(block, total - index * block)
        part = zstandard.ZstdDecompressor().decompress(raw[pos:pos+size], max_output_size=max(1, expected))
        c.require(len(part) == expected, 'Exact decompressed block extent')
        chunks.append(part); pos += size
    c.require(raw[pos:] == b'RSCC', 'Exact compressed trailer')
    body = b''.join(chunks); doc = CompressedReader(body).parse()
    c.require(not doc['external_resources'] and [r['type'] for r in doc['resources']] == ['StandardMaterial3D', 'ArrayMesh', 'PackedScene'], 'Actual embedded material/mesh/scene only')
    surfaces = doc['resources'][1]['properties']['_surfaces']
    c.require(len(surfaces) == 1, 'One actual surface')
    surface = surfaces[0]
    c.require(surface['format'] == 34359742471 and surface['primitive'] == 3 and surface['vertex_count'] == surface['index_count'] == 1152, 'Observed V/N/T/I triangle surface')
    def payload(key):
        item = surface[key]; data = body[item['payload_offset']:item['payload_offset']+item['payload_bytes']]
        c.require(hashlib.sha256(data).hexdigest() == item['payload_sha256'], 'Packed payload SHA')
        return data
    vertex_data = payload('vertex_data'); index_data = payload('index_data')
    c.require(len(vertex_data) == 1152 * (12 + 4 + 4) and len(index_data) == 1152 * 2, 'Uncompressed position plus two packed oct pairs')
    positions = np.frombuffer(vertex_data[:1152*12], dtype='<f4').reshape(-1, 3)
    normal_tangent = np.frombuffer(vertex_data[1152*12:], dtype='<u2').reshape(-1, 4)
    indices = np.frombuffer(index_data, dtype='<u2').astype(int)
    c.require(np.isfinite(positions).all() and indices.max() < 1152, 'Finite position and bounded index values')
    return doc, body, positions, normal_tangent, indices


def oct_decode(values):
    values = np.asarray(values, np.float32)
    f = values * np.float32(2) - np.float32(1)
    n = np.stack([f[:, 0], f[:, 1], np.float32(1) - np.abs(f[:, 0]) - np.abs(f[:, 1])], axis=1)
    amount = np.clip(-n[:, 2], np.float32(0), np.float32(1))
    n[:, 0] += np.where(n[:, 0] >= 0, -amount, amount)
    n[:, 1] += np.where(n[:, 1] >= 0, -amount, amount)
    return n / np.sqrt(np.sum(n*n, axis=1))[:, None]


def unpack_channels(q):
    normals = oct_decode(q[:, :2].astype(np.float32) / np.float32(65535))
    tangent_oct = q[:, 2:].astype(np.float32) / np.float32(65535)
    tangent_oct[:, 1] = tangent_oct[:, 1] * np.float32(2) - np.float32(1)
    signs = np.where(tangent_oct[:, 1] >= 0, 1, -1).astype(np.float32)
    tangent_oct[:, 1] = np.abs(tangent_oct[:, 1])
    tangents = oct_decode(tangent_oct)
    return normals, np.column_stack([tangents, signs])


def mapped_source_normals(positions, indices, source):
    expected = c.mapped(source['positions']); faces = np.asarray(source['triangles']); actual_corners = np.asarray(source['corner_normals'])
    distance = np.max(np.abs(positions[:, None] - expected), axis=2)
    c.require(np.all((distance == 0).sum(axis=1) == 1), 'Actual cache positions map uniquely to source')
    mapping = distance.argmin(axis=1); actual = mapping[indices.reshape(-1, 3)[:, [0, 2, 1]]]
    by_face = {c.canonical(face): index for index, face in enumerate(faces)}
    c.require(sorted(map(c.canonical, actual)) == sorted(by_face), 'Godot clockwise triangle bijection')
    result = np.empty((1152, 3), np.float32); assigned = np.zeros(1152, bool)
    for face, render_indices in zip(actual, indices.reshape(-1, 3)):
        source_face = by_face[c.canonical(face)]; loops = source['polygon_loop_indices'][source_face]
        normal = c.mapped(actual_corners[loops[0]])
        for index in render_indices:
            c.require(not assigned[index] or np.array_equal(result[index], normal), 'One cached vertex has one source normal')
            result[index] = normal; assigned[index] = True
    c.require(assigned.all(), 'Every cached vertex assigned')
    return result


def main():
    verified = c.source_preconditions()
    wrapper = c.read(RUN / 'wrapper-report.json'); stopped = c.read(RUN / 'godot-import.json')
    c.require(wrapper['passed'] is False and [row['returncode'] for row in wrapper['stages']] == [0, 1], 'Original native import/readback boundary')
    c.require(stopped['passed'] is False and stopped['error'] == 'Only positions, normals and indices', 'Original channel failure unchanged')
    c.require(all(wrapper[key] is True for key in ['inputs_unchanged', 'main_project_unchanged', 'source_unchanged']), 'Original protected finalization')
    sidecar = RUN / 'cloud58k.glb.import'
    c.require(c.sha(sidecar) == 'a21107419255bdf37968d48464e4f5996bf3289c266f5d832447e256ac6b2d1d', 'Actual importer sidecar identity')
    options = dict(line.split('=', 1) for line in sidecar.read_text().splitlines() if '=' in line)
    c.require(options['meshes/ensure_tangents'] == 'false' and options['meshes/force_disable_compression'] == 'true', 'Actual importer options')
    doc, body, v, packed, indices = decode_cache()
    normals, tangents = unpack_channels(packed)
    source = c.read(RUN / 'transfer-source.json')
    c.require(c.geometry_fingerprint(source['positions'], source['triangles']) == verified['native_identity']['mesh'], 'Accepted source array identity')
    geometry = c.validate_geometry(dict(positions=v.tolist(), normals=normals.tolist(), indices=indices.tolist()), source, clockwise=True)
    native_source = mapped_source_normals(v, indices, source)
    per_face = indices.reshape(-1, 3)
    summary = dict(status='offline_actual_saved_channel_diagnosis', original_native_readback_passed=False,
                   cache_sha256=CACHE_SHA, cache_bytes=CACHE.stat().st_size, decompressed_bytes=len(body), decompressed_sha256=hashlib.sha256(body).hexdigest(),
                   source_bytes_unchanged=c.sha(c.SOURCE) == c.SOURCE_SHA, source_sha256=c.SOURCE_SHA,
                   sidecar_sha256=c.sha(sidecar), wrapper_sha256=c.sha(RUN / 'wrapper-report.json'),
                   format=34359742471, format_hex='0x800001007', format_bits=[0, 1, 2, 12, 35],
                   channels=['VERTEX', 'NORMAL', 'TANGENT', 'INDEX'], vertex_count=1152, index_count=1152, triangle_count=384,
                   all_other_vertex_channels_absent=True, compression_flag=False, actual_ensure_tangents_option=False,
                   geometry_contract=geometry, tangent_count=1152, tangent_components=4608,
                   tangent_unit_error=float(np.max(np.abs(np.linalg.norm(tangents[:, :3], axis=1) - 1))),
                   tangent_normal_dot_max=float(np.max(np.abs(np.sum(normals*tangents[:, :3], axis=1)))),
                   tangent_source_normal_dot_max=float(np.max(np.abs(np.sum(native_source*tangents[:, :3], axis=1)))),
                   tangent_signs=sorted(set(tangents[:, 3].tolist())),
                   all_face_tangents_equal=bool(np.array_equal(tangents[per_face], np.repeat(tangents[per_face[:, 0]][:, None], 3, axis=1))),
                   packed_normal_sha256=hashlib.sha256(packed[:, :2].astype('<u2').tobytes()).hexdigest(),
                   packed_tangent_sha256=hashlib.sha256(packed[:, 2:].astype('<u2').tobytes()).hexdigest(),
                   decoded_arrays_are_offline_not_native_api_readback=True, exact_insertion_call_not_proven=True,
                   engines_started=0, images=0, world_loaded=False)
    c.require(c.read(HERE / 'decoded-resource.json') == doc, 'Earlier decoded record replay identical')
    c.write(HERE / 'diagnosis-final.json', summary)
    print(c.json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
