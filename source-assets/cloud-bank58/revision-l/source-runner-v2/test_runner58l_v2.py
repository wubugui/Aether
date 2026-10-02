"""Pure fixtures and short Python-only process tests; NEVER an engine invocation."""
import copy, hashlib, io, json, math, os, signal, tempfile, textwrap, time, unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import run58l_v2 as r
import deadline58l as d
import test_native58l as original_tests
import run58l as rejected
s=r.native_support
HERE=Path(__file__).resolve().parent


def fixture_evidence():
    c,b,baseline,_=original_tests.fixture()
    c['manual_edit_probe']={'vertex_index':3,'delta_local':[0.,0.,.125]}
    baseline['pid']=12345
    texts=s.expected_texts(r.ORIGINAL,c,b)
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
        probes.append(dict(id=row['id'],field=field,value=spec['exercise_value'],exact_identity_restored=True,moved_path=put('moved'+str(i),moved),moved_sha256='fixture-sha',restored_path=put('restored'+str(i),baseline),restored_sha256='fixture-sha',geometry=oracle))
    p=dict(id='manual_edit',vertex_index=3,delta_local=[0.,0.,.125],geometry=oracle,exact_identity_restored=True)
    for key,a in [('manual',raw(manual=True)),('combined',raw(r.expected_state(c,c['controls'][0]['id'],'value',1.),manual=True)),('manual_restored',raw(manual=True)),('restored',baseline)]:p[key+'_path']=put(key,a);p[key+'_sha256']='fixture-sha'
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
    def test_original_R1_counterexample_accepts_and_new_rejects(self):
        case=fixture_evidence();data=case[4];probes=case[5]
        for p in probes[:-1]:data[Path(p['moved_path'])]=copy.deepcopy(data[Path(probes[0]['moved_path'])])
        data[Path(probes[-1]['combined_path'])]=copy.deepcopy(data[Path(probes[-1]['manual_path'])])
        self.assertEqual(self.invoke(case,rejected.validate_exercise)['controls'],7)
        with self.assertRaisesRegex(ValueError,'Complete actual prescribed'):self.invoke(case)
    def test_wrong_label_rejected(self):
        case=fixture_evidence();case[5][0]['id']='C6'
        with self.assertRaises(ValueError):self.invoke(case)
    def test_valid_raw_extra_control_rejected(self):
        case=fixture_evidence();values=r.expected_state(case[0],'C0','value',1.);values['C1']=1.
        case[4][Path(case[5][0]['moved_path'])]=case[6](values)
        with self.assertRaisesRegex(ValueError,'Complete actual prescribed'):self.invoke(case)
    def test_valid_raw_extra_secondary_rejected(self):
        case=fixture_evidence();values=r.expected_state(case[0],'C0','value',1.);values['C4.width_multiplier']=1.05
        case[4][Path(case[5][0]['moved_path'])]=case[6](values)
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
    def test_combined_actual_spatial_failure_rejected(self):
        case=fixture_evidence();combined=case[4][Path(case[5][-1]['combined_path'])]
        target=[s.world(v) for v in combined['mesh']['vertices']]
        def oracle(c,points,values):
            if points==target:raise ValueError('Combined spatial violation fixture')
            return case[-1]
        with self.assertRaisesRegex(ValueError,'Combined spatial'):self.invoke(case,oracle=oracle)
    def test_preserve_full_raw_validation_not_just_labels(self):
        case=fixture_evidence();case[4][Path(case[5][0]['moved_path'])]['mesh']['polygon_normals'][0]=[0,0,1]
        with self.assertRaisesRegex(ValueError,'normals'):self.invoke(case)
    def test_pid_and_restore_still_required(self):
        for kind in ('pid','restore'):
            case=fixture_evidence();p=Path(case[5][0]['restored_path']);case[4][p]=copy.deepcopy(case[4][p])
            if kind=='pid':case[4][p]['pid']=54321
            else:case[4][p]['mesh']['vertices'][0][0]+=.25
            with self.assertRaises(ValueError):self.invoke(case)


