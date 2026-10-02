"""Focused pure normal/-O controls. No engine launch, source save or render."""
import ast,copy,hashlib,importlib.util,io,json,struct,sys,tempfile,unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import run58l_recovery as r
import recovery58l as recovery
import native_support58l as s
import native58l as n
import geometry58l as g
HERE=Path(__file__).resolve().parent
ORIGINAL=HERE.parent/'source-v1'
spec=importlib.util.spec_from_file_location('old_fixture',ORIGINAL/'test_native58l.py')
fixture_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture_module)

def fixture():
    c,b,raw,_=fixture_module.fixture()
    raw['settings']['pixel_aspect']=s.calibrated_pixel_aspect(b)
    for cam in raw['cameras']:cam['projection_sampling']=s.capture_projection_args(raw['settings'])
    expected=s.expected_texts(HERE,c,b)
    raw['texts']=[dict(name=k,sha256=s.digest(v),bytes=len(v),is_in_memory=True,filepath='',use_module=False) for k,v in sorted(expected.items())]
    return c,b,raw,expected

class Groups(list):
    def new(self,*,name):
        if any(x.name==name for x in self):name+='.001'
        group=SimpleNamespace(name=name,weights={})
        def add(indices,weight,mode):
            if mode!='REPLACE':raise ValueError(mode)
            group.weights.update({i:weight for i in indices})
        group.add=add;self.append(group);return group

def shared_objects():
    mesh=object();groups=Groups()
    return SimpleNamespace(data=mesh,vertex_groups=groups),SimpleNamespace(data=mesh,vertex_groups=groups)

