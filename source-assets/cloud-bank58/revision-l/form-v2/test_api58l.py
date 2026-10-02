"""Focused pure normal/-O controls. No engine launch, source save or render."""
import ast,copy,hashlib,importlib.util,io,json,struct,sys,tempfile,unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import run58l_form_v2 as r
import diagnostic58l as recovery
import native_support58l as s
import native58l as n
import geometry58l as g
HERE=Path(__file__).resolve().parent
ORIGINAL=HERE.parent/'source-v1'
spec=importlib.util.spec_from_file_location('old_fixture',ORIGINAL/'test_native58l.py')
fixture_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture_module)

def fixture():
    c,b,raw,_=fixture_module.fixture()
    raw['scene_flags'].update(acceptance_mode=s.DIAGNOSTIC_MODE,historical_default_corner_geometry_passed=False,full_native_acceptance=False)
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

class PreparationTests(unittest.TestCase):
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
            self.assertTrue(v['api_diagnostic_rna_passed']);self.assertFalse(v['contact_acceptance']);self.assertFalse(v['global_GOAL'])
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
    def test_geometry_original_bytes_embedded_and_candidate_not_copied(self):
            c=g.read(g.CANDIDATE_PATH);b=g.read(g.BINDING_PATH);texts=s.expected_texts(HERE,c,b)
            self.assertEqual(texts['GEOMETRY58L.py'],(HERE/'geometry58l.py').read_bytes())
            self.assertEqual(texts['CANDIDATE58L.json'],g.CANDIDATE_PATH.read_bytes());self.assertEqual(texts['BINDINGS58L.json'],g.BINDING_PATH.read_bytes())
            self.assertTrue((HERE/'candidate.json').exists());self.assertTrue((HERE/'bindings.json').exists());self.assertEqual(len(texts),8)
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

class NormalOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path=r.ROOT/'cloud-evidence/cloudbank58l-source-recovery-v1-source-20261002T183837Z-52w0vvfv/outputs/build-raw.json'
        cls.raw=json.loads(cls.path.read_text());cls.mesh=cls.raw['mesh']
    def test_actual_historical_raw_api_pass_does_not_pass_old_geometry(self):
        before=self.path.read_bytes();result=s.validate_normals(self.mesh)
        self.assertTrue(result['diagnostic_normal_acceptance']);self.assertFalse(result['full_native_acceptance']);self.assertFalse(result['original_corner_geometry_passed'])
        self.assertEqual(len(result['original_corner_geometry_faces_over_limit']),22)
        self.assertAlmostEqual(result['original_corner_geometry_max_abs'],.00015941344933428914,places=15)
        self.assertAlmostEqual(result['original_corner_geometry_max_angle_degrees'],.009158468662372497,places=10)
        self.assertLessEqual(result['corner_newell_api_max_abs'],1.2e-7)
        self.assertLessEqual(result['polygon_geometry_max_abs'],3e-5)
        self.assertEqual(self.path.read_bytes(),before)
    def test_original_full_oracle_still_rejects_actual_raw(self):
        sp=importlib.util.spec_from_file_location('unchanged_old_support',HERE.parent/'source-recovery-v1/native_support58l.py');old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
        c=g.read(ORIGINAL/'candidate.json');b=g.read(ORIGINAL/'bindings.json')
        with self.assertRaisesRegex(ValueError,'Actual outward flat polygon/corner normals'):old.validate_capture(self.raw,c,b,old.expected_texts(HERE.parent/'source-recovery-v1',c,b))
    def test_current_state_may_pass_old_criterion_history_stays_false(self):
        c,b,raw,texts=fixture();value=s.validate_capture(raw,c,b,texts)
        self.assertTrue(value['normals']['original_corner_geometry_passed']);self.assertFalse(value['normals']['historical_default_failure']['original_corner_geometry_passed']);self.assertFalse(value['full_native_acceptance'])
    def test_corner_direction_reversal_rejected(self):
        mesh=copy.deepcopy(self.mesh)
        for i in range(3):mesh['corner_normals'][i]=[-x for x in mesh['corner_normals'][i]]
        with self.assertRaisesRegex(ValueError,'outward'):s.validate_normals(mesh)
    def test_polygon_direction_reversal_rejected(self):
        mesh=copy.deepcopy(self.mesh);mesh['polygon_normals'][0]=[-x for x in mesh['polygon_normals'][0]]
        with self.assertRaisesRegex(ValueError,'outward'):s.validate_normals(mesh)
    def test_unequal_three_corners_rejected(self):
        mesh=copy.deepcopy(self.mesh);mesh['corner_normals'][1][0]+=1e-8
        with self.assertRaisesRegex(ValueError,'three flat corners'):s.validate_normals(mesh)
    def test_nonfinite_rejected_all_three_fields(self):
        for field in ('vertices','polygon_normals','corner_normals'):
            for bad in (float('nan'),float('inf'),-float('inf')):
                mesh=copy.deepcopy(self.mesh);mesh[field][0][0]=bad
                with self.assertRaisesRegex(ValueError,'Finite actual'):s.validate_normals(mesh)
    def test_flat_false_rejected(self):
        mesh=copy.deepcopy(self.mesh);mesh['flat'][0]=False
        with self.assertRaisesRegex(ValueError,'remain flat'):s.validate_normals(mesh)
    def test_newell_mismatch_rejected_not_substituted_geometry(self):
        # Synthetic negative control: swapping exact geometry normals for the
        # real cached corners must not erase the actual API-path difference.
        mesh=copy.deepcopy(self.mesh);i=s.validate_normals(mesh)['original_corner_geometry_faces_over_limit'][-1]
        # Rotate the actual unit corner by 0.001 radians, retaining equality,
        # unit length and outward hemisphere to isolate API inconsistency.
        import math
        v=mesh['corner_normals'][3*i];angle=.001;q=[v[0]*math.cos(angle)-v[1]*math.sin(angle),v[0]*math.sin(angle)+v[1]*math.cos(angle),v[2]]
        for k in range(3):mesh['corner_normals'][3*i+k]=q[:]
        with self.assertRaisesRegex(ValueError,'Newell API consistency'):s.validate_normals(mesh)
    def test_polygon_geometry_gate_preserved(self):
        c,b,raw,_=fixture();raw['mesh']['polygon_normals'][0]=[.001,0.,-1.]
        with self.assertRaisesRegex(ValueError,'polygon-to-mathematical'):s.validate_normals(raw['mesh'])
    def test_zero_and_wrong_count_rejected(self):
        for mutate in (lambda m:m['corner_normals'].pop(),lambda m:m['polygon_normals'].__setitem__(0,[0.,0.,0.])):
            mesh=copy.deepcopy(self.mesh);mutate(mesh)
            with self.assertRaises(ValueError):s.validate_normals(mesh)
    def test_diagnostic_scene_mode_and_full_acceptance_enforced(self):
        for key,bad in [('acceptance_mode','old-native'),('full_native_acceptance',True),('historical_default_corner_geometry_passed',True)]:
            c,b,raw,texts=fixture();raw['scene_flags'][key]=bad
            with self.assertRaises(ValueError):s.validate_capture(raw,c,b,texts)
    def test_newell_independent_numpy_float32_replay(self):
        import numpy as np
        triangles=np.asarray(self.mesh['vertices'],dtype=np.float32)[self.mesh['faces']];q=np.zeros((len(triangles),3),dtype=np.float32);previous=triangles[:,-1]
        for k in range(3):
            current=triangles[:,k]
            for axis in range(3):
                j=(axis+1)%3;z=(axis+2)%3;q[:,axis]+=(previous[:,j]-current[:,j])*(previous[:,z]+current[:,z])
            previous=current
        result=q/np.sqrt(np.sum(q*q,axis=1))[:,None]
        std=np.array([s.float32_newell(t.tolist()) for t in triangles],dtype=np.float32)
        self.assertEqual(std.tobytes(),result.tobytes())