class ProtectionTests(unittest.TestCase):
    def test_original_R2_counterexample_and_stage_specific_protection(self):
        with tempfile.TemporaryDirectory(dir=HERE,prefix='test-') as tmp:
            root=Path(tmp);source=root/'cloud_bank58l.blend'
            for name in ('source-attempt.json','source-terminal.json','views-attempt.json','prior-evidence.json','cloud_bank58l.blend'):(root/name).write_text(name)
            with patch.object(rejected,'HERE',root),patch.object(r,'HERE',root):
                old=rejected.protected_manifest(root);self.assertNotIn(str(root/'source-attempt.json'),old)
                before=r.protected_manifest(root,new_outputs=r.output_exclusions('views',source))
                self.assertEqual(len(before),5)
                for name in ('source-attempt.json','source-terminal.json','views-attempt.json','cloud_bank58l.blend'):
                    p=root/name;oldbytes=p.read_bytes();p.write_text('changed')
                    self.assertNotEqual(before,r.protected_manifest(root,new_outputs=r.output_exclusions('views',source)));p.write_bytes(oldbytes)
                (root/'views-terminal.json').write_text('new');(root/'views-terminal.json.tmp').write_text('new')
                self.assertEqual(before,r.protected_manifest(root,new_outputs=r.output_exclusions('views',source)))
    def test_source_only_exact_new_outputs_excluded(self):
        with tempfile.TemporaryDirectory(dir=HERE,prefix='test-') as tmp:
            root=Path(tmp);source=root/'cloud_bank58l.blend'
            with patch.object(r,'HERE',root):
                for name in ('source-attempt.json','views-attempt.json','views-terminal.json','prior.blend'):(root/name).write_text(name)
                before=r.protected_manifest(root,new_outputs=r.output_exclusions('source',source));self.assertEqual(len(before),4)
                source.write_text('new native placeholder, never engine');(root/'source-terminal.json').write_text('new')
                self.assertEqual(before,r.protected_manifest(root,new_outputs=r.output_exclusions('source',source)))
    def test_symlink_never_exempted(self):
        with tempfile.TemporaryDirectory(dir=HERE,prefix='test-') as tmp:
            root=Path(tmp);p=root/'new';p.symlink_to(root/'missing')
            with self.assertRaises(ValueError):r.protected_manifest(root,new_outputs={p})
    def test_noop_no_admission_and_one_shot(self):
        with patch.object(r.support,'run_child',side_effect=AssertionError('No engine')),redirect_stdout(io.StringIO()):self.assertEqual(r.main([]),0)
        with tempfile.TemporaryDirectory(dir=HERE,prefix='test-') as tmp:
            root=Path(tmp);(root/'source-attempt.json').write_text('{}')
            with patch.object(r,'HERE',root),self.assertRaisesRegex(ValueError,'One-shot'):r.main(['--run-approved','source'])
    def test_prepared_label_alone_is_not_success(self):
        self.assertFalse(d.accepted({'passed':True,'state':'completed'}))
    def test_limits_unchanged(self):
        self.assertEqual(r.TOTAL,{'source':120,'views':120});self.assertEqual(r.CAPS,{'build':80,'verify':30,'render':27});self.assertEqual(d.MAX_RSS_KIB,r.support.MAX_RSS_KIB)
        self.assertIn('-20;',Path(r.__file__).read_text())


