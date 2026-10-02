"""Pure normal-only transfer functions. Never write output or launch on import."""
from pathlib import Path
import hashlib
import struct
import sys
import numpy as np
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'normal-readback-v1'))
import guard58k as g
c = g.c
VERSION = 'cloud58k-transfer-v2'
READBACK = c.ROOT / 'cloud-evidence/cloudbank58k-normal-readback-v1-20261002T091816Z-whfkeukw'
RAW_SHA = '35cde26e14f8767c015295cff3b8f271a85052a111d8fd68e066784a18e1b1c7'
DIAGNOSIS = c.ROOT / 'cloud-evidence/cloudbank58k-native-normal-diagnosis-20261002/analyze_actual_normals.py'
DIAGNOSIS_SHA = '3833e0d73a60d466bed3617c2d2f4e6b18c7f1fe18b0c69c60197b8ca4cf8b3c'


def evidence_source():
    verified = c.source_preconditions()
    raw_path = READBACK / 'outputs/source-normal-arrays.json'
    c.require(raw_path.stat().st_size == 281016 and c.sha(raw_path) == RAW_SHA, 'Exact actual native normal capture')
    d = c.read(raw_path); native = c.read(READBACK / 'outputs/native-result.json')
    process = c.read(READBACK / 'blender-normal-readback.process.json'); wrapper = c.read(READBACK / 'wrapper-report.json')
    c.require(d['pid'] == native['pid'] == process['pid'] == wrapper['stages'][0]['pid'] and type(d['pid']) is int, 'Native actual/wait4 PID binding')
    c.require(native['raw_sha256'] == RAW_SHA and native['passed'] is False and wrapper['passed'] is False, 'Original failed validation retained and raw bound')
    c.require(process['native_exit_observed'] is True and process['returncode'] == 1 and process['wrapper_received_signal'] is None and not process['timeout_triggered'] and not process['rss_limit_triggered'], 'Observed bounded original failure')
    c.require(d['cpu_affinity'] == process['cpu_affinity'] == wrapper['stages'][0]['cpu_affinity'] and len(d['cpu_affinity']) == 2, 'Actual CPU2 readback')
    c.require(all(wrapper[key] is True for key in ['inputs_unchanged', 'main_project_unchanged', 'source_unchanged']), 'Original read-only finalization passed')
    c.require(c.sha(DIAGNOSIS) == DIAGNOSIS_SHA, 'Frozen independent diagnostic checker')
    analysis = c.load(DIAGNOSIS)
    checked = analysis.inspect_arrays(d, verified)[0]
    try:
        g.validate_readback(d, d['pid'], verified)
    except ValueError as error:
        c.require(str(error) == 'Actual flat corner normals equal polygon normal exactly', 'Only original incorrect API equality failure')
    else:
        raise ValueError('Original readback failure must not be silently reclassified')
    settings = c.read(c.SETTINGS)
    # Color/roughness were checked against these pinned settings by the actual
    # source collector before raw capture. Metallic/culling remain original
    # source-authoring and import-v1 contract values, not newly measured fields.
    material = dict(base_color_linear_rgba=np.asarray(settings['material_linear_rgba'], np.float32).astype(float).tolist(),
                    roughness=float(np.float32(settings['material_roughness'])), metallic=0., double_sided=True)
    return dict(positions=d['positions'], triangles=d['triangles'], material=material,
                corner_normals=d['corner_normals'], polygon_normals=d['polygon_normals'],
                polygon_loop_indices=d['polygon_loop_indices'], loop_vertex_indices=d['loop_vertex_indices'],
                loop_polygon_indices=d['loop_polygon_indices'], source_sha256=c.SOURCE_SHA,
                actual_native_normal_sha256=RAW_SHA, actual_native_normal_pid=d['pid'],
                original_native_validation_passed=False, independent_array_checks=checked,
                material_evidence='Pinned authored settings enforced by actual readback light_material_identity; original v1 metallic/culling contract; no new material readback claimed',
                source_saved=False, world_loaded=False, visual_acceptance=False)


def assigned_normals(raw, source):
    v = np.asarray(raw['positions'], float); idx = np.asarray(raw['indices'], int).reshape(-1, 3)
    sv = c.mapped(source['positions']); faces = np.asarray(source['triangles'], int)
    corners = np.asarray(source['corner_normals'], float); loops = source['polygon_loop_indices']
    c.require(corners.shape == (1152, 3) and np.isfinite(corners).all() and np.array_equal(corners, corners.astype(np.float32).astype(float)), 'Exact finite actual corner values')
    c.require(len(loops) == 384 and all(len(row) == 3 for row in loops) and sorted(x for row in loops for x in row) == list(range(1152)), 'Exact corner ownership coverage')
    distances = np.max(np.abs(v[:, None] - sv), axis=2)
    c.require(np.all((distances == 0).sum(axis=1) == 1), 'Each render position maps uniquely and exactly to an authored point')
    mapping = distances.argmin(axis=1); actual = mapping[idx]
    by_face = {c.canonical(face): j for j, face in enumerate(faces)}
    c.require(len(by_face) == 384 and sorted(map(c.canonical, actual)) == sorted(by_face), 'Oriented triangle bijection')
    normals = np.empty_like(v); assigned = np.zeros(len(v), bool)
    for face, render_indices in zip(actual, idx):
        source_face = by_face[c.canonical(face)]; source_vertices = faces[source_face].tolist(); row = loops[source_face]
        c.require([source['loop_vertex_indices'][loop] for loop in row] == source_vertices and [source['loop_polygon_indices'][loop] for loop in row] == [source_face] * 3, 'Native source loop mapping')
        c.require(np.array_equal(corners[row], np.repeat(corners[row[0]][None], 3, axis=0)), 'Actual source corners flat exactly')
        for point, render_index in zip(face, render_indices):
            loop = row[source_vertices.index(int(point))]; normal = c.mapped(corners[loop])
            c.require(not assigned[render_index] or np.array_equal(normals[render_index], normal), 'Shared render normal must have unambiguous source ownership')
            assigned[render_index] = True; normals[render_index] = normal
    c.require(assigned.all(), 'No unassigned render vertex')
    return normals


