"""Strict v3 geometry evidence layered on the unchanged v2/v1 validators.

This validates an observation protocol, not native execution. Digests bind native
products; Python fixtures alone cannot establish that those products were read.
Legacy face_* denotes actual indexed base faces. The runtime rock oracle is the
separate, exactly proved Mesh.get_faces() product, which may extend beyond raw
vertices because the fixed engine snaps it to a float32 0.1 mm grid.
"""
from __future__ import annotations

import copy
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / 'version-guard-v2'), str(HERE.parent)]
import version_schema62 as v2

original = v2.original
require = original.require
union = original.union
contains = original.contains
sha_ok = original.sha_ok
bounds_ok = original.bounds_ok

AUDIT_SHA = '966c863a02d136aefacb78e76d7301649b96c628408c589d3a4345fac30086f7'
GEOMETRY_POLICY = 'strict_existing_shadow_indexed_arrays_plus_actual_get_faces_v3'
FACE_METHOD = 'actual_indexed_base_faces'
COVERAGE_METHOD = 'existing_audit_array_mesh_exact_oriented_multiset_all_base_lods'
SNAP_METHOD = 'exact_float32_Vector3_snapped_base_indexed_faces'
STEP_FLOAT32_HEX = '17b7d138'

# Fixed 4.5.1 static 3D format checked by visible_geometry61.gd. Reject all
# additional flags (2D, skinning, custom attributes, dynamic/unreviewed layouts).
VERTEX, NORMAL, TANGENT = 1 << 0, 1 << 1, 1 << 2
COLOR, UV, UV2, INDEX = 1 << 3, 1 << 4, 1 << 5, 1 << 12
COMPRESSED, CURRENT_VERSION = 1 << 29, 1 << 35
ALLOWED_FORMAT = CURRENT_VERSION | COMPRESSED | VERTEX | NORMAL | TANGENT | COLOR | UV | UV2 | INDEX

SURFACE_KEYS = {'index', 'primitive', 'format', 'index_count', 'vertex_count',
                'vertex_bytes_sha256', 'vertex_bounds', 'api_vertex_missing', 'levels'}
LEVEL_KEYS = {'threshold', 'face_vertex_count', 'face_bytes_sha256',
              'source_faces_hex_text_sha256', 'oriented_faces_sha256', 'bounds'}
MESH_KEYS = {'mesh_resource', 'surface_storage_sha256', 'surfaces', 'vertex_count',
             'vertex_bounds', 'face_method', 'face_vertex_count', 'face_bounds',
             'face_bytes_sha256', 'indexed_visual_bounds', 'shadow_mesh_resource',
             'shadow_surface_storage_sha256', 'combined_vertex_bounds',
             'get_faces_observed', 'get_faces_bounds', 'get_faces_vertex_count',
             'get_faces_bytes_sha256', 'get_faces_snap_proof', 'combined_clearance_bounds'}
ROCK_KEYS = {'prefab', 'imported_scene', 'mesh_node_count', 'first_mesh_node_path',
             'mesh_node_transform_applied_to_proxy', 'mesh_node_transform_variant_hex',
             'imported_node_inventory', 'source_rule'}
PROOF_KEYS = {'passed', 'method', 'helper_sha256', 'shadow_present', 'surfaces'}
LEDGER_KEYS = {'surface', 'source_format', 'source_vertices', 'shadow_vertices',
               'shadow_api_vertex_missing', 'levels'}
LEDGER_LEVEL_KEYS = {'threshold', 'triangles', 'source_faces_hex_text_sha256'}
SNAP_KEYS = {'passed', 'method', 'step_float32_hex', 'predicted_face_bytes_sha256',
             'predicted_bounds'}


def exact_keys(value, keys, label):
    require(type(value) is dict and set(value) == keys, label + ' fields')


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def positive_int(value):
    return type(value) is int and value > 0


def request_v3(base_v2_request):
    """Copy the v2 request and add only the pinned geometry policy and helper."""
    require(type(base_v2_request) is dict, 'v3 base request must be a dictionary')
    require(v2.engine_mismatches(base_v2_request.get('engine_version_info')) == []
            and base_v2_request.get('engine_version_policy') == v2.POLICY
            and 'engine_version' not in base_v2_request, 'v3 requires unchanged v2 request')
    result = copy.deepcopy(base_v2_request)
    result['geometry_policy'] = GEOMETRY_POLICY
    result['shadow_audit_sha256'] = AUDIT_SHA
    return result


