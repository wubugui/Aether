#!/usr/bin/env python3
"""Default no-op; only source is admitted here.

Original views validation/branch is retained unchanged but is unreachable from
this source-only CLI and admission. A later adapter requires source publication.
"""
from __future__ import annotations
import argparse,json,os,resource,signal,struct,sys,tempfile,time,traceback,zlib
from pathlib import Path
sys.dont_write_bytecode=True
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
ORIGINAL=HERE.parent/'source-v1'
VERSION='cloudbank58l-form-v3'
SUPERVISION=HERE.parent/'source-runner-v3'
sys.path.insert(0,str(ORIGINAL));sys.path.insert(0,str(ROOT/'source-assets/cloud-bank58/revision-k/import-v1'));sys.path.insert(0,str(SUPERVISION));sys.path.insert(0,str(HERE))
import bounded_support58k as support
import native_support58l as native_support
import deadline58l_v3
import diagnostic58l
import runtime58l
TOTAL={'source':120,'views':120}
CAPS={'build':80,'verify':30,'render':27}
def output_exclusions(stage, source):
    native_support.require(stage in TOTAL, 'Known stage')
    terminal=HERE/(stage+'-terminal.json')
    # attempt is immutable once admitted and is deliberately NOT excluded.
    return {terminal, terminal.with_suffix('.json.tmp')} | ({source} if stage=='source' else set())


def protected_manifest(root=ROOT,run=None,*,new_outputs=()):
    """Exclude only this newly allocated run and explicitly absent stage outputs."""
    result={};root=Path(root);run=Path(run).resolve() if run else None
    excluded={Path(p).absolute() for p in new_outputs}
    for current,dirs,files in os.walk(root,followlinks=False):
        p=Path(current);dirs[:]=sorted(d for d in dirs if not (p==root and d=='.git') and not(run and (p/d).resolve()==run))
        for d in dirs:native_support.require(not(p/d).is_symlink(),'Symlink in protected project: '+str(p/d))
        for name in sorted(files):
            path=p/name
            native_support.require(not path.is_symlink(),'Symlink in protected project: '+str(path))
            if path.absolute() in excluded:continue
            result[str(path)]=support.sha(path)
    return result


def frozen_inputs(g):
    freeze=HERE/'FINAL_SHA256.json';data=support.strict_json(freeze);paths={}
    for rel,row in data['files'].items():
        original=ROOT/rel;p=original.resolve();native_support.require(p.is_relative_to(ROOT.resolve()) and p.is_file() and not original.is_symlink(),'Frozen path boundary '+rel)
        native_support.require(p.stat().st_size==row['bytes'],'Frozen input size '+rel);paths[str(p)]=row['sha256']
    paths[str(freeze)]=support.sha(freeze)
    required={str(p) for p in [HERE/'runtime58l.py',HERE/'observe_form58l.py',HERE/'run58l_form_v3.py',SUPERVISION/'deadline58l_v3.py',HERE/'SOURCE_BINDING.json',ORIGINAL/'FINAL_SHA256.json',HERE/'native58l.py',ORIGINAL/'native_support58l.py',ORIGINAL/'geometry58l.py',HERE/'geometry58l.py',HERE/'native_support58l.py',HERE/'diagnostic58l.py',HERE/'DEPENDENCY_SHA256.json',g.CANDIDATE_PATH,g.BINDING_PATH,ROOT/'source-assets/cloud-bank58/revision-k/import-v1/bounded_support58k.py',ROOT/'source-assets/cloud-bank58/revision-k/poly58k.py']}
    native_support.require(required<=set(paths),'All executed preparation/dependency inputs pinned')
    _,changed,errors=support.inspect_inputs(paths);native_support.require(not changed and not errors,'Frozen input identity '+repr(changed+errors));return paths


def expected_state(c, control=None, field='value', value=None):
    state={r['id']:r['default'] for r in c['controls']}
    state.update({r['id']+'.'+p['id']:p['default'] for r in c['controls'] for p in r.get('secondary_parameters',[])})
    if control is not None:state[control if field=='value' else control+'.'+field]=value
    return state


def require_state(raw, wanted):
    native_support.require(native_support.state_values(raw)==wanted,'Complete actual prescribed control/secondary state')

