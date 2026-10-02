#!/usr/bin/env python3
"""Default no-op. Separate one-shot source/views stages; never fallback rebuild."""
from __future__ import annotations
import argparse,json,os,resource,signal,struct,sys,tempfile,time,traceback,zlib
from pathlib import Path
sys.dont_write_bytecode=True
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
ORIGINAL=HERE.parent/'source-v1'
VERSION='cloudbank58l-source-runner-v2'
sys.path.insert(0,str(ORIGINAL));sys.path.insert(0,str(ROOT/'source-assets/cloud-bank58/revision-k/import-v1'))
import bounded_support58k as support
import native_support58l as native_support
import deadline58l
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
    required={str(p) for p in [HERE/'run58l_v2.py',HERE/'deadline58l.py',HERE/'SOURCE_BINDING.json',ORIGINAL/'FINAL_SHA256.json',ORIGINAL/'native58l.py',ORIGINAL/'native_support58l.py',ORIGINAL/'geometry58l.py',g.CANDIDATE_PATH,g.BINDING_PATH,ROOT/'source-assets/cloud-bank58/revision-k/import-v1/bounded_support58k.py',ROOT/'source-assets/cloud-bank58/revision-k/poly58k.py']}
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
    expected=native_support.expected_texts(ORIGINAL,c,b)
    require_state(baseline,expected_state(c))
    for p,(row,field,spec) in zip(probes[:-1],specs):
        native_support.require(p['id']==row['id'] and p['field']==field and p['value']==spec['exercise_value'] and p['exact_identity_restored'],'Seven actual prescribed exercise states')
        paths=[Path(p['moved_path']),Path(p['restored_path'])]
        native_support.require(all(x.resolve().parent==out.resolve() for x in paths),'Exercise evidence output boundary')
        native_support.require(support.sha(paths[0])==p['moved_sha256'] and support.sha(paths[1])==p['restored_sha256'],'Exercise original bytes')
        moved=support.strict_json(paths[0]);restored=support.strict_json(paths[1]);native_support.validate_capture(moved,c,b,expected)
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
    native_support.validate_capture(actual['manual'],c,b,expected,manual_base=base);native_support.validate_capture(actual['combined'],c,b,expected,manual_base=base)
    native_support.require(native_support.identity(actual['manual_restored'])==native_support.identity(actual['manual']) and native_support.identity(actual['restored'])==native_support.identity(baseline),'Manual offsets preserved and baseline exactly restored')
    native_support.require(p['geometry']==g.validate_evaluated(c,[native_support.world(v) for v in actual['manual']['mesh']['vertices']],native_support.state_values(actual['manual'])),'Independent manual spatial validation')
    native_support.require(actual['combined']['mesh']['vertices']!=actual['manual']['mesh']['vertices'],'Actual combined control response')
    combined_geometry=g.validate_evaluated(c,[native_support.world(v) for v in actual['combined']['mesh']['vertices']],native_support.state_values(actual['combined']))
    return dict(combined_geometry=combined_geometry,controls=7,secondary_parameters=len(specs)-7,manual_edit_preserved=True,exact_identity_restored=True)