class AdmissionTests(unittest.TestCase):
    def test_both_actual_failed_chains_readonly_and_new_source_absent(self):
        self.assertEqual(recovery.original_failures(),list(s.FAILURE_ADMISSIONS));recovery.require_new_admission('source',g.SOURCE);self.assertFalse(g.SOURCE.exists())
    def test_original_success_wrong_error_and_admission_rejected(self):
        binding=json.loads((HERE/'SOURCE_BINDING.json').read_text())
        for spec in binding['failures']:
            directory=r.ROOT/spec['directory'];run=r.ROOT/'cloud-evidence'/spec['run'];source=r.ROOT/spec['source']
            records=[json.loads(p.read_text()) for p in (directory/'source-attempt.json',directory/'source-terminal.json',run/'supervisor-terminal.json',run/'outputs/build-result.json',directory/'source-launch-observation.json')]
            kwargs=dict(spec=spec,run=run,source=source);recovery.validate_failed_records(*records,**kwargs)
            for index,key,value in [(1,'passed',True),(3,'error','different failure'),(1,'admission_sha256','0'*64),(2,'all_owned_children_reaped',False)]:
                changed=copy.deepcopy(records);changed[index][key]=value
                with self.assertRaises(ValueError):recovery.validate_failed_records(*changed,**kwargs)
    def test_new_foreign_and_duplicate_attempts_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);here=root/'form-v2';here.mkdir();(here/'SOURCE_BINDING.json').write_text(json.dumps({'predecessor':{'consumed_admissions':{}}}))
            with patch.object(recovery,'HERE',here),patch.object(recovery,'original_failures',return_value=list(s.FAILURE_ADMISSIONS)),patch.object(recovery,'prior_form_source',return_value=True):
                source=here/'cloud_bank58l_form_v2.blend';recovery.require_new_admission('source',source)
                for directory,name in [(here,'source-attempt.json'),(here,'source-terminal.json'),(here,'views-attempt.json'),(root/'source-api-diagnostic-v2','source-attempt.json'),(root/'source-recovery-v9','source-terminal.json'),(root/'source-v1','source-attempt.json')]:
                    directory.mkdir(exist_ok=True);p=directory/name;p.write_text('{}')
                    with self.assertRaises(ValueError):recovery.require_new_admission('source',source)
                    p.unlink()
                source.write_text('Fixture only; not a native file')
                with self.assertRaisesRegex(ValueError,'Never overwrite'):recovery.require_new_admission('source',source)
    def test_views_preserve_current_source_only(self):
        with tempfile.TemporaryDirectory() as folder:
            here=Path(folder)/'form-v2';here.mkdir();(here/'SOURCE_BINDING.json').write_text(json.dumps({'predecessor':{'consumed_admissions':{}}}));source=here/'cloud_bank58l_form_v2.blend'
            with patch.object(recovery,'HERE',here),patch.object(recovery,'original_failures',return_value=list(s.FAILURE_ADMISSIONS)),patch.object(recovery,'prior_form_source',return_value=True):
                (here/'source-attempt.json').write_text('{}');(here/'source-terminal.json').write_text('{}');recovery.require_new_admission('views',source)
                (here/'views-attempt.json').write_text('{}')
                with self.assertRaises(ValueError):recovery.require_new_admission('views',source)
    def test_unchanged_core_edit_geometry_and_supervision_functions(self):
        def funcs(path):
            text=path.read_text();return {x.name:ast.get_source_segment(text,x) for x in ast.parse(text).body if isinstance(x,ast.FunctionDef)}
        old=funcs(HERE.parent/'source-recovery-v1/native58l.py');new=funcs(HERE/'native58l.py')
        for name in ('rebuild_from_controls','read_collection','write_collection','create_shared_groups'):self.assertEqual(old[name],new[name])
        old=funcs(HERE.parent/'source-recovery-v1/run58l_recovery.py');new=funcs(HERE/'run58l_form_v2.py')
        for name in ('protected_manifest','output_exclusions','expected_state','require_state','png_info','native_command'):self.assertEqual(old[name],new[name])
    def test_every_entry_and_exercise_uses_actual_diagnostic_oracle(self):
        tree=ast.parse((HERE/'native58l.py').read_text());funcs={x.name:ast.get_source_segment((HERE/'native58l.py').read_text(),x) for x in tree.body if isinstance(x,ast.FunctionDef)}
        self.assertIn("report['validation']=g.validate_native_raw(raw,c,b)",funcs['main'])
        for key in ('moved_validation','manual_validation','combined_validation','manual_restored_validation','restored_validation'):self.assertIn(key,funcs['exercise'])
        self.assertIn("s.validate_normals(rendered['mesh'])",funcs['main'])
        self.assertIn("report.update(passed=True,diagnostic_acceptance=True",funcs['main'])