def _surface(surface, shadow_only):
    exact_keys(surface, SURFACE_KEYS, 'v3 surface')
    fmt = surface['format']
    require(type(fmt) is int and fmt & CURRENT_VERSION and fmt & VERTEX
            and not fmt & ~ALLOWED_FORMAT, 'unsupported static 3D surface format')
    require(not (fmt & COMPRESSED and fmt & TANGENT and not fmt & NORMAL),
            'unsupported compressed tangent layout')
    require(bool(fmt & INDEX) == (surface['index_count'] > 0), 'index format/count mismatch')
    missing = surface['api_vertex_missing']
    require(type(missing) is bool, 'api_vertex_missing must be boolean')
    require(not missing or (shadow_only and bool(fmt & COMPRESSED) and not fmt & NORMAL),
            'missing API vertices outside narrow compressed no-normal shadow branch')
    levels = surface['levels']
    require(type(levels) is list and len(levels) > 0, 'missing indexed base/LOD levels')
    previous = -1
    for index, level in enumerate(levels):
        exact_keys(level, LEVEL_KEYS, 'indexed level')
        threshold = level['threshold']
        require(number(threshold) and threshold > previous
                and (threshold == 0 if index == 0 else threshold > 0),
                'indexed levels require base zero and strictly increasing finite thresholds')
        previous = threshold
        count = level['face_vertex_count']
        require(positive_int(count) and count % 3 == 0, 'indexed level triangle count')
        require(all(sha_ok(level[key]) for key in
                    ('face_bytes_sha256', 'source_faces_hex_text_sha256', 'oriented_faces_sha256')),
                'invalid indexed level hash')
        require(contains(surface['vertex_bounds'], level['bounds']),
                'indexed level outside actual raw vertex domain')
        if index == 0:
            require(count == (surface['index_count'] or surface['vertex_count']),
                    'base indexed count differs from surface count')
        else:
            require(surface['index_count'] > 0, 'unindexed surface cannot contain LODs')
    return levels


def _snap(item, shadow_only):
    if shadow_only:
        require(item['get_faces_observed'] is False
                and item['get_faces_bounds'] is None
                and type(item['get_faces_vertex_count']) is int and item['get_faces_vertex_count'] == 0
                and item['get_faces_bytes_sha256'] == ''
                and item['get_faces_snap_proof'] is None,
                'shadow must not claim or construct get_faces evidence')
        return
    require(item['get_faces_observed'] is True, 'primary actual get_faces observation missing')
    require(positive_int(item['get_faces_vertex_count'])
            and item['get_faces_vertex_count'] == item['face_vertex_count'],
            'actual get_faces count differs from indexed base')
    require(sha_ok(item['get_faces_bytes_sha256']) and bounds_ok(item['get_faces_bounds']),
            'invalid actual get_faces hash/bounds')
    proof = item['get_faces_snap_proof']
    exact_keys(proof, SNAP_KEYS, 'get_faces snap proof')
    require(proof['passed'] is True and proof['method'] == SNAP_METHOD
            and proof['step_float32_hex'] == STEP_FLOAT32_HEX, 'get_faces snap policy mismatch')
    require(sha_ok(proof['predicted_face_bytes_sha256'])
            and proof['predicted_face_bytes_sha256'] == item['get_faces_bytes_sha256'],
            'actual/predicted get_faces byte hashes differ')
    require(bounds_ok(proof['predicted_bounds']) and proof['predicted_bounds'] == item['get_faces_bounds'],
            'actual/predicted get_faces bounds differ')
    # Deliberately no containment in raw vertices: this is the native snapped
    # product. Exact predicted bytes AND bounds, rather than epsilon, justify it.


