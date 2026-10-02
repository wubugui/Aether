"""Checks only the preserved K imported cache and its exact native roundtrip."""
from pathlib import Path
import math
import sys
import numpy as np
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'transfer-v2'))
import transfer58k as transfer
c = transfer.c
VERSION = 'cloud58k-cache-readback-v3'
DIAG_DIR = c.ROOT / 'cloud-evidence/cloudbank58k-import-channel-diagnosis-20261002'
DECODER_PATH = DIAG_DIR / 'decode_imported_channels.py'
CACHE = transfer.READBACK.parent / 'cloudbank58k-transfer-v2-20261002T094351Z-egb4wx8d/imported-cache/cloud58k-native-import.scn'
CACHE_SHA = '1b94f241fba9cc48a7879ec71dee4ecff3854955be37f344158494997d3c3e42'
Q = 65535.0
U = 2.0 ** -24
TANGENT_UNIT_EPS = 64 * U


def oct_error(a, b):
    return 2 * math.sqrt(3) * math.sqrt(a*a + b*b + (a+b)*(a+b))


TANGENT_DOT_EPS = oct_error(1/Q + 8*U, 1/Q + 8*U) + oct_error(1/Q + 8*U, 1/32767.0 + 17*U) + 72*U + 1024*U*U


def reference():
    c.require(c.sha(CACHE) == CACHE_SHA and CACHE.stat().st_size == 11096, 'Exact preserved successful import cache')
    decoder = c.load(DECODER_PATH)
    doc, body, vertices, packed, indices = decoder.decode_cache(CACHE)
    source = transfer.evidence_source()
    stored = doc['resources'][1]['properties']['_surfaces'][0]
    lower = vertices.min(axis=0); upper = vertices.max(axis=0)
    size = (upper-lower).astype(np.float32); end = (lower+size).astype(np.float32)
    c.require(np.array_equal(np.asarray(stored['aabb']['values'], np.float32), np.concatenate([lower, size])), 'Cached AABB position/size exactly float32 vertex extrema construction')
    expected = dict(format=stored['format'], primitive=stored['primitive'], vertex_count=stored['vertex_count'], index_count=stored['index_count'],
                    vertex_data_bytes=stored['vertex_data']['payload_bytes'], index_data_bytes=stored['index_data']['payload_bytes'],
                    vertex_data_sha256=stored['vertex_data']['payload_sha256'], index_data_sha256=stored['index_data']['payload_sha256'],
                    aabb_position=lower.astype(float).tolist(), aabb_size=size.astype(float).tolist(), aabb_end=end.astype(float).tolist())
    return source, expected, decoder, (vertices, packed, indices)


def tangent_checks(normals, tangents):
    n = np.asarray(normals, float); flat = np.asarray(tangents, float)
    c.require(n.shape == (1152, 3) and flat.shape == (4608,) and np.isfinite(n).all() and np.isfinite(flat).all(), 'Complete finite actual tangent/normal values')
    t = flat.reshape(-1, 4)
    c.require(np.all(t[:, 3] == 1), 'Fixed-cache positive handedness exactly')
    nl = np.linalg.norm(n, axis=1); tl = np.linalg.norm(t[:, :3], axis=1)
    unit_error = float(np.max(np.abs(tl-1)))
    c.require(float(nl.min()) > 0 and float(tl.min()) > 0 and unit_error <= TANGENT_UNIT_EPS, 'Tangent unit-vector float32 arithmetic bound')
    normalized_dot = np.abs(np.sum((n/nl[:, None]) * (t[:, :3]/tl[:, None]), axis=1))
    error = float(normalized_dot.max())
    c.require(error <= TANGENT_DOT_EPS, 'Signed-oct16-derived tangent perpendicularity bound')
    return dict(passed=True, count=1152, components=4608, handedness=1, maximum_unit_error=unit_error,
                maximum_normalized_absolute_dot=error, unit_bound=TANGENT_UNIT_EPS, orthogonality_bound=TANGENT_DOT_EPS,
                bound_source='signed-oct16 positive-handedness quantization and explicit float32 operation budget; not fitted to observations',
                prequantization_exact_orthogonality_proven=False)


def validate(report, source, expected, mode, pid):
    c.require(report['version'] == VERSION and report['passed'] is True and report['mode'] == mode and report['pid'] == pid, 'Actual successful native result/PID/mode')
    c.require(report['world_loaded'] is False and report['images'] == 0, 'No world or images')
    c.require([report['engine'][key] for key in ('major', 'minor', 'patch')] == [4, 5, 1], 'Pinned native Godot')
    c.require(report['format'] == expected['format'] and report['stored_surface'] == expected, 'Original exact native surface storage identity')
    rows = report['channels']; c.require(len(rows) == 13 and [row['channel'] for row in rows] == list(range(13)), 'Complete actual native channel inventory')
    counts = {0: ('PackedVector3Array', 1152), 1: ('PackedVector3Array', 1152), 2: ('PackedFloat32Array', 4608), 12: ('PackedInt32Array', 1152)}
    c.require(all((row['type'], row['count']) == counts[row['channel']] if row['channel'] in counts else row['count'] == 0 for row in rows), 'Exact V/N/T/I types/counts; no other channel')
    geometry = c.validate_geometry(report['geometry'], source, clockwise=True)
    material = c.validate_material(report['material'], source, godot=True)
    tangent = tangent_checks(report['geometry']['normals'], report['tangents'])
    tangent_rows = np.asarray(report['tangents']).reshape(-1, 4)
    triangles = np.asarray(report['geometry']['indices']).reshape(-1, 3)
    c.require(np.array_equal(tangent_rows[triangles], np.repeat(tangent_rows[triangles[:, 0]][:, None], 3, axis=1)), 'Fixed-cache same-face tangents remain exactly equal')
    expected_box = dict(position=expected['aabb_position'], size=expected['aabb_size'], end=expected['aabb_end'])
    c.require(report['aabb_storage'] == expected_box and report['aabb'] == [expected['aabb_position'], expected['aabb_end']], 'Exact native AABB float32 position/size/end arithmetic')
    c.require(np.array_equal(np.asarray(report['geometry']['positions'], np.float32).min(axis=0), expected['aabb_position']), 'Actual vertex minimum equals native AABB position')
    verts = np.asarray(report['geometry']['positions'], np.float32)
    c.require(np.array_equal(verts.max(axis=0)-verts.min(axis=0), expected['aabb_size']), 'Actual vertex extrema yield exact native float32 AABB size')
    for row in report['transforms']:
        c.require(row['origin'] == [0, 0, 0] and row['basis'] == [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 'Original identity node transforms')
    c.require(not report['dependencies'], 'Native snapshot has no external dependency')
    return dict(geometry=geometry, material=material, tangents=tangent, exact_original_surface_storage=True,
                exact_float32_aabb_storage=True, vertex_tolerance_unchanged=c.POSITION_EPS,
                aabb_endpoint_epsilon_added=False)
