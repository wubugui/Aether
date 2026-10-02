#!/usr/bin/env python3
"""Default no-op; one saved-source verify-only stage under original v3 supervision."""
from __future__ import annotations
import argparse,json,os,resource,signal,sys,tempfile,time,traceback
from pathlib import Path
sys.dont_write_bytecode=True
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
import recovery58l as r
HERE,ROOT,VERSION=r.HERE,r.ROOT,r.VERSION
original,g,native_support,support,deadline58l_v3=r.original,r.g,r.s,r.support,r.deadline
CAPS=r.CAPS

def phase(stage,run,started,limit):
    r.runtime(); r.require_source()
    out=run/'outputs';out.mkdir()
    admission=dict(predecessor=r.saved_predecessor(check_pins=False),source_sha256=r.SOURCE_SHA,source_bytes=r.SOURCE_BYTES,prior_failure_admissions=list(native_support.FAILURE_ADMISSIONS),acceptance_mode=native_support.DIAGNOSTIC_MODE,full_native_acceptance=False,state='admitted_one_shot_not_complete',wrapper_pid=os.getpid(),stage=stage,run=str(run),source=str(g.SOURCE),output=str(out),native_sha256=support.sha(HERE/'verify_saved58l.py'),runner_version=VERSION,runner_sha256=support.sha(HERE/'run_saved58l.py'),supervisor_pid=os.getppid(),candidate_sha256=support.sha(g.CANDIDATE_PATH),binding_sha256=support.sha(g.BINDING_PATH),utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
    with (r.ATTEMPT).open('x') as f:json.dump(admission,f);f.flush();os.fsync(f.fileno())
    print(run,flush=True);report=dict(predecessor=r.saved_predecessor(check_pins=False),original_source_stage='failed',runtime=r.runtime(),prior_failure_admissions=list(native_support.FAILURE_ADMISSIONS),acceptance_mode=native_support.DIAGNOSTIC_MODE,full_native_acceptance=False,version=g.VERSION,runner_version=VERSION,stage=stage,state='preparing',passed=False,run=str(run),source=str(g.SOURCE),runner_sha256=support.sha(HERE/'run_saved58l.py'),supervisor_pid=os.getppid(),limits=dict(total_wall_seconds=limit,cpu_threads=2,native_caps=CAPS,max_wrapper_plus_child_rss_kib=support.MAX_RSS_KIB),stages=[],images=[],normal_validation_by_stage=[],historical_default_failure=dict(native_support.HISTORICAL_DEFAULT_FAILURE),world_loaded=False,world_modified=False,world_integration_allowed=False,contact_acceptance=False,world_acceptance=False,global_GOAL=False,visual_acceptance=False,weather_acceptance=False,source_diagnostic_only=True)
    admission_path=r.ATTEMPT;admission_sha=support.sha(admission_path)
    excluded=r.exclusions()
    pins={};before={};outputs={};handlers={};source_sha=r.SOURCE_SHA
    def stop(number,frame):raise InterruptedError('Wrapper stop signal '+str(number))
    try:
        for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM):handlers[sig]=signal.signal(sig,stop)
        signal.setitimer(signal.ITIMER_REAL,max(.001,limit-(time.monotonic()-started)));cpus=sorted(os.sched_getaffinity(0))[:2];native_support.require(len(cpus)==2,'CPU2 available');os.sched_setaffinity(0,cpus)
        pins=r.verify_pins(HERE/'FINAL_SHA256.json');native_support.require(support.sha(g.BLENDER)==g.BLENDER_SHA,'Pinned official Blender executable')
        before=original.protected_manifest(root=ROOT,run=run,new_outputs=excluded);support.atomic_json(run/'protected-before.json',before);support.atomic_json(run/'input-sha256.json',pins)
        # Exact source inputs are already frozen and published; retain SHA/size
        # identities without another redundant preparation backup tree.
        b=support.strict_json(g.BINDING_PATH);c=support.strict_json(g.CANDIDATE_PATH);g.validate_candidate(c)
        env=os.environ.copy();env.pop('PYTHONOPTIMIZE',None);env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1')
        for key,name in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data'),('BLENDER_USER_CONFIG','blender-config')]:p=run/name;p.mkdir();env[key]=str(p)
        jobs=[('verify',None)]
        build_raw=native_support.identity(support.strict_json(r.OLD_RUN/'outputs/build-raw.json'))
        for mode,view in jobs:
            native_support.require(support.sha(admission_path)==admission_sha,'Immutable current stage admission')
            native_support.require(r.verify_pins(HERE/'FINAL_SHA256.json')==pins,'Frozen inputs changed between children')
            if source_sha:native_support.require(support.sha(g.SOURCE)==source_sha,'Saved source changed between children')
            native_support.require(all(p.is_file() and support.sha(p)==v for p,v in outputs.items()),'Earlier output altered')
            left=limit-(time.monotonic()-started)-20;native_support.require(left>0,'Total stage budget exhausted')
            label=mode+('-'+view if view else '');command=r.native_command(out,admission_path)
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
            report.setdefault('exercise',[]).append(original.validate_exercise(out,label,c,b,g,raw))
            native_support.require(not terminal['source_saved'] and terminal['images']==0,'Independent no-save fresh-open process')
            native_support.require(terminal['recovery_version']==VERSION and terminal['recovery_stage']==stage and terminal['original_source_stage']=='failed' and terminal['admission_sha256']==admission_sha,'Actual recovery native identity')
            native_support.require(Path(raw['opened_filepath']).resolve()==g.SOURCE.resolve() and native_support.identity(raw)==build_raw,'Actual fresh-open path and complete original build identity')
            if source_sha:native_support.require(support.sha(g.SOURCE)==source_sha,'No-save source unchanged')
            else:source_sha=support.sha(g.SOURCE)
            outputs.update({p:support.sha(p) for p in out.rglob('*') if p.is_file()})
        native_support.require(len(report['stages'])==len(jobs),'All child processes complete');report.update(passed=True,state='completed')
    except BaseException:report.update(passed=False,state='failed',error=traceback.format_exc())
    finally:
        try:
            _,changed,errors=support.inspect_inputs(pins);after=original.protected_manifest(root=ROOT,run=run,new_outputs=excluded);support.atomic_json(run/'protected-after.json',after)
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
        report['recovery_output_sha256']={str(p):v for p,v in outputs.items()}
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