def _coverage(item):
    proof = item['shadow_coverage_proof']
    exact_keys(proof, PROOF_KEYS, 'shadow coverage proof')
    shadow = item.get('shadow')
    require(proof['passed'] is True and proof['method'] == COVERAGE_METHOD
            and proof['helper_sha256'] == AUDIT_SHA, 'shadow coverage policy mismatch')
    require(type(proof['shadow_present']) is bool and proof['shadow_present'] == (shadow is not None),
            'shadow presence proof mismatch')
    ledger = proof['surfaces']
    surfaces = item['surfaces']
    require(type(ledger) is list and len(ledger) == len(surfaces), 'coverage surface ledger incomplete')
    if shadow is not None:
        require(len(shadow['surfaces']) == len(surfaces), 'shadow/source surface count mismatch')
    for index, (row, source) in enumerate(zip(ledger, surfaces)):
        exact_keys(row, LEDGER_KEYS, 'coverage surface ledger')
        require(type(row['surface']) is int and row['surface'] == index
                and type(row['source_format']) is int and row['source_format'] == source['format']
                and type(row['source_vertices']) is int and row['source_vertices'] == source['vertex_count'],
                'coverage source surface identity mismatch')
        partner = shadow['surfaces'][index] if shadow is not None else None
        require(type(row['shadow_vertices']) is int
                and row['shadow_vertices'] == (partner['vertex_count'] if partner else 0)
                and type(row['shadow_api_vertex_missing']) is bool
                and row['shadow_api_vertex_missing'] == (partner['api_vertex_missing'] if partner else False),
                'coverage shadow surface identity mismatch')
        levels = row['levels']
        require(type(levels) is list and len(levels) == len(source['levels']), 'coverage level ledger incomplete')
        if partner is not None:
            require(len(partner['levels']) == len(source['levels']), 'shadow/source LOD count mismatch')
        for level_index, (entry, level) in enumerate(zip(levels, source['levels'])):
            exact_keys(entry, LEDGER_LEVEL_KEYS, 'coverage level ledger')
            # The unchanged helper uses GDScript division; JSON can encode an
            # integral triangle count as a float. Reject booleans/fractions.
            require(number(entry['threshold']) and entry['threshold'] == level['threshold']
                    and number(entry['triangles']) and entry['triangles'] > 0
                    and entry['triangles'] * 3 == level['face_vertex_count'],
                    'coverage level threshold/triangle count mismatch')
            require(sha_ok(entry['source_faces_hex_text_sha256'])
                    and entry['source_faces_hex_text_sha256'] == level['source_faces_hex_text_sha256'],
                    'coverage source face witness mismatch')
            if partner is not None:
                other = partner['levels'][level_index]
                require(other['threshold'] == level['threshold']
                        and other['face_vertex_count'] == level['face_vertex_count']
                        and other['oriented_faces_sha256'] == level['oriented_faces_sha256']
                        and other['bounds'] == level['bounds'],
                        'shadow/source exact oriented multiset coverage mismatch')
                # Byte order may differ after vertex fusion or triangle reorder.
                # Oriented multiset digests preserve winding and multiplicity.


def _mesh(item, shadow_only=False, rock=False):
    keys = MESH_KEYS | (ROCK_KEYS if rock else set())
    if not shadow_only:
        keys |= {'geometry_policy', 'shadow_coverage_proof'}
        if item['shadow_mesh_resource']:
            keys |= {'shadow'}
    exact_keys(item, keys, 'v3 mesh')
    require(item['face_method'] == FACE_METHOD, 'legacy face fields must denote actual indexed base faces')
    if not shadow_only:
        require(item['geometry_policy'] == GEOMETRY_POLICY, 'mesh geometry policy mismatch')
    levels = [_surface(surface, shadow_only) for surface in item['surfaces']]
    require(item['face_bounds'] == union(*(rows[0]['bounds'] for rows in levels)),
            'indexed base face bounds union mismatch')
    require(bounds_ok(item['indexed_visual_bounds'])
            and item['indexed_visual_bounds'] == union(*(level['bounds'] for rows in levels for level in rows)),
            'indexed visual base/LOD bounds union mismatch')
    if len(levels) == 1:
        require(item['face_bytes_sha256'] == levels[0][0]['face_bytes_sha256'],
                'single-surface indexed base byte hash mismatch')
    _snap(item, shadow_only)
    boxes = [item['vertex_bounds'], item['indexed_visual_bounds']]
    if not shadow_only:
        boxes.append(item['get_faces_bounds'])
        if 'shadow' in item:
            _mesh(item['shadow'], shadow_only=True)
            boxes.append(item['shadow']['combined_clearance_bounds'])
        _coverage(item)
    require(bounds_ok(item['combined_clearance_bounds'])
            and item['combined_clearance_bounds'] == union(*boxes),
            'combined clearance must be the exact actual geometry union')


def validate_mesh(item, expected_surfaces=None, allow_shadow=True, *, shadow_only=False, rock=False):
    """Retain every legacy check before validating the additional v3 evidence."""
    original.validate_mesh(item, expected_surfaces, allow_shadow)
    _mesh(item, shadow_only=shadow_only, rock=rock)


def validate_native(value, request):
    # Do not replace or weaken the old engine, source, face-containment or rock
    # binding checks. Legacy face_* explicitly retains its raw indexed meaning.
    v2.validate_native(value, request)
    require(request.get('geometry_policy') == GEOMETRY_POLICY
            and request.get('shadow_audit_sha256') == AUDIT_SHA, 'v3 requested geometry policy changed')
    for item in value['visual_meshes']:
        _mesh(item)
    _mesh(value['rock'], rock=True)
    return value['rock']['get_faces_bounds']