def png_info(path):
    data=path.read_bytes();native_support.require(data[:8]==b'\x89PNG\r\n\x1a\n','Actual PNG signature');at=8;payload=[];header=None;ended=False
    while at<len(data):
        native_support.require(at+12<=len(data),'Complete PNG chunk header');n=struct.unpack('>I',data[at:at+4])[0];kind=data[at+4:at+8];chunk=data[at+8:at+8+n];crc=data[at+8+n:at+12+n]
        native_support.require(len(chunk)==n and len(crc)==4 and zlib.crc32(kind+chunk)&0xffffffff==struct.unpack('>I',crc)[0],'Actual PNG chunk CRC')
        if kind==b'IHDR':native_support.require(header is None,'One PNG header');header=struct.unpack('>IIBBBBB',chunk)
        if kind==b'IDAT':payload.append(chunk)
        at+=12+n
        if kind==b'IEND':native_support.require(n==0 and at==len(data),'Complete PNG end');ended=True;break
    native_support.require(header==(1179,664,8,6,0,0,0) and ended and payload,'Original 1179x664 RGBA8 source image, no downscale')
    decoded=zlib.decompress(b''.join(payload));stride=1+1179*4
    native_support.require(len(decoded)==664*stride and all(decoded[i*stride] in range(5) for i in range(664)),'Fully decoded PNG scanlines')
    return dict(bytes=len(data),sha256=support.sha(path),width=1179,height=664,crc_and_scanlines_validated=True)

def validate_exercise(out,label,c,b,g,baseline):
    """Independent wrapper reads all native trial evidence, not just seven bools."""
    rows=support.strict_json(out/(label+'-result.json'));probes=json.loads((out/(label+'-exercise.json')).read_text());specs=[(r,'value',r) for r in c['controls']]+[(r,p['id'],p) for r in c['controls'] for p in r.get('secondary_parameters',[])];native_support.require(len(probes)==len(specs)+1 and rows['exercise_sha256']==support.sha(out/(label+'-exercise.json')),'Full exercise evidence identity')
    expected=native_support.expected_texts(HERE,c,b)
    require_state(baseline,expected_state(c))
    for p,(row,field,spec) in zip(probes[:-1],specs):
        native_support.require(p['id']==row['id'] and p['field']==field and p['value']==spec['exercise_value'] and p['exact_identity_restored'],'Seven actual prescribed exercise states')
        paths=[Path(p['moved_path']),Path(p['restored_path'])]
        native_support.require(all(x.resolve().parent==out.resolve() for x in paths),'Exercise evidence output boundary')
        native_support.require(support.sha(paths[0])==p['moved_sha256'] and support.sha(paths[1])==p['restored_sha256'],'Exercise original bytes')
        moved=support.strict_json(paths[0]);restored=support.strict_json(paths[1]);native_support.require(p['moved_validation']==native_support.validate_capture(moved,c,b,expected) and p['restored_validation']==native_support.validate_capture(restored,c,b,expected),'Actual prescribed states share diagnostic oracle')
        require_state(moved,expected_state(c,row['id'],field,spec['exercise_value']));require_state(restored,expected_state(c))
        native_support.require(moved['pid']==restored['pid']==baseline['pid'] and moved['mesh']['vertices']!=baseline['mesh']['vertices'] and native_support.identity(restored)==native_support.identity(baseline),'Actual native response and exact restoration')
        native_support.require(p['geometry']==g.validate_evaluated(c,[native_support.world(v) for v in moved['mesh']['vertices']],native_support.state_values(moved)),'Independent actual exercise spatial validation')
    p=probes[-1];probe=c['manual_edit_probe'];native_support.require(p['id']=='manual_edit' and p['vertex_index']==probe['vertex_index'] and p['delta_local']==probe['delta_local'],'Actual prescribed manual probe')
    actual={}
    for key in ('manual','combined','manual_restored','restored'):
        path=Path(p[key+'_path']);native_support.require(path.resolve().parent==out.resolve() and support.sha(path)==p[key+'_sha256'],'Manual evidence boundary/bytes');actual[key]=support.strict_json(path)
        native_support.require(actual[key]['pid']==baseline['pid'],'Manual native PID')
    base=[row[:] for row in baseline['mesh']['vertices']];i=probe['vertex_index'];base[i]=[native_support.f32(x+d) for x,d in zip(base[i],probe['delta_local'])]
    require_state(actual['manual'],expected_state(c));require_state(actual['combined'],expected_state(c,c['controls'][0]['id'],'value',c['controls'][0]['exercise_value']))
    native_support.require(p['manual_validation']==native_support.validate_capture(actual['manual'],c,b,expected,manual_base=base) and p['combined_validation']==native_support.validate_capture(actual['combined'],c,b,expected,manual_base=base),'Actual manual and combined diagnostic oracle')
    native_support.require(p['manual_restored_validation']==native_support.validate_capture(actual['manual_restored'],c,b,expected,manual_base=base) and p['restored_validation']==native_support.validate_capture(actual['restored'],c,b,expected),'Actual restored diagnostic oracle')
    native_support.require(native_support.identity(actual['manual_restored'])==native_support.identity(actual['manual']) and native_support.identity(actual['restored'])==native_support.identity(baseline),'Manual offsets preserved and baseline exactly restored')
    native_support.require(p['geometry']==g.validate_evaluated(c,[native_support.world(v) for v in actual['manual']['mesh']['vertices']],native_support.state_values(actual['manual'])),'Independent manual spatial validation')
    native_support.require(actual['combined']['mesh']['vertices']!=actual['manual']['mesh']['vertices'],'Actual combined control response')
    combined_geometry=g.validate_evaluated(c,[native_support.world(v) for v in actual['combined']['mesh']['vertices']],native_support.state_values(actual['combined']))
    return dict(acceptance_mode=native_support.DIAGNOSTIC_MODE,full_native_acceptance=False,normal_validation_by_state=[dict(id=q['id'],**{k:v['normals'] for k,v in q.items() if k.endswith('_validation')}) for q in probes],combined_geometry=combined_geometry,controls=7,secondary_parameters=len(specs)-7,manual_edit_preserved=True,exact_identity_restored=True)