def main(arguments=None):
    parser=argparse.ArgumentParser();parser.add_argument('--run-approved',choices=[r.STAGE]);a=parser.parse_args(arguments)
    if not a.run_approved:print('No-op: saved-source fresh-open recovery only; no stage admission or engine.');return 0
    started=time.monotonic();stage=a.run_approved;limit=r.TOTAL
    r.runtime(); r.install_pidfd_bridge(); r.require_new_admission(stage)
    r.verify_pins(HERE/'FINAL_SHA256.json')
    for path in r.exclusions():native_support.require(not path.exists() and not path.is_symlink(),'Only absent exact stage outputs may be excluded')
    cpus=sorted(os.sched_getaffinity(0))[:2];native_support.require(len(cpus)==2,'CPU2 available');os.sched_setaffinity(0,cpus)
    run=Path(tempfile.mkdtemp(prefix=VERSION+'-'+stage+'-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=ROOT/'cloud-evidence'))
    print(run,flush=True)
    def finish(record):
        record.update(predecessor=r.saved_predecessor(check_pins=False),original_source_stage='failed',runtime=r.runtime(),prior_failure_admissions=list(native_support.FAILURE_ADMISSIONS),acceptance_mode=native_support.DIAGNOSTIC_MODE,full_native_acceptance=False,runner_version=VERSION,runner_sha256=support.sha(HERE/'run_saved58l.py'),stage=stage,run=str(run),source=str(g.SOURCE),cpu_affinity=cpus,
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
        record['diagnostic_acceptance']=bool(record['passed']);record['historical_default_failure']=dict(native_support.HISTORICAL_DEFAULT_FAILURE)
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
