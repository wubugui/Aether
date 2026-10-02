"""Pure saved-data/fixture checks; no engine, cache import, GLB or native save."""
import ast
from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import numpy as np
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_cache58k as r
g = r.g; c = g.c


def fixture():
    source, expected, decoder, (v, packed, indices) = g.reference()
    normal, tangent = decoder.unpack_channels(packed)
    meta = decoder.decode_cache()[0]
    native_material = meta['resources'][0]['properties']
    channels = [dict(channel=i, type='Nil', count=0) for i in range(13)]
    for index, name, count in [(0, 'PackedVector3Array', 1152), (1, 'PackedVector3Array', 1152), (2, 'PackedFloat32Array', 4608), (12, 'PackedInt32Array', 1152)]:
        channels[index].update(type=name, count=count)
    report = dict(version=g.VERSION, passed=True, mode='import', pid=123, world_loaded=False, images=0,
                  engine=dict(major=4, minor=5, patch=1), channels=channels, format=expected['format'], stored_surface=deepcopy(expected),
                  geometry=dict(positions=v.astype(float).tolist(), normals=normal.astype(float).tolist(), indices=indices.tolist()),
                  tangents=tangent.astype(float).ravel().tolist(),
                  material=dict(albedo_srgb_rgba=native_material['albedo_color']['values'], roughness=native_material['roughness'],
                                metallic=0., texture_count=0, shader_material=False, emission_enabled=False, emission_rgb=[0, 0, 0], transparency=0, cull_mode=native_material['cull_mode']),
                  transforms=[dict(origin=[0, 0, 0], basis=[[1, 0, 0], [0, 1, 0], [0, 0, 1]])], dependencies=[],
                  aabb=[expected['aabb_position'], expected['aabb_end']],
                  aabb_storage=dict(position=expected['aabb_position'], size=expected['aabb_size'], end=expected['aabb_end']))
    return report, source, expected


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report, cls.source, cls.expected = fixture()

    def reject(self, mutate):
        report = deepcopy(self.report); mutate(report)
        with self.assertRaises((ValueError, TypeError, KeyError, IndexError)):
            g.validate(report, self.source, self.expected, 'import', 123)

    def test_saved_array_fixture_original_contract(self):
        result = g.validate(self.report, self.source, self.expected, 'import', 123)
        self.assertEqual(result['geometry']['maximum_position_error_m'], 0)
        self.assertLess(result['geometry']['maximum_normal_component_error'], 2e-4)
        self.assertTrue(result['tangents']['passed'])

    def test_derived_tangent_bounds(self):
        self.assertEqual(g.TANGENT_UNIT_EPS, 64 * 2**-24)
        self.assertAlmostEqual(g.TANGENT_DOT_EPS, 0.00034205286850920414, places=16)
        self.assertEqual(c.POSITION_EPS, 1e-5); self.assertEqual(c.NORMAL_EPS, 3e-5)

    def test_tangent_semantic_rejections(self):
        self.reject(lambda d: d['tangents'].__setitem__(3, -1))
        self.reject(lambda d: d['tangents'].__setitem__(0, float('nan')))
        self.reject(lambda d: d['tangents'].__setitem__(0, float('inf')))
        self.reject(lambda d: d['tangents'].__setitem__(slice(0, 3), d['geometry']['normals'][0]))
        self.reject(lambda d: d['tangents'].__setitem__(slice(0, 3), [2*x for x in d['tangents'][:3]]))
        self.reject(lambda d: d['tangents'].pop())

    def test_unit_and_perpendicular_boundary(self):
        n = np.tile([0., 0., 1.], (1152, 1))
        t = np.tile([1., 0., 0., 1.], (1152, 1))
        self.assertTrue(g.tangent_checks(n, t.ravel())['passed'])
        t[:, 0] = 1 + 2*g.TANGENT_UNIT_EPS
        with self.assertRaises(ValueError):g.tangent_checks(n, t.ravel())
        t[:, 0] = np.sqrt(1-(2*g.TANGENT_DOT_EPS)**2); t[:, 2] = 2*g.TANGENT_DOT_EPS
        with self.assertRaises(ValueError):g.tangent_checks(n, t.ravel())

    def test_all_other_channels_and_types_rejected(self):
        for channel in [3, 4, 5, 6, 7, 8, 9, 10, 11]:
            self.reject(lambda d: d['channels'][channel].update(count=1, type='PackedFloat32Array'))
        self.reject(lambda d: d['channels'][2].update(type='PackedFloat64Array'))
        self.reject(lambda d: d['channels'][2].update(count=4607))
        self.reject(lambda d: d['channels'].pop())

    def test_exact_storage_and_identity_rejected(self):
        for key in ['vertex_data_sha256', 'index_data_sha256']:
            self.reject(lambda d: d['stored_surface'].update({key: 'wrong'}))
        self.reject(lambda d: d['stored_surface'].update(format=34359742467))
        self.reject(lambda d: d.update(format=34359742467))
        self.reject(lambda d: d.update(pid=124))
        self.reject(lambda d: d.update(passed=False))

    def test_exact_aabb_representation_and_old_negative(self):
        v = np.asarray(self.report['geometry']['positions'], np.float32)
        ends = np.asarray(self.report['aabb'][1])
        old_error = float(np.max(np.abs(ends-v.max(axis=0))))
        self.assertEqual(old_error, 1.52587890625e-5)
        self.assertGreater(old_error, c.POSITION_EPS) # Old endpoint comparison would fail.
        self.assertTrue(np.array_equal((v.max(axis=0)-v.min(axis=0)), self.expected['aabb_size']))
        self.reject(lambda d: d['aabb_storage']['size'].__setitem__(2, d['aabb_storage']['size'][2] + 1e-5))
        self.reject(lambda d: d['aabb'][1].__setitem__(2, float(v.max(axis=0)[2])))

    def test_geometry_material_gates_retained(self):
        self.reject(lambda d: d['geometry']['positions'][0].__setitem__(0, d['geometry']['positions'][0][0]+.001))
        self.reject(lambda d: d['geometry']['normals'][0].__setitem__(0, 0))
        self.reject(lambda d: d['material'].update(texture_count=1))
        self.reject(lambda d: d['material'].update(shader_material=True))
        self.reject(lambda d: d['material'].update(metallic=.5))
        self.reject(lambda d: d['material'].update(emission_enabled=True))

    def test_all_triangles_reversed_rejected(self):
        for face in range(384):
            def flip(d):
                index = face*3; d['geometry']['indices'][index+1], d['geometry']['indices'][index+2] = d['geometry']['indices'][index+2], d['geometry']['indices'][index+1]
            self.reject(flip)

    def test_default_no_launch_copy_or_allocation(self):
        with (patch.object(sys, 'argv', ['run_cache58k.py']), patch.object(r.support, 'run_child', side_effect=AssertionError('No native')),
              patch.object(r.tempfile, 'mkdtemp', side_effect=AssertionError('No output')), patch.object(r.shutil, 'copy2', side_effect=AssertionError('No copying'))):
            self.assertEqual(r.main(), 0)

    def test_scope_and_limits(self):
        self.assertEqual(r.NATIVE_SECONDS, (20, 20)); self.assertEqual(r.TOTAL_SECONDS, 120)
        self.assertEqual(r.support.MAX_RSS_KIB, 1572864)
        code = (g.HERE / 'run_cache58k.py').read_text()
        for token in ["'--editor'", "'--import'", 'restore_bytes(', 'c.BLENDER']:
            self.assertNotIn(token, code)
        probe = (g.HERE / 'probe58k.gd').read_text()
        self.assertIn('res://imported.scn', probe); self.assertNotIn('res://cloud58k.glb', probe)
        self.assertIn("'tangents', 'channels'", code)
        for path in g.HERE.glob('*.py'):
            ast.parse(path.read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)