def phase(stage,run,started,limit):
    import geometry58l as g
    out=run/'outputs';out.mkdir()
    admission=dict(runtime=runtime58l.runtime(),original_source_stage='failed',predecessor=diagnostic58l.predecessor(),prior_failure_admissions=diagnostic58l.original_failures(),acceptance_mode=native_support.DIAGNOSTIC_MODE,full_native_acceptance=False,state='admitted_one_shot_not_complete',wrapper_pid=os.getpid(),stage=stage,run=str(run),source=str(g.SOURCE),output=str(out),native_sha256=support.sha(HERE/'native58l.py'),runner_version=VERSION,runner_sha256=support.sha(HERE/'run58l_form_v3.py'),supervisor_pid=os.getppid(),candidate_sha256=support.sha(g.CANDIDATE_PATH),binding_sha256=support.sha(g.BINDING_PATH),utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
    with (HERE/(stage+'-attempt.json')).open('x') as f:json.dump(admission,f);f.flush();os.fsync(f.fileno())
    print(run,flush=True);report=dict(runtime=runtime58l.runtime(),original_source_stage='failed',predecessor=diagnostic58l.predecessor(),prior_failure_admissions=list(native_support.FAILURE_ADMISSIONS),acceptance_mode=native_support.DIAGNOSTIC_MODE,full_native_acceptance=False,version=g.VERSION,runner_version=VERSION,stage=stage,state='preparing',passed=False,run=str(run),source=str(g.SOURCE),runner_sha256=support.sha(HERE/'run58l_form_v3.py'),supervisor_pid=os.getppid(),limits=dict(total_wall_seconds=limit,cpu_threads=2,native_caps=CAPS,max_wrapper_plus_child_rss_kib=support.MAX_RSS_KIB),stages=[],images=[],normal_validation_by_stage=[],historical_default_failure=dict(native_support.HISTORICAL_DEFAULT_FAILURE),historical_form_v2_default_failure=dict(native_support.HISTORICAL_FORM_V2_DEFAULT_FAILURE),world_loaded=False,world_modified=False,world_integration_allowed=False,contact_acceptance=False,world_acceptance=False,global_GOAL=False,visual_acceptance=False,weather_acceptance=False,source_diagnostic_only=True)
    admission_path=HERE/(stage+'-attempt.json');admission_sha=support.sha(admission_path)
    excluded=output_exclusions(stage,g.SOURCE)
    pins={};before={};outputs={};handlers={};source_sha=support.sha(g.SOURCE) if stage=='views' else None
    def stop(number,frame):raise InterruptedError('Wrapper stop signal '+str(number))
    try:
        for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM):handlers[sig]=signal.signal(sig,stop)
        signal.setitimer(signal.ITIMER_REAL,max(.001,limit-(time.monotonic()-started)));cpus=sorted(os.sched_getaffinity(0))[:2];native_support.require(len(cpus)==2,'CPU2 available');os.sched_setaffinity(0,cpus)
        pins=frozen_inputs(g);native_support.require(support.sha(g.BLENDER)==g.BLENDER_SHA,'Pinned official Blender executable')
        before=protected_manifest(run=run,new_outputs=excluded);support.atomic_json(run/'protected-before.json',before);support.atomic_json(run/'input-sha256.json',pins)
        # Exact source inputs are already frozen and published; retain SHA/size
        # identities without another redundant preparation backup tree.
        b=support.strict_json(g.BINDING_PATH);c=support.strict_json(g.CANDIDATE_PATH);g.validate_candidate(c)
        env=os.environ.copy();env.pop('PYTHONOPTIMIZE',None);env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1')
        for key,name in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data'),('BLENDER_USER_CONFIG','blender-config')]:p=run/name;p.mkdir();env[key]=str(p)
        jobs=[('build',None),('verify',None)] if stage=='source' else [('render',v['name']) for v in b['world_cameras']]
        build_raw=None
        for mode,view in jobs:
            native_support.require(support.sha(admission_path)==admission_sha,'Immutable current stage admission')
            native_support.require(frozen_inputs(g)==pins,'Frozen inputs changed between children')
            if source_sha:native_support.require(support.sha(g.SOURCE)==source_sha,'Saved source changed between children')
            native_support.require(all(p.is_file() and support.sha(p)==v for p,v in outputs.items()),'Earlier output altered')
            left=limit-(time.monotonic()-started)-20;native_support.require(left>0,'Total stage budget exhausted')
            label=mode+('-'+view if view else '');command=native_command(g,mode,out,admission_path,view)
            report['state']='running';support.atomic_json(run/'wrapper-report.json',report)
            # Register the actual Popen before returning to original child supervision.
            # Keep the original native/process helper untouched.
            with deadline58l_v3.registered_native_launches(support):
                row=support.run_child(command,run,env,run,min(CAPS[mode],left),label,heartbeat=out/(label+'-progress.json'))
            report['stages'].append(row);support.atomic_json(run/'wrapper-report.json',report)
            native_support.require(support.process_passed(row),'Native child failed '+label)
            native_support.require(not support.error_lines([run/(label+'.stdout.log'),run/(label+'.stderr.log')]),'Actual native error/leak log')
            terminal=support.strict_json(out/(label+'-result.json'));raw=support.strict_json(out/(label+'-raw.json'))
            native_support.require(terminal['passed'] is True and terminal['state']=='completed' and terminal['version']==g.VERSION and terminal['mode']==mode and terminal['view']==view and terminal['pid']==row['pid']==raw['pid'],'Actual complete child/PID terminal')
            native_support.require(raw['cpu_affinity']==row['cpu_affinity']==cpus and terminal['raw_sha256']==support.sha(out/(label+'-raw.json')),'Actual CPU2/raw bytes')
            native_support.require(not any(terminal[k] for k in ('world_loaded','world_integration_allowed','contact_acceptance','world_acceptance','global_GOAL','visual_acceptance','weather_acceptance')),'Isolated source scope')
            native_support.require(terminal['validation']==g.validate_native_raw(raw,c,b),'Independent complete actual raw validation')
            native_support.require(terminal['acceptance_mode']==native_support.DIAGNOSTIC_MODE and terminal['full_native_acceptance'] is False and terminal['diagnostic_acceptance'] is True,'Actual child API diagnostic acceptance only')
            report['normal_validation_by_stage'].append(dict(stage=label,**terminal['validation']['normals']))
            native_support.require(terminal['source_sha256']==support.sha(g.SOURCE),'Actual saved source bytes')
            if mode in ('build','verify'):report.setdefault('exercise',[]).append(validate_exercise(out,label,c,b,g,raw))
            if mode=='build':native_support.require(terminal['source_saved'] and terminal['images']==0,'One native save');build_raw=native_support.identity(raw)
            elif mode=='verify':
                native_support.require(not terminal['source_saved'] and terminal['images']==0 and row['pid']!=report['stages'][0]['pid'],'Independent no-save fresh-open process')
                native_support.require(Path(raw['opened_filepath']).resolve()==g.SOURCE.resolve() and native_support.identity(raw)==build_raw,'Actual fresh-open path and complete source identity')
            else:
                native_support.require(not terminal['source_saved'] and terminal['images']==1 and terminal['exact_identity_restored'],'One no-save restored source view')
                image=png_info(out/(view+'.png'));native_support.require(image['sha256']==terminal['image_sha256'],'Actual original image bytes')
                rendered=support.strict_json(out/(label+'-rendered-raw.json'));native_support.require(terminal['rendered_raw_sha256']==support.sha(out/(label+'-rendered-raw.json')) and rendered['pid']==raw['pid'],'Actual rendered RNA evidence/PID')
                expected_settings=dict(raw['settings'],active_camera=native_support.CAMERA_PREFIX+view,render_filepath=str(out/(view+'.png')))
                native_support.require(rendered['settings']==expected_settings and all(img['type']=='RENDER_RESULT' and img['source']=='VIEWER' for img in rendered['images']),'Actual named original camera used for the render')
                native_support.require({k:v for k,v in native_support.identity(rendered).items() if k not in ('settings','images')}=={k:v for k,v in native_support.identity(raw).items() if k not in ('settings','images')},'Geometry/material/cameras unchanged during actual render')
                native_support.require(terminal['rendered_normals']==native_support.validate_normals(rendered['mesh']),'Rendered actual normals share diagnostic oracle')
                restored=support.strict_json(out/(label+'-restored-raw.json'));native_support.require(terminal['restored_validation']==native_support.validate_capture(restored,c,b,native_support.expected_texts(HERE,c,b)),'Restored source uses complete diagnostic oracle');native_support.require(terminal['restored_raw_sha256']==support.sha(out/(label+'-restored-raw.json')) and native_support.identity(restored)==native_support.identity(raw),'Actual restored native view identity');report['images'].append(dict(view=view,**image))
            if source_sha:native_support.require(support.sha(g.SOURCE)==source_sha,'No-save source unchanged')
            else:source_sha=support.sha(g.SOURCE)
            outputs.update({p:support.sha(p) for p in out.rglob('*') if p.is_file()})
        native_support.require(len(report['stages'])==len(jobs),'All child processes complete');report.update(passed=True,state='completed')
    except BaseException:report.update(passed=False,state='failed',error=traceback.format_exc())
    finally:
        try:
            _,changed,errors=support.inspect_inputs(pins);after=protected_manifest(run=run,new_outputs=excluded);support.atomic_json(run/'protected-after.json',after)
            report.update(frozen_inputs_unchanged=bool(pins and not changed and not errors),changed_inputs=changed,input_errors=errors,protected_originals_unchanged=bool(before and before==after),protected_file_count=len(before),earlier_outputs_unchanged=all(p.is_file() and support.sha(p)==v for p,v in outputs.items()),saved_source_unchanged=bool(source_sha and g.SOURCE.is_file() and support.sha(g.SOURCE)==source_sha))
            report['passed']=bool(report['passed'] and report['frozen_inputs_unchanged'] and report['protected_originals_unchanged'] and report['earlier_outputs_unchanged'] and report['saved_source_unchanged'])
        except BaseException:report.update(passed=False,finalization_error=traceback.format_exc())
        # All expensive final observations and both durable terminal writes are
        # still in the supervised worker and under the same absolute deadline.
        try:
            native_support.require(support.sha(admission_path)==admission_sha,'Immutable current stage admission at finalization')
            source_observed=dict(source_sha256=support.sha(g.SOURCE),source_bytes=g.SOURCE.stat().st_size) if g.SOURCE.is_file() else dict(source_sha256=None,source_bytes=None)
            native_support.require(time.monotonic()-started<limit,'Final source observation exceeded total budget')
        except BaseException:
            source_observed=dict(source_sha256=None,source_bytes=None,source_observation_error=traceback.format_exc());report['passed']=False
        if stage=='source':report['source_output_sha256']={str(p):v for p,v in outputs.items()}
        prepared=bool(report['passed'])
        report.update(state='awaiting_external_process_terminal' if prepared else 'failed',passed=False,prepared_passed=prepared,
                      diagnostic_prepared_passed=prepared,diagnostic_acceptance=False,completion_authority=str(run/'supervisor-terminal.json'),worker_pid=os.getpid(),
                      worker_prewrite_wall_seconds=time.monotonic()-started,actual_wrapper_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      intended_worker_exit_code=0 if prepared else 1,admission_sha256=admission_sha,**source_observed)
        support.atomic_json(run/'wrapper-report.json',report);support.atomic_json(HERE/(stage+'-terminal.json'),report)
        (run/'worker-intended-exit-code.txt').write_text(str(report['intended_worker_exit_code'])+'\n')
        # This check is AFTER both flush/fsync/replace operations and final file.
        # The external parent also waits for actual exit, not this timestamp.
        if time.monotonic()-started>=limit:return 1
    return report['intended_worker_exit_code']


