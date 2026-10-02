"""Pure readback checks; imports never launch native processes or write files."""
from pathlib import Path
import sys
import numpy as np
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'import-v1'))
import contract58k as c

VERSION = 'cloud58k-normal-readback-v1'
FAILED_GLB = c.ROOT / 'cloud-evidence/cloudbank58k-import-v1-20261002T085359Z-6_g0g1ax/export/cloud58k.glb'
FAILED_GLB_SHA = '48a0aa816dc5dd247958fb883d4114b8d07e7fdf2d458af6a408e0af4c22dd60'
CAMERA_KEYS = ('name', 'matrix_world', 'projection', 'resolution_xy', 'pixel_aspect_xy')


def camera_expectations(verified):
    return [{key: row[key] for key in CAMERA_KEYS} for row in verified['cameras']]


def reconstructed_source(verified=None):
    verified = c.source_preconditions() if verified is None else verified
    poly = c.load(c.K / 'poly58k.py')
    proof = c.strict_json_text(verified['native_identity']['construction_proof'])
    frame = c.strict_json_text(verified['native_identity']['source_frame'])
    candidate = poly.build(proof['effective_control_config'])
    vertices = (candidate['vertices'] @ poly.source_basis(frame).T).astype(np.float32).astype(float)
    c.require(c.geometry_fingerprint(vertices, candidate['faces']) == verified['native_identity']['mesh'], 'Exact accepted saved geometry reconstruction')
    return vertices, np.asarray(candidate['faces'], int)


def replay_newell(vertices, faces, previous_first=True):
    """Numerical prediction only, never a substitute for actual native normals."""
    v = np.asarray(vertices, np.float32)[faces]
    normal = np.zeros((len(faces), 3), np.float32)
    for step in range(3):
        a, b = (v[:, step - 1], v[:, step]) if previous_first else (v[:, step], v[:, (step + 1) % 3])
        normal[:, 0] += (a[:, 1] - b[:, 1]) * (a[:, 2] + b[:, 2])
        normal[:, 1] += (a[:, 2] - b[:, 2]) * (a[:, 0] + b[:, 0])
        normal[:, 2] += (a[:, 0] - b[:, 0]) * (a[:, 1] + b[:, 1])
    normal /= np.linalg.norm(normal, axis=1, keepdims=True)
    return normal


def replay_exporter(normals):
    normal = np.round(np.asarray(normals, np.float32), 4)
    np.divide(normal, np.linalg.norm(normal, axis=1, keepdims=True), out=normal)
    normal[:, [1, 2]] = normal[:, [2, 1]]
    normal[:, 2] *= -1
    return normal


