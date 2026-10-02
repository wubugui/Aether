"""Small pure-Python adapter negatives only. No engine, child process or geometry replay."""
import ast, contextlib, copy, io, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import views58l as v
import render_saved58l as native_adapter
import run_views58l as runner

class Views(unittest.TestCase):
    def test_official_runtime_and_original_imports(self):
        self.assertEqual(v.runtime()['python_sha256'],v.PYTHON_SHA)
        self.assertEqual(Path(v.native.__file__).resolve(),v.FORM/"native58l.py")
        self.assertEqual(Path(v.g.__file__).resolve(),v.FORM/"geometry58l.py")
        self.assertEqual(Path(v.s.__file__).resolve(),v.FORM/"native_support58l.py")
        self.assertIs(v.runtime,v.form_runtime.runtime)
        self.assertEqual(Path(v.original.__file__).resolve(),v.FORM/"run58l_form_v3.py")
        self.assertIs(v.deadline,v.original.deadline58l_v3)
        self.assertIs(v.install_pidfd_bridge,v.form_runtime.install_pidfd_bridge)
    def test_noop_without_engine(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(native_adapter.main([]),0)
            self.assertEqual(runner.main([]),0)
    def test_native_forbids_build_save_verify_export(self):
        for mode in ('build','save','verify','source','export'):
            with self.subTest(mode=mode),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
                native_adapter.main(['--mode',mode])
    def test_wrapper_forbids_nonviews(self):
        for stage in ('build','source','save','verify','export','saved-source-fresh-open'):
            with self.subTest(stage=stage),self.assertRaises(Exception): v.require_new_admission(stage)
    def test_missing_or_wrong_source_no_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'wrong.blend'
            with self.assertRaises(Exception):v.require_source(p)
            p.write_bytes(b'not the source')
            with self.assertRaises(Exception):v.require_source(p)
    def test_duplicate_new_admission_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            h=Path(tmp)
            for suffix in ('attempt','terminal','launch-observation','launch-validation'):
                p=h/('views-'+suffix+'.json');p.write_text('{}')
                with patch.object(v,'HERE',h),self.assertRaises(Exception):v.require_new_admission('views')
                p.unlink()
    def test_actual_form_v3_required_and_fake_old_success_refused(self):
        expected=v.predecessor()
        with tempfile.TemporaryDirectory() as tmp,patch.object(v,'HERE',Path(tmp)/'isolated'),patch.object(v,'verify_pins',return_value={}),patch.object(v,'require_source',return_value=v.SOURCE_SHA),patch.object(v,'predecessor',return_value=expected):
            with patch.object(v,'completed_source',return_value=expected) as actual:
                self.assertEqual(v.require_new_admission('views'),expected);actual.assert_called_once_with()
            fake=copy.deepcopy(expected);fake['original_source_stage']='completed'
            with patch.object(v,'completed_source',return_value=fake),self.assertRaises(Exception):v.require_new_admission('views')
            with patch.object(v,'completed_source',side_effect=RuntimeError('Old source cannot be accepted')),self.assertRaises(Exception):v.require_new_admission('views')
    def test_scope_rejects_fake_acceptance(self):
        row=dict(original_source_stage='failed',acceptance_mode=v.s.DIAGNOSTIC_MODE,full_native_acceptance=False,historical_form_v2_default_failure=v.s.HISTORICAL_FORM_V2_DEFAULT_FAILURE,
                 world_loaded=False,world_integration_allowed=False,contact_acceptance=False,world_acceptance=False,
                 global_GOAL=False,visual_acceptance=False,weather_acceptance=False)
        v.require_scope(row)
        for key in row:
            fake=dict(row);fake[key]='completed' if key=='original_source_stage' else ('full' if key=='acceptance_mode' else True)
            with self.subTest(key=key),self.assertRaises(Exception):v.require_scope(fake)
    def test_exact_original_four_camera_bindings(self):
        binding=v.read(v.HERE/'RENDER_BINDINGS.json');old=v.read(v.g.BINDING_PATH)
        self.assertEqual(binding['world_cameras'],old['world_cameras'])
        self.assertEqual(tuple(r['name'] for r in old['world_cameras']),v.VIEWS)
        self.assertEqual(old['world_cameras'][0]['camera_transform'],old['world_cameras'][1]['camera_transform'])
        self.assertEqual(len({r['camera_transform'] for r in old['world_cameras']}),3)
        self.assertEqual(binding['original_settings']['resolution'],[1179,664])
        self.assertEqual(binding['original_settings']['pixel_aspect'],[1.0006932020187378,1.0])
        self.assertEqual(binding['original_settings']['samples'],8)
        self.assertFalse(binding['original_settings']['denoising'])
        for view in v.VIEWS:
            command=v.native_command(Path('/tmp/new-output'),v.ATTEMPT,view)
            self.assertEqual(command[-2:],['--view',view]);self.assertIn('render',command);self.assertNotIn('build',command)
        with self.assertRaises(Exception):v.native_command(Path('/tmp/new-output'),v.ATTEMPT,'wrong-original-camera')
    def test_wrong_old_image_and_sha_refused(self):
        # Lightweight fake bytes: exercise binding rejection while bypassing only
        # already tested original CRC/parser here; actual execution calls it intact.
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);p=out/(v.VIEWS[0]+'.png');p.write_bytes(b'fixture')
            image=dict(sha256=v.sha(p),bytes=7,width=1179,height=664,crc_and_scanlines_validated=True)
            good=dict(image_path=str(p),image_sha256=v.sha(p))
            with patch.object(v.original,'png_info',return_value=image):
                self.assertEqual(v.validate_image(out,v.VIEWS[0],good),image)
                for bad in (dict(good,image_path='/old-run/01-original61-front.png'),dict(good,image_sha256='0'*64)):
                    with self.assertRaises(Exception):v.validate_image(out,v.VIEWS[0],bad)
    def test_source_always_protected(self):
        self.assertEqual(v.exclusions(),{v.TERMINAL,v.TERMINAL.with_suffix('.json.tmp')})
        self.assertNotIn(v.g.SOURCE,v.exclusions())
    def test_render_restore_ast_exact_original(self):
        old=ast.parse((v.FORM/'native58l.py').read_text())
        main=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        branch=next(n for n in ast.walk(main) if isinstance(n,ast.If) and ast.unparse(n.test)=="a.mode == 'render'")
        new=ast.parse((v.HERE/'render_saved58l.py').read_text())
        nm=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        tr=next(n for n in nm.body if isinstance(n,ast.Try))
        body=tr.body;start=next(i for i,n in enumerate(body) if ast.dump(n,include_attributes=False)==ast.dump(branch.body[0],include_attributes=False))
        self.assertEqual([ast.dump(n,include_attributes=False) for n in body[start:start+len(branch.body)]],
                         [ast.dump(n,include_attributes=False) for n in branch.body])
        calls=[ast.unparse(n.func) for n in ast.walk(new) if isinstance(n,ast.Call)]
        self.assertEqual([x for x in calls if x.startswith('bpy.ops.')],['bpy.ops.wm.open_mainfile','bpy.ops.render.render'])
        self.assertFalse(any(x.endswith(('create_source','rebuild_from_controls','exercise','save_as_mainfile','export')) for x in calls))
    def test_embedded_text_identity_and_prior_failure(self):
        b=v.read(v.HERE/'RENDER_BINDINGS.json')
        old=v.read(v.SOURCE_RUN/'outputs/build-raw.json')
        self.assertEqual(b['source_texts'],old['texts']);self.assertEqual(len(old['texts']),8)
        self.assertEqual(v.read(v.FORM/'source-terminal.json')['state'],'awaiting_external_process_terminal')
        self.assertEqual(v.source_binding(v.read(v.FORM/'source-terminal.json')),v.predecessor())
        self.assertTrue(v.predecessor()['source_chain_verified'])
        self.assertEqual(v.predecessor()['original_source_stage_refers_to'],'form-v2')
        old_form=v.FORM.parent/'form-v2'
        self.assertEqual(v.read(old_form/'source-terminal.json')['state'],'failed')
        self.assertEqual(v.sha(old_form/'source-terminal.json'),'c4856a8ffeaf5b28280beab2316f32e5b02f52720fcfed39a546d3ab9b7e7531')
        self.assertFalse(b['current_default_normals']['original_corner_geometry_passed'])
        self.assertEqual(len(b['current_default_normals']['original_corner_geometry_faces_over_limit']),24)
        self.assertEqual(v.require_source(),v.SOURCE_SHA)

if __name__=='__main__':unittest.main(verbosity=2)
