#!/usr/bin/env python3
"""Isolated Python-only wrapper regression tests. Never launches Godot.

Mock native payloads test acceptance/rejection logic only. The process-launcher
cases launch the Python interpreter, testing actual PID ownership and reaping.
Neither kind establishes native fixture/GDScript/world success.
"""
from __future__ import annotations

import importlib.util
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import signal
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WrapperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='orbit61-v6-python-test-')
        self.root = Path(self.temp.name)
        self.orbit = self.root / 'source-assets/coast61-nearbay-orbit'
        self.here = self.orbit / 'continuous-v6'
        self.here.mkdir(parents=True)
        for name in ('run_fixture.py', 'fixture.gd', 'wrapper_support.py'):
            shutil.copy2(HERE / name, self.here / name)
        shutil.copy2(HERE.parent / 'run_orbit61.py', self.orbit / 'run_orbit61.py')
        # Import only the copied helper. No test modifies checkout sources.
        self.support = load('wrapper_support', self.here / 'wrapper_support.py')
        self.import_patch = patch.dict(sys.modules, {'wrapper_support': self.support})
        self.import_patch.start()
        self.fixture = load('fixture_under_test', self.here / 'run_fixture.py')
        self.runner = load('orbit_under_test', self.orbit / 'run_orbit61.py')
        self.asset = self.root / 'protected.data'
        self.asset.write_text('frozen fixture test data')
        self.protected = {str(self.asset): self.support.sha(self.asset)}
        self.engine = self.root / 'NOT_AN_ENGINE.data'
        self.engine.write_text('This data file is never executed')
        self.fixture.GODOT = self.engine
        self.fixture.EXPECTED_GODOT = self.support.sha(self.engine)
        self.fixture.protected_manifest = lambda: dict(self.protected)
        self.fixture.source_paths = lambda: sorted(self.here.glob('*'))
        self.out = self.root / 'out'
        self.out.mkdir()
        self.launches = 0
        self.env_patch = patch.dict(os.environ, {'DISPLAY': ':unit-test-not-connected'})
        self.env_patch.start()
        self.valid = {'version': 'orbit61-continuous-v6', 'passed': True,
                      'display_backend': 'X11', 'rendering_method': 'gl_compatibility',
                      'rendering_driver': 'opengl3', 'world_loaded': False, 'engine': {'major': 4, 'minor': 5, 'patch': 1},
                      'checks': [{'name': n, 'passed': True} for n in self.fixture.required_checks()]}

    def tearDown(self):
        self.env_patch.stop()
        self.import_patch.stop()
        self.temp.cleanup()

    def process(self):
        return {'status': 'finished', 'returncode': 0, 'native_exit_observed': True,
                'wall_seconds': .01, 'timeout_triggered': False, 'wrapper_received_signal': None,
                'cpu_affinity': [0, 1], 'max_rss_kib': 100}

    def native_stub(self, payload=None, mutate=None, row=None):
        def launch(command, out, env, cwd, timeout, label):
            self.launches += 1
            self.assertNotIn('--headless', command)
            self.assertEqual(command[command.index('--rendering-method') + 1], 'gl_compatibility')
            self.assertEqual(command[command.index('--resolution') + 1], '320x180')
            self.assertEqual(timeout, 59)
            self.assertNotEqual(cwd, self.runner.PROJECT)
            (out / 'fixture.stdout.log').write_text('Python mock payload; not Godot\n')
            (out / 'fixture.stderr.log').write_text('')
            text = json.dumps(self.valid) if payload is None else payload
            (out / 'result.json').write_text(text)
            if mutate:
                mutate()
            return self.process() if row is None else row
        return launch

    def fixture_run(self, launch=None):
        with patch.object(self.fixture, 'run_child', launch or self.native_stub()):
            result = self.fixture.execute(self.out)
        saved = json.loads((self.out / 'wrapper-report.json').read_text())
        self.assertEqual(saved, result)
        self.assertTrue(result['input_aftercheck_attempted'])
        self.assertTrue((self.out / 'sources-after.json').exists())
        self.assertTrue((self.out / 'protected-after.json').exists())
        return result

    def test_fixture_positive_acceptance_logic_only(self):
        result = self.fixture_run()
        self.assertTrue(result['passed'])
        self.assertEqual(self.launches, 1)
        self.assertTrue(result['inputs_unchanged'])

    def test_fixture_missing_display_denies_before_launch(self):
        with patch.dict(os.environ, {'DISPLAY': ''}):
            result = self.fixture_run()
        self.assertFalse(result['passed'])
        self.assertEqual(self.launches, 0)

    def test_fixture_engine_mismatch_denies_before_launch(self):
        self.engine.write_text('changed')
        result = self.fixture_run()
        self.assertFalse(result['passed'])
        self.assertEqual(self.launches, 0)

    def test_fixture_before_guard_error_denies_launch(self):
        self.fixture.protected_manifest = lambda: (_ for _ in ()).throw(RuntimeError('before guard rejected'))
        result = self.fixture_run()
        self.assertFalse(result['passed'])
        self.assertEqual(self.launches, 0)

    def test_fixture_after_guard_error_rejects_successful_child(self):
        count = 0
        def guard():
            nonlocal count
            count += 1
            if count == 3:
                raise RuntimeError('after guard rejected')
            return dict(self.protected)
        self.fixture.protected_manifest = guard
        result = self.fixture_run()
        self.assertFalse(result['passed'])
        self.assertTrue(result['native_exit_observed'])
        self.assertIn('after guard rejected', result['input_recheck_error'])

    def test_fixture_saved_failure_changed_is_rejected(self):
        result = self.fixture_run(self.native_stub(mutate=lambda: self.asset.write_text('changed')))
        self.assertFalse(result['passed'])
        self.assertEqual(result['protected_changed_inputs'], [str(self.asset)])

    def test_fixture_source_removed_is_rejected(self):
        result = self.fixture_run(self.native_stub(mutate=lambda: (self.here / 'fixture.gd').unlink()))
        self.assertFalse(result['passed'])
        self.assertIn(str(self.here / 'fixture.gd'), result['changed_inputs'])

    def test_fixture_malformed_json_preserves_exit_and_afterchecks(self):
        result = self.fixture_run(self.native_stub(payload='{"passed":true'))
        self.assertFalse(result['passed'])
        self.assertEqual(result['returncode'], 0)
        self.assertTrue(result['native_exit_observed'])

    def test_fixture_strict_payload_rejections(self):
        bad = [[], {'passed': True}, dict(self.valid, passed='true'), dict(self.valid, checks=[]),
               dict(self.valid, display_backend='headless'), dict(self.valid, world_loaded=True),
               dict(self.valid, rendering_method='dummy'), dict(self.valid, engine={'major': 4, 'minor': 5, 'patch': 0}),
               dict(self.valid, checks=self.valid['checks'][:-1]),
               dict(self.valid, checks=self.valid['checks'] + [self.valid['checks'][0]])]
        path = self.out / 'payload.json'
        for payload in bad:
            with self.subTest(payload=str(payload)[:80]):
                path.write_text(json.dumps(payload))
                with self.assertRaises(ValueError):
                    self.fixture.validate_result(path, self.fixture.required_checks())
        for text in ('{"passed":true,"passed":false}', '{"value":NaN}', '{"value":Infinity}', '{"value":1e999}'):
            path.write_text(text)
            with self.assertRaises(ValueError):
                self.support.strict_json(path)

    def test_fixture_child_cancel_or_timeout_never_passes(self):
        for field, value in [('wrapper_received_signal', signal.SIGTERM), ('timeout_triggered', True), ('returncode', -9), ('native_exit_observed', False)]:
            with self.subTest(field=field):
                row = dict(self.process(), **{field: value})
                result = self.fixture_run(self.native_stub(row=row))
                self.assertFalse(result['passed'])

    def test_fixture_setup_cancellation_runs_aftercheck(self):
        real_copy = self.fixture.shutil.copy2
        signaled = False
        def copy_then_signal(*args, **kwargs):
            nonlocal signaled
            value = real_copy(*args, **kwargs)
            if not signaled:
                signaled = True
                os.kill(os.getpid(), signal.SIGTERM)
            return value
        with patch.object(self.fixture.shutil, 'copy2', copy_then_signal):
            result = self.fixture_run()
        self.assertFalse(result['passed'])
        self.assertEqual(result['wrapper_received_signal'], signal.SIGTERM)
        self.assertEqual(self.launches, 0)

    def prepare_orbit(self):
        self.runner.ROOT = self.root
        (self.root / 'tools-feiting').mkdir(exist_ok=True)
        self.runner.source_manifest = lambda: dict(self.protected)
        self.runner.own_sources = lambda: []
        self.runner.DEPENDENCY_FILES = ()
        self.runner.dependency_validation = lambda: ({}, {'status': 'unit-test-only'})
        self.args = SimpleNamespace(run_renderer=True, parse_only=False, wall_timeout=720)
        def launch(command, out, env, timeout, label):
            self.launches += 1
            (out / 'images').mkdir(exist_ok=True)
            self.write_mock_completion(out)
            return self.process()
        self.runner.child_run = launch

    def write_mock_completion(self, out):
        # Explicit test-only payloads. No native clock or engine is exercised.
        report_path = out / 'images/orbit-report.json'
        report_path.write_text('{"complete":true,"first_item_runtime_passed":true}')
        def wall(boundary, msec):
            return {'limit_seconds': 600, 'verification_completed_wall_seconds': msec / 1000,
                    'first_exceeded_at': {}, 'last_check': {'boundary': boundary,
                    'elapsed_msec': msec, 'wall_seconds': msec / 1000}}
        receipt_path = out / 'images/orbit-completion.json'
        receipt = {'version': 'orbit61-completion-v1', 'first_item_runtime_passed': True,
                   'native_report_sha256': self.support.sha(report_path),
                   'wall_deadline': wall('finish_after_final_report_and_sha', 590000)}
        receipt_path.write_text(json.dumps(receipt))
        terminal = {'version': 'orbit61-terminal-wall-v1', 'first_item_runtime_passed': True,
                    'native_report_sha256': self.support.sha(report_path),
                    'completion_receipt_sha256': self.support.sha(receipt_path),
                    'wall_deadline': wall('finish_before_cleanup', 591000)}
        (out / 'renderer.stdout.log').write_text('ORBIT61_TERMINAL_WALL ' + json.dumps(terminal) + '\n')

    def orbit_run(self):
        result = self.runner.execute(self.args, self.out, {'python_test_only': True})
        self.assertTrue(result['input_aftercheck_attempted'])
        self.assertEqual(json.loads((self.out / 'wrapper-report.json').read_text()), result)
        self.assertTrue((self.out / 'output-sha256.json').exists())
        return result

    def test_orbit_positive_acceptance_logic_only(self):
        self.prepare_orbit()
        result = self.orbit_run()
        self.assertTrue(result['passed'])
        self.assertEqual(self.launches, 1)
        self.assertIn('dependency_guard_before', result)
        self.assertIn('dependency_guard_after', result)

    def test_orbit_before_dependency_guard_denies_launch(self):
        self.prepare_orbit()
        self.runner.dependency_validation = lambda: (_ for _ in ()).throw(RuntimeError('before dependency guard'))
        result = self.orbit_run()
        self.assertFalse(result['passed'])
        self.assertEqual(self.launches, 0)
        self.assertIn('dependency_guard_recheck_error', result)

    def test_orbit_after_dependency_guard_denies_native_success(self):
        self.prepare_orbit()
        count = 0
        def guard():
            nonlocal count
            count += 1
            if count >= 2:
                raise RuntimeError('reviewed-absent override appeared')
            return {}, {'status': 'unit-test-only'}
        self.runner.dependency_validation = guard
        result = self.orbit_run()
        self.assertFalse(result['passed'])
        self.assertEqual(result['processes'][0]['returncode'], 0)
        self.assertFalse(result['first_item_runtime_passed'])
        self.assertIn('reviewed-absent override appeared', result['dependency_guard_recheck_error'])

    def test_orbit_mutated_input_fails_even_if_native_passes(self):
        self.prepare_orbit()
        launch = self.runner.child_run
        def mutate(*args):
            row = launch(*args)
            self.asset.write_text('mutated')
            return row
        self.runner.child_run = mutate
        result = self.orbit_run()
        self.assertFalse(result['passed'])
        self.assertEqual(result['changed_inputs'], [str(self.asset)])

    def test_orbit_malformed_native_json_is_terminal_failure(self):
        self.prepare_orbit()
        launch = self.runner.child_run
        def malformed(*args):
            row = launch(*args)
            (self.out / 'images/orbit-report.json').write_text('{"complete":true')
            return row
        self.runner.child_run = malformed
        result = self.orbit_run()
        self.assertFalse(result['passed'])
        self.assertEqual(result['processes'][0]['returncode'], 0)
        self.assertIn('dependency_guard_after', result)

    def test_orbit_empty_process_list_cannot_pass(self):
        self.prepare_orbit()
        self.runner.child_run = lambda *args: (_ for _ in ()).throw(OSError('spawn denied'))
        result = self.orbit_run()
        self.assertFalse(result['passed'])
        self.assertEqual(result['processes'], [])
        self.assertIn('dependency_guard_after', result)

    def test_orbit_setup_cancellation_is_terminal(self):
        self.prepare_orbit()
        def cancel():
            os.kill(os.getpid(), signal.SIGINT)
            return []
        self.runner.own_sources = cancel
        result = self.orbit_run()
        self.assertFalse(result['passed'])
        self.assertEqual(result['wrapper_received_signal'], signal.SIGINT)
        self.assertEqual(self.launches, 0)

    def test_orbit_parse_stops_after_cancelled_child(self):
        self.prepare_orbit()
        self.args.run_renderer = False
        self.args.parse_only = True
        self.runner.child_run = lambda *args: dict(self.process(), wrapper_received_signal=signal.SIGTERM)
        result = self.orbit_run()
        self.assertFalse(result['passed'])
        self.assertEqual(len(result['processes']), 1)
        self.assertFalse(result['godot_parse_passed'])

    def actual_python(self, code, timeout=2):
        row = self.support.run_child([sys.executable, '-c', code], self.out, os.environ.copy(), self.root, timeout, 'python-test')
        self.assertTrue(row['native_exit_observed'])
        self.assertIsNotNone(row.get('pid'))
        with self.assertRaises(ChildProcessError):
            os.waitpid(row['pid'], os.WNOHANG)
        self.assertEqual(json.loads((self.out / 'python-test.process.json').read_text())['returncode'], row['returncode'])
        return row

    def test_orbit_copied_dependency_guard_tampering_rejected(self):
        original_home = HERE.parents[1] / 'north-ridge62-intake'
        copied = self.root / 'copied-north-guard'
        copied.mkdir()
        shutil.copy2(original_home / 'dependency_guard62.py', copied / 'dependency_guard62.py')
        (copied / 'dependency_guard62.py').write_text('# changed, must not execute\n')
        self.runner.DEPENDENCY_HOME = copied
        with self.assertRaisesRegex(RuntimeError, 'Previously verified dependency_guard62.py identity changed'):
            self.runner.dependency_validation()

    def test_orbit_exact_copied_guard_rejects_changed_review(self):
        original_home = HERE.parents[1] / 'north-ridge62-intake'
        copied = self.root / 'copied-north-guard'
        copied.mkdir()
        shutil.copy2(original_home / 'dependency_guard62.py', copied / 'dependency_guard62.py')
        shutil.copy2(original_home / 'DEPENDENCY_REVIEW.json.gz', copied / 'DEPENDENCY_REVIEW.json.gz')
        with (copied / 'DEPENDENCY_REVIEW.json.gz').open('ab') as handle:
            handle.write(b'changed')
        self.runner.DEPENDENCY_HOME = copied
        with self.assertRaisesRegex(RuntimeError, 'frozen review gzip'):
            self.runner.dependency_validation()

    def test_launcher_actual_python_exit_is_reaped(self):
        row = self.actual_python('raise SystemExit(7)')
        self.assertEqual(row['returncode'], 7)
        self.assertFalse(self.support.process_passed(row))

    def test_launcher_timeout_kills_and_reaps_python(self):
        row = self.actual_python('import time; time.sleep(20)', .08)
        self.assertEqual(row['returncode'], -signal.SIGKILL)
        self.assertTrue(row['timeout_triggered'])
        self.assertLess(row['wall_seconds'], 2)

    def test_launcher_sigterm_kills_and_reaps_python(self):
        row = self.actual_python('import os,signal,time; os.kill(os.getppid(),signal.SIGTERM); time.sleep(20)')
        self.assertEqual(row['wrapper_received_signal'], signal.SIGTERM)
        self.assertEqual(row['returncode'], -signal.SIGKILL)
        self.assertFalse(self.support.process_passed(row))

    def test_launcher_sigint_kills_and_reaps_python(self):
        row = self.actual_python('import os,signal,time; os.kill(os.getppid(),signal.SIGINT); time.sleep(20)')
        self.assertEqual(row['wrapper_received_signal'], signal.SIGINT)
        self.assertEqual(row['returncode'], -signal.SIGKILL)

    def test_launcher_logging_exception_kills_and_reaps_python(self):
        real = self.support.atomic_json
        count = 0
        def fail_once(path, value):
            nonlocal count
            count += 1
            if count == 1:
                raise OSError('simulated evidence-write failure after admission')
            return real(path, value)
        with patch.object(self.support, 'atomic_json', fail_once):
            row = self.actual_python('import time; time.sleep(20)')
        self.assertEqual(row['status'], 'wrapper_exception')
        self.assertEqual(row['returncode'], -signal.SIGKILL)
        self.assertIn('evidence-write failure', row['exception'])

    def test_launcher_spawn_failure_is_not_native_success(self):
        row = self.support.run_child(['/path/to/nonexistent-executable'], self.out, os.environ.copy(), self.root, 2, 'spawn-failure')
        self.assertEqual(row['status'], 'wrapper_exception')
        self.assertFalse(row['native_exit_observed'])
        self.assertIsNone(row['returncode'])
        self.assertFalse(self.support.process_passed(row))

    def test_launcher_pending_admission_signal_still_reaps(self):
        real = self.support.subprocess.Popen
        def spawn_then_signal(*args, **kwargs):
            child = real(*args, **kwargs)
            os.kill(os.getpid(), signal.SIGTERM)  # blocked until PID is owned
            return child
        with patch.object(self.support.subprocess, 'Popen', spawn_then_signal):
            row = self.actual_python('import time; time.sleep(20)')
        self.assertEqual(row['wrapper_received_signal'], signal.SIGTERM)
        self.assertEqual(row['returncode'], -signal.SIGKILL)

    def test_launcher_keyboard_interrupt_still_reaps(self):
        real = self.support.atomic_json
        count = 0
        def interrupt_once(path, value):
            nonlocal count
            count += 1
            if count == 1:
                raise KeyboardInterrupt('simulated wrapper interruption')
            return real(path, value)
        with patch.object(self.support, 'atomic_json', interrupt_once):
            row = self.actual_python('import time; time.sleep(20)')
        self.assertEqual(row['status'], 'wrapper_exception')
        self.assertEqual(row['returncode'], -signal.SIGKILL)


def main():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(WrapperTests)
    names = [case.id() for case in suite]
    stream = io.StringIO()
    began = time.monotonic()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    print(stream.getvalue(), file=sys.stderr)
    report = {'version': 'orbit61-continuous-v6-python-wrapper-tests', 'passed': result.wasSuccessful(),
              'test_names': names, 'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
              'wall_seconds': time.monotonic() - began, 'isolated_copies': True,
              'godot_invoked': False, 'gdscript_parse_passed': False,
              'native_fixture_passed': False, 'world_run_passed': False,
              'scope': 'Python wrapper failure/acceptance logic with mock native payloads; actual Python child timeout, signal and exception reaping only.',
              'tested_source_sha256': {str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in [HERE.parent / 'run_orbit61.py', HERE / 'run_fixture.py',
                                                HERE / 'wrapper_support.py', HERE / 'fixture.gd', Path(__file__)]}}
    print(json.dumps(report, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
