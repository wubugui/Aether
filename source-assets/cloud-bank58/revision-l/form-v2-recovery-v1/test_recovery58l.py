"""Pure bounded tests. No Blender, real stage admission, model write or render."""
import contextlib, copy, errno, io, json, os, signal, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import recovery58l as r
import run_saved58l as runner
import verify_saved58l as verifier


class RecoveryTests(unittest.TestCase):
    def test_runtime(self):
        self.assertEqual(r.runtime()['python_sha256'], r.PYTHON_SHA)

    def test_original_saved_predecessor(self):
        self.assertEqual(r.saved_predecessor()['original_source_stage'], 'failed')

    def test_noop_no_supervision(self):
        with patch.object(r.deadline, 'supervise', side_effect=AssertionError('No engine')):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(runner.main([]), 0)
                self.assertEqual(verifier.main([]), 0)

    def test_build_source_views_refused(self):
        with patch.object(r.deadline, 'supervise', side_effect=AssertionError('No supervisor')):
            for mode in ('build', 'source', 'views', 'render'):
                with self.assertRaises(ValueError): r.require_new_admission(mode)
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    runner.main(['--run-approved', mode])
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    verifier.main(['--mode', mode])

    def test_missing_source_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'Existing saved source'): r.require_source(Path(tmp) / 'absent.blend')

    def test_changed_source_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'non_native_fixture'; p.write_bytes(bytes(r.SOURCE_BYTES))
            with self.assertRaisesRegex(ValueError, 'SHA/size'): r.require_source(p)

    def test_symlink_source_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'link'; p.symlink_to(r.g.SOURCE)
            with self.assertRaises(ValueError): r.require_source(p)

    def test_duplicate_admission_refused(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(r, 'HERE', Path(tmp)):
            (Path(tmp) / (r.STAGE + '-attempt.json')).write_text('test-only non-native fixture')
            with self.assertRaisesRegex(ValueError, 'already attempted'): r.require_new_admission(r.STAGE)

    def test_wrong_predecessor_not_relabelled_success(self):
        read = r.read
        def altered(p):
            d = read(p)
            if Path(p) == r.FORM / 'source-terminal.json': d = dict(d, state='completed', passed=True)
            return d
        with patch.object(r, 'read', side_effect=altered), self.assertRaisesRegex(ValueError, 'failure'):
            r.saved_predecessor(check_pins=False)

    def test_failed_build_refused(self):
        read = r.read
        def altered(p):
            d = read(p)
            if Path(p) == r.OLD_RUN / 'outputs/build-result.json': d = dict(d, passed=False, source_saved=False)
            return d
        with patch.object(r, 'read', side_effect=altered), self.assertRaisesRegex(ValueError, 'single-save'):
            r.saved_predecessor(check_pins=False)

    def test_old_complete_source_still_rejected(self):
        with self.assertRaises(ValueError): r.original.prior_source(r.g)

    def test_original_functions_directly_reused(self):
        self.assertEqual(Path(r.native.__file__).resolve(), r.FORM / 'native58l.py')
        self.assertEqual(Path(r.g.__file__).resolve(), r.FORM / 'geometry58l.py')
        self.assertEqual(Path(r.original.__file__).resolve(), r.FORM / 'run58l_form_v2.py')
        self.assertEqual(len(r.s.expected_texts(r.g.HERE, r.read(r.g.CANDIDATE_PATH), r.read(r.g.BINDING_PATH))), 8)

    def test_no_save_or_build_calls_in_adapter(self):
        import ast
        tree = ast.parse((r.HERE / 'verify_saved58l.py').read_text())
        calls = [n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
        self.assertIn('exercise', calls)
        for forbidden in ('create_source', 'save_as_mainfile', 'save_mainfile', 'render', 'export'):
            self.assertNotIn(forbidden, calls)

    def test_saved_source_never_excluded(self):
        self.assertNotIn(r.g.SOURCE, r.exclusions())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / 'existing.blend'; source.write_bytes(b'non-native fixture')
            before = r.original.protected_manifest(root=root, new_outputs=r.exclusions())
            self.assertEqual(before[str(source)], r.sha(source))
            source.write_bytes(b'changed fixture')
            self.assertNotEqual(before, r.original.protected_manifest(root=root, new_outputs=r.exclusions()))

    def test_exact_native_command_only_verify(self):
        command = r.native_command(Path('/tmp/outputs'), r.ATTEMPT)
        self.assertEqual(command[command.index('--mode') + 1], 'verify')
        self.assertIn(str(r.HERE / 'verify_saved58l.py'), command)
        self.assertNotIn(str(r.FORM / 'native58l.py'), command)

    def test_bridge_real_fd_closed(self):
        r.install_pidfd_bridge()
        count = len(list(Path('/proc/self/fd').iterdir()))
        fd = r.deadline.os.pidfd_open(os.getpid())
        try:
            self.assertFalse(os.get_inheritable(fd))
            signal.pidfd_send_signal(fd, 0)
        finally: os.close(fd)
        self.assertEqual(count, len(list(Path('/proc/self/fd').iterdir())))
        with self.assertRaises(OSError) as caught: os.fstat(fd)
        self.assertEqual(caught.exception.errno, errno.EBADF)

    def test_bridge_errno_failure_no_fd_leak(self):
        r.install_pidfd_bridge()
        count = len(list(Path('/proc/self/fd').iterdir()))
        with self.assertRaises(OSError) as caught: r.deadline.os.pidfd_open(2147483647)
        self.assertEqual(caught.exception.errno, errno.ESRCH)
        self.assertEqual(count, len(list(Path('/proc/self/fd').iterdir())))
        with self.assertRaises(ValueError): r.deadline.os.pidfd_open(os.getpid(), 1)

    def test_bridge_missing_symbol_stops(self):
        class Missing: pass
        with patch.object(r.deadline, 'os', os), patch.object(r.ctypes, 'CDLL', return_value=Missing()):
            with self.assertRaises(AttributeError): r.install_pidfd_bridge()
        self.assertFalse(hasattr(os, 'pidfd_open'))


if __name__ == '__main__':
    r.install_pidfd_bridge()
    sys.path.insert(0, str(r.HERE.parent / 'source-runner-v3'))
    import test_runner58l_v3 as prior
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RecoveryTests)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(prior.IdentityTests))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