def native_command(g,mode,out,admission_path,view=None):
    command=[str(g.BLENDER),'--factory-startup','--disable-autoexec','-b','-t','2','--python-exit-code','1','--python',str(HERE/'native58l.py'),'--','--mode',mode,'--out',str(out),'--admission',str(admission_path)]
    if view:command+=['--view',view]
    return command


def require_positive_pid(pid):
    native_support.require(type(pid) is int and pid>0,'Actual positive integer process identity')


def prior_source(g):
    """Bind the actual source-only admission, bytes, native rows and real exits."""
    admission_path=HERE/'source-attempt.json';terminal_path=HERE/'source-terminal.json'
    prior=support.strict_json(terminal_path);admission=support.strict_json(admission_path)
    run=Path(prior['run']);receipt_path=run/'supervisor-terminal.json';wrapper_path=run/'wrapper-report.json';out=run/'outputs'
    native_support.require(run.is_absolute() and run==run.resolve() and run.parent==(ROOT/'cloud-evidence').resolve() and run.name.startswith(VERSION+'-source-') and run.is_dir() and not run.is_symlink(),'Prior actual source run boundary')
    paths=(admission_path,terminal_path,wrapper_path,receipt_path,HERE/'source-launch-observation.json',g.SOURCE)
    native_support.require(all(p.is_file() and not p.is_symlink() for p in paths) and out.is_dir() and not out.is_symlink(),'Original source-chain files, no symlinks')
    wrapper=support.strict_json(wrapper_path);receipt=support.strict_json(receipt_path)
    native_support.require(terminal_path.read_bytes()==wrapper_path.read_bytes() and prior==wrapper,'Source terminal and wrapper report must be identical original bytes and content')
    native_support.require(all(row['prior_failure_admissions']==list(native_support.FAILURE_ADMISSIONS) and row['acceptance_mode']==native_support.DIAGNOSTIC_MODE and row['full_native_acceptance'] is False for row in (admission,prior,wrapper,receipt)),'Both exact failures and API diagnostic scope in all source records')
    native_support.require(all(row['original_source_stage']=='failed' and row['predecessor']==diagnostic58l.predecessor() for row in (admission,prior,wrapper,receipt)), 'Actual historical combination remains bound; old source stays failed')
    native_support.require(all(row['historical_form_v2_default_failure']==native_support.HISTORICAL_FORM_V2_DEFAULT_FAILURE for row in (prior,wrapper,receipt)), 'Original form-v2 23-face failure retained separately from older 22-face history')
    native_support.require(all(row['stage']=='source' for row in (admission,prior,wrapper,receipt)),'Every source-chain record must have source stage')
    native_support.require(all(row['runner_version']==VERSION and row['run']==str(run) and row['source']==str(g.SOURCE) for row in (admission,prior,wrapper,receipt)),'One source runner version, actual run and original source path')
    native_support.require(g.SOURCE.resolve()==(HERE/'cloud_bank58l_form_v3.blend').resolve(),'Only the original future native source path')
    native_support.require(all(row['runner_sha256']==support.sha(HERE/'run58l_form_v3.py') for row in (admission,prior,wrapper,receipt)),'Actual corrected runner bytes')
    native_support.require(admission['state']=='admitted_one_shot_not_complete' and admission['output']==str(out),'Actual one-shot source admission and output')
    native_support.require(admission['native_sha256']==support.sha(HERE/'native58l.py') and admission['candidate_sha256']==support.sha(g.CANDIDATE_PATH) and admission['binding_sha256']==support.sha(g.BINDING_PATH),'Original admitted native/candidate/binding bytes')
    native_support.require(receipt['limit_seconds']==TOTAL['source'] and deadline58l_v3.accepted(receipt),'Prior complete externally observed source process within the unchanged limit')
    observed=support.strict_json(HERE/'source-launch-observation.json')
    for pid in (admission['wrapper_pid'],admission['supervisor_pid'],prior['worker_pid'],prior['supervisor_pid'],receipt['worker_pid'],receipt['supervisor_pid'],observed['supervisor_pid']):require_positive_pid(pid)
    native_support.require(admission['wrapper_pid']==prior['worker_pid']==receipt['worker_pid'] and admission['supervisor_pid']==prior['supervisor_pid']==receipt['supervisor_pid']==observed['supervisor_pid'] and receipt['worker_pid']!=receipt['supervisor_pid'],'Actual admission/worker/supervisor PID chain')
    native_support.require(type(observed['actual_exit_code']) is int and observed['actual_exit_code']==0 and observed['process_exit_observed'] is True and type(observed['wall_seconds']) in (int,float) and 0<observed['wall_seconds']<TOTAL['source'] and observed['supervisor_terminal_sha256']==support.sha(receipt_path),'External caller must observe the whole launcher exit zero within 120 seconds')
    native_support.require(observed['command']==[str(runtime58l.PYTHON),'-B',str(HERE/'run58l_form_v3.py'),'--run-approved','source'] and observed['runtime']['python_sha256']==runtime58l.PYTHON_SHA and not observed['timeout'] and observed['remaining_owned_pids']==[] and not any(observed.get(k) for k in ('caller_error','cleanup_error','orphan_or_live_owned_detected')), 'Pinned official outside Popen/wait and complete cleanup')
    native_support.require(receipt['diagnostic_acceptance'] is True and prior['diagnostic_acceptance'] is False and prior['diagnostic_prepared_passed'] is True and receipt['historical_default_failure']==prior['historical_default_failure']==native_support.HISTORICAL_DEFAULT_FAILURE,'Diagnostic completion authority and historical failure remain explicit')
    native_support.require(prior['prepared_passed'] is True and prior['passed'] is False and prior['state']=='awaiting_external_process_terminal' and prior['intended_worker_exit_code']==0 and prior['completion_authority']==str(receipt_path),'Prior source prepared under actual external completion authority')
    native_support.require(receipt['terminal_sha256']==support.sha(terminal_path) and receipt['wrapper_report_sha256']==support.sha(wrapper_path),'Prior actual wait4 / both complete terminal bytes')
    admission_sha=support.sha(admission_path);source_sha=support.sha(g.SOURCE);source_bytes=g.SOURCE.stat().st_size
    native_support.require(all(row['admission_sha256']==admission_sha and row['source_sha256']==source_sha and type(row['source_bytes']) is int and row['source_bytes']==source_bytes>0 for row in (prior,wrapper,receipt)),'Actual immutable admission and saved source bytes/size')
    native_support.require(prior['version']==g.VERSION and prior['limits']==dict(total_wall_seconds=TOTAL['source'],cpu_threads=2,native_caps=CAPS,max_wrapper_plus_child_rss_kib=support.MAX_RSS_KIB),'Unchanged original source version and resource limits')
    native_support.require(all(prior[key] is True for key in ('frozen_inputs_unchanged','protected_originals_unchanged','earlier_outputs_unchanged','saved_source_unchanged','source_diagnostic_only')) and not prior['changed_inputs'] and not prior['input_errors'],'Complete unchanged source preparation evidence')
    native_support.require(all(prior[key] is False for key in ('world_loaded','world_modified','world_integration_allowed','contact_acceptance','world_acceptance','global_GOAL','visual_acceptance','weather_acceptance')) and prior['images']==[],'Source-only scope and no renders')
    # Bind every actual native output to the worker bytes sealed by the receipt.
    output_shas=prior['source_output_sha256'];native_support.require(type(output_shas) is dict and output_shas,'Actual source-output identities')
    actual_outputs={str(p):support.sha(p) for p in out.rglob('*') if p.is_file() and not p.is_symlink()}
    native_support.require(all(not p.is_symlink() for p in out.rglob('*')) and actual_outputs==output_shas,'All original native source-output bytes unchanged')
    cpus=receipt['cpu_affinity'];native_support.require(type(cpus) is list and len(cpus)==2 and all(type(cpu) is int and cpu>=0 for cpu in cpus) and cpus==sorted(set(cpus)),'Actual CPU2 receipt')
    candidate=support.strict_json(g.CANDIDATE_PATH);binding=support.strict_json(g.BINDING_PATH);secondary_count=sum(len(row.get('secondary_parameters',[])) for row in candidate['controls'])
    stages=prior['stages'];native_support.require(type(stages) is list and len(stages)==2,'Exactly build then independent fresh-open verify')
    native_support.require(len(prior['exercise'])==2 and all(row['controls']==7 and row['secondary_parameters']==secondary_count and row['manual_edit_preserved'] is True and row['exact_identity_restored'] is True for row in prior['exercise']),'Both complete prescribed source exercise summaries')
    baseline=None;native_pids=[]
    for mode,row in zip(('build','verify'),stages):
        process_path=run/(mode+'.process.json');native_support.require(process_path.is_file() and not process_path.is_symlink(),'Actual process evidence file')
        native_support.require(row==support.strict_json(process_path) and support.process_passed(row) and row['command']==native_command(g,mode,out,admission_path) and row['cpu_affinity']==cpus,'Actual successful prescribed build/verify process row')
        require_positive_pid(row['pid']);native_pids.append(row['pid'])
        native_support.require(row['pid'] not in (receipt['worker_pid'],receipt['supervisor_pid']) and type(row['wall_timeout_seconds']) in (int,float) and 0<row['wall_timeout_seconds']<=CAPS[mode] and type(row['wall_seconds']) in (int,float) and 0<=row['wall_seconds']<=row['wall_timeout_seconds'] and row['wall_timeout_limit_seconds']==720,'Actual separately bounded native process')
        terminal=support.strict_json(out/(mode+'-result.json'));raw_path=out/(mode+'-raw.json');raw=support.strict_json(raw_path)
        native_support.require(terminal['passed'] is True and terminal['state']=='completed' and terminal['version']==g.VERSION and terminal['mode']==mode and terminal['view'] is None and terminal['pid']==row['pid']==raw['pid'] and raw['version']==g.VERSION and raw['cpu_affinity']==cpus,'Actual source native completion, mode and PID')
        native_support.require(terminal['acceptance_mode']==native_support.DIAGNOSTIC_MODE and terminal['full_native_acceptance'] is False and terminal['diagnostic_acceptance'] is True and terminal['validation']==g.validate_native_raw(raw,candidate,binding),'Prior actual source API diagnostic oracle, never full native acceptance')
        native_support.require(terminal['raw_path']==str(raw_path) and terminal['raw_sha256']==support.sha(raw_path) and terminal['source_sha256']==source_sha and type(terminal['source_bytes']) is int and terminal['source_bytes']==source_bytes,'Actual native raw and saved-source identity')
        native_support.require(terminal['source_saved'] is (mode=='build') and type(terminal['images']) is int and terminal['images']==0 and type(terminal['controls_exercised']) is int and terminal['controls_exercised']==7 and type(terminal['secondary_exercised']) is int and terminal['secondary_exercised']==secondary_count and terminal['manual_edit_exercised'] is True and terminal['exact_identity_restored'] is True and terminal['exercise_sha256']==support.sha(out/(mode+'-exercise.json')),'Exactly one source save and original source exercises, no render')
        native_support.require(all(terminal[key] is False for key in ('world_loaded','world_integration_allowed','contact_acceptance','world_acceptance','global_GOAL','visual_acceptance','weather_acceptance')),'Actual native source-only scope')
        native_support.require(not support.error_lines([run/(mode+'.stdout.log'),run/(mode+'.stderr.log')]),'Prior actual native error/leak log')
        if mode=='build':
            native_support.require(raw['opened_filepath']=='','Build starts from factory source without opening a prior file');baseline=native_support.identity(raw)
        else:native_support.require(raw['opened_filepath']==str(g.SOURCE) and native_support.identity(raw)==baseline,'Actual independent no-save fresh-open path and complete identity')
        native_support.require(prior['exercise'][0 if mode=='build' else 1]==validate_exercise(out,mode,candidate,binding,g,raw),'Full original actual exercise report equality')
    native_support.require(len(set(native_pids))==2,'Independent actual build and verify PIDs')
    return prior


