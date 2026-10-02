"""Offline diagnosis of preserved native arrays. No native process or GLB writes."""
from pathlib import Path
from copy import deepcopy
import json
import sys
import numpy as np
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'source-assets/cloud-bank58/revision-k/normal-readback-v1'))
import guard58k as g
c = g.c
RUN = ROOT / 'cloud-evidence/cloudbank58k-normal-readback-v1-20261002T091816Z-whfkeukw'
RAW = RUN / 'outputs/source-normal-arrays.json'
RAW_SHA = '35cde26e14f8767c015295cff3b8f271a85052a111d8fd68e066784a18e1b1c7'


def inspect_arrays(d, verified):
    checks = dict(
        source_sha=d['source_sha256_before'] == d['source_sha256_after'] == c.SOURCE_SHA,
        full_identity=d['identity_before'] == d['identity_after'] == verified['native_identity'],
        camera_identity=d['cameras_before'] == d['cameras_after'] == g.camera_expectations(verified),
        scene_identity=d['scene_state_before'] == d['scene_state_after'],
        dependencies=d['dependencies_before'] == d['dependencies_after'] and d['dependencies_before']['strict_saved_source_dependencies_passed'] is True,
        source_flat_flags=d['identity_before']['checks']['flat_faces'] is True,
        version=d['version'] == g.VERSION and d['blender_version'] == [4, 5, 14] and d['state'] == 'captured',
        scope=all(d[key] is False for key in ['source_saved', 'export_performed', 'godot_started', 'world_loaded', 'visual_acceptance']) and d['images'] == 0)
    v = np.asarray(d['positions']); f = np.asarray(d['triangles']); p = np.asarray(d['polygon_normals']); n = np.asarray(d['corner_normals'])
    c.require(v.shape == (194, 3) and f.shape == (384, 3) and p.shape == (384, 3) and n.shape == (1152, 3), 'Native array dimensions')
    c.require(np.isfinite(v).all() and np.isfinite(p).all() and np.isfinite(n).all(), 'Finite native arrays')
    checks['geometry_fingerprint'] = c.geometry_fingerprint(v, f) == verified['native_identity']['mesh']
    checks['exact_float32_normals'] = np.array_equal(p, p.astype(np.float32).astype(float)) and np.array_equal(n, n.astype(np.float32).astype(float))
    loops = d['polygon_loop_indices']; owners = d['loop_polygon_indices']; vertices = d['loop_vertex_indices']
    c.require(len(loops) == 384 and len(owners) == len(vertices) == 1152, 'Complete mapping lengths')
    c.require(all(len(row) == 3 for row in loops) and all(type(i) is int for row in loops for i in row), 'Integer triangle loops')
    c.require(sorted(i for row in loops for i in row) == list(range(1152)), 'Exact loop bijection')
    checks['all_loop_owners_and_vertices'] = all([owners[i] for i in row] == [face] * 3 and [vertices[i] for i in row] == f[face].tolist() for face, row in enumerate(loops))
    cn = n[loops]
    math_normals = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    math_normals /= np.linalg.norm(math_normals, axis=1, keepdims=True)
    per_face_flat = np.max(np.abs(cn - cn[:, 0, None]), axis=(1, 2))
    p_geometry_error = np.max(np.abs(p - math_normals), axis=1)
    c_geometry_error = np.max(np.abs(cn - math_normals[:, None]), axis=(1, 2))
    p_unit = float(np.max(np.abs(np.linalg.norm(p, axis=1) - 1)))
    c_unit = float(np.max(np.abs(np.linalg.norm(n, axis=1) - 1)))
    checks['all_actual_corners_flat_bit_equal'] = bool(np.all(per_face_flat == 0))
    checks['original_3e5_polygon_unit_and_outward_gate'] = p_unit <= c.NORMAL_EPS and float(p_geometry_error.max()) <= c.NORMAL_EPS
    checks['original_3e5_corner_unit_and_outward_gate'] = c_unit <= c.NORMAL_EPS and float(c_geometry_error.max()) <= c.NORMAL_EPS
    c.require(all(checks.values()), 'Independent native array checks: ' + repr({k: value for k, value in checks.items() if not value}))
    return checks, v, f, p, n, cn, math_normals, p_geometry_error, c_geometry_error, p_unit, c_unit