def validate_readback(data, pid, verified):
    c.require(data['version'] == VERSION and data['state'] == 'captured' and type(data['pid']) is int and data['pid'] == pid and type(pid) is int and pid > 0, 'Native readback identity/PID')
    c.require(data['blender_version'] == [4, 5, 14], 'Pinned Blender version')
    c.require(len(data['cpu_affinity']) == 2 and all(type(x) is int and x >= 0 for x in data['cpu_affinity']) and data['cpu_affinity'] == sorted(set(data['cpu_affinity'])), 'Native CPU2 affinity')
    for key in ('source_saved', 'export_performed', 'godot_started', 'world_loaded', 'visual_acceptance'):
        c.require(data[key] is False, 'Read-only scope: ' + key)
    c.require(type(data['images']) is int and data['images'] == 0, 'No image output')
    c.require(data['source_sha256_before'] == data['source_sha256_after'] == c.SOURCE_SHA, 'Source bytes unchanged')
    c.require(data['identity_before'] == data['identity_after'] == verified['native_identity'] and data['identity_before']['passed'] is True, 'Complete native identity before/after')
    c.require(data['cameras_before'] == data['cameras_after'] == camera_expectations(verified), 'Original camera matrix/projection identity before/after')
    c.require(data['scene_state_before'] == data['scene_state_after'] and set(data['scene_state_before']) == {'active_camera', 'resolution_x', 'resolution_y', 'resolution_percentage', 'pixel_aspect_x', 'pixel_aspect_y'}, 'Original active camera and render settings unchanged')
    c.require(data['dependencies_before'] == data['dependencies_after'] and data['dependencies_before']['strict_saved_source_dependencies_passed'] is True, 'No native dependency changes')
    v = np.asarray(data['positions'], float); f = np.asarray(data['triangles'])
    c.require(v.shape == (194, 3) and f.shape == (384, 3) and f.dtype.kind in 'iu' and np.isfinite(v).all(), 'Exact source array dimensions/types')
    c.require(c.geometry_fingerprint(v, f) == verified['native_identity']['mesh'], 'Exact source geometry fingerprint')
    p = np.asarray(data['polygon_normals'], float); n = np.asarray(data['corner_normals'], float)
    c.require(p.shape == (384, 3) and n.shape == (1152, 3) and np.isfinite(p).all() and np.isfinite(n).all(), 'Finite polygon/corner normals')
    c.require(np.array_equal(p, p.astype(np.float32).astype(float)) and np.array_equal(n, n.astype(np.float32).astype(float)), 'Actual normals are exact float32')
    loops = data['polygon_loop_indices']; vertex = data['loop_vertex_indices']; owners = data['loop_polygon_indices']
    c.require(len(loops) == 384 and len(vertex) == len(owners) == 1152, 'Complete loop mapping dimensions')
    c.require(all(type(x) is int for row in loops for x in row) and all(type(x) is int for x in vertex + owners), 'Integer loop mapping')
    c.require(all(len(row) == 3 for row in loops) and sorted(x for row in loops for x in row) == list(range(1152)), 'Loop mapping exact bijection')
    for face, row in enumerate(loops):
        c.require([owners[x] for x in row] == [face] * 3 and [vertex[x] for x in row] == f[face].tolist(), 'Loop owner and vertex mapping')
        c.require(np.array_equal(n[row], np.repeat(p[face][None, :], 3, axis=0)), 'Actual flat corner normals equal polygon normal exactly')
    unit = float(np.max(np.abs(np.linalg.norm(p, axis=1) - 1)))
    exact = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    exact /= np.linalg.norm(exact, axis=1, keepdims=True)
    error = float(np.max(np.abs(p - exact)))
    c.require(unit <= c.NORMAL_EPS and error <= c.NORMAL_EPS, 'Original unit/outward 3e-5 source-normal gate')
    c.require(c.sha(FAILED_GLB) == FAILED_GLB_SHA, 'Original failed GLB unchanged')
    _, raw, _ = c.parse_glb(FAILED_GLB)
    rv = np.asarray(raw['positions']); rn = np.asarray(raw['normals']); ix = np.asarray(raw['indices']).reshape(-1, 3)
    expected = c.mapped(v); distance = np.max(np.abs(rv[:, None] - expected), axis=2)
    mapping = distance.argmin(axis=1)
    c.require(float(distance[np.arange(len(rv)), mapping].max()) == 0, 'Failed GLB exact source positions')
    by_face = {c.canonical(face): j for j, face in enumerate(f)}
    actual = mapping[ix]
    c.require(sorted(map(c.canonical, actual)) == sorted(by_face), 'Failed GLB exact triangle bijection')
    rounded = replay_exporter(p)
    replay_error = max(float(np.max(np.abs(rn[idx] - rounded[by_face[c.canonical(face)]]))) for face, idx in zip(actual, ix))
    c.require(replay_error == 0, 'Actual source normals reproduce every failed GLB normal exactly')
    return dict(passed=True, polygon_count=384, corner_count=1152, maximum_source_unit_error=unit,
                maximum_source_normal_component_error=error, failed_glb_replay_max_error=replay_error,
                actual_native_normals=True, source_geometry_unchanged=True, transfer_success=False)
