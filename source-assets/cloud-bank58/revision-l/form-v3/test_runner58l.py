"""Pure source-only adaptation tests; never engine, stage admission, save or render."""
import ast, contextlib, copy, io, json, os, runpy, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import diagnostic58l as diagnostic
import geometry58l as g
import native58l as native
import native_support58l as s
import run58l_form_v3 as runner
import runtime58l as runtime
HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'form-v2'

def functions(path):
    source = path.read_text()
    return {n.name: ast.get_source_segment(source,n) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}

class RunnerTests(unittest.TestCase):
    def test_exact_official_runtime(self):
        self.assertEqual(runtime.runtime()['python_sha256'], runtime.PYTHON_SHA)

    def test_foreign_runtime_rejected(self):
        with patch.object(sys,'version','3.12.foreign'), self.assertRaisesRegex(ValueError,'3.11.15'):
            runtime.runtime()

    def test_all_support_math_and_api_functions_unchanged(self):
        self.assertEqual(functions(HERE/'native_support58l.py'),functions(OLD/'native_support58l.py'))

    def test_native_controls_capture_build_exercise_unchanged(self):
        a,b=functions(HERE/'native58l.py'),functions(OLD/'native58l.py')
        self.assertEqual({k:v for k,v in a.items() if k!='main'},{k:v for k,v in b.items() if k!='main'})

    def test_core_geometry_functions_unchanged(self):
        a,b=functions(HERE/'geometry58l.py'),functions(OLD/'geometry58l.py')
        for key in ('spatial_gate','planar_certificate','evaluate','validate_evaluated','validate_native_raw'):
            self.assertEqual(a[key],b[key],key)

    def test_full_exercise_and_protection_helpers_unchanged(self):
        a,b=functions(HERE/'run58l_form_v3.py'),functions(OLD/'run58l_form_v2.py')
        for key in ('validate_exercise','protected_manifest','output_exclusions','expected_state','require_state','png_info','native_command'):
            self.assertEqual(a[key],b[key],key)

    def test_inert_noop(self):
        with patch.object(runner.deadline58l_v3,'supervise',side_effect=AssertionError('No engine')):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(runner.main([]),0);self.assertEqual(native.main([]),0)
        self.assertNotIn('bpy',sys.modules)

    def test_observer_noop_does_not_start_process(self):
        with patch.object(sys,'argv',['observe_form58l.py']), patch('subprocess.Popen',side_effect=AssertionError('No Popen')):
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as cm:
                runpy.run_path(str(HERE/'observe_form58l.py'),run_name='__main__')
            self.assertEqual(cm.exception.code,0)

    def test_views_refused_all_executable_layers(self):
        with self.assertRaisesRegex(ValueError,'Source-only'): diagnostic.require_new_admission('views',g.SOURCE)
        with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit): runner.main(['--run-approved','views'])
        with self.assertRaisesRegex(ValueError,'Source-only'): native.main(['--mode','render'])
        with patch.object(sys,'argv',['observe_form58l.py','--run-approved','views']),self.assertRaisesRegex(RuntimeError,'source-only'):
            runpy.run_path(str(HERE/'observe_form58l.py'),run_name='__main__')

    def test_new_unique_source_identity(self):
        self.assertEqual(g.VERSION,runner.VERSION)
        self.assertEqual(g.SOURCE,HERE/'cloud_bank58l_form_v3.blend')
        self.assertFalse(g.SOURCE.exists())
        with self.assertRaisesRegex(ValueError,'Unique'): diagnostic.require_new_admission('source',OLD/'cloud_bank58l_form_v2.blend')

    def test_duplicate_admission_rejected_before_other_work(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(diagnostic,'HERE',Path(temp)):
            source=Path(temp)/'cloud_bank58l_form_v3.blend'
            (Path(temp)/'source-attempt.json').write_text('pure non-native fixture')
            with self.assertRaisesRegex(ValueError,'already attempted'): diagnostic.require_new_admission('source',source)

    def test_no_overwrite_even_without_admission(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(diagnostic,'HERE',Path(temp)):
            source=Path(temp)/'cloud_bank58l_form_v3.blend';source.write_bytes(b'pure non-native fixture')
            with self.assertRaisesRegex(ValueError,'Never overwrite'): diagnostic.require_new_admission('source',source)

    def test_legacy_imports_restore_live_form_v3_modules(self):
        before=sys.path[:];names={name:sys.modules.get(name) for name in runtime._NAMES}
        with runtime.legacy() as (r,v):
            self.assertEqual(Path(r.g.__file__),OLD/'geometry58l.py')
            self.assertIsNot(r.g,g);self.assertIsNot(r.s,s)
            self.assertIs(r.deadline,runner.deadline58l_v3)
        self.assertEqual(sys.path,before)
        for name,module in names.items(): self.assertIs(sys.modules.get(name),module)

    def test_old_whole_source_still_rejected(self):
        with runtime.legacy() as (r,v), self.assertRaises(ValueError): r.original.prior_source(r.g)

    def test_all_three_failed_source_admissions_bound(self):
        self.assertEqual(diagnostic.original_failures(),list(s.FAILURE_ADMISSIONS))
        self.assertEqual(len(s.FAILURE_ADMISSIONS),3)

    def test_form_v2_actual_23_face_failure_preserved(self):
        raw=json.loads((g.ROOT/'cloud-evidence/cloudbank58l-form-v2-source-20261002T203132Z-gplbz9_7/outputs/build-raw.json').read_text())
        report=s.validate_normals(raw['mesh']);h=s.HISTORICAL_FORM_V2_DEFAULT_FAILURE
        self.assertFalse(report['original_corner_geometry_passed'])
        self.assertEqual(len(report['original_corner_geometry_faces_over_limit']),h['faces_over_3e_5'])
        self.assertEqual(report['original_corner_geometry_max_abs'],h['max_abs'])
        self.assertEqual(report['original_corner_geometry_max_angle_degrees'],h['max_angle_degrees'])
        self.assertFalse(report['full_native_acceptance'])
        self.assertEqual(s.HISTORICAL_DEFAULT_FAILURE['faces_over_3e_5'],22)

    def test_runtime_bridge_is_direct_original_reuse(self):
        code=(HERE/'runtime58l.py').read_text()
        self.assertIn('recovery.install_pidfd_bridge()',code)
        self.assertNotIn('ctypes',code);self.assertNotIn('syscall',code)
        self.assertEqual(runner.CAPS,{'build':80,'verify':30,'render':27})
        self.assertEqual(runner.TOTAL,{'source':120,'views':120})
        self.assertEqual(runner.support.MAX_RSS_KIB,1572864)
        self.assertIn("left=limit-(time.monotonic()-started)-20",functions(HERE/'run58l_form_v3.py')['phase'])

    def test_observer_retains_actual_popen_wait_and_owned_cleanup(self):
        text=(HERE/'observe_form58l.py').read_text()
        for token in ('subprocess.Popen(command','p.wait(timeout=','owned.pin(p.pid','signal.pidfd_send_signal','os.wait4','remaining_owned_pids','supervisor_terminal_sha256'):
            self.assertIn(token,text)
        self.assertIn("[str(r.PYTHON),'-B',str(HERE/'run58l_form_v3.py')",text)

    def test_old_source_never_excluded(self):
        excluded=runner.output_exclusions('source',g.SOURCE)
        self.assertEqual(excluded,{g.SOURCE,HERE/'source-terminal.json',HERE/'source-terminal.json.tmp'})
        self.assertNotIn(OLD/'cloud_bank58l_form_v2.blend',excluded)

    def test_current_eight_embedded_texts(self):
        c,b=g.read(g.CANDIDATE_PATH),g.read(g.BINDING_PATH)
        values=s.expected_texts(HERE,c,b)
        self.assertEqual(len(values),8)
        self.assertIn(b'/form-v3/geometry58l.py',values['EDIT58L.py'])
        self.assertIn(b'23 faces',values['README58L.txt'])
        self.assertEqual(values['GEOMETRY58L.py'],(HERE/'geometry58l.py').read_bytes())
        self.assertEqual(values['NATIVE58L.py'],(HERE/'native58l.py').read_bytes())

if __name__=='__main__': unittest.main(verbosity=2)