# Synthetic tetrahedron exercise fixtures only; never stored as actual native raw.
import math
def fixture_evidence():
    c,b,baseline,_=fixture()
    c['manual_edit_probe']={'vertex_index':3,'delta_local':[0.,0.,.125]}
    baseline['pid']=12345
    texts=s.expected_texts(HERE,c,b)
    baseline['texts']=[dict(name=k,sha256=s.digest(v),bytes=len(v),is_in_memory=True,filepath='',use_module=False) for k,v in sorted(texts.items())]
    def raw(values=None,manual=False):
        a=copy.deepcopy(baseline);base=copy.deepcopy(baseline['mesh']['vertices'])
        if manual:base[3][2]=s.f32(base[3][2]+.125)
        values=values or r.expected_state(c)
        for control in a['controls']:
            control['value']=control['last_applied_value']=values[control['id']]
            for p in control['secondary_parameters']:p['value']=p['last_applied_value']=values[control['id']+'.'+p['id']]
        _,points=s.edit(c,base,base,base,[values[x['id']] for x in c['controls']],{k:v for k,v in values.items() if '.' in k})
        a['mesh']['vertices']=points;a['mesh']['attributes'][s.BASE]['values']=base;a['mesh']['attributes'][s.LAST]['values']=points
        a['scene_flags']['edited_after_frozen_build']=points!=baseline['mesh']['vertices'] or base!=baseline['mesh']['vertices']
        normals=[]
        for face in c['faces']:
            x,y,z=[points[i] for i in face];u=[y[i]-x[i] for i in range(3)];v=[z[i]-x[i] for i in range(3)]
            n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];length=math.sqrt(sum(x*x for x in n));normals.append([s.f32(x/length) for x in n])
        a['mesh']['polygon_normals']=normals;a['mesh']['corner_normals']=[n for n in normals for _ in range(3)]
        # Always execute the real complete raw validator, with real normals.
        s.validate_capture(a,c,b,texts,manual_base=base if manual else None)
        return a
    out=HERE/'fixture-output-not-created';data={};probes=[]
    def put(name,value):data[out/name]=value;return str(out/name)
    oracle={'fixture_only':'not actual candidate geometry'}
    for i,(row,field,spec) in enumerate([(x,'value',x) for x in c['controls']]+[(x,p['id'],p) for x in c['controls'] for p in x.get('secondary_parameters',[])]):
        moved=raw(r.expected_state(c,row['id'],field,spec['exercise_value']))
        probes.append(dict(id=row['id'],field=field,value=spec['exercise_value'],exact_identity_restored=True,moved_path=put('moved'+str(i),moved),moved_sha256='fixture-sha',restored_path=put('restored'+str(i),baseline),restored_sha256='fixture-sha',geometry=oracle,moved_validation=s.validate_capture(moved,c,b,texts),restored_validation=s.validate_capture(baseline,c,b,texts)))
    p=dict(id='manual_edit',vertex_index=3,delta_local=[0.,0.,.125],geometry=oracle,exact_identity_restored=True)
    for key,a in [('manual',raw(manual=True)),('combined',raw(r.expected_state(c,c['controls'][0]['id'],'value',1.),manual=True)),('manual_restored',raw(manual=True)),('restored',baseline)]:p[key+'_path']=put(key,a);p[key+'_sha256']='fixture-sha'
    for key in ('manual','combined','manual_restored','restored'):
        raw_record=data[Path(p[key+'_path'])];p[key+'_validation']=s.validate_capture(raw_record,c,b,texts,manual_base=raw_record['mesh']['attributes'][s.BASE]['values'] if key!='restored' else None)
    probes.append(p);data[out/'build-result.json']={'exercise_sha256':'fixture-sha'}
    return c,b,baseline,out,data,probes,raw,oracle

