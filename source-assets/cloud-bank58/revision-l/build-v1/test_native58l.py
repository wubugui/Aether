"""Source-only tests. No bpy, engine process, native parse, or fixture acceptance."""
import ast
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True


def load(name):
    spec = importlib.util.spec_from_file_location('test_'+name, HERE/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BlockedPreparation(unittest.TestCase):
    def test_static_python_syntax_only(self):
        for name in ('native58l.py', 'run58l.py', 'test_native58l.py'):
            text = (HERE/name).read_text()
            ast.parse(text, filename=name)
            compile(text, name, 'exec')

    def test_native_default_inert(self):
        before = set(sys.modules)
        native = load('native58l')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(native.main([]), 0)
        self.assertNotIn('bpy', set(sys.modules)-before)

    def test_all_native_stages_unconditionally_reject(self):
        native = load('native58l')
        for mode in ('build', 'verify'):
            with self.assertRaisesRegex(ValueError, 'SPATIAL_IMPLEMENTATION_UNRESOLVED'):
                native.main(['--mode', mode, '--out', '/tmp/not-created-l58', '--admission', '/tmp/not-read-l58'])

    def test_direct_create_helper_unconditionally_rejects(self):
        with self.assertRaisesRegex(ValueError, 'SPATIAL_IMPLEMENTATION_UNRESOLVED'):
            load('native58l').create_source(None, None, None, None)

    def test_direct_rebuild_helper_unconditionally_rejects(self):
        with self.assertRaisesRegex(ValueError, 'SPATIAL_IMPLEMENTATION_UNRESOLVED'):
            load('native58l').rebuild_from_controls()

    def test_direct_exercise_helper_unconditionally_rejects(self):
        with self.assertRaisesRegex(ValueError, 'SPATIAL_IMPLEMENTATION_UNRESOLVED'):
            load('native58l').exercise_controls(None, None, None, None, None)

    def test_wrapper_default_noop(self):
        runner = load('run58l')
        with contextlib.redirect_stdout(io.StringIO()) as stream:
            self.assertEqual(runner.main([]), 0)
        self.assertEqual(json.loads(stream.getvalue())['status'], 'no_op')

    def test_wrapper_release_cannot_bypass_blocker(self):
        runner = load('run58l')
        for stage in ('source', 'views'):
            with contextlib.redirect_stdout(io.StringIO()) as stream:
                self.assertEqual(runner.main(['--run-approved', stage, '--release', '/tmp/not-read-l58']), 2)
            row = json.loads(stream.getvalue())
            self.assertFalse(row['engine_started'])
            self.assertFalse(row['native_stage_allowed'])

    def test_runner_has_no_process_launcher(self):
        tree = ast.parse((HERE/'run58l.py').read_text())
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertFalse(any('subprocess' in ast.unparse(node) or 'bounded_support' in ast.unparse(node) for node in imports))
        self.assertFalse(any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in
                             ('Popen', 'run_child', 'system', 'spawn', 'run', 'execv') for node in ast.walk(tree)))

    def test_blocked_candidate_is_not_geometry(self):
        row = json.loads((HERE/'candidate-status.json').read_text())
        self.assertIs(row['implementation_ready'], False)
        self.assertNotIn('vertices_world', row)
        with self.assertRaisesRegex(ValueError, 'Missing or blocked'):
            load('native58l').validate_edit_schema(row)

    def test_exact_camera_fields_preserved(self):
        native = load('native58l')
        binding = json.loads((HERE/'input-bindings.json').read_text())
        original = json.loads((HERE.parent/'design-v1/evidence-bindings.json').read_text())
        for row, old in zip(binding['world_cameras'], original['fixed_actual_camera_records']):
            self.assertEqual(row['camera_transform'], old['camera_transform'])
            self.assertEqual(row['camera_projection'], old['camera_projection'])
            matrix = native.camera_matrix(row)
            self.assertEqual(matrix[3], [0., 0., 0., 1.])
        self.assertEqual(len(binding['world_cameras']), 4)

    def test_native_has_no_render_call_or_text_write(self):
        tree = ast.parse((HERE/'native58l.py').read_text())
        calls = [ast.unparse(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)]
        self.assertNotIn('bpy.ops.render.render', calls)
        self.assertIn('bpy.data.texts.load', calls)
        self.assertNotIn('text.write', calls)

    def test_local_mapping_rounds_after_anchor(self):
        native = load('native58l')
        point = [4399.82146152658, 632.99383508028, 4606.95685873829]
        exact = native.local(point)
        self.assertEqual(exact, [native.f32(point[0]-3958), native.f32(3667-point[2]), native.f32(point[1])])
        self.assertNotEqual(exact[0], native.f32(native.f32(point[0])-3958))


if __name__ == '__main__':
    unittest.main(verbosity=2)