def main():
    c.require(RAW.stat().st_size == 281016 and c.sha(RAW) == RAW_SHA, 'Native raw identity')
    d = c.read(RAW); terminal = c.read(RUN / 'outputs/native-result.json'); process = c.read(RUN / 'blender-normal-readback.process.json'); wrapper = c.read(RUN / 'wrapper-report.json')
    c.require(terminal['raw_sha256'] == RAW_SHA and d['pid'] == terminal['pid'] == process['pid'] == wrapper['stages'][0]['pid'], 'Preserved raw/native/wait4 PID and SHA binding')
    c.require(process['native_exit_observed'] is True and process['returncode'] == 1 and not process['timeout_triggered'] and not process['rss_limit_triggered'], 'Original observed failure without timeout/RSS')
    c.require(wrapper['passed'] is False and terminal['passed'] is False, 'Original failures remain failures')
    c.require(all(wrapper[key] is True for key in ['inputs_unchanged', 'main_project_unchanged', 'source_unchanged']), 'Original finalization protections passed')
    verified = c.source_preconditions()
    try:
        g.validate_readback(d, process['pid'], verified)
        raise RuntimeError('Old validator unexpectedly passed')
    except ValueError as error:
        original_error = str(error)
        c.require(original_error == 'Actual flat corner normals equal polygon normal exactly', 'Same preserved validation failure')
    checks, v, f, p, n, cn, math_normals, pe, ce, pu, cu = inspect_arrays(d, verified)
    c.require(c.sha(g.FAILED_GLB) == g.FAILED_GLB_SHA, 'Original GLB identity')
    _, raw, material = c.parse_glb(g.FAILED_GLB)
    rv = np.asarray(raw['positions']); rn = np.asarray(raw['normals']); ix = np.asarray(raw['indices']).reshape(-1, 3)
    distance = np.max(np.abs(rv[:, None] - c.mapped(v)), axis=2); mapping = distance.argmin(axis=1); actual = mapping[ix]
    c.require(float(distance[np.arange(len(rv)), mapping].max()) == 0, 'Original GLB exact native source positions')
    by_face = {c.canonical(face): j for j, face in enumerate(f)}
    c.require(sorted(map(c.canonical, actual)) == sorted(by_face), 'Original GLB exact oriented triangle bijection')
    rounded = g.replay_exporter(cn[:, 0]); replay_errors = []
    preserved_corner_normals = np.empty_like(rn); assigned = np.zeros(len(rn), bool)
    for face, idx in zip(actual, ix):
        source_face = by_face[c.canonical(face)]
        replay_errors.append(float(np.max(np.abs(rn[idx] - rounded[source_face]))))
        mapped_normal = c.mapped(cn[source_face, 0])
        for vertex in idx:
            c.require(not assigned[vertex] or np.array_equal(preserved_corner_normals[vertex], mapped_normal), 'Unambiguous source-corner normal ownership')
            assigned[vertex] = True; preserved_corner_normals[vertex] = mapped_normal
    c.require(all(assigned) and max(replay_errors) == 0, 'Every actual source corner reproduces original GLB normals')
    source = dict(positions=d['positions'], triangles=d['triangles'])
    memory_geometry = deepcopy(raw); memory_geometry['normals'] = preserved_corner_normals.tolist()
    original_contract = c.validate_geometry(memory_geometry, source)
    difference = np.max(np.abs(cn - p[:, None]), axis=(1, 2))
    newell_error = np.max(np.abs(g.replay_newell(v, f).astype(float) - cn[:, 0]), axis=1)
    rows = [dict(face=face, vertices=f[face].tolist(), polygon=p[face].tolist(), corner=cn[face, 0].tolist(),
                 corner_minus_polygon=(cn[face, 0] - p[face]).tolist(), max_corner_polygon_difference=float(difference[face]),
                 all_three_corners_bit_equal=bool(np.array_equal(cn[face], np.repeat(cn[face, 0][None], 3, axis=0))),
                 polygon_geometry_error=float(pe[face]), corner_geometry_error=float(ce[face])) for face in range(384)]
    result = dict(version='cloud58k-native-normal-diagnosis-20261002', diagnosis_passed=True,
                  native_collection_data_preserved=True, original_native_validation_passed=False, original_wrapper_passed=False,
                  original_failure=original_error, source_sha256=c.SOURCE_SHA, raw_sha256=RAW_SHA, raw_bytes=RAW.stat().st_size,
                  native_pid=d['pid'], native_exit=process['returncode'], native_seconds=process['wall_seconds'], wrapper_seconds=wrapper['elapsed_seconds'],
                  checks=checks, polygon_count=384, corner_count=1152, differing_polygon_corner_faces=int((difference != 0).sum()),
                  maximum_polygon_corner_difference=float(difference.max()), maximum_difference_face=rows[int(difference.argmax())],
                  all_triangles_corner_normals_exactly_flat=True, polygon_geometric_max=float(pe.max()), corner_geometric_max=float(ce.max()),
                  polygon_unit_max=pu, corner_unit_max=cu, original_normal_epsilon=c.NORMAL_EPS,
                  actual_corner_exporter_replay_exact_faces=sum(x == 0 for x in replay_errors), actual_corner_exporter_replay_max=max(replay_errors),
                  mathematical_newell_vs_native_corner_exact_faces=int((newell_error == 0).sum()), mathematical_newell_vs_native_corner_max=float(newell_error.max()),
                  memory_only_actual_corner_substitution_original_contract=original_contract, modified_glb_created=False,
                  transfer_passed=False, native_processes_started_for_diagnosis=0, images=0, world_loaded=False,
                  source_custom_normal_attribute_presence_not_collected=True,
                  references=['https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/makesrna/intern/rna_mesh.cc',
                              'https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/blenkernel/intern/mesh_normals.cc'], per_face=rows)
    c.write(HERE / 'diagnosis.json', result)
    print(json.dumps({k: value for k, value in result.items() if k not in ['per_face']}, indent=2))


if __name__ == '__main__':
    main()