class ExerciseTests(unittest.TestCase):
    def invoke(self,case,validator=r.validate_exercise,oracle=None):
            c,b,baseline,out,data,probes,_,default=case
            geo=SimpleNamespace(validate_evaluated=oracle or (lambda *args:default))
            with patch.object(r.support,'strict_json',side_effect=lambda p:copy.deepcopy(data[p])),patch.object(r.support,'sha',return_value='fixture-sha'),patch.object(Path,'read_text',return_value=json.dumps(probes)):
                return validator(out,'build',c,b,geo,baseline)
    def test_complete_correct_raw_trials(self):
            case=fixture_evidence();calls=[]
            result=self.invoke(case,oracle=lambda *args:(calls.append(copy.deepcopy(args)),case[-1])[1])
            self.assertEqual(result['controls'],7);self.assertEqual(result['secondary_parameters'],1);self.assertEqual(len(calls),10)
            self.assertEqual(calls[-1][1],[s.world(v) for v in case[4][Path(case[5][-1]['combined_path'])]['mesh']['vertices']])
    def test_wrong_label_rejected(self):
            case=fixture_evidence();case[5][0]['id']='C6'
            with self.assertRaises(ValueError):self.invoke(case)
    def test_valid_raw_extra_control_rejected(self):
            case=fixture_evidence();values=r.expected_state(case[0],'C0','value',1.);values['C1']=1.
            case[4][Path(case[5][0]['moved_path'])]=case[6](values)
            case[5][0]['moved_validation']=s.validate_capture(case[4][Path(case[5][0]['moved_path'])],case[0],case[1],s.expected_texts(HERE,case[0],case[1]))
            with self.assertRaisesRegex(ValueError,'Complete actual prescribed'):self.invoke(case)
    def test_valid_raw_extra_secondary_rejected(self):
            case=fixture_evidence();values=r.expected_state(case[0],'C0','value',1.);values['C4.width_multiplier']=1.05
            case[4][Path(case[5][0]['moved_path'])]=case[6](values)
            case[5][0]['moved_validation']=s.validate_capture(case[4][Path(case[5][0]['moved_path'])],case[0],case[1],s.expected_texts(HERE,case[0],case[1]))
            with self.assertRaises(ValueError):self.invoke(case)
    def test_manual_must_be_defaults(self):
            case=fixture_evidence();case[4][Path(case[5][-1]['manual_path'])]=case[6](r.expected_state(case[0],'C1','value',1.),manual=True)
            with self.assertRaises(ValueError):self.invoke(case)
    def test_combined_no_change_rejected(self):
            case=fixture_evidence();case[4][Path(case[5][-1]['combined_path'])]=copy.deepcopy(case[4][Path(case[5][-1]['manual_path'])])
            with self.assertRaisesRegex(ValueError,'Complete actual prescribed'):self.invoke(case)
    def test_combined_wrong_control_rejected(self):
            case=fixture_evidence();case[4][Path(case[5][-1]['combined_path'])]=case[6](r.expected_state(case[0],'C1','value',1.),manual=True)
            with self.assertRaises(ValueError):self.invoke(case)
    def test_preserve_full_raw_validation_not_just_labels(self):
            case=fixture_evidence();case[4][Path(case[5][0]['moved_path'])]['mesh']['polygon_normals'][0]=[0,0,1]
            with self.assertRaisesRegex(ValueError,'normals'):self.invoke(case)
    def test_pid_and_restore_still_required(self):
            for kind in ('pid','restore'):
                case=fixture_evidence();p=Path(case[5][0]['restored_path']);case[4][p]=copy.deepcopy(case[4][p])
                if kind=='pid':case[4][p]['pid']=54321
                else:case[4][p]['mesh']['vertices'][0][0]+=.25
                with self.assertRaises(ValueError):self.invoke(case)

class BindingAndBudgetTests(unittest.TestCase):
    def test_supervision_original_and_limits_identical(self):
        self.assertEqual(Path(r.deadline58l_v3.__file__).resolve(),HERE.parent/'source-runner-v3/deadline58l_v3.py')
        self.assertEqual(r.TOTAL,dict(source=120,views=120));self.assertEqual(r.CAPS,dict(build=80,verify=30,render=27));self.assertEqual(r.support.MAX_RSS_KIB,1572864)
        self.assertIn('left=limit-(time.monotonic()-started)-20',(HERE/'run58l_form_v2.py').read_text())
    def test_source_views_exact_output_exclusions_preserve_old_attempts(self):
        self.assertEqual(r.output_exclusions('source',g.SOURCE),{HERE/'source-terminal.json',HERE/'source-terminal.json.tmp',g.SOURCE})
        self.assertEqual(r.output_exclusions('views',g.SOURCE),{HERE/'views-terminal.json',HERE/'views-terminal.json.tmp'})
        self.assertNotIn(HERE/'source-attempt.json',r.output_exclusions('source',g.SOURCE))
    def test_default_noop_never_admits(self):
        before=sorted(str(p) for p in HERE.iterdir())
        with redirect_stdout(io.StringIO()),patch.object(r.diagnostic58l,'require_new_admission',side_effect=AssertionError('No admission')):
            self.assertEqual(r.main([]),0)
        self.assertEqual(before,sorted(str(p) for p in HERE.iterdir()))

if __name__=='__main__':unittest.main(verbosity=2)