def normal_byte_slots(blob, document):
    json_length, json_kind = struct.unpack_from('<I4s', blob, 12)
    c.require(json_kind == b'JSON', 'JSON first')
    bin_header = 20 + json_length
    bin_length, bin_kind = struct.unpack_from('<I4s', blob, bin_header)
    bin_start = bin_header + 8
    c.require(bin_kind == b'BIN\0' and bin_start + bin_length == len(blob), 'Exact final BIN extent')
    primitive = document['meshes'][0]['primitives'][0]
    accessor_index = primitive['attributes']['NORMAL']; accessor = document['accessors'][accessor_index]
    c.require(accessor['componentType'] == 5126 and accessor['type'] == 'VEC3' and not accessor.get('sparse') and not accessor.get('normalized') and 'min' not in accessor and 'max' not in accessor, 'Uncompressed FLOAT NORMAL with no metadata requiring edits')
    c.require(len(document['accessors']) == 3 and set([primitive['attributes']['POSITION'], accessor_index, primitive['indices']]) == set(range(3)), 'Only the three observed accessors')
    view = document['bufferViews'][accessor['bufferView']]
    c.require(view.get('buffer', 0) == 0 and not view.get('extensions'), 'Embedded ordinary NORMAL view')
    start = bin_start + view.get('byteOffset', 0) + accessor.get('byteOffset', 0); stride = view.get('byteStride', 12)
    c.require(type(stride) is int and stride >= 12 and stride % 4 == 0 and start % 4 == 0, 'Aligned NORMAL slots')
    slots = [(start + i * stride, start + i * stride + 12) for i in range(accessor['count'])]
    c.require(len(slots) == 1152 and all(bin_start <= a < b <= bin_start + document['buffers'][0]['byteLength'] for a, b in slots), 'Exact bounded normal slots')
    allowed = set(offset for a, b in slots for offset in range(a, b))
    c.require(len(allowed) == 1152 * 12, 'Distinct normal byte slots')
    for index, other in enumerate(document['accessors']):
        if index == accessor_index:
            continue
        other_view = document['bufferViews'][other['bufferView']]
        width = (3 if other['type'] == 'VEC3' else 1) * {5123: 2, 5125: 4, 5126: 4}[other['componentType']]
        base = bin_start + other_view.get('byteOffset', 0) + other.get('byteOffset', 0)
        step = other_view.get('byteStride', width)
        c.require(all(not any(offset in allowed for offset in range(base + i * step, base + i * step + width)) for i in range(other['count'])), 'NORMAL slots cannot overlap another accessor')
    return slots, allowed


def validate_restored_bytes(blob, result, source):
    document, raw, material = c.parse_glb_bytes(blob)
    normals = assigned_normals(raw, source)
    slots, allowed = normal_byte_slots(blob, document)
    c.require(len(result) == len(blob) and all(result[i] == byte for i, byte in enumerate(blob) if i not in allowed), 'Every non-NORMAL byte unchanged')
    new_document, restored, new_material = c.parse_glb_bytes(result)
    c.require(new_document == document and new_material == material and restored['positions'] == raw['positions'] and restored['indices'] == raw['indices'], 'JSON/material/position/index identity')
    c.require(np.array_equal(np.asarray(restored['normals']), normals), 'Restored NORMAL equals mapped actual source corner exactly')
    geometry = c.validate_geometry(restored, source); material_result = c.validate_material(new_material, source)
    changed = [index for index, (a, b) in enumerate(zip(blob, result)) if a != b]
    return dict(passed=True, source_sha256=source['source_sha256'], actual_native_normal_sha256=source['actual_native_normal_sha256'],
                raw_glb_sha256=hashlib.sha256(blob).hexdigest(), adjusted_glb_sha256=hashlib.sha256(result).hexdigest(),
                bytes=len(blob), normal_slots=len(slots), allowed_normal_byte_count=len(allowed), changed_byte_count=len(changed),
                all_non_normal_bytes_identical=True, native_corner_values_preserved_exactly=True,
                original_geometry_contract=geometry, original_material_contract=material_result,
                unmodified_official_export=False, source_saved=False, world_loaded=False, visual_acceptance=False)


def restore_bytes(blob, source):
    document, raw, material = c.parse_glb_bytes(blob)
    c.validate_material(material, source)
    normals = assigned_normals(raw, source)
    # Independently show this exact source reproduces the unmodified exporter
    # normals before restoring full precision. No rounding tolerance is widened.
    expected_rounded = g.replay_exporter(normals @ c.MAP)
    c.require(np.array_equal(expected_rounded.astype(float), np.asarray(raw['normals'], float)), 'Raw exported normals equal exact actual-corner round/normalize/Y-up replay')
    slots, allowed = normal_byte_slots(blob, document)
    result = bytearray(blob)
    for (begin, end), normal in zip(slots, normals):
        result[begin:end] = struct.pack('<3f', *normal)
    result = bytes(result)
    return result, validate_restored_bytes(blob, result, source)