class DeadlineTests(unittest.TestCase):
    def tearDown(self):signal.setitimer(signal.ITIMER_REAL,0)
    def simulated(self,finish,initial=119.9,waitcode=0,tree=None):
        now=[initial];records=[]
        def finished(record):
            records.append(copy.deepcopy(record));finish(record,now)
        with patch.object(d.os,'fork',return_value=999999),patch.object(d.os,'wait4',side_effect=[(999999,waitcode,SimpleNamespace(ru_maxrss=1)),ChildProcessError()]),patch.object(d,'process_tree',side_effect=tree or (lambda pid:{pid:1})),patch.object(d.signal,'setitimer'),patch.object(d.ctypes,'CDLL',return_value=SimpleNamespace(prctl=lambda *args:0)):
            code,result=d.supervise(lambda:0,started=0,limit=120,finish=finished,clock=lambda:now[0])
        return code,result,records,now
    def test_original_R3_counterexample_exact_original_tail(self):
        source=Path(rejected.__file__).read_text();tail=source[source.index('        signal.setitimer(signal.ITIMER_REAL,0)'):source.index("    return report['actual_wrapper_exit_code']")]
        now=[119.9]
        class FakePath:
            def __truediv__(self,key):return self
            def is_file(self):return True
            def stat(self):return SimpleNamespace(st_size=10)
            def write_text(self,text):now[0]+=.2
        def sha(path):now[0]+=1.;return 'source-sha'
        def write(path,value):now[0]+=.2
        report={'passed':True};path=FakePath()
        ns=dict(signal=SimpleNamespace(setitimer=lambda *a:None,ITIMER_REAL=0),handlers={},time=SimpleNamespace(monotonic=lambda:now[0]),started=0,limit=120,report=report,support=SimpleNamespace(sha=sha,atomic_json=write),g=SimpleNamespace(SOURCE=path),resource=SimpleNamespace(getrusage=lambda *_:SimpleNamespace(ru_maxrss=1),RUSAGE_SELF=0),run=path,HERE=path,stage='source')
        exec(compile(textwrap.dedent(tail),'original-R3-exact-tail','exec'),ns)
        self.assertTrue(report['passed']);self.assertEqual(report['total_wall_seconds'],119.9);self.assertAlmostEqual(now[0],121.5)
    def test_late_actual_worker_exit_rejected(self):
        now=[119.9];records=[]
        def wait(pid,flags):
            if pid==-1:raise ChildProcessError()
            now[0]=121.5;return 999999,0,SimpleNamespace(ru_maxrss=1)
        with patch.object(d.os,'fork',return_value=999999),patch.object(d.os,'wait4',side_effect=wait),patch.object(d,'process_tree',side_effect=lambda pid:{pid:1}),patch.object(d.signal,'setitimer'),patch.object(d.ctypes,'CDLL',return_value=SimpleNamespace(prctl=lambda *a:0)):
            code,result=d.supervise(lambda:0,started=0,limit=120,finish=lambda record:records.append(copy.deepcopy(record)),clock=lambda:now[0])
        self.assertEqual(code,1);self.assertFalse(result['passed']);self.assertEqual(result['worker_observed_wall_seconds'],121.5)
    def test_119_9_plus_final_hash_and_writes_must_fail(self):
        def finish(record,now):
            if record['passed']:now[0]+=1.0+.2+.2+.2
        code,result,records,now=self.simulated(finish)
        self.assertEqual(code,1);self.assertFalse(result['passed']);self.assertTrue(result['timeout_triggered']);self.assertAlmostEqual(now[0],121.5);self.assertFalse(records[-1]['passed'])
    def test_final_receipt_io_exception_must_fail(self):
        def finish(record,now):
            if record['passed']:raise OSError('simulated fsync failure')
        code,result,records,now=self.simulated(finish)
        self.assertEqual(code,1);self.assertFalse(result['passed']);self.assertIn('fsync failure',result['error'])
    def test_nonzero_real_wait_status_never_passes(self):
        code,result,_,_=self.simulated(lambda *_:None,waitcode=256)
        self.assertEqual(code,1);self.assertEqual(result['worker_returncode'],1)
    def test_within_budget_receipt_accepted(self):
        code,result,_,_=self.simulated(lambda record,now:now.__setitem__(0,119.95))
        self.assertEqual(code,0);self.assertTrue(d.accepted(result));self.assertEqual(result['parent_after_receipt_wall_seconds'],119.95)
    def test_real_python_worker_exit_after_two_durable_writes(self):
        with tempfile.TemporaryDirectory(dir=HERE,prefix='test-') as tmp:
            root=Path(tmp);records=[];start=time.monotonic()
            def operation():
                for name in ('one','two'):r.support.atomic_json(root/name,{'prepared_passed':True,'passed':False})
                return 0
            def finish(record):
                self.assertTrue((root/'one').is_file() and (root/'two').is_file());records.append(copy.deepcopy(record));r.support.atomic_json(root/'receipt',record)
            code,result=d.supervise(operation,started=start,limit=2,finish=finish)
            self.assertEqual(code,0);self.assertTrue(result['worker_exit_observed']);self.assertTrue(result['all_owned_children_reaped']);self.assertGreater(result['worker_observed_wall_seconds'],0)
    def test_real_python_timeout_kills_and_reaps(self):
        records=[]
        def operation():time.sleep(2);return 0
        code,result=d.supervise(operation,started=time.monotonic(),limit=.08,finish=lambda row:records.append(copy.deepcopy(row)))
        self.assertEqual(code,1);self.assertFalse(result['passed']);self.assertTrue(result['timeout_triggered']);self.assertTrue(result['worker_exit_observed']);self.assertTrue(result['all_owned_children_reaped'])
        with self.assertRaises(ChildProcessError):os.waitpid(result['worker_pid'],os.WNOHANG)


def suite():
    result=unittest.TestSuite()
    for cls in (ExerciseTests,ProtectionTests,DeadlineTests):result.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
    # Reuse unchanged complete raw checks, not a new permissive replacement.
    names=[x for x in dir(original_tests.PureSourceTests) if x.startswith('test_raw_') or x in ('test_rna_fixture_only_positive','test_real_candidate_all_controls_manual_and_identity','test_real_rejected_inrange_state_preserves_input_arrays','test_edit_manual_preservation','test_edit_nonaccumulation_and_restore','test_secondary_real_response_and_range','test_identity_excludes_only_process_fields','test_full_png_decode_and_crc','test_missing_admission_refuses_before_engine')]
    for name in names:result.addTest(original_tests.PureSourceTests(name))
    return result

if __name__=='__main__':
    with patch.object(r.support,'run_child',side_effect=AssertionError('Engine launch forbidden in these tests')):
        outcome=unittest.TextTestRunner(verbosity=2).run(suite())
    raise SystemExit(not outcome.wasSuccessful())
