#!/usr/bin/env python3
"""Pure protocol/source tests, including all 29 v1/v2 tests. No native proof.

Run this suite with Python and Python -O. No asserts implement validation; no
engine, process launcher, download, resource edits or fixture writes occur here.
"""
import copy
import hashlib
import inspect
import math
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / 'version-guard-v2'), str(HERE.parent)]
import schema_shadow62 as s
import test_version_guard62 as previous

OriginalMath = previous.OriginalMath
OriginalProtocol = previous.OriginalProtocol
OriginalVersionGuard = previous.VersionGuard


def hash_text(value):
    return hashlib.sha256(value.encode()).hexdigest()


class ShadowProtocol(unittest.TestCase):
    def setUp(self):
        prior = previous.OriginalProtocol()
        prior.setUp()
        self.request = s.request_v3(s.v2.request_v2(prior.req))
        self.native = prior.fixture
        self.native.update(previous.VersionGuard().observation())
        # Synthetic, internally consistent protocol evidence. Its arbitrary
        # hashes are deliberately not represented as observed native geometry.
        self.raw = {'min': [-0.9999600052833557, 0., -0.9999600052833557],
                    'max': [0.9999600052833557, 2., 0.9999600052833557]}
        self.snapped = {'min': [-1., 0., -1.], 'max': [1., 2., 1.]}
        for item in self.native['visual_meshes'] + [self.native['rock']]:
            self.augment(item)
        self.native['rock']['source_rule'] = 'open_world.gd first_mesh(scene).mesh, mesh_body(mesh).get_faces(), then full saved body transform'

    def augment(self, item, shadow=False):
        for key in ['vertex_bounds', 'combined_vertex_bounds', 'face_bounds', 'indexed_visual_bounds']:
            item[key] = copy.deepcopy(self.raw)
        item['face_method'] = s.FACE_METHOD
        for surface in item['surfaces']:
            surface['vertex_bounds'] = copy.deepcopy(self.raw)
            surface['api_vertex_missing'] = shadow
            surface['levels'] = []
            for index, threshold in enumerate([0., 1.25, 5.]):
                surface['levels'].append({
                    'threshold': threshold,
                    'face_vertex_count': (surface['index_count'] or surface['vertex_count']) if index == 0 else 3 * index,
                    'face_bytes_sha256': hash_text(f'bytes-{shadow}-{surface["index"]}-{index}'),
                    'source_faces_hex_text_sha256': hash_text(f'hex-{shadow}-{surface["index"]}-{index}'),
                    'oriented_faces_sha256': hash_text(f'oriented-{surface["index"]}-{index}'),
                    'bounds': copy.deepcopy(self.raw),
                })
        item['face_bytes_sha256'] = item['surfaces'][0]['levels'][0]['face_bytes_sha256']
        item.update(get_faces_observed=False, get_faces_bounds=None, get_faces_vertex_count=0,
                    get_faces_bytes_sha256='', get_faces_snap_proof=None,
                    combined_clearance_bounds=copy.deepcopy(self.raw))
        if shadow:
            return
        if 'shadow' in item:
            self.augment(item['shadow'], True)
        item.update(geometry_policy=s.GEOMETRY_POLICY, get_faces_observed=True,
                    get_faces_bounds=copy.deepcopy(self.snapped), get_faces_vertex_count=item['face_vertex_count'],
                    get_faces_bytes_sha256=hash_text('actual snapped bytes'),
                    combined_clearance_bounds=s.union(self.raw, self.snapped))
        item['get_faces_snap_proof'] = {
            'passed': True, 'method': s.SNAP_METHOD, 'step_float32_hex': s.STEP_FLOAT32_HEX,
            'predicted_face_bytes_sha256': item['get_faces_bytes_sha256'],
            'predicted_bounds': copy.deepcopy(self.snapped),
        }
        self.rebuild_ledger(item)

    def rebuild_ledger(self, item):
        rows = []
        for index, surface in enumerate(item['surfaces']):
            partner = item['shadow']['surfaces'][index] if 'shadow' in item else None
            rows.append({
                'surface': index, 'source_format': surface['format'],
                'source_vertices': surface['vertex_count'],
                'shadow_vertices': partner['vertex_count'] if partner else 0,
                'shadow_api_vertex_missing': partner['api_vertex_missing'] if partner else False,
                'levels': [{'threshold': level['threshold'], 'triangles': level['face_vertex_count'] / 3,
                            'source_faces_hex_text_sha256': level['source_faces_hex_text_sha256']}
                           for level in surface['levels']],
            })
        item['shadow_coverage_proof'] = {'passed': True, 'method': s.COVERAGE_METHOD,
                                        'helper_sha256': s.AUDIT_SHA, 'shadow_present': 'shadow' in item,
                                        'surfaces': rows}

    def rejected(self, edit, request_edit=None):
        native, request = copy.deepcopy(self.native), copy.deepcopy(self.request)
        edit(native)
        if request_edit:
            request_edit(request)
        with self.assertRaises((ValueError, KeyError, TypeError)):
            s.validate_native(native, request)

    def mesh_mutation(self, path, value, *, shadow=False, rock=False):
        def edit(native):
            item = native['rock'] if rock else native['visual_meshes'][0]
            if shadow:
                item = item['shadow']
            for key in path[:-1]:
                item = item[key]
            item[path[-1]] = value
        self.rejected(edit)

    def test_positive_synthetic_fixture_is_not_native_proof(self):
        self.assertEqual(s.validate_native(self.native, self.request), self.snapped)
        self.assertNotEqual(self.native['rock']['face_bounds'], self.snapped)
        self.assertFalse(s.contains(self.raw, self.snapped))
        self.assertEqual(s.validate_native(self.native, self.request), self.native['rock']['get_faces_bounds'])

    def test_all_29_previous_test_groups_reused(self):
        loader = unittest.TestLoader()
        self.assertEqual(sum(loader.loadTestsFromTestCase(case).countTestCases()
                             for case in [OriginalMath, OriginalProtocol, OriginalVersionGuard]), 29)

    def test_request_exact_derivative_and_no_input_mutation(self):
        prior = previous.OriginalProtocol(); prior.setUp()
        base = s.v2.request_v2(prior.req)
        saved = copy.deepcopy(base)
        request = s.request_v3(base)
        self.assertEqual(base, saved)
        self.assertEqual(set(request) - set(base), {'geometry_policy', 'shadow_audit_sha256'})
        for key in base:
            self.assertEqual(request[key], base[key])
        request['visual_meshes'][0]['primary_surfaces'][0]['vertex_count'] += 1
        self.assertEqual(base, saved)
        for key, value in [('geometry_policy', 'loose'), ('shadow_audit_sha256', '0' * 64)]:
            self.rejected(lambda _: None, lambda request, k=key, v=value: request.__setitem__(k, v))
            self.rejected(lambda _: None, lambda request, k=key: request.pop(k))
        for bad in [None, [], prior.req]:
            with self.assertRaises(ValueError):
                s.request_v3(bad)

    def test_unchanged_v2_validator_runs_first(self):
        sentinel = ValueError('old guard reached first')
        with mock.patch.object(s.v2, 'validate_native', side_effect=sentinel) as old:
            with self.assertRaisesRegex(ValueError, 'old guard reached first'):
                s.validate_native({}, {})
            old.assert_called_once_with({}, {})
        with mock.patch.object(s.original, 'validate_mesh', side_effect=sentinel) as old:
            with self.assertRaisesRegex(ValueError, 'old guard reached first'):
                s.validate_mesh({})
            old.assert_called_once_with({}, None, True)

    def test_old_source_version_and_storage_guards_retained(self):
        for key, value in [('major', 5), ('major', 4.), ('hash', 'f62fdbde')]:
            def edit(native, key=key, value=value):
                native['engine_version_info'][key] = value
                native['engine_version_guard'] = s.v2.engine_guard(native['engine_version_info'])
            self.rejected(edit)
        for key in ['surface_storage_sha256', 'shadow_surface_storage_sha256', 'mesh_resource', 'shadow_mesh_resource']:
            self.mesh_mutation([key], '0' * 64)
        for key in ['format', 'vertex_count', 'index_count']:
            self.mesh_mutation(['surfaces', 0, key], self.native['visual_meshes'][0]['surfaces'][0][key] + 1)
        self.mesh_mutation(['surfaces', 0, 'vertex_count'], 1, shadow=True)
        self.mesh_mutation(['mesh_resource'], 'res://assets/meshes/rock.res', rock=True)

    def test_every_new_mesh_field_is_required(self):
        fields = ['face_method', 'indexed_visual_bounds', 'geometry_policy', 'shadow_coverage_proof',
                  'get_faces_observed', 'get_faces_bounds', 'get_faces_vertex_count',
                  'get_faces_bytes_sha256', 'get_faces_snap_proof', 'combined_clearance_bounds']
        for key in fields:
            with self.subTest(key=key):
                self.rejected(lambda native, k=key: native['visual_meshes'][0].pop(k))
        for key in set(fields) - {'geometry_policy', 'shadow_coverage_proof'}:
            self.rejected(lambda native, k=key: native['visual_meshes'][0]['shadow'].pop(k))
        self.mesh_mutation(['unexpected'], True)
        self.mesh_mutation(['face_method'], 'get_faces')
        self.mesh_mutation(['geometry_policy'], 'loose')

    def test_surface_fields_and_types_fail_closed(self):
        for key in ['api_vertex_missing', 'levels']:
            self.rejected(lambda native, k=key: native['visual_meshes'][0]['surfaces'][0].pop(k))
        self.mesh_mutation(['surfaces', 0, 'unexpected'], True)
        for value in [None, 0, 1, 'false', []]:
            self.mesh_mutation(['surfaces', 0, 'api_vertex_missing'], value)
        for value in [None, {}, [], 'levels']:
            self.mesh_mutation(['surfaces', 0, 'levels'], value)

    def test_missing_api_only_narrow_shadow_branch(self):
        self.mesh_mutation(['surfaces', 0, 'api_vertex_missing'], True)
        self.mesh_mutation(['surfaces', 0, 'api_vertex_missing'], True, rock=True)
        shadow = copy.deepcopy(self.native['visual_meshes'][0]['shadow'])
        s.validate_mesh(shadow, allow_shadow=False, shadow_only=True)
        for fmt in [shadow['surfaces'][0]['format'] & ~s.COMPRESSED,
                    shadow['surfaces'][0]['format'] | s.NORMAL,
                    shadow['surfaces'][0]['format'] | s.TANGENT]:
            item = copy.deepcopy(shadow)
            item['surfaces'][0]['format'] = fmt
            with self.assertRaisesRegex(ValueError, 'missing API|tangent'):
                s.validate_mesh(item, allow_shadow=False, shadow_only=True)

    def test_static_format_unknown_flags_and_index_mismatch(self):
        item = copy.deepcopy(self.native['rock'])
        fmt = item['surfaces'][0]['format']
        for bad in [fmt | (1 << 6), fmt | (1 << 36), fmt & ~s.CURRENT_VERSION,
                    fmt & ~s.VERTEX, fmt & ~s.INDEX, True, 1.5]:
            value = copy.deepcopy(item); value['surfaces'][0]['format'] = bad
            with self.assertRaises(ValueError):
                s.validate_mesh(value, rock=True)

    def test_shadow_never_claims_get_faces(self):
        for key, value in [('get_faces_observed', True), ('get_faces_observed', 0),
                           ('get_faces_bounds', self.raw), ('get_faces_vertex_count', 3),
                           ('get_faces_vertex_count', False), ('get_faces_bytes_sha256', '0' * 64),
                           ('get_faces_snap_proof', {}), ('get_faces_fabricated', True),
                           ('shadow_coverage_proof', {}), ('geometry_policy', s.GEOMETRY_POLICY)]:
            self.mesh_mutation([key], value, shadow=True)

    def test_all_level_fields_required_and_unknown_rejected(self):
        for key in s.LEVEL_KEYS:
            self.rejected(lambda native, k=key: native['visual_meshes'][0]['surfaces'][0]['levels'][0].pop(k))
        self.mesh_mutation(['surfaces', 0, 'levels', 0, 'unexpected'], 0)

    def test_threshold_base_order_duplicates_nonfinite_wrong_types(self):
        for value in [1., -1., True, '0', None, math.nan, math.inf]:
            self.mesh_mutation(['surfaces', 0, 'levels', 0, 'threshold'], value)
        for value in [0., -1., True, '1.25', math.nan, math.inf, -math.inf]:
            self.mesh_mutation(['surfaces', 0, 'levels', 1, 'threshold'], value)
        self.mesh_mutation(['surfaces', 0, 'levels', 2, 'threshold'], 1.25)
        self.mesh_mutation(['surfaces', 0, 'levels', 2, 'threshold'], .5)

    def test_level_counts_hashes_and_bounds(self):
        for index in [0, 1, 2]:
            for value in [0, -3, 1, 4, 3., True, '3', None]:
                self.mesh_mutation(['surfaces', 0, 'levels', index, 'face_vertex_count'], value)
            for key in ['face_bytes_sha256', 'source_faces_hex_text_sha256', 'oriented_faces_sha256']:
                for value in ['', 'g' * 64, 'A' * 64, '0' * 63, None, 0]:
                    self.mesh_mutation(['surfaces', 0, 'levels', index, key], value)
            for value in [None, {}, {'min': [0, 0, 0], 'max': [math.nan, 1, 1]},
                          {'min': [0, 0, 0], 'max': [math.inf, 1, 1]},
                          {'min': [1, 0, 0], 'max': [0, 1, 1]}]:
                self.mesh_mutation(['surfaces', 0, 'levels', index, 'bounds'], value)

    def test_all_indexed_levels_require_exact_raw_containment(self):
        for shadow in [False, True]:
            for index in [0, 1, 2]:
                box = copy.deepcopy(self.raw)
                box['max'][0] = math.nextafter(box['max'][0], math.inf)
                self.mesh_mutation(['surfaces', 0, 'levels', index, 'bounds'], box, shadow=shadow)
        # The legacy face containment check also remains exact, not an epsilon.
        box = copy.deepcopy(self.raw); box['min'][0] = math.nextafter(box['min'][0], -math.inf)
        self.mesh_mutation(['face_bounds'], box)

    def test_base_face_union_indexed_union_and_single_surface_hash(self):
        narrower = {'min': [-.5, .5, -.5], 'max': [.5, 1.5, .5]}
        self.mesh_mutation(['face_bounds'], narrower)
        self.mesh_mutation(['indexed_visual_bounds'], narrower)
        self.mesh_mutation(['indexed_visual_bounds'], self.snapped)
        boolean_box = copy.deepcopy(self.raw); boolean_box['min'][1] = False
        self.mesh_mutation(['indexed_visual_bounds'], boolean_box)
        self.mesh_mutation(['face_bytes_sha256'], 'f' * 64)
        self.mesh_mutation(['surfaces', 0, 'levels', 0, 'face_bytes_sha256'], 'e' * 64)
        self.mesh_mutation(['surfaces', 0, 'levels', 0, 'face_vertex_count'], 3)

    def test_exact_clearance_union_no_extra_epsilon(self):
        for shadow in [False, True]:
            box = copy.deepcopy(self.raw if shadow else self.snapped)
            for direction in [-math.inf, math.inf]:
                changed = copy.deepcopy(box)
                changed['max'][0] = math.nextafter(changed['max'][0], direction)
                self.mesh_mutation(['combined_clearance_bounds'], changed, shadow=shadow)
        self.mesh_mutation(['combined_clearance_bounds'], self.raw)

    def test_primary_snap_requires_observation_count_and_hash(self):
        for key, values in [('get_faces_observed', [False, 1, None]),
                            ('get_faces_vertex_count', [0, True, 168., 3, None]),
                            ('get_faces_bytes_sha256', ['', None, 'g' * 64, '0' * 64]),
                            ('get_faces_bounds', [None, {}, self.raw])]:
            for value in values:
                self.mesh_mutation([key], value)

    def test_every_snap_proof_field_required_and_exact(self):
        for key in s.SNAP_KEYS:
            self.rejected(lambda native, k=key: native['visual_meshes'][0]['get_faces_snap_proof'].pop(k))
        for key, value in [('unexpected', True), ('passed', False), ('passed', 1),
                           ('method', 'epsilon'), ('step_float32_hex', '38d1b717'),
                           ('step_float32_hex', '17B7D138'), ('step_float32_hex', .0001),
                           ('predicted_face_bytes_sha256', '0' * 64),
                           ('predicted_face_bytes_sha256', ''), ('predicted_bounds', self.raw)]:
            self.mesh_mutation(['get_faces_snap_proof', key], value)
        changed = copy.deepcopy(self.snapped)
        changed['max'][0] = math.nextafter(changed['max'][0], math.inf)
        self.mesh_mutation(['get_faces_snap_proof', 'predicted_bounds'], changed)

    def test_snap_need_not_equal_raw_indexed_bytes_or_bounds(self):
        item = self.native['visual_meshes'][0]
        self.assertNotEqual(item['face_bytes_sha256'], item['get_faces_bytes_sha256'])
        self.assertNotEqual(item['face_bounds'], item['get_faces_bounds'])
        self.assertFalse(s.contains(item['vertex_bounds'], item['get_faces_bounds']))
        s.validate_native(self.native, self.request)

    def test_every_coverage_proof_field_required_and_exact(self):
        for key in s.PROOF_KEYS:
            self.rejected(lambda native, k=key: native['visual_meshes'][0]['shadow_coverage_proof'].pop(k))
        for key, value in [('unexpected', True), ('passed', False), ('passed', 1),
                           ('method', 'bounds_only'), ('helper_sha256', '0' * 64),
                           ('shadow_present', False), ('shadow_present', 1),
                           ('surfaces', []), ('surfaces', {}), ('surfaces', None)]:
            self.mesh_mutation(['shadow_coverage_proof', key], value)

    def test_coverage_surface_ledger_source_specific_and_complete(self):
        path = ['shadow_coverage_proof', 'surfaces', 0]
        for key in s.LEDGER_KEYS:
            self.rejected(lambda native, k=key: native['visual_meshes'][0]['shadow_coverage_proof']['surfaces'][0].pop(k))
        for key, value in [('surface', 1), ('surface', False), ('source_format', 34896613407.),
                           ('source_format', 34896613377), ('source_vertices', 36),
                           ('source_vertices', 120.), ('shadow_vertices', 120),
                           ('shadow_vertices', 36.), ('shadow_api_vertex_missing', False),
                           ('shadow_api_vertex_missing', 1), ('unexpected', True), ('levels', []), ('levels', None)]:
            self.mesh_mutation(path + [key], value)

    def test_coverage_level_ledger_matches_hash_count_threshold(self):
        path = ['shadow_coverage_proof', 'surfaces', 0, 'levels', 0]
        for key in s.LEDGER_LEVEL_KEYS:
            self.rejected(lambda native, k=key: native['visual_meshes'][0]['shadow_coverage_proof']['surfaces'][0]['levels'][0].pop(k))
        for key, value in [('threshold', 1), ('threshold', False), ('threshold', math.nan),
                           ('triangles', 55), ('triangles', 56.5), ('triangles', True),
                           ('triangles', '56'), ('triangles', math.inf),
                           ('source_faces_hex_text_sha256', '0' * 64),
                           ('source_faces_hex_text_sha256', 'bad'), ('unexpected', True)]:
            self.mesh_mutation(path + [key], value)

    def test_shadow_all_levels_oriented_winding_and_multiplicity(self):
        for index in [0, 1, 2]:
            self.mesh_mutation(['surfaces', 0, 'levels', index, 'oriented_faces_sha256'],
                               hash_text('reversed winding'), shadow=True)
            self.mesh_mutation(['surfaces', 0, 'levels', index, 'oriented_faces_sha256'],
                               hash_text('same unique triangles but different multiplicity'), shadow=True)
            self.mesh_mutation(['surfaces', 0, 'levels', index, 'face_vertex_count'], 9, shadow=True)
            self.mesh_mutation(['surfaces', 0, 'levels', index, 'threshold'], 6., shadow=True)
        self.rejected(lambda native: native['visual_meshes'][0]['shadow']['surfaces'][0]['levels'].pop())

    def test_shadow_exact_bounds_even_if_oriented_digest_forged_equal(self):
        box = {'min': [-.5, .5, -.5], 'max': [.5, 1.5, .5]}
        self.mesh_mutation(['surfaces', 0, 'levels', 1, 'bounds'], box, shadow=True)

    def test_shadow_fusion_and_triangle_reordering_need_not_equal_byte_hash(self):
        item = self.native['visual_meshes'][0]
        source, shadow = item['surfaces'][0], item['shadow']['surfaces'][0]
        self.assertNotEqual(source['vertex_count'], shadow['vertex_count'])
        for a, b in zip(source['levels'], shadow['levels']):
            self.assertNotEqual(a['face_bytes_sha256'], b['face_bytes_sha256'])
            self.assertEqual(a['oriented_faces_sha256'], b['oriented_faces_sha256'])
        s.validate_native(self.native, self.request)

    def test_shadow_available_api_vertices_also_supported(self):
        native = copy.deepcopy(self.native)
        for item in native['visual_meshes'] + [native['rock']]:
            for surface in item['shadow']['surfaces']:
                surface['api_vertex_missing'] = False
            self.rebuild_ledger(item)
        s.validate_native(native, self.request)

    def test_no_shadow_proof_requires_zero_partner_fields(self):
        item = copy.deepcopy(self.native['rock'])
        del item['shadow']
        item['shadow_mesh_resource'] = item['shadow_surface_storage_sha256'] = ''
        self.rebuild_ledger(item)
        s.validate_mesh(item, rock=True)
        item['shadow_coverage_proof']['surfaces'][0]['shadow_vertices'] = 24
        with self.assertRaises(ValueError):
            s.validate_mesh(item, rock=True)

    def test_unindexed_surface_support_and_lod_rejection(self):
        item = copy.deepcopy(self.native['rock'])
        del item['shadow']
        item['shadow_mesh_resource'] = item['shadow_surface_storage_sha256'] = ''
        surface = item['surfaces'][0]
        surface['format'] &= ~s.INDEX
        surface['index_count'] = 0
        surface['levels'] = surface['levels'][:1]
        self.rebuild_ledger(item)
        s.validate_mesh(item, rock=True)
        surface['levels'].append(copy.deepcopy(surface['levels'][0]))
        surface['levels'][1]['threshold'] = 1.
        self.rebuild_ledger(item)
        with self.assertRaisesRegex(ValueError, 'unindexed'):
            s.validate_mesh(item, rock=True)

    def test_multi_surface_base_and_all_lod_unions(self):
        item = copy.deepcopy(self.native['rock'])
        for mesh in [item, item['shadow']]:
            second = copy.deepcopy(mesh['surfaces'][0]); second['index'] = 1
            mesh['surfaces'].append(second)
            mesh['vertex_count'] *= 2
            mesh['face_vertex_count'] *= 2
            mesh['face_bytes_sha256'] = hash_text('concatenated base faces')
        item['get_faces_vertex_count'] *= 2
        self.rebuild_ledger(item)
        s.validate_mesh(item, rock=True)
        item['shadow_coverage_proof']['surfaces'].pop()
        with self.assertRaises(ValueError):
            s.validate_mesh(item, rock=True)

    def test_wrapper_source_guards_and_three_substitution_adapter(self):
        import run_shadow62_v3 as runner
        runner.source_guards()
        self.assertIs(runner.replay.validate_native, s.validate_native)

    def test_collector_only_calls_get_faces_on_primary_and_reuses_audit(self):
        source = (HERE / 'read_proxy_meshes62_v3.gd').read_text()
        helper = (HERE / 'visible_geometry61.gd').read_bytes()
        self.assertEqual(hashlib.sha256(helper).hexdigest(), s.AUDIT_SHA)
        self.assertIn('extends "../version-guard-v2/read_proxy_meshes62_v2.gd"', source)
        self.assertIn('auditor.audit_array_mesh(mesh)', source)
        self.assertIn('auditor.audit_surface(mesh,index,raw[index])', source)
        self.assertIn('auditor.surface_positions(raw[index]', source)
        self.assertIn('source_faces_hex_text_sha256', source)
        self.assertEqual(source.count('mesh.get_faces()'), 1)
        lines = source.splitlines()
        call = next(i for i, line in enumerate(lines) if 'mesh.get_faces()' in line)
        guard = max(i for i in range(call) if lines[i].strip() == 'if not shadow_only:')
        self.assertGreater(call, guard)
        self.assertTrue(lines[call].startswith('\t\t'))
        for forbidden in ['func _initialize(', 'func read_visual(', 'func read_rock(',
                          '.prepare(', '.add_shape(', '.indexed_shape(', '.instantiate(',
                          '.create_trimesh_shape(', 'PhysicsServer3D', 'ResourceSaver']:
            self.assertNotIn(forbidden, source)
        self.assertNotIn('assert ', inspect.getsource(s))


if __name__ == '__main__':
    unittest.main(verbosity=2)