class RecoveryTests(unittest.TestCase):
    def test_default_noop_and_no_engine_import(self):
        with redirect_stdout(io.StringIO()),patch.object(r.deadline58l_v3,'supervise',side_effect=AssertionError('No process allowed')):
            self.assertEqual(r.main([]),0);self.assertEqual(n.main([]),0)
        self.assertNotIn('bpy',sys.modules)
    def test_missing_admission_refused_before_engine(self):
        with self.assertRaisesRegex(ValueError,'admission'):n.main(['--mode','build'])
    def test_shared_groups_created_once_with_exact_sparse_weights(self):
        c,_,_,_=fixture();master,export=shared_objects();n.create_shared_groups(master,export,c)
        self.assertIs(master.vertex_groups,export.vertex_groups);self.assertEqual(len(master.vertex_groups),7)
        for actual,(name,weights) in zip(master.vertex_groups,s.groups(c)):
            self.assertEqual(actual.name,name);self.assertEqual(actual.weights,{i:s.f32(v) for i,v in enumerate(weights) if v})
    def test_duplicate_group_precondition_refused(self):
        c,_,_,_=fixture();master,export=shared_objects();master.vertex_groups.new(name='old')
        with self.assertRaisesRegex(ValueError,'pre-existing'):n.create_shared_groups(master,export,c)
        self.assertEqual(len(master.vertex_groups),1)
    def test_separate_mesh_refused(self):
        c,_,_,_=fixture();master,export=shared_objects();export.data=object()
        with self.assertRaisesRegex(ValueError,'shared mesh'):n.create_shared_groups(master,export,c)
    def test_old_loop_reproduces_fourteen_in_shared_table_mock(self):
        c,_,_,_=fixture();master,export=shared_objects()
        tree=ast.parse((ORIGINAL/'native58l.py').read_text());create=next(v for v in tree.body if isinstance(v,ast.FunctionDef) and v.name=='create_source')
        loop=next(v for v in create.body if isinstance(v,ast.For) and ast.unparse(v.iter)=='s.groups(c)')
        exec(compile(ast.Module(body=[loop],type_ignores=[]),'original-group-loop-only','exec'),dict(s=s,c=c,master=master,export=export))
        self.assertEqual(len(master.vertex_groups),14);self.assertEqual([x.weights for x in master.vertex_groups[1::2]],[{}]*7)
    def test_four_exact_projection_ratios_no_averaging(self):
        b=g.read(g.BINDING_PATH);self.assertEqual(len({r['camera_projection'] for r in b['world_cameras']}),1)
        self.assertEqual(s.calibrated_pixel_aspect(b),[1.0006932020187378,1.0])
        p=s.projection(b['world_cameras'][0]);a=s.calibrated_pixel_aspect(b)
        predicted=p[1][1]*664*a[1]/(1179*a[0]);self.assertLess(abs(predicted-p[0][0]),2e-5)
        self.assertGreater(abs(p[1][1]*664/1179-p[0][0]),2e-5)
    def test_mismatched_fourth_projection_refused_not_averaged(self):
        b=g.read(g.BINDING_PATH);q=bytearray.fromhex(b['world_cameras'][3]['camera_projection']);struct.pack_into('<f',q,4,.93);b['world_cameras'][3]['camera_projection']=q.hex()
        with self.assertRaisesRegex(ValueError,'no averaging'):s.calibrated_pixel_aspect(b)
    def test_actual_render_sampling_read_not_hardcoded(self):
        render=SimpleNamespace(resolution_x=1179,resolution_y=664,resolution_percentage=100,pixel_aspect_x=s.f32(1.0006931668767207),pixel_aspect_y=1.)
        self.assertEqual(s.render_projection_args(render),dict(x=1179,y=664,scale_x=1.0006932020187378,scale_y=1.))
        render.resolution_percentage=50;render.pixel_aspect_x=1.02
        self.assertEqual(s.render_projection_args(render),dict(x=589,y=332,scale_x=1.02,scale_y=1.))
    def test_complete_fixture_accepts_calibrated_sampling_only(self):
        c,b,raw,e=fixture();v=s.validate_capture(raw,c,b,e)
        self.assertTrue(v['actual_rna_passed']);self.assertFalse(v['contact_acceptance']);self.assertFalse(v['global_GOAL'])
    def test_raw_old_square_sampling_refused(self):
        c,b,raw,e=fixture();raw['settings']['pixel_aspect']=[1.,1.]
        for cam in raw['cameras']:cam['projection_sampling']=s.capture_projection_args(raw['settings'])
        with self.assertRaisesRegex(ValueError,'render setup'):s.validate_capture(raw,c,b,e)
    def test_capture_sampling_must_match_actual_settings(self):
        c,b,raw,e=fixture();raw['cameras'][0]['projection_sampling']['scale_x']=1.
        with self.assertRaisesRegex(ValueError,'actual captured render sampling'):s.validate_capture(raw,c,b,e)
    def test_original_projection_tolerance_still_rejects_original_error(self):
        c,b,raw,e=fixture();raw['cameras'][0]['projection_matrix'][0][0]=0.9373040795326233
        with self.assertRaisesRegex(ValueError,'numerical transform/projection'):s.validate_capture(raw,c,b,e)
    def test_camera_pose_or_hex_change_refused(self):
        for kind in ('pose','bytes'):
            c,b,raw,e=fixture()
            if kind=='pose':raw['cameras'][0]['matrix_world'][0][3]+=1
            else:raw['cameras'][0]['declared_projection_hex']='00'
            with self.assertRaises(ValueError):s.validate_capture(raw,c,b,e)
    def test_empty_extra_group_still_refused_not_filtered(self):
        c,b,raw,e=fixture();raw['mesh']['group_names'].append('CONTROL_C0.001')
        for row in raw['mesh']['weights']:row.append(0.)
        with self.assertRaisesRegex(ValueError,'group identities'):s.validate_capture(raw,c,b,e)
    def test_weight_and_membership_gates_unchanged(self):
        for key in ('weights','memberships'):
            c,b,raw,e=fixture()
            if key=='weights':raw['mesh'][key][3][0]=.5
            else:raw['mesh'][key][3]=[]
            with self.assertRaises(ValueError):s.validate_capture(raw,c,b,e)
    def test_original_failure_exact_binding_readonly(self):
        self.assertEqual(recovery.original_failure(),s.RECOVERY_FAILURE_SHA256)
        recovery.require_new_admission('source',g.SOURCE)
    def failed_records(self):
        run=recovery.ROOT/'cloud-evidence'/recovery.FAILURE_RUN
        paths=[recovery.OLD/'source-attempt.json',recovery.OLD/'source-terminal.json',run/'supervisor-terminal.json',run/'outputs/build-result.json',recovery.OLD/'source-launch-observation.json']
        return [json.loads(p.read_text()) for p in paths],dict(run=run,source=ORIGINAL/'cloud_bank58l.blend')
    def test_old_success_cannot_authorize_recovery(self):
        rows,kwargs=self.failed_records();rows[1].update(state='completed',passed=True,prepared_passed=True,intended_worker_exit_code=0)
        with self.assertRaisesRegex(ValueError,'successful original'):recovery.validate_failed_records(*rows,**kwargs)
    def test_old_saved_or_different_failure_refused(self):
        for kind in ('saved','different'):
            rows,kwargs=self.failed_records()
            if kind=='saved':rows[3]['source_saved']=True
            else:rows[1]['admission_sha256']='0'*64
            with self.assertRaises(ValueError):recovery.validate_failed_records(*rows,**kwargs)
    def test_any_new_or_other_runner_attempt_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);here=root/'source-recovery-v1';here.mkdir();old=root/'source-runner-v3';old.mkdir()
            with patch.object(recovery,'HERE',here),patch.object(recovery,'OLD',old),patch.object(recovery,'original_failure',return_value=s.RECOVERY_FAILURE_SHA256):
                source=here/'cloud_bank58l_recovery_v1.blend';recovery.require_new_admission('source',source)
                for directory,name in [(here,'source-attempt.json'),(here,'source-terminal.json'),(here,'views-attempt.json'),(root/'source-recovery-v99','source-attempt.json'),(root/'source-runner-v9','source-terminal.json'),(root/'source-v1','source-attempt.json')]:
                    directory.mkdir(exist_ok=True);p=directory/name;p.write_text('{}')
                    with self.assertRaisesRegex(ValueError,'already attempted or foreign'):recovery.require_new_admission('source',source)
                    p.unlink()
    def test_views_only_may_preserve_current_source_records(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);here=root/'source-recovery-v1';here.mkdir();old=root/'source-runner-v3';old.mkdir()
            with patch.object(recovery,'HERE',here),patch.object(recovery,'OLD',old),patch.object(recovery,'original_failure',return_value=s.RECOVERY_FAILURE_SHA256):
                source=here/'cloud_bank58l_recovery_v1.blend';(here/'source-attempt.json').write_text('{}');(here/'source-terminal.json').write_text('{}')
                recovery.require_new_admission('views',source)
                (here/'views-attempt.json').write_text('{}')
                with self.assertRaises(ValueError):recovery.require_new_admission('views',source)
    def test_output_must_be_unique_and_absent(self):
        with self.assertRaisesRegex(ValueError,'Unique recovery source'):recovery.require_new_admission('source',ORIGINAL/'cloud_bank58l.blend')
    def test_unmodified_v3_supervision_and_budgets(self):
        self.assertEqual(Path(r.deadline58l_v3.__file__).resolve(),HERE.parent/'source-runner-v3/deadline58l_v3.py')
        self.assertEqual(r.TOTAL,dict(source=120,views=120));self.assertEqual(r.CAPS,dict(build=80,verify=30,render=27));self.assertEqual(r.support.MAX_RSS_KIB,1572864)
        self.assertIn('left=limit-(time.monotonic()-started)-20',(HERE/'run58l_recovery.py').read_text())
    def test_exercise_and_protection_functions_retained(self):
        def funcs(path):
            text=path.read_text();tree=ast.parse(text)
            return {x.name:ast.get_source_segment(text,x) for x in tree.body if isinstance(x,ast.FunctionDef)}
        old=funcs(HERE.parent/'source-runner-v3/run58l_v3.py');new=funcs(HERE/'run58l_recovery.py')
        for name in ('validate_exercise','protected_manifest','output_exclusions','expected_state','require_state','png_info'):
            self.assertEqual(new[name],old[name].replace('expected_texts(ORIGINAL,c,b)','expected_texts(HERE,c,b)'))
        old_native=funcs(ORIGINAL/'native58l.py');new_native=funcs(HERE/'native58l.py')
        for name in ('rebuild_from_controls','exercise','read_collection','write_collection'):self.assertEqual(new_native[name],old_native[name])
    def test_geometry_original_bytes_embedded_and_candidate_not_copied(self):
        c=g.read(g.CANDIDATE_PATH);b=g.read(g.BINDING_PATH);texts=s.expected_texts(HERE,c,b)
        self.assertEqual(texts['GEOMETRY58L.py'],(ORIGINAL/'geometry58l.py').read_bytes())
        self.assertEqual(texts['CANDIDATE58L.json'],g.CANDIDATE_PATH.read_bytes());self.assertEqual(texts['BINDINGS58L.json'],g.BINDING_PATH.read_bytes())
        self.assertFalse((HERE/'candidate.json').exists());self.assertFalse((HERE/'bindings.json').exists());self.assertEqual(len(texts),8)
        ast.parse(texts['EDIT58L.py']);self.assertIn('_EMBEDDED_TOPOLOGY',s.EDIT_TEXT)
    def test_native_command_unique_source_adapter(self):
        command=r.native_command(g,'build',Path('/fixture/out'),Path('/fixture/attempt'))
        self.assertEqual(command[command.index('--python')+1],str(HERE/'native58l.py'));self.assertEqual(command[command.index('-t')+1],'2')
    def test_old_dependency_bytes_unchanged(self):
        pins=json.loads((HERE/'DEPENDENCY_SHA256.json').read_text())['files']
        for path,row in pins.items():
            p=r.ROOT/path;self.assertEqual(p.stat().st_size,row['bytes'],path);self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),row['sha256'],path)
    def test_entire_preparation_syntax(self):
        for p in HERE.glob('*.py'):ast.parse(p.read_text())

if __name__=='__main__':unittest.main(verbosity=2)