def phase(stage,run,started,limit):
    import geometry58l as g
    out=run/'outputs';out.mkdir()
    admission=dict(state='admitted_one_shot_not_complete',wrapper_pid=os.getpid(),stage=stage,source=str(g.SOURCE),output=str(out),native_sha256=support.sha(ORIGINAL/'native58l.py'),runner_version=VERSION,runner_sha256=support.sha(HERE/'run58l_v2.py'),supervisor_pid=os.getppid(),candidate_sha256=support.sha(g.CANDIDATE_PATH),binding_sha256=support.sha(g.BINDING_PATH),utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
    with (HERE/(stage+'-attempt.json')).open('x') as f:json.dump(admission,f);f.flush();os.fsync(f.fileno())
    print(run,flush=True);report=dict(version=g.VERSION,runner_version=VERSION,stage=stage,state='preparing',passed=False,run=str(run),limits=dict(total_wall_seconds=limit,cpu_threads=2,native_caps=CAPS,max_wrapper_plus_child_rss_kib=support.MAX_RSS_KIB),stages=[],images=[],world_loaded=False,world_modified=False,world_integration_allowed=False,contact_acceptance=False,world_acceptance=False,global_GOAL=False,visual_acceptance=False,weather_acceptance=False,source_diagnostic_only=True)
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
            label=mode+('-'+view if view else '');command=[str(g.BLENDER),'--factory-startup','--disable-autoexec','-b','-t','2','--python-exit-code','1','--python',str(ORIGINAL/'native58l.py'),'--','--mode',mode,'--out',str(out),'--admission',str(HERE/(stage+'-attempt.json'))]
            if view:command+=['--view',view]
            report['state']='running';support.atomic_json(run/'wrapper-report.json',report)
            row=support.run_child(command,run,env,run,min(CAPS[mode],left),label,heartbeat=out/(label+'-progress.json'));report['stages'].append(row);support.atomic_json(run/'wrapper-report.json',report)
            native_support.require(support.process_passed(row),'Native child failed '+label)
            native_support.require(not support.error_lines([run/(label+'.stdout.log'),run/(label+'.stderr.log')]),'Actual native error/leak log')
            terminal=support.strict_json(out/(label+'-result.json'));raw=support.strict_json(out/(label+'-raw.json'))
            native_support.require(terminal['passed'] is True and terminal['state']=='completed' and terminal['version']==g.VERSION and terminal['mode']==mode and terminal['view']==view and terminal['pid']==row['pid']==raw['pid'],'Actual complete child/PID terminal')
            native_support.require(raw['cpu_affinity']==row['cpu_affinity']==cpus and terminal['raw_sha256']==support.sha(out/(label+'-raw.json')),'Actual CPU2/raw bytes')
            native_support.require(not any(terminal[k] for k in ('world_loaded','world_integration_allowed','contact_acceptance','world_acceptance','global_GOAL','visual_acceptance','weather_acceptance')),'Isolated source scope')
            native_support.require(terminal['validation']==g.validate_native_raw(raw,c,b),'Independent complete actual raw validation')
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
                restored=support.strict_json(out/(label+'-restored-raw.json'));native_support.require(terminal['restored_raw_sha256']==support.sha(out/(label+'-restored-raw.json')) and native_support.identity(restored)==native_support.identity(raw),'Actual restored native view identity');report['images'].append(dict(view=view,**image))
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
        prepared=bool(report['passed'])
        report.update(state='awaiting_external_process_terminal' if prepared else 'failed',passed=False,prepared_passed=prepared,
                      completion_authority=str(run/'supervisor-terminal.json'),worker_pid=os.getpid(),
                      worker_prewrite_wall_seconds=time.monotonic()-started,actual_wrapper_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      intended_worker_exit_code=0 if prepared else 1,admission_sha256=admission_sha,**source_observed)
        support.atomic_json(run/'wrapper-report.json',report);support.atomic_json(HERE/(stage+'-terminal.json'),report)
        (run/'worker-intended-exit-code.txt').write_text(str(report['intended_worker_exit_code'])+'\n')
        # This check is AFTER both flush/fsync/replace operations and final file.
        # The external parent also waits for actual exit, not this timestamp.
        if time.monotonic()-started>=limit:return 1
    return report['intended_worker_exit_code']


def prior_source(g):
    prior=support.strict_json(HERE/'source-terminal.json')
    run=Path(prior['run']);receipt_path=run/'supervisor-terminal.json'
    native_support.require(run.resolve().parent==(ROOT/'cloud-evidence').resolve(),'Prior actual source run boundary')
    receipt=support.strict_json(receipt_path)
    native_support.require(deadline58l.accepted(receipt),'Prior complete externally observed source process')
    observed=support.strict_json(HERE/'source-launch-observation.json')
    native_support.require(observed['actual_exit_code']==0 and observed['process_exit_observed'] is True and 0<observed['wall_seconds']<TOTAL['source'] and observed['supervisor_pid']==receipt['supervisor_pid'] and observed['supervisor_terminal_sha256']==support.sha(receipt_path),'External caller must observe the whole launcher exit zero within 120 seconds')
    native_support.require(prior['prepared_passed'] is True and prior['passed'] is False and prior['state']=='awaiting_external_process_terminal' and len(prior['stages'])==2,'Prior source build and fresh-open prepared')
    native_support.require(receipt['worker_pid']==prior['worker_pid'] and receipt['terminal_sha256']==support.sha(HERE/'source-terminal.json') and receipt['wrapper_report_sha256']==support.sha(run/'wrapper-report.json'),'Prior actual wait4 / two terminal bytes')
    native_support.require(receipt['runner_version']==VERSION and prior['runner_version']==VERSION and prior['source_sha256']==support.sha(g.SOURCE),'Same corrected runner and saved source')
    native_support.require(prior['admission_sha256']==support.sha(HERE/'source-attempt.json'),'Prior fixed source admission')
    return prior


def main(arguments=None):
    parser=argparse.ArgumentParser();parser.add_argument('--run-approved',choices=['source','views']);a=parser.parse_args(arguments)
    if not a.run_approved:print('No-op: prepared source only. No engine, source, image, project mutation or stage admission.');return 0
    started=time.monotonic();stage=a.run_approved;limit=TOTAL[stage]
    # Do not accept a prior attempt made by either the rejected or corrected runner.
    for directory in (HERE,ORIGINAL):
        native_support.require(not(directory/(stage+'-terminal.json')).exists() and not(directory/(stage+'-attempt.json')).exists(),'One-shot stage already attempted; preserve evidence and stop')
    import geometry58l as g
    for path in output_exclusions(stage,g.SOURCE):native_support.require(not path.exists() and not path.is_symlink(),'Only absent exact stage outputs may be excluded')
    if stage=='source':native_support.require(not g.SOURCE.exists(),'Never overwrite native source')
    else:prior_source(g)
    cpus=sorted(os.sched_getaffinity(0))[:2];native_support.require(len(cpus)==2,'CPU2 available');os.sched_setaffinity(0,cpus)
    run=Path(tempfile.mkdtemp(prefix='cloudbank58l-source-runner-v2-'+stage+'-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=ROOT/'cloud-evidence'))
    print(run,flush=True)
    def finish(record):
        record.update(runner_version=VERSION,stage=stage,run=str(run),cpu_affinity=cpus,
                      terminal_sha256=support.sha(HERE/(stage+'-terminal.json')) if (HERE/(stage+'-terminal.json')).is_file() else None,
                      wrapper_report_sha256=support.sha(run/'wrapper-report.json') if (run/'wrapper-report.json').is_file() else None)
        if record['passed']:
            prepared=support.strict_json(HERE/(stage+'-terminal.json'))
            peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss+prepared['actual_wrapper_peak_rss_kib']+max((row.get('max_rss_kib') or 0 for row in prepared['stages']),default=0)
            record['conservative_three_level_peak_rss_kib']=peak
            native_support.require(peak<=support.MAX_RSS_KIB,'Supervisor + worker + native peak RSS within 1.5 GiB')
            native_support.require(prepared['prepared_passed'] and prepared['passed'] is False and prepared['worker_pid']==record['worker_pid'],'Actual complete prepared worker terminal')
        support.atomic_json(run/'supervisor-terminal.json',record)
    code,record=deadline58l.supervise(lambda:phase(stage,run,started,limit),started=started,limit=limit,finish=finish)
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
