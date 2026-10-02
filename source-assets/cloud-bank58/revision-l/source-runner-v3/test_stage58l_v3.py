"""Source-chain fixtures only: real /tmp bytes and SHA, NEVER a native launch.

The small synthetic raw records test source evidence association, not Blender,
geometry, editability or source acceptance. The original complete validators
remain covered separately by the preserved source-runner-v2 regressions.
"""
from __future__ import annotations
import copy
import io
import json
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import run58l_v3 as r


def encoded(value):
    return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()


class SourceChainTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        temporary = self.stack.enter_context(tempfile.TemporaryDirectory(prefix='source58l-v3-chain-', dir='/tmp'))
        self.root = Path(temporary)
        self.here = self.root/'source-assets/cloud-bank58/revision-l/source-runner-v3'
        self.original = self.here.parent/'source-v1'
        self.run = self.root/'cloud-evidence'/(r.VERSION+'-source-fixture')
        self.out = self.run/'outputs'
        for directory in (self.here, self.original, self.out):
            directory.mkdir(parents=True)
        for name, value in [('HERE', self.here), ('ROOT', self.root), ('ORIGINAL', self.original)]:
            self.stack.enter_context(patch.object(r, name, value))
        self.stack.enter_context(patch.object(r.support, 'run_child', side_effect=AssertionError('No native/engine launch in stage fixtures')))
        self.stack.enter_context(patch.object(r.deadline58l_v3, 'supervise', side_effect=AssertionError('No actual phase admission in stage fixtures')))
        self.g = SimpleNamespace(SOURCE=self.original/'cloud_bank58l.blend', BLENDER=self.root/'official-blender-not-created', CANDIDATE_PATH=self.original/'candidate.json', BINDING_PATH=self.original/'bindings.json', VERSION='explicit-non-native-fixture')
        self.admission_path = self.here/'source-attempt.json'
        self.terminal_path = self.here/'source-terminal.json'
        self.wrapper_path = self.run/'wrapper-report.json'
        self.receipt_path = self.run/'supervisor-terminal.json'
        self.observation_path = self.here/'source-launch-observation.json'
        self.g.SOURCE.write_bytes(b'Explicit non-native fixture, not a Blender file.\n')
        (self.here/'run58l_v3.py').write_bytes(b'Explicit non-executable fixture runner bytes\n')
        (self.original/'native58l.py').write_bytes(b'Explicit non-executable fixture native bytes\n')
        self.g.CANDIDATE_PATH.write_bytes(encoded({'controls': [{'id': str(i)} for i in range(7)]}))
        self.g.BINDING_PATH.write_bytes(encoded({}))
        sha = r.support.sha
        source_sha = sha(self.g.SOURCE)
        source_size = self.g.SOURCE.stat().st_size
        common = dict(stage='source', run=str(self.run), source=str(self.g.SOURCE), runner_version=r.VERSION, runner_sha256=sha(self.here/'run58l_v3.py'))
        self.admission = dict(common, state='admitted_one_shot_not_complete', wrapper_pid=102, supervisor_pid=101, output=str(self.out), native_sha256=sha(self.original/'native58l.py'), candidate_sha256=sha(self.g.CANDIDATE_PATH), binding_sha256=sha(self.g.BINDING_PATH))
        self.prior = dict(common, version=self.g.VERSION, worker_pid=102, supervisor_pid=101, passed=False, prepared_passed=True, state='awaiting_external_process_terminal', intended_worker_exit_code=0, completion_authority=str(self.receipt_path), source_sha256=source_sha, source_bytes=source_size, limits=dict(total_wall_seconds=120, cpu_threads=2, native_caps=r.CAPS, max_wrapper_plus_child_rss_kib=r.support.MAX_RSS_KIB), changed_inputs=[], input_errors=[], images=[], stages=[], exercise=[])
        for key in ('frozen_inputs_unchanged', 'protected_originals_unchanged', 'earlier_outputs_unchanged', 'saved_source_unchanged', 'source_diagnostic_only'):
            self.prior[key] = True
        for key in ('world_loaded', 'world_modified', 'world_integration_allowed', 'contact_acceptance', 'world_acceptance', 'global_GOAL', 'visual_acceptance', 'weather_acceptance'):
            self.prior[key] = False
        self.receipt = dict(common, worker_pid=102, supervisor_pid=101, limit_seconds=120, state='completed', passed=True, worker_exit_observed=True, worker_returncode=0, worker_observed_wall_seconds=1., receipt_ready_wall_seconds=1.1, timeout_triggered=False, rss_limit_triggered=False, all_owned_children_reaped=True, ownership_observable=True, cpu_affinity=[0, 1], source_sha256=source_sha, source_bytes=source_size)
        self.observation = dict(actual_exit_code=0, process_exit_observed=True, wall_seconds=1.2, supervisor_pid=101)
        self.records = {self.admission_path: self.admission, self.terminal_path: self.prior, self.receipt_path: self.receipt, self.observation_path: self.observation}
        for index, mode in enumerate(('build', 'verify')):
            pid = 103 + index
            raw_path = self.out/(mode+'-raw.json')
            raw = dict(version=self.g.VERSION, pid=pid, cpu_affinity=[0, 1], opened_filepath='' if mode=='build' else str(self.g.SOURCE), identity_data='Synthetic association fixture, not actual RNA')
            process = dict(status='finished', native_exit_observed=True, returncode=0, wrapper_received_signal=None, timeout_triggered=False, rss_limit_triggered=False, command=r.native_command(self.g, mode, self.out, self.admission_path), cpu_affinity=[0, 1], pid=pid, wall_timeout_seconds=r.CAPS[mode], wall_seconds=.5, wall_timeout_limit_seconds=720)
            native = dict(passed=True, state='completed', version=self.g.VERSION, mode=mode, view=None, pid=pid, raw_path=str(raw_path), source_sha256=source_sha, source_bytes=source_size, source_saved=mode=='build', images=0, controls_exercised=7, secondary_exercised=0, manual_edit_exercised=True, exact_identity_restored=True)
            for key in ('world_loaded', 'world_integration_allowed', 'contact_acceptance', 'world_acceptance', 'global_GOAL', 'visual_acceptance', 'weather_acceptance'):
                native[key] = False
            self.records[raw_path] = raw
            self.records[self.out/(mode+'-result.json')] = native
            self.records[self.run/(mode+'.process.json')] = process
            (self.out/(mode+'-exercise.json')).write_bytes(encoded([]))
            (self.run/(mode+'.stdout.log')).write_bytes(b'')
            (self.run/(mode+'.stderr.log')).write_bytes(b'')
            self.prior['stages'].append(process)
            self.prior['exercise'].append(dict(controls=7, secondary_parameters=0, manual_edit_preserved=True, exact_identity_restored=True))
        self.seal()

    def seal(self):
        """Write real fixture bytes, then bind unchanged real SHA dependencies."""
        for path, row in self.records.items():
            path.write_bytes(encoded(row))
        for mode in ('build', 'verify'):
            path = self.out/(mode+'-result.json')
            native = self.records[path]
            native['raw_sha256'] = r.support.sha(self.out/(mode+'-raw.json'))
            native['exercise_sha256'] = r.support.sha(self.out/(mode+'-exercise.json'))
            path.write_bytes(encoded(native))
        admission_sha = r.support.sha(self.admission_path)
        self.prior['admission_sha256'] = self.receipt['admission_sha256'] = admission_sha
        self.prior['source_output_sha256'] = {str(path): r.support.sha(path) for path in self.out.rglob('*') if path.is_file()}
        self.terminal_path.write_bytes(encoded(self.prior))
        self.wrapper_path.write_bytes(self.terminal_path.read_bytes())
        self.receipt['terminal_sha256'] = r.support.sha(self.terminal_path)
        self.receipt['wrapper_report_sha256'] = r.support.sha(self.wrapper_path)
        self.receipt_path.write_bytes(encoded(self.receipt))
        self.observation['supervisor_terminal_sha256'] = r.support.sha(self.receipt_path)
        self.observation_path.write_bytes(encoded(self.observation))

    def rejected(self, mutation, *, reseal=True):
        mutation(self)
        if reseal:
            self.seal()
        with self.assertRaises((ValueError, KeyError)):
            r.prior_source(self.g)

    def test_complete_source_chain_positive(self):
        self.assertEqual(r.prior_source(self.g), self.prior)
        self.assertEqual(self.terminal_path.read_bytes(), self.wrapper_path.read_bytes())

    def test_default_noop(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(r.main([]), 0)

    def test_raw_or_process_hash_is_not_mocked(self):
        self.rejected(lambda case: (case.out/'build-raw.json').write_bytes(b'{"changed": true}\n'), reseal=False)

    def test_wrapper_same_content_different_bytes_rejected(self):
        self.rejected(lambda case: case.wrapper_path.write_bytes(case.wrapper_path.read_bytes()+b' '), reseal=False)

    def test_wrapper_different_content_rejected(self):
        self.rejected(lambda case: case.wrapper_path.write_bytes(encoded(dict(case.prior, stage='views'))), reseal=False)

    def test_changed_admission_hash_rejected(self):
        self.rejected(lambda case: case.admission_path.write_bytes(case.admission_path.read_bytes()+b' '), reseal=False)

    def test_changed_source_bytes_rejected(self):
        self.rejected(lambda case: case.g.SOURCE.write_bytes(b'Different explicit non-native fixture\n'), reseal=False)

    def test_receipt_hash_mismatch_rejected(self):
        self.rejected(lambda case: case.receipt_path.write_bytes(case.receipt_path.read_bytes()+b' '), reseal=False)

    def test_missing_native_process_record_rejected(self):
        self.rejected(lambda case: (case.run/'verify.process.json').unlink(), reseal=False)

    def test_process_record_different_from_actual_stage_row_rejected(self):
        self.rejected(lambda case: (case.run/'verify.process.json').write_bytes(encoded(dict(case.prior['stages'][1], pid=999))), reseal=False)

    def test_duplicate_native_pids_rejected(self):
        def mutate(case):
            for path in (case.run/'verify.process.json', case.out/'verify-result.json', case.out/'verify-raw.json'):
                case.records[path]['pid'] = 103
        self.rejected(mutate)

    def test_raw_source_identity_mismatch_rejected(self):
        self.rejected(lambda case: case.records[case.out/'verify-raw.json'].__setitem__('identity_data', 'Changed identity'))

    def test_symlink_source_chain_rejected(self):
        def mutate(case):
            content = case.wrapper_path.read_bytes()
            case.wrapper_path.unlink()
            other = case.run/'other-report.json'
            other.write_bytes(content)
            case.wrapper_path.symlink_to(other)
        self.rejected(mutate, reseal=False)

    def test_symlink_native_output_rejected(self):
        def mutate(case):
            target = case.out/'build-exercise.json'
            (case.out/'alias.json').symlink_to(target)
        self.rejected(mutate, reseal=False)


# Each negative is a separately named unittest rather than an unreported loop.
def install_record_negative(name, target, field, value):
    def test(self):
        self.rejected(lambda case: getattr(case, target).__setitem__(field, copy.deepcopy(value)))
    test.__name__ = 'test_'+name
    setattr(SourceChainTests, test.__name__, test)


for target in ('admission', 'prior', 'receipt'):
    for field, value in [('stage', 'views'), ('run', '/wrong/run'), ('source', '/wrong/source'), ('runner_version', 'wrong-version'), ('runner_sha256', 'wrong-sha'), ('supervisor_pid', 999)]:
        install_record_negative(target+'_'+field+'_mismatch_rejected', target, field, value)
for target in ('prior', 'receipt'):
    for field, value in [('source_bytes', 999), ('source_sha256', 'wrong-sha'), ('worker_pid', 999)]:
        install_record_negative(target+'_'+field+'_mismatch_rejected', target, field, value)
for label, field, value in [('nonzero', 'actual_exit_code', 1), ('unobserved', 'process_exit_observed', False), ('late', 'wall_seconds', 120), ('boolean_wall', 'wall_seconds', True), ('wrong_pid', 'supervisor_pid', 999)]:
    install_record_negative('external_'+label+'_rejected', 'observation', field, value)
install_record_negative('expanded_receipt_limit_rejected', 'receipt', 'limit_seconds', 121)
install_record_negative('unobserved_ownership_rejected', 'receipt', 'ownership_observable', False)
install_record_negative('changed_source_flag_rejected', 'prior', 'saved_source_unchanged', False)


def install_native_negative(name, relative, field, value):
    def test(self):
        self.rejected(lambda case: case.records[case.run/relative].__setitem__(field, copy.deepcopy(value)))
    test.__name__ = 'test_'+name
    setattr(SourceChainTests, test.__name__, test)


for name, relative, field, value in [
    ('nonzero_build', 'build.process.json', 'returncode', 1),
    ('timeout_build', 'build.process.json', 'timeout_triggered', True),
    ('expanded_verify_cap', 'verify.process.json', 'wall_timeout_seconds', 31),
    ('verify_save', 'outputs/verify-result.json', 'source_saved', True),
    ('build_nosave', 'outputs/build-result.json', 'source_saved', False),
    ('verify_wrong_mode', 'outputs/verify-result.json', 'mode', 'build'),
    ('verify_wrong_raw_pid', 'outputs/verify-raw.json', 'pid', 999),
    ('verify_wrong_open_path', 'outputs/verify-raw.json', 'opened_filepath', ''),
    ('build_wrong_source_size', 'outputs/build-result.json', 'source_bytes', 999),
    ('build_render', 'outputs/build-result.json', 'images', 1),
    ('incomplete_exercises', 'outputs/build-result.json', 'controls_exercised', 6),
    ('native_scope', 'outputs/verify-result.json', 'world_loaded', True),
]:
    install_native_negative(name+'_rejected', relative, field, value)


def test_swapped_rows(self):
    self.rejected(lambda case: case.prior['stages'].reverse())
SourceChainTests.test_swapped_build_verify_rows_rejected = test_swapped_rows


def test_swapped_commands(self):
    def mutate(case):
        build = case.records[case.run/'build.process.json']
        verify = case.records[case.run/'verify.process.json']
        build['command'], verify['command'] = verify['command'], build['command']
    self.rejected(mutate)
SourceChainTests.test_swapped_actual_build_verify_commands_rejected = test_swapped_commands


def install_one_shot(stage, directory, filename):
    def test(self):
        # Remove only this test's fixture admissions before creating the one
        # historical record under test. Never remove real repository evidence.
        self.admission_path.unlink()
        self.terminal_path.unlink()
        location = self.original if directory=='source-v1' else self.here.parent/directory
        location.mkdir(exist_ok=True)
        path = location/(stage+'-'+filename+'.json')
        path.write_bytes(b'Explicit historical fixture evidence\n')
        with self.assertRaisesRegex(ValueError, 'One-shot stage already attempted'):
            r.main(['--run-approved', stage])
        self.assertEqual(path.read_bytes(), b'Explicit historical fixture evidence\n')
    test.__name__ = 'test_one_shot_'+stage+'_'+directory.replace('-', '_')+'_'+filename
    setattr(SourceChainTests, test.__name__, test)


for stage in ('source', 'views'):
    for directory in ('source-v1', 'source-runner-v2', 'source-runner-v3', 'source-runner-v987future'):
        for filename in ('attempt', 'terminal'):
            install_one_shot(stage, directory, filename)


def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(SourceChainTests)


if __name__=='__main__':
    outcome = unittest.TextTestRunner(verbosity=2).run(suite())
    raise SystemExit(not outcome.wasSuccessful())