def main(arguments=None):
    parser=argparse.ArgumentParser();parser.add_argument('--run-approved',choices=['source']);a=parser.parse_args(arguments)
    if not a.run_approved:print('No-op: prepared source only. No engine, source, image, project mutation or stage admission.');return 0
    started=time.monotonic();stage=a.run_approved;limit=TOTAL[stage]
    import geometry58l as g
    runtime58l.runtime();runtime58l.install_pidfd_bridge()
    diagnostic58l.require_new_admission(stage,g.SOURCE)
    for path in output_exclusions(stage,g.SOURCE):native_support.require(not path.exists() and not path.is_symlink(),'Only absent exact stage outputs may be excluded')
    if stage=='source':native_support.require(not g.SOURCE.exists(),'Never overwrite native source')
    else:prior_source(g)
    cpus=sorted(os.sched_getaffinity(0))[:2];native_support.require(len(cpus)==2,'CPU2 available');os.sched_setaffinity(0,cpus)
    run=Path(tempfile.mkdtemp(prefix=VERSION+'-'+stage+'-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=ROOT/'cloud-evidence'))
    print(run,flush=True)
    def finish(record):
        record.update(runtime=runtime58l.runtime(),original_source_stage='failed',predecessor=diagnostic58l.predecessor(),prior_failure_admissions=list(native_support.FAILURE_ADMISSIONS),acceptance_mode=native_support.DIAGNOSTIC_MODE,full_native_acceptance=False,runner_version=VERSION,runner_sha256=support.sha(HERE/'run58l_form_v3.py'),stage=stage,run=str(run),source=str(g.SOURCE),cpu_affinity=cpus,
                      admission_sha256=support.sha(HERE/(stage+'-attempt.json')) if (HERE/(stage+'-attempt.json')).is_file() else None,source_sha256=None,source_bytes=None,
                      terminal_sha256=support.sha(HERE/(stage+'-terminal.json')) if (HERE/(stage+'-terminal.json')).is_file() else None,
                      wrapper_report_sha256=support.sha(run/'wrapper-report.json') if (run/'wrapper-report.json').is_file() else None)
        if record['passed']:
            prepared=support.strict_json(HERE/(stage+'-terminal.json'))
            peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss+prepared['actual_wrapper_peak_rss_kib']+max((row.get('max_rss_kib') or 0 for row in prepared['stages']),default=0)
            record['conservative_three_level_peak_rss_kib']=peak
            native_support.require(peak<=support.MAX_RSS_KIB,'Supervisor + worker + native peak RSS within 1.5 GiB')
            native_support.require(prepared['acceptance_mode']==native_support.DIAGNOSTIC_MODE and prepared['full_native_acceptance'] is False and prepared['diagnostic_prepared_passed'] is True and prepared['historical_default_failure']==native_support.HISTORICAL_DEFAULT_FAILURE,'Actual prepared diagnostic-only scope')
            native_support.require(prepared['prepared_passed'] is True and prepared['passed'] is False and prepared['worker_pid']==record['worker_pid'] and prepared['supervisor_pid']==record['supervisor_pid'] and prepared['stage']==stage and prepared['run']==str(run) and prepared['source']==str(g.SOURCE) and prepared['runner_version']==VERSION and prepared['runner_sha256']==record['runner_sha256'] and prepared['admission_sha256']==record['admission_sha256'],'Actual complete prepared worker terminal')
            native_support.require((HERE/(stage+'-terminal.json')).read_bytes()==(run/'wrapper-report.json').read_bytes(),'Prepared terminal and wrapper bytes identical')
            record.update(source_sha256=prepared['source_sha256'],source_bytes=prepared['source_bytes'])
        record['diagnostic_acceptance']=bool(record['passed']);record['historical_default_failure']=dict(native_support.HISTORICAL_DEFAULT_FAILURE);record['historical_form_v2_default_failure']=dict(native_support.HISTORICAL_FORM_V2_DEFAULT_FAILURE)
        support.atomic_json(run/'supervisor-terminal.json',record)
    code,record=deadline58l_v3.supervise(lambda:phase(stage,run,started,limit),started=started,limit=limit,finish=finish)
    # No success IO follows this bound. CLI uses os._exit under an armed hard timer,
    # avoiding interpreter shutdown/destructor work outside the real deadline.
    if time.monotonic()-started>=limit:code=1
    if code==0:
        signal.signal(signal.SIGALRM,lambda *_:os._exit(124))
        signal.setitimer(signal.ITIMER_REAL,max(.000001,limit-(time.monotonic()-started)))
    else:signal.setitimer(signal.ITIMER_REAL,0)
    return code

if __name__=='__main__':
    code=main()
    if '--run-approved' in sys.argv:os._exit(code)
    raise SystemExit(code)
