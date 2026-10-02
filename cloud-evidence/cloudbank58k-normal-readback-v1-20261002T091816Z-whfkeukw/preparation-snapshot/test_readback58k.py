"""Pure simulated normal/protocol negative controls, not native observations."""
import ast
from copy import deepcopy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_readback58k as r
g = r.g; c = g.c


def fixture():
    verified = c.source_preconditions(); v, f = g.reconstructed_source(verified)
    normals = g.replay_newell(v, f).astype(float)
    data = dict(version=g.VERSION, state='captured', pid=123, blender_version=[4, 5, 14], cpu_affinity=[0, 1],
                source_sha256_before=c.SOURCE_SHA, source_sha256_after=c.SOURCE_SHA,
                identity_before=deepcopy(verified['native_identity']), identity_after=deepcopy(verified['native_identity']),
                cameras_before=g.camera_expectations(verified), cameras_after=g.camera_expectations(verified),
                scene_state_before=dict(active_camera='VIEW58K_1216-source-front', resolution_x=836, resolution_y=471, resolution_percentage=100, pixel_aspect_x=1., pixel_aspect_y=1.),
                scene_state_after=dict(active_camera='VIEW58K_1216-source-front', resolution_x=836, resolution_y=471, resolution_percentage=100, pixel_aspect_x=1., pixel_aspect_y=1.),
                dependencies_before=deepcopy(verified['loaded_datablocks']), dependencies_after=deepcopy(verified['loaded_datablocks']),
                positions=v.tolist(), triangles=f.tolist(), polygon_normals=normals.tolist(),
                corner_normals=np.repeat(normals, 3, axis=0).tolist(), polygon_loop_indices=np.arange(1152).reshape(-1, 3).tolist(),
                loop_vertex_indices=f.ravel().tolist(), loop_polygon_indices=np.repeat(np.arange(384), 3).tolist(),
                source_saved=False, export_performed=False, godot_started=False, world_loaded=False, images=0, visual_acceptance=False)
    return data, verified


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.verified = fixture()

    def reject(self, mutate):
        data = deepcopy(self.data); mutate(data)
        with self.assertRaises((ValueError, KeyError, TypeError, IndexError)):
            g.validate_readback(data, 123, self.verified)

    def test_predicted_fixture_valid(self):
        result = g.validate_readback(self.data, 123, self.verified)
        self.assertTrue(result['passed']); self.assertFalse(result['transfer_success'])
        self.assertEqual(result['failed_glb_replay_max_error'], 0)

    def test_source_identity_and_pid(self):
        for key, value in [('pid', 124), ('version', 'wrong'), ('state', 'running'), ('blender_version', [4, 5, 13]),
                           ('source_sha256_before', 'wrong'), ('source_sha256_after', 'wrong'), ('cpu_affinity', [0, 1, 2]),
                           ('cpu_affinity', [0, 0, 1]), ('cpu_affinity', [False, 1]), ('pid', 123.0)]:
            self.reject(lambda d: d.update({key: value}))
        self.reject(lambda d: d['identity_after'].update(passed=False))
        self.reject(lambda d: d['cameras_after'].clear())
        self.reject(lambda d: d['dependencies_after'].update(strict_saved_source_dependencies_passed=False))
        self.reject(lambda d: d['scene_state_after'].update(active_camera='changed'))

    def test_scope_guards(self):
        for key in ['source_saved', 'export_performed', 'godot_started', 'world_loaded', 'visual_acceptance']:
            self.reject(lambda d: d.update({key: True}))
        self.reject(lambda d: d.update(images=1))

    def test_geometry_mutations(self):
        self.reject(lambda d: d['positions'][0].__setitem__(0, d['positions'][0][0] + .001))
        self.reject(lambda d: d['triangles'][0].reverse())
        self.reject(lambda d: d['positions'].pop())
        self.reject(lambda d: d['positions'][0].__setitem__(0, float('nan')))

    def test_loop_mapping(self):
        self.reject(lambda d: d['polygon_loop_indices'][0].__setitem__(0, 1))
        self.reject(lambda d: d['polygon_loop_indices'][0].__setitem__(0, -1))
        self.reject(lambda d: d['loop_polygon_indices'].__setitem__(0, 1))
        self.reject(lambda d: d['loop_vertex_indices'].__setitem__(0, 1))
        self.reject(lambda d: d['loop_vertex_indices'].__setitem__(0, False))

    def test_all_384_flipped_normals(self):
        for face in range(384):
            def flip(d):
                d['polygon_normals'][face] = [-x for x in d['polygon_normals'][face]]
                for loop in d['polygon_loop_indices'][face]:
                    d['corner_normals'][loop] = list(d['polygon_normals'][face])
            self.reject(flip)

    def test_normal_corruption(self):
        self.reject(lambda d: d['polygon_normals'][0].__setitem__(0, float('nan')))
        self.reject(lambda d: d['corner_normals'][0].__setitem__(0, float('inf')))
        self.reject(lambda d: d['corner_normals'][0].__setitem__(0, 0))
        self.reject(lambda d: d['corner_normals'].pop())
        self.reject(lambda d: d['polygon_normals'][0].__setitem__(0, d['polygon_normals'][0][0] + 1e-12))

    def test_original_gates_not_relaxed(self):
        self.assertEqual(c.NORMAL_EPS, 3e-5); self.assertEqual(c.POSITION_EPS, 1e-5)
        self.assertEqual(r.NATIVE_SECONDS, 30); self.assertEqual(r.TOTAL_SECONDS, 60)
        self.assertEqual(r.support.MAX_RSS_KIB, 1572864)

    def test_default_cannot_launch_or_allocate(self):
        with (patch.object(sys, 'argv', ['run_readback58k.py']), patch.object(r.support, 'run_child', side_effect=AssertionError('No native')),
                patch.object(r.tempfile, 'mkdtemp', side_effect=AssertionError('No output'))):
            self.assertEqual(r.main(), 0)

    def test_source_scope_ast(self):
        for path in g.HERE.glob('*.py'):
            ast.parse(path.read_text())
        script = (g.HERE / 'collect58k.py').read_text()
        tree = ast.parse(script)
        operators = [ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call) and ast.unparse(n.func).startswith('bpy.ops.')]
        self.assertEqual(operators, ['bpy.ops.wm.open_mainfile'])
        self.assertNotIn('core.cameras(', script)
        self.assertNotIn('camera_resolution(', script)
        self.assertLess(script.index("c.write(out / 'source-normal-arrays.json'"), script.index('g.validate_readback(data'))
        self.assertIn("(g.HERE / 'native-attempt.json').open('x')", (g.HERE / 'run_readback58k.py').read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)
